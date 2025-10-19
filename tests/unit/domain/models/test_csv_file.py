"""CsvFile model のテスト"""
import pytest
import pandas as pd
from pathlib import Path
from domain.models.csv_file import CsvFile
from domain.exceptions import InvalidCsvFormatError, EmptyDataError


# テスト用の有効なカラム名
VALID_COLUMNS = ["日時", "No", "電圧", "周波数", "パワー", "工事フラグ", "参照"]


class TestCsvFile:
    """CsvFileモデルのテスト"""

    def test_create_csv_file_with_valid_data(self):
        """有効なデータでCsvFileを作成できる"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("test.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert csv_file.file_path == file_path
        assert csv_file.row_count == 24
        assert csv_file.column_names == VALID_COLUMNS
        assert not csv_file.is_empty

    def test_csv_file_with_empty_dataframe_raises_error(self):
        """空のDataFrameでCsvFileを作成するとエラー"""
        # Arrange
        file_path = Path("empty.csv")
        empty_data = pd.DataFrame()
        
        # Act & Assert
        with pytest.raises(EmptyDataError) as exc_info:
            CsvFile(file_path=file_path, data=empty_data)
        
        assert "empty" in str(exc_info.value).lower()

    def test_csv_file_properties(self):
        """CsvFileのプロパティが正しく動作する"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("data.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert csv_file.row_count == 24
        assert csv_file.column_count == 7
        assert csv_file.column_names == VALID_COLUMNS
        assert csv_file.file_name == "data.csv"

    def test_csv_file_data_access(self):
        """CsvFileのデータにアクセスできる"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("test.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert isinstance(csv_file.data, pd.DataFrame)
        assert csv_file.data.shape == (24, 7)
        assert list(csv_file.data.columns) == VALID_COLUMNS

    def test_csv_file_is_empty_property(self):
        """is_emptyプロパティが正しく動作する"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("test.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert csv_file.is_empty is False

    def test_csv_file_string_representation(self):
        """CsvFileの文字列表現が適切"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("test.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        str_repr = str(csv_file)
        assert "test.csv" in str_repr
        assert "24" in str_repr  # row count

    def test_csv_file_repr(self):
        """CsvFileのrepr表現が適切"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("data.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        repr_str = repr(csv_file)
        assert "CsvFile" in repr_str
        assert "data.csv" in repr_str

    def test_csv_file_with_pathlib_path(self):
        """pathlibのPathオブジェクトを受け付ける"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("folder/subfolder/test.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert csv_file.file_path == file_path
        assert csv_file.file_name == "test.csv"

    def test_csv_file_with_string_path(self):
        """文字列パスも受け付ける"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = "test.csv"
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert csv_file.file_path == Path(file_path)
        assert csv_file.file_name == "test.csv"

    def test_csv_file_with_invalid_schema_raises_error(self):
        """スキーマが不正なCSVでは作成できない"""
        # Arrange
        file_path = Path("invalid.csv")
        data = pd.DataFrame({
            "日時": ["2024-01-01"],
            "No": [1],
            "電圧": [100.0]
            # 他のカラムが不足
        })
        
        # Act & Assert
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            CsvFile(file_path=file_path, data=data)
        
        error_message = str(exc_info.value)
        assert "周波数" in error_message or "パワー" in error_message

    def test_csv_file_with_extra_columns(self):
        """余分なカラムがあっても作成できる"""
        # Arrange: 1日分の正しいデータ（24時間）
        file_path = Path("extra.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 25)),
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
            "備考": ["テスト"] * 24
        })
        
        # Act
        csv_file = CsvFile(file_path=file_path, data=data)
        
        # Assert
        assert csv_file.row_count == 24
        assert csv_file.column_count == 8  # 7 + 1
        assert "備考" in csv_file.column_names

    def test_csv_file_with_incomplete_daily_data(self):
        """1日分のデータが不完全な場合はエラー"""
        # Arrange: 00時〜22時（23時が欠けている）
        file_path = Path("incomplete.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(23)]
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 24)),
            "電圧": [100] * 23,
            "周波数": [50] * 23,
            "パワー": [1000] * 23,
            "工事フラグ": [0] * 23,
            "参照": [1] * 23,
        })
        
        # Act & Assert
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            CsvFile(file_path=file_path, data=data)
        
        assert "1日分のデータ（00時〜23時）" in str(exc_info.value)

    def test_csv_file_with_multiple_days_data(self):
        """複数日にまたがるデータの場合はエラー"""
        # Arrange: 2日分のデータ
        file_path = Path("multiday.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        datetime_list += ["2025/10/19 00:00:00"]
        
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 26)),
            "電圧": [100] * 25,
            "周波数": [50] * 25,
            "パワー": [1000] * 25,
            "工事フラグ": [0] * 25,
            "参照": [1] * 25,
        })
        
        # Act & Assert
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            CsvFile(file_path=file_path, data=data)
        
        assert "1日分のデータ（00時〜23時）" in str(exc_info.value)

    def test_csv_file_with_wrong_start_time(self):
        """00時以外から始まるデータの場合はエラー"""
        # Arrange: 01時〜23時（00時が欠けている）
        file_path = Path("wrong_start.csv")
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(1, 24)]
        
        data = pd.DataFrame({
            "日時": datetime_list,
            "No": list(range(1, 24)),
            "電圧": [100] * 23,
            "周波数": [50] * 23,
            "パワー": [1000] * 23,
            "工事フラグ": [0] * 23,
            "参照": [1] * 23,
        })
        
        # Act & Assert
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            CsvFile(file_path=file_path, data=data)
        
        assert "1日分のデータ（00時〜23時）" in str(exc_info.value)

