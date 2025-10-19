"""CSVファイルの読み書きを担当するリポジトリ

このモジュールは多様なCSVフォーマットを読み込み、
統一された7列フォーマットに正規化してDomain層に渡します。
"""
from pathlib import Path
import pandas as pd

from domain.models.csv_file import CsvFile
from domain.models.csv_schema import CsvSchema
from domain.exceptions import CsvFileNotFoundError, InvalidCsvFormatError


class CsvRepository:
    """CSVファイルの読み書きを行うリポジトリ
    
    多様なCSVフォーマット（ヘッダーあり/なし、No列あり/なし、
    文字コード多様）を統一された7列フォーマットに正規化します。
    """

    # 正規化後のカラム順序
    COLUMN_ORDER = ["No", "日時", "電圧", "周波数", "パワー", "工事フラグ", "参照"]

    def load(self, file_path: str | Path) -> CsvFile:
        """CSVファイルを読み込み、正規化してCsvFileを返す
        
        Args:
            file_path: 読み込むCSVファイルのパス
            
        Returns:
            正規化された CsvFile オブジェクト
            
        Raises:
            CsvFileNotFoundError: ファイルが存在しない場合
            InvalidCsvFormatError: CSVフォーマットが不正な場合
        """
        # ファイル存在チェック
        path = Path(file_path)
        if not path.exists():
            raise CsvFileNotFoundError(f"CSVファイルが見つかりません: {file_path}")
        
        # 文字コードを自動判定
        encoding = self._detect_encoding(path)
        
        # CSVを読み込み
        df = self._read_csv(path, encoding)
        
        # 正規化
        df = self._normalize(df)
        
        # データの妥当性を検証（日時の妥当性チェック）
        self._validate_data(df, path.name)
        
        # CsvFileオブジェクトを作成して返す
        return CsvFile(file_path=path, data=df)

    def save(self, csv_file: CsvFile, output_dir: str | Path) -> Path:
        """CsvFileを指定ディレクトリに保存
        
        Args:
            csv_file: 保存するCsvFileオブジェクト
            output_dir: 出力先のディレクトリ
            
        Returns:
            保存されたファイルのパス
        """
        from datetime import datetime
        
        output_dir_path = Path(output_dir)
        
        # 出力ディレクトリが存在しない場合は作成
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        # タイムスタンプ付きのファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"merged_{timestamp}.csv"
        output_path = output_dir_path / output_file_name
        
        # UTF-8で保存
        csv_file.data.to_csv(output_path, index=False, encoding="utf-8")
        
        return output_path

    def _detect_encoding(self, file_path: Path) -> str:
        """ファイルの文字コードを自動判定
        
        Windows日本語環境で使われる典型的なエンコーディングを順番に試します。
        
        Args:
            file_path: ファイルパス
            
        Returns:
            検出されたエンコーディング名
        """
        # 試行するエンコーディングのリスト（優先順）
        # utf-8-sig: BOM付きUTF-8
        encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    # ファイル全体を読み込んで、エラーが発生しないか確認
                    f.read()
                # 正常に読み込めたらこのエンコーディングを使用
                return encoding
            except (UnicodeDecodeError, LookupError):
                # このエンコーディングでは読めない、次を試す
                continue
        
        # どれも読めない場合はUTF-8をデフォルトとする
        return "utf-8"

    def _read_csv(self, file_path: Path, encoding: str) -> pd.DataFrame:
        """CSVファイルを読み込む
        
        ヘッダーの有無を自動判定して読み込みます。
        
        Args:
            file_path: ファイルパス
            encoding: 文字コード
            
        Returns:
            読み込んだDataFrame
        """
        # まずヘッダーありとして読み込んでみる
        try:
            df_with_header = pd.read_csv(file_path, encoding=encoding)
            
            # カラム名をチェックしてヘッダーの有無を判定
            # ヘッダーなしの場合、カラム名が日時フォーマットになっている
            first_col_name = str(df_with_header.columns[0])
            
            # カラム名が日時フォーマットなら → ヘッダーなし
            if self._looks_like_datetime(first_col_name):
                df = pd.read_csv(file_path, encoding=encoding, header=None)
                return df
            else:
                # ヘッダーありと判断
                return df_with_header
        except Exception as e:
            raise InvalidCsvFormatError(f"CSVファイルの読み込みに失敗しました: {e}")

    def _looks_like_datetime(self, value: str) -> bool:
        """文字列が日時フォーマットに見えるかチェック
        
        Args:
            value: チェックする文字列
            
        Returns:
            日時フォーマットに見える場合True
        """
        return CsvSchema.validate_datetime_format(value)

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrameを7列統一フォーマットに正規化
        
        Args:
            df: 正規化するDataFrame
            
        Returns:
            正規化されたDataFrame
        """
        # ヘッダーなしの場合（列名が 0, 1, 2, ... となっている）
        if all(isinstance(col, int) for col in df.columns):
            df = self._normalize_headerless(df)
        else:
            df = self._normalize_with_header(df)
        
        # カラムの順番を統一
        df = df[self.COLUMN_ORDER]
        
        return df

    def _normalize_headerless(self, df: pd.DataFrame) -> pd.DataFrame:
        """ヘッダーなしのDataFrameを正規化
        
        ヘッダーなしの場合は5列（日時、電圧、周波数、パワー、工事フラグ）のみ
        No列と参照列を追加します。
        
        Args:
            df: ヘッダーなしのDataFrame
            
        Returns:
            正規化されたDataFrame
        """
        if len(df.columns) != 5:
            raise InvalidCsvFormatError(
                f"ヘッダーなしCSVは5列である必要があります（実際: {len(df.columns)}列）"
            )
        
        # 列名を設定
        df.columns = ["日時", "電圧", "周波数", "パワー", "工事フラグ"]
        
        # No列を追加（1から連番）
        df.insert(0, "No", range(1, len(df) + 1))
        
        # 参照列を追加（0で埋める）
        df["参照"] = 0
        
        return df

    def _normalize_with_header(self, df: pd.DataFrame) -> pd.DataFrame:
        """ヘッダーありのDataFrameを正規化
        
        No列がない場合は追加します。
        
        Args:
            df: ヘッダーありのDataFrame
            
        Returns:
            正規化されたDataFrame
        """
        # No列がない場合は追加
        if "No" not in df.columns:
            df.insert(0, "No", range(1, len(df) + 1))
        
        # 参照列がない場合は追加（念のため）
        if "参照" not in df.columns:
            df["参照"] = 0
        
        # 必須カラムが揃っているかチェック
        missing_cols = CsvSchema.get_missing_columns(list(df.columns))
        if missing_cols:
            raise InvalidCsvFormatError(
                f"必須カラムが不足しています: {', '.join(missing_cols)}"
            )
        
        return df

    def _validate_data(self, df: pd.DataFrame, file_name: str) -> None:
        """データの妥当性を検証
        
        日時カラムの各行をチェックし、不正な値があれば詳細なエラーを発生させます。
        
        Args:
            df: 検証するDataFrame
            file_name: ファイル名（エラーメッセージ用）
            
        Raises:
            InvalidCsvFormatError: 不正な値が検出された場合
        """
        if CsvSchema.TIMESTAMP_COLUMN not in df.columns:
            return
        
        invalid_lines = []
        
        # 各行の日時をチェック（1行目はヘッダーなので、データは2行目から）
        for idx, datetime_value in enumerate(df[CsvSchema.TIMESTAMP_COLUMN], start=2):
            datetime_str = str(datetime_value)
            # 日時の妥当性をチェック
            if not CsvSchema.validate_datetime_value(datetime_str):
                invalid_lines.append(idx)
        
        # 不正な行が見つかった場合はエラーを発生
        if invalid_lines:
            raise InvalidCsvFormatError.with_invalid_lines(
                file_name=file_name,
                invalid_lines=invalid_lines,
                error_type="不正な日時"
            )

