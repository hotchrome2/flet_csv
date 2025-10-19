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
            csv_files = []
            for path in input_paths:
                csv_file = self.repository.load(path)
                csv_files.append(csv_file)

            # 2. CSVファイルを結合
            merged_file = self.merger.merge(csv_files)

            # 3. 結合結果を保存
            output_path = self.repository.save(merged_file, output_dir)

            # 4. 成功結果を返す
            return MergeResult.create_success(
                output_path=output_path,
                merged_file_count=len(csv_files),
                total_rows=len(merged_file.data),
                message=f"CSVファイルの結合が完了しました。出力: {output_path}"
            )

        except CsvFileNotFoundError as e:
            # ファイルが見つからないエラー
            return MergeResult.create_failure(
                error_message=f"ファイルが見つかりません: {str(e)}"
            )

        except InvalidCsvFormatError as e:
            # CSVフォーマットエラー
            return MergeResult.create_failure(
                error_message=f"CSVフォーマットが不正です: {str(e)}"
            )

        except MergeError as e:
            # 結合処理エラー
            return MergeResult.create_failure(
                error_message=f"結合処理でエラーが発生しました: {str(e)}"
            )

        except EmptyDataError as e:
            # 空データエラー
            return MergeResult.create_failure(
                error_message=f"データが空です: {str(e)}"
            )

        except CsvMergerError as e:
            # その他のドメインエラー
            return MergeResult.create_failure(
                error_message=f"CSV結合エラー: {str(e)}"
            )

        except Exception as e:
            # 予期しないエラー
            return MergeResult.create_failure(
                error_message=f"予期しないエラーが発生しました: {str(e)}"
            )

