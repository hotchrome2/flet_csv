"""MergeResult model のテスト"""
import pytest
from pathlib import Path
from domain.models.merge_result import MergeResult


class TestMergeResult:
    """MergeResultモデルのテスト"""

    def test_create_successful_merge_result(self):
        """成功した結合結果を作成できる"""
        # Arrange & Act
        result = MergeResult(
            success=True,
            output_path=Path("output.csv"),
            merged_file_count=5,
            total_rows=1000,
            message="結合が成功しました"
        )
        
        # Assert
        assert result.success == True
        assert result.output_path == Path("output.csv")
        assert result.merged_file_count == 5
        assert result.total_rows == 1000
        assert result.message == "結合が成功しました"
        assert result.error_message is None

    def test_create_failed_merge_result(self):
        """失敗した結合結果を作成できる"""
        # Arrange & Act
        result = MergeResult(
            success=False,
            output_path=None,
            merged_file_count=0,
            total_rows=0,
            message="結合に失敗しました",
            error_message="CSVフォーマットが不正です"
        )
        
        # Assert
        assert result.success == False
        assert result.output_path is None
        assert result.merged_file_count == 0
        assert result.total_rows == 0
        assert result.message == "結合に失敗しました"
        assert result.error_message == "CSVフォーマットが不正です"

    def test_merge_result_is_successful_property(self):
        """is_successfulプロパティが正しく動作する"""
        # Arrange
        success_result = MergeResult(
            success=True,
            output_path=Path("output.csv"),
            merged_file_count=3,
            total_rows=500
        )
        
        failed_result = MergeResult(
            success=False,
            output_path=None,
            merged_file_count=0,
            total_rows=0
        )
        
        # Assert
        assert success_result.is_successful is True
        assert failed_result.is_successful is False

    def test_merge_result_has_error_property(self):
        """has_errorプロパティが正しく動作する"""
        # Arrange
        result_with_error = MergeResult(
            success=False,
            output_path=None,
            merged_file_count=0,
            total_rows=0,
            error_message="エラーが発生しました"
        )
        
        result_without_error = MergeResult(
            success=True,
            output_path=Path("output.csv"),
            merged_file_count=1,
            total_rows=100
        )
        
        # Assert
        assert result_with_error.has_error is True
        assert result_without_error.has_error is False

    def test_merge_result_with_default_message(self):
        """デフォルトメッセージで作成できる"""
        # Arrange & Act
        result = MergeResult(
            success=True,
            output_path=Path("output.csv"),
            merged_file_count=2,
            total_rows=200
        )
        
        # Assert
        assert result.message is not None
        assert len(result.message) > 0

    def test_merge_result_string_representation(self):
        """文字列表現が適切"""
        # Arrange
        result = MergeResult(
            success=True,
            output_path=Path("merged.csv"),
            merged_file_count=3,
            total_rows=600,
            message="完了"
        )
        
        # Act
        str_repr = str(result)
        
        # Assert
        assert "merged.csv" in str_repr or "600" in str_repr or "3" in str_repr

    def test_merge_result_repr(self):
        """repr表現が適切"""
        # Arrange
        result = MergeResult(
            success=True,
            output_path=Path("output.csv"),
            merged_file_count=1,
            total_rows=50
        )
        
        # Act
        repr_str = repr(result)
        
        # Assert
        assert "MergeResult" in repr_str

    def test_merge_result_with_string_path(self):
        """文字列パスも受け付ける"""
        # Arrange & Act
        result = MergeResult(
            success=True,
            output_path="output.csv",
            merged_file_count=2,
            total_rows=300
        )
        
        # Assert
        assert result.output_path == Path("output.csv")

    def test_merge_result_success_factory_method(self):
        """成功結果を作成するファクトリメソッド"""
        # Arrange & Act
        result = MergeResult.create_success(
            output_path=Path("merged.csv"),
            merged_file_count=5,
            total_rows=1500
        )
        
        # Assert
        assert result.success == True
        assert result.is_successful == True
        assert result.has_error == False
        assert result.output_path == Path("merged.csv")
        assert result.merged_file_count == 5
        assert result.total_rows == 1500

    def test_merge_result_failure_factory_method(self):
        """失敗結果を作成するファクトリメソッド"""
        # Arrange & Act
        result = MergeResult.create_failure(
            error_message="ファイルが見つかりません",
            merged_file_count=2
        )
        
        # Assert
        assert result.success == False
        assert result.is_successful == False
        assert result.has_error == True
        assert result.output_path is None
        assert result.error_message == "ファイルが見つかりません"
        assert result.merged_file_count == 2
        assert result.total_rows == 0

    def test_merge_result_output_file_name_property(self):
        """output_file_nameプロパティが正しく動作する"""
        # Arrange
        result_with_path = MergeResult(
            success=True,
            output_path=Path("folder/output.csv"),
            merged_file_count=1,
            total_rows=10
        )
        
        result_without_path = MergeResult(
            success=False,
            output_path=None,
            merged_file_count=0,
            total_rows=0
        )
        
        # Assert
        assert result_with_path.output_file_name == "output.csv"
        assert result_without_path.output_file_name is None

