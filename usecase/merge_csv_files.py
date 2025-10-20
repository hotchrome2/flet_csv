"""CSV結合ユースケース

このモジュールは、複数のCSVファイルを結合するユースケースを提供します。
"""
from pathlib import Path

from domain.models.merge_result import MergeResult
from domain.exceptions import (
    CsvFileNotFoundError,
    InvalidCsvFormatError,
    MergeError,
    EmptyDataError,
    CsvMergerError,
)
from infra.repositories.csv_repository import CsvRepository
from domain.services.csv_merger import CsvMerger


class MergeCsvFilesUseCase:
    """CSV結合ユースケース
    
    複数のCSVファイルを読み込み、結合して保存するユースケースを実行します。
    
    Attributes:
        repository: CSVファイルの読み書きを担当するリポジトリ
        merger: CSV結合のドメインサービス
    """

    def __init__(
        self,
        repository: CsvRepository | None = None,
        merger: CsvMerger | None = None
    ):
        """初期化
        
        Args:
            repository: CSVリポジトリ（Noneの場合は新規作成）
            merger: CSVマージャー（Noneの場合は新規作成）
        """
        self.repository = repository or CsvRepository()
        self.merger = merger or CsvMerger()

    def execute(
        self,
        input_paths: list[str | Path],
        output_dir: str | Path
    ) -> MergeResult:
        """CSV結合ユースケースを実行
        
        Args:
            input_paths: 入力CSVファイルのパスリスト
            output_dir: 出力先ディレクトリ
            
        Returns:
            結合結果を表すMergeResultオブジェクト
        """
        # 入力ファイルリストの検証
        if not input_paths:
            return MergeResult.create_failure(
                error_message="入力ファイルが指定されていません。"
            )

        try:
            # 1. ファイルを読み込み
            csv_files = [self.repository.load(path) for path in input_paths]
            # 2-4. 結合して保存し、結果を生成
            return self._merge_and_save(csv_files, output_dir)
        except Exception as e:
            return self._handle_exception(e)


    def execute_from_zip(
        self,
        zip_path: str | Path,
        output_dir: str | Path
    ) -> MergeResult:
        """ZIP内のCSVを読み込み結合するユースケースを実行
        
        Args:
            zip_path: 入力ZIPファイルのパス
            output_dir: 出力先ディレクトリ
        
        Returns:
            結合結果を表すMergeResultオブジェクト
        """
        try:
            # 1. ZIPからCSV群を読み込み
            csv_files = self.repository.load_from_zip(zip_path)
            # 空チェック
            if not csv_files:
                return MergeResult.create_failure(
                    error_message="ZIPファイル内にCSVファイルがありません"
                )
            # 2-4. 結合して保存し、結果を生成
            return self._merge_and_save(csv_files, output_dir)
        except Exception as e:
            return self._handle_exception(e)

    # 共通処理の抽出
    def _merge_and_save(self, csv_files, output_dir: str | Path) -> MergeResult:
        merged_file = self.merger.merge(csv_files)
        output_path = self.repository.save(merged_file, output_dir)
        return MergeResult.create_success(
            output_path=output_path,
            merged_file_count=len(csv_files),
            total_rows=len(merged_file.data),
            message=f"CSVファイルの結合が完了しました。出力: {output_path}"
        )

    def _handle_exception(self, e: Exception) -> MergeResult:
        if isinstance(e, CsvFileNotFoundError):
            return MergeResult.create_failure(error_message=f"ファイルが見つかりません: {str(e)}")
        if isinstance(e, InvalidCsvFormatError):
            return MergeResult.create_failure(error_message=f"CSVフォーマットが不正です: {str(e)}")
        if isinstance(e, MergeError):
            return MergeResult.create_failure(error_message=f"結合処理でエラーが発生しました: {str(e)}")
        if isinstance(e, EmptyDataError):
            return MergeResult.create_failure(error_message=f"データが空です: {str(e)}")
        if isinstance(e, CsvMergerError):
            return MergeResult.create_failure(error_message=f"CSV結合エラー: {str(e)}")
        return MergeResult.create_failure(error_message=f"予期しないエラーが発生しました: {str(e)}")

