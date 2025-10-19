"""Domain exceptions のテスト"""
import pytest
from domain.exceptions import (
    CsvMergerError,
    InvalidCsvFormatError,
    CsvFileNotFoundError,
    MergeError,
    EmptyDataError,
)


class TestDomainExceptions:
    """ドメイン例外クラスのテスト"""

    def test_csv_merger_error_is_base_exception(self):
        """CsvMergerErrorは基底例外クラスである"""
        error = CsvMergerError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_invalid_csv_format_error_inherits_from_base(self):
        """InvalidCsvFormatErrorはCsvMergerErrorを継承する"""
        error = InvalidCsvFormatError("invalid format")
        assert isinstance(error, CsvMergerError)
        assert isinstance(error, Exception)
        assert str(error) == "invalid format"

    def test_csv_file_not_found_error_inherits_from_base(self):
        """CsvFileNotFoundErrorはCsvMergerErrorを継承する"""
        error = CsvFileNotFoundError("file not found")
        assert isinstance(error, CsvMergerError)
        assert str(error) == "file not found"

    def test_merge_error_inherits_from_base(self):
        """MergeErrorはCsvMergerErrorを継承する"""
        error = MergeError("merge failed")
        assert isinstance(error, CsvMergerError)
        assert str(error) == "merge failed"

    def test_empty_data_error_inherits_from_base(self):
        """EmptyDataErrorはCsvMergerErrorを継承する"""
        error = EmptyDataError("no data")
        assert isinstance(error, CsvMergerError)
        assert str(error) == "no data"

    def test_exceptions_can_be_raised_and_caught(self):
        """例外が正しく発生・キャッチできる"""
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            raise InvalidCsvFormatError("test error")
        
        assert "test error" in str(exc_info.value)

    def test_exceptions_can_be_caught_by_base_exception(self):
        """すべてのドメイン例外は基底例外でキャッチできる"""
        with pytest.raises(CsvMergerError):
            raise InvalidCsvFormatError("test")

        with pytest.raises(CsvMergerError):
            raise CsvFileNotFoundError("test")

        with pytest.raises(CsvMergerError):
            raise MergeError("test")

        with pytest.raises(CsvMergerError):
            raise EmptyDataError("test")

    def test_invalid_csv_format_error_with_line_numbers(self):
        """InvalidCsvFormatErrorは行番号情報を含むエラーメッセージを生成できる"""
        error = InvalidCsvFormatError.with_invalid_lines(
            file_name="test.csv",
            invalid_lines=[1, 2, 3, 5, 7, 8, 9],
            error_type="不正な日時"
        )
        
        error_message = str(error)
        assert "test.csv" in error_message
        assert "不正な日時" in error_message
        # 連続する行番号は範囲として表示される
        assert "1行目から3行目" in error_message or "1-3行目" in error_message
        assert "5行目" in error_message
        assert "7行目から9行目" in error_message or "7-9行目" in error_message

    def test_invalid_csv_format_error_with_single_line(self):
        """InvalidCsvFormatErrorは単一行のエラーメッセージを生成できる"""
        error = InvalidCsvFormatError.with_invalid_lines(
            file_name="test.csv",
            invalid_lines=[10],
            error_type="不正な値"
        )
        
        error_message = str(error)
        assert "test.csv" in error_message
        assert "10行目" in error_message
        assert "不正な値" in error_message

    def test_invalid_csv_format_error_with_all_consecutive_lines(self):
        """InvalidCsvFormatErrorは全て連続した行番号を範囲として表示できる"""
        error = InvalidCsvFormatError.with_invalid_lines(
            file_name="data.csv",
            invalid_lines=[5, 6, 7, 8, 9, 10],
            error_type="フォーマットエラー"
        )
        
        error_message = str(error)
        assert "data.csv" in error_message
        assert "5行目から10行目" in error_message or "5-10行目" in error_message
        assert "フォーマットエラー" in error_message

