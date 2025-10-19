"""CSVファイルのドメインモデル

このモジュールはCSVファイルを表現するドメインモデルを定義します。
"""
from pathlib import Path
import pandas as pd

from domain.exceptions import EmptyDataError, InvalidCsvFormatError
from domain.models.csv_schema import CsvSchema


class CsvFile:
    """CSVファイルを表現するドメインモデル
    
    CSVファイルのパス、データ、メタデータを保持します。
    
    Attributes:
        file_path: CSVファイルのパス
        data: CSVデータ（pandas.DataFrame）
    """

    def __init__(
        self,
        file_path: str | Path,
        data: pd.DataFrame,
        skip_daily_validation: bool = False
    ):
        """CsvFileを初期化
        
        Args:
            file_path: CSVファイルのパス（文字列またはPathオブジェクト）
            data: CSVデータ（pandas.DataFrame）
            skip_daily_validation: 1日分データ検証をスキップするか（結合後のファイル用）
            
        Raises:
            EmptyDataError: dataが空の場合
            InvalidCsvFormatError: 必須カラムが不足している場合
        """
        # パスをPathオブジェクトに変換
        self._file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # データが空でないかチェック
        if data.empty:
            raise EmptyDataError(f"CSV file '{self.file_name}' contains no data")
        
        # スキーマバリデーション（必須カラムのチェック）
        CsvSchema.validate_and_raise(list(data.columns))
        
        # 1日分のデータ制約の検証（スキップオプションで無効化可能）
        if not skip_daily_validation and CsvSchema.TIMESTAMP_COLUMN in data.columns:
            datetime_values = data[CsvSchema.TIMESTAMP_COLUMN].astype(str).tolist()
            if not CsvSchema.validate_daily_time_range(datetime_values):
                raise InvalidCsvFormatError(
                    f"CSV file '{self.file_name}' は1日分のデータ（00時〜23時）を含む必要があります"
                )
        
        self._data = data

    @property
    def file_path(self) -> Path:
        """ファイルパスを取得"""
        return self._file_path

    @property
    def data(self) -> pd.DataFrame:
        """CSVデータを取得"""
        return self._data

    @property
    def file_name(self) -> str:
        """ファイル名を取得"""
        return self._file_path.name

    @property
    def row_count(self) -> int:
        """行数を取得"""
        return len(self._data)

    @property
    def column_count(self) -> int:
        """列数を取得"""
        return len(self._data.columns)

    @property
    def column_names(self) -> list[str]:
        """カラム名のリストを取得"""
        return list(self._data.columns)

    @property
    def is_empty(self) -> bool:
        """データが空かどうかを判定"""
        return self._data.empty

    def __str__(self) -> str:
        """文字列表現"""
        return f"CsvFile('{self.file_name}', {self.row_count} rows, {self.column_count} columns)"

    def __repr__(self) -> str:
        """repr表現"""
        return f"CsvFile(file_path={self._file_path!r}, rows={self.row_count}, columns={self.column_count})"

