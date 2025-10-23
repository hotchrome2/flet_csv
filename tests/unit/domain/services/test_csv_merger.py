"""CsvMerger service のテスト"""
import pytest
import pandas as pd
from pathlib import Path

from domain.services.csv_merger import CsvMerger
from domain.models.csv_file import CsvFile
from domain.exceptions import MergeError


class TestCsvMerger:
    """CsvMergerドメインサービスのテスト"""

    @pytest.fixture
    def csv_merger(self):
        """CsvMergerインスタンスを提供"""
        return CsvMerger()

    @pytest.fixture
    def valid_csv_file_day1(self):
        """1日目のCSVファイル（2025/10/18）"""
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "No": list(range(1, 25)),
            "日時": datetime_list,
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        return CsvFile(file_path="day1.csv", data=data)

    @pytest.fixture
    def valid_csv_file_day2(self):
        """2日目のCSVファイル（2025/10/19）"""
        datetime_list = [f"2025/10/19 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "No": list(range(1, 25)),
            "日時": datetime_list,
            "電圧": [105] * 24,
            "周波数": [51] * 24,
            "パワー": [1100] * 24,
            "工事フラグ": [0] * 24,
            "参照": [0] * 24,
        })
        return CsvFile(file_path="day2.csv", data=data)

    @pytest.fixture
    def valid_csv_file_day3(self):
        """3日目のCSVファイル（2025/10/20）"""
        datetime_list = [f"2025/10/20 {hour:02d}:00:00" for hour in range(24)]
        data = pd.DataFrame({
            "No": list(range(1, 25)),
            "日時": datetime_list,
            "電圧": [110] * 24,
            "周波数": [52] * 24,
            "パワー": [1200] * 24,
            "工事フラグ": [1] * 24,
            "参照": [1] * 24,
        })
        return CsvFile(file_path="day3.csv", data=data)

    def test_merge_two_files(self, csv_merger, valid_csv_file_day1, valid_csv_file_day2):
        """2つのCSVファイルを正常に結合できる"""
        # Arrange
        csv_files = [valid_csv_file_day1, valid_csv_file_day2]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        assert isinstance(result, CsvFile)
        assert result.row_count == 48  # 24 + 24
        assert result.column_count == 7
        assert "日時" in result.column_names

    def test_merge_multiple_files(
        self, csv_merger, valid_csv_file_day1, valid_csv_file_day2, valid_csv_file_day3
    ):
        """3つ以上のCSVファイルを正常に結合できる"""
        # Arrange
        csv_files = [valid_csv_file_day1, valid_csv_file_day2, valid_csv_file_day3]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        assert result.row_count == 72  # 24 * 3
        assert result.column_count == 7

    def test_merge_sorts_by_datetime_ascending(
        self, csv_merger, valid_csv_file_day1, valid_csv_file_day2, valid_csv_file_day3
    ):
        """結合後のデータが日時で昇順にソートされる"""
        # Arrange: 意図的に逆順で渡す
        csv_files = [valid_csv_file_day3, valid_csv_file_day1, valid_csv_file_day2]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        datetimes = result.data["日時"].tolist()
        assert datetimes[0] == "2025/10/18 00:00:00"  # 最初
        assert datetimes[-1] == "2025/10/20 23:00:00"  # 最後
        # ソート確認
        assert datetimes == sorted(datetimes)

    def test_merge_renumbers_no_column(self, csv_merger, valid_csv_file_day1, valid_csv_file_day2):
        """結合後のNo列が1から連番で採番される"""
        # Arrange
        csv_files = [valid_csv_file_day1, valid_csv_file_day2]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        no_values = result.data["No"].tolist()
        assert no_values == list(range(1, 49))  # 1〜48

    def test_merge_detects_duplicate_datetime(self, csv_merger):
        """同じ日時のデータが複数ある場合にMergeErrorを発生させる"""
        # Arrange: 同じ日時を含む2つのファイル
        datetime_list = [f"2025/10/18 {hour:02d}:00:00" for hour in range(24)]
        
        data1 = pd.DataFrame({
            "No": list(range(1, 25)),
            "日時": datetime_list,
            "電圧": [100] * 24,
            "周波数": [50] * 24,
            "パワー": [1000] * 24,
            "工事フラグ": [0] * 24,
            "参照": [1] * 24,
        })
        
        data2 = pd.DataFrame({
            "No": list(range(1, 25)),
            "日時": datetime_list,  # 同じ日時
            "電圧": [105] * 24,
            "周波数": [51] * 24,
            "パワー": [1100] * 24,
            "工事フラグ": [0] * 24,
            "参照": [0] * 24,
        })
        
        csv_file1 = CsvFile(file_path="dup1.csv", data=data1)
        csv_file2 = CsvFile(file_path="dup2.csv", data=data2)
        
        # Act & Assert
        with pytest.raises(MergeError) as exc_info:
            csv_merger.merge([csv_file1, csv_file2])
        
        assert "重複" in str(exc_info.value)

    def test_merge_requires_consecutive_days(self, csv_merger, valid_csv_file_day1, valid_csv_file_day3):
        """日付が連続でない場合はエラーになる"""
        # Arrange: 2025/10/18 と 2025/10/20（19日が欠損）
        csv_files = [valid_csv_file_day1, valid_csv_file_day3]
        
        # Act & Assert
        with pytest.raises(MergeError) as exc_info:
            csv_merger.merge(csv_files)
        
        assert "連続" in str(exc_info.value) or "欠損" in str(exc_info.value)

    def test_merge_accepts_consecutive_days(self, csv_merger, valid_csv_file_day1, valid_csv_file_day2, valid_csv_file_day3):
        """日付が連続である場合は正常に結合できる"""
        # Arrange: 2025/10/18, 2025/10/19, 2025/10/20（連続）
        csv_files = [valid_csv_file_day1, valid_csv_file_day2, valid_csv_file_day3]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        assert result.row_count == 24 * 3
        datetimes = result.data["日時"].tolist()
        assert datetimes[0] == "2025/10/18 00:00:00"
        assert datetimes[-1] == "2025/10/20 23:00:00"

    def test_merge_with_empty_list_raises_error(self, csv_merger):
        """空リストを渡すとエラーを発生させる"""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            csv_merger.merge([])
        
        assert "空" in str(exc_info.value) or "empty" in str(exc_info.value).lower()

    def test_merge_single_file(self, csv_merger, valid_csv_file_day1):
        """1つのファイルのみでも結合できる"""
        # Arrange
        csv_files = [valid_csv_file_day1]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        assert result.row_count == 24
        assert result.column_count == 7

    def test_merge_preserves_all_columns(self, csv_merger, valid_csv_file_day1, valid_csv_file_day2):
        """結合後も全てのカラムが保持される"""
        # Arrange
        csv_files = [valid_csv_file_day1, valid_csv_file_day2]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        expected_columns = ["No", "日時", "電圧", "周波数", "パワー", "工事フラグ", "参照"]
        assert list(result.data.columns) == expected_columns

    def test_merge_preserves_data_values(self, csv_merger, valid_csv_file_day1, valid_csv_file_day2):
        """結合後もデータ値が正しく保持される"""
        # Arrange
        csv_files = [valid_csv_file_day1, valid_csv_file_day2]
        
        # Act
        result = csv_merger.merge(csv_files)
        
        # Assert
        # 1日目の最初のレコード
        first_row = result.data.iloc[0]
        assert first_row["日時"] == "2025/10/18 00:00:00"
        assert first_row["電圧"] == 100
        
        # 2日目の最初のレコード（25行目）
        day2_first_row = result.data.iloc[24]
        assert day2_first_row["日時"] == "2025/10/19 00:00:00"
        assert day2_first_row["電圧"] == 105

