"""CSV結合ドメインサービス

このモジュールは複数のCSVファイルを1つに結合する
ドメインサービスを提供します。
"""
from pathlib import Path
import pandas as pd
from datetime import timedelta

from domain.models.csv_file import CsvFile
from domain.models.csv_schema import CsvSchema
from domain.exceptions import MergeError


class CsvMerger:
    """複数のCSVファイルを結合するドメインサービス
    
    このサービスは、複数のCsvFileオブジェクトを受け取り、
    入力が連続した日付であることを検証した上で、
    日時順にソートして1つのCsvFileに結合します。
    """

    def merge(self, csv_files: list[CsvFile]) -> CsvFile:
        """複数のCSVファイルを1つに結合
        
        以下の処理を行います：
        1. 入力の妥当性チェック
        2. 連続日検証（最小日〜最大日に欠損日がないこと、重複日がないこと）
        3. 全てのDataFrameを結合
        4. 日時カラムで昇順ソート
        5. 日時の重複チェック
        6. No列の再採番（1から連番）
        7. 新しいCsvFileオブジェクトを生成して返却
        
        Args:
            csv_files: 結合するCSVファイルのリスト
            
        Returns:
            結合後の新しいCsvFileオブジェクト
            
        Raises:
            ValueError: 空リストが渡された場合
            MergeError: 日時の重複がある場合
        """
        # 空リストチェック
        if not csv_files:
            raise ValueError("結合するCSVファイルが指定されていません（空リスト）")
        
        # 1ファイルのみの場合は、No列を再採番して返す（連続日検証は不要）
        if len(csv_files) == 1:
            return self._renumber_and_create_csv_file(csv_files[0].data)
        
        # 入力CSVが連続日であることを検証
        self._validate_continuous_days(csv_files)

        # 複数ファイルの結合
        dataframes = [csv_file.data for csv_file in csv_files]
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # 日時カラムでソート（datetime型に変換してソート）
        timestamp_col = CsvSchema.TIMESTAMP_COLUMN
        merged_df[timestamp_col] = pd.to_datetime(merged_df[timestamp_col])
        merged_df = merged_df.sort_values(by=timestamp_col).reset_index(drop=True)
        # ソート後、標準フォーマット（YYYY/MM/DD HH:MM:SS）に統一
        # 注: 入力は様々なフォーマット（ISO 8601など）を受け入れるが、
        #     出力は統一されたフォーマットに変換される
        merged_df[timestamp_col] = merged_df[timestamp_col].dt.strftime("%Y/%m/%d %H:%M:%S")
        
        # 日時の重複チェック
        self._check_duplicate_datetime(merged_df)
        
        # No列の再採番
        return self._renumber_and_create_csv_file(merged_df)

    def _validate_continuous_days(self, csv_files: list[CsvFile]) -> None:
        """入力CSVが連続した日付で並ぶことを検証
        
        前提:
          - 各CsvFileは1日分（00〜23時）のデータ
        検証:
          - 同一日付の重複がないこと（重複日なし）
          - 最小日から最大日まで欠損日がないこと（完全連続）
        違反時:
          - MergeError を送出
        """
        # 各ファイルの日付（date型）を抽出
        dates = []
        for csv_file in csv_files:
            dt_series = pd.to_datetime(csv_file.data[CsvSchema.TIMESTAMP_COLUMN])
            unique_dates = dt_series.dt.date.unique()
            if len(unique_dates) != 1:
                # 1日分制約は通常 CsvFile 側で保証されるが、念のため
                raise MergeError("各入力CSVは1日分のデータである必要があります")
            dates.append(unique_dates[0])

        # 重複日付の検出
        if len(set(dates)) != len(dates):
            raise MergeError("入力CSVに同一日付のファイルが含まれています（重複日）")

        # 連続性チェック（最小日〜最大日が連続しているか）
        min_date = min(dates)
        max_date = max(dates)
        unique_count = len(set(dates))
        expected_count = (max_date - min_date).days + 1
        if expected_count != unique_count:
            raise MergeError("入力CSVは連続した日付である必要があります（欠損日が存在）")

    def _check_duplicate_datetime(self, df: pd.DataFrame) -> None:
        """日時カラムの重複をチェック
        
        Args:
            df: チェック対象のDataFrame
            
        Raises:
            MergeError: 重複がある場合
        """
        timestamp_col = CsvSchema.TIMESTAMP_COLUMN
        duplicates = df[timestamp_col].duplicated()
        
        if duplicates.any():
            # 重複している日時を取得
            duplicate_values = df[duplicates][timestamp_col].unique()
            duplicate_str = ", ".join(str(v) for v in duplicate_values[:5])
            
            raise MergeError(
                f"日時の重複が検出されました: {duplicate_str}"
                + ("..." if len(duplicate_values) > 5 else "")
            )

    def _renumber_and_create_csv_file(self, df: pd.DataFrame) -> CsvFile:
        """No列を再採番して新しいCsvFileを作成
        
        Args:
            df: データフレーム
            
        Returns:
            No列が再採番された新しいCsvFile
        """
        # No列を1から連番で再採番
        df = df.copy()
        df["No"] = range(1, len(df) + 1)
        
        # 新しいCsvFileオブジェクトを作成
        # 結合後は複数日分のデータなので、1日分制約の検証をスキップ
        return CsvFile(
            file_path=Path("merged.csv"),
            data=df,
            skip_daily_validation=True
        )

