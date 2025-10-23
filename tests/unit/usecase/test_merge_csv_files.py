"""MergeCsvFilesUseCaseの単体テスト

このモジュールは、CSV結合ユースケースの統合テストを提供します。
"""
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock

from usecase.merge_csv_files import MergeCsvFilesUseCase
from domain.models.csv_file import CsvFile
from domain.models.merge_result import MergeResult
from domain.exceptions import (
    CsvFileNotFoundError,
    InvalidCsvFormatError,
    MergeError,
    EmptyDataError,
)


class TestMergeCsvFilesUseCase:
    """MergeCsvFilesUseCaseクラスのテスト"""

    @pytest.fixture
    def mock_repository(self):
        """モックリポジトリのフィクスチャ"""
        return Mock()

    @pytest.fixture
    def mock_merger(self):
        """モックマージャーのフィクスチャ"""
        return Mock()

    @pytest.fixture
    def usecase(self, mock_repository, mock_merger):
        """UseCaseインスタンスのフィクスチャ"""
        return MergeCsvFilesUseCase(
            repository=mock_repository,
            merger=mock_merger
        )

    def test_successful_merge_with_two_files(self, usecase, mock_repository, mock_merger):
        """2つのCSVファイルを正常に結合できる"""
        # Arrange
        input_paths = [
            Path("tests/fixtures/csv/full_format.csv"),
            Path("tests/fixtures/csv/no_column_missing.csv"),
        ]
        output_dir = Path("static/downloads")

        # モックの設定
        mock_csv_file1 = Mock(spec=CsvFile)
        mock_csv_file2 = Mock(spec=CsvFile)
        mock_merged_file = Mock(spec=CsvFile)
        mock_merged_file.data = [1, 2, 3, 4, 5]  # 5行のデータ
        mock_output_path = Path("static/downloads/merged_20251019_120000.csv")

        mock_repository.load.side_effect = [mock_csv_file1, mock_csv_file2]
        mock_merger.merge.return_value = mock_merged_file
        mock_repository.save.return_value = mock_output_path

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is True
        assert result.output_path == mock_output_path
        assert mock_repository.load.call_count == 2
        mock_merger.merge.assert_called_once()
        mock_repository.save.assert_called_once_with(mock_merged_file, output_dir)

    def test_successful_merge_with_single_file(self, usecase, mock_repository, mock_merger):
        """1つのCSVファイルでも正常に処理できる"""
        # Arrange
        input_paths = [Path("tests/fixtures/csv/full_format.csv")]
        output_dir = Path("static/downloads")

        mock_csv_file = Mock(spec=CsvFile)
        mock_merged_file = Mock(spec=CsvFile)
        mock_merged_file.data = [1, 2, 3]  # 3行のデータ
        mock_output_path = Path("static/downloads/merged_20251019_120000.csv")

        mock_repository.load.return_value = mock_csv_file
        mock_merger.merge.return_value = mock_merged_file
        mock_repository.save.return_value = mock_output_path

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is True
        assert result.output_path == mock_output_path

    def test_failure_when_file_not_found(self, usecase, mock_repository):
        """ファイルが見つからない場合、失敗を返す"""
        # Arrange
        input_paths = [Path("nonexistent.csv")]
        output_dir = Path("static/downloads")

        mock_repository.load.side_effect = CsvFileNotFoundError(
            "CSVファイルが見つかりません: nonexistent.csv"
        )

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is False
        assert "ファイルが見つかりません" in result.error_message
        assert "nonexistent.csv" in result.error_message

    def test_failure_when_invalid_csv_format(self, usecase, mock_repository):
        """CSVフォーマットが不正な場合、失敗を返す"""
        # Arrange
        input_paths = [Path("tests/fixtures/csv/invalid_dates.csv")]
        output_dir = Path("static/downloads")

        mock_repository.load.side_effect = InvalidCsvFormatError(
            "invalid_dates.csv: 不正な日時が検出されました（3行目、5行目から6行目）"
        )

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is False
        assert "CSVフォーマットが不正です" in result.error_message
        assert "invalid_dates.csv" in result.error_message

    def test_failure_when_merge_error_occurs(self, usecase, mock_repository, mock_merger):
        """結合時にエラーが発生した場合、失敗を返す"""
        # Arrange
        input_paths = [
            Path("tests/fixtures/csv/full_format.csv"),
            Path("tests/fixtures/csv/full_format.csv"),  # 重複したファイル
        ]
        output_dir = Path("static/downloads")

        mock_csv_file1 = Mock(spec=CsvFile)
        mock_csv_file2 = Mock(spec=CsvFile)

        mock_repository.load.side_effect = [mock_csv_file1, mock_csv_file2]
        mock_merger.merge.side_effect = MergeError(
            "日時の重複が検出されました: 2025/10/18 10:00:00"
        )

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is False
        assert "結合処理でエラーが発生しました" in result.error_message
        assert "日時の重複" in result.error_message

    def test_failure_when_empty_data(self, usecase, mock_repository):
        """空のCSVファイルの場合、失敗を返す"""
        # Arrange
        input_paths = [Path("tests/fixtures/csv/empty.csv")]
        output_dir = Path("static/downloads")

        mock_repository.load.side_effect = EmptyDataError(
            "CSVファイルが空です"
        )

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is False
        assert "データが空です" in result.error_message

    def test_failure_when_empty_file_list(self, usecase):
        """入力ファイルリストが空の場合、失敗を返す"""
        # Arrange
        input_paths = []
        output_dir = Path("static/downloads")

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is False
        assert "入力ファイルが指定されていません" in result.error_message

    def test_returns_merge_result_object(self, usecase, mock_repository, mock_merger):
        """MergeResultオブジェクトを返す"""
        # Arrange
        input_paths = [Path("tests/fixtures/csv/full_format.csv")]
        output_dir = Path("static/downloads")

        mock_csv_file = Mock(spec=CsvFile)
        mock_merged_file = Mock(spec=CsvFile)
        mock_merged_file.data = [1, 2, 3, 4]  # 4行のデータ
        mock_output_path = Path("static/downloads/merged_20251019_120000.csv")

        mock_repository.load.return_value = mock_csv_file
        mock_merger.merge.return_value = mock_merged_file
        mock_repository.save.return_value = mock_output_path

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert isinstance(result, MergeResult)

    def test_multiple_files_merge(self, usecase, mock_repository, mock_merger):
        """複数ファイル（3つ以上）を正常に結合できる"""
        # Arrange
        input_paths = [
            Path("tests/fixtures/csv/file1.csv"),
            Path("tests/fixtures/csv/file2.csv"),
            Path("tests/fixtures/csv/file3.csv"),
        ]
        output_dir = Path("static/downloads")

        mock_csv_files = [Mock(spec=CsvFile) for _ in range(3)]
        mock_merged_file = Mock(spec=CsvFile)
        mock_merged_file.data = [1, 2, 3, 4, 5, 6, 7]  # 7行のデータ
        mock_output_path = Path("static/downloads/merged_20251019_120000.csv")

        mock_repository.load.side_effect = mock_csv_files
        mock_merger.merge.return_value = mock_merged_file
        mock_repository.save.return_value = mock_output_path

        # Act
        result = usecase.execute(input_paths, output_dir)

        # Assert
        assert result.is_successful is True
        assert mock_repository.load.call_count == 3
        # mergerには3つのCsvFileオブジェクトが渡されることを確認
        called_csv_files = mock_merger.merge.call_args[0][0]
        assert len(called_csv_files) == 3

    # ZIP入力関連のテストは要件撤廃につき削除

    # ZIP入力関連のテストは要件撤廃につき削除

    # ZIP入力関連のテストは要件撤廃につき削除

