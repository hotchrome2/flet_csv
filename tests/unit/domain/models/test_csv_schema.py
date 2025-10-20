"""CSVスキーマのテスト"""
import pytest
from domain.models.csv_schema import CsvSchema
from domain.exceptions import InvalidCsvFormatError


class TestCsvSchema:
    """CSVスキーマ定義のテスト"""

    def test_required_columns_definition(self):
        """必須カラムが定義されている"""
        required = CsvSchema.REQUIRED_COLUMNS
        
        assert "日時" in required
        assert "No" in required
        assert "電圧" in required
        assert "周波数" in required
        assert "パワー" in required
        assert "工事フラグ" in required
        assert "参照" in required
        assert len(required) == 7

    def test_timestamp_column_definition(self):
        """時系列カラムが定義されている"""
        assert CsvSchema.TIMESTAMP_COLUMN == "日時"

    def test_validate_columns_with_all_required_columns(self):
        """全ての必須カラムが存在する場合、検証に成功する"""
        columns = ["日時", "No", "電圧", "周波数", "パワー", "工事フラグ", "参照"]
        
        result = CsvSchema.validate_columns(columns)
        
        assert result is True

    def test_validate_columns_with_extra_columns(self):
        """余分なカラムがあっても検証に成功する"""
        columns = ["日時", "No", "電圧", "周波数", "パワー", "工事フラグ", "参照", "備考"]
        
        result = CsvSchema.validate_columns(columns)
        
        assert result is True

    def test_validate_columns_with_missing_column(self):
        """必須カラムが欠けている場合、検証に失敗する"""
        columns = ["日時", "No", "電圧", "周波数", "パワー", "参照"]  # 工事フラグが欠けている
        
        result = CsvSchema.validate_columns(columns)
        
        assert result is False

    def test_validate_columns_with_empty_list(self):
        """空のカラムリストの場合、検証に失敗する"""
        columns = []
        
        result = CsvSchema.validate_columns(columns)
        
        assert result is False

    def test_get_missing_columns(self):
        """不足しているカラムのリストを取得できる"""
        columns = ["日時", "No", "電圧"]
        
        missing = CsvSchema.get_missing_columns(columns)
        
        assert "周波数" in missing
        assert "パワー" in missing
        assert "工事フラグ" in missing
        assert "参照" in missing
        assert len(missing) == 4

    def test_get_missing_columns_when_all_present(self):
        """全てのカラムが存在する場合、空リストが返る"""
        columns = ["日時", "No", "電圧", "周波数", "パワー", "工事フラグ", "参照"]
        
        missing = CsvSchema.get_missing_columns(columns)
        
        assert missing == []

    def test_validate_and_raise_on_invalid_schema(self):
        """スキーマが不正な場合、例外を発生させる"""
        columns = ["日時", "No"]  # 不足している
        
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            CsvSchema.validate_and_raise(columns)
        
        error_message = str(exc_info.value)
        assert "電圧" in error_message or "周波数" in error_message

    def test_validate_and_raise_on_valid_schema(self):
        """スキーマが正しい場合、例外は発生しない"""
        columns = ["日時", "No", "電圧", "周波数", "パワー", "工事フラグ", "参照"]
        
        # 例外が発生しないことを確認
        CsvSchema.validate_and_raise(columns)

    def test_is_timestamp_column(self):
        """指定されたカラムが時系列カラムかどうかを判定できる"""
        assert CsvSchema.is_timestamp_column("日時") is True
        assert CsvSchema.is_timestamp_column("No") is False
        assert CsvSchema.is_timestamp_column("電圧") is False

    def test_column_count(self):
        """必須カラムの数を取得できる"""
        assert CsvSchema.column_count() == 7

    def test_column_types_definition(self):
        """各カラムのデータ型が定義されている"""
        column_types = CsvSchema.COLUMN_TYPES
        
        assert column_types["日時"] == "datetime_string"
        assert column_types["No"] == int
        assert column_types["電圧"] == int
        assert column_types["周波数"] == int
        assert column_types["パワー"] == int
        assert column_types["工事フラグ"] == int
        assert column_types["参照"] == int

    def test_validate_datetime_format_valid(self):
        """有効な日時フォーマットを検証できる"""
        valid_datetimes = [
            "2025/10/01 10:00:00",
            "2024/01/15 00:00:00",
            "2023/12/31 23:00:00",
        ]
        
        for dt in valid_datetimes:
            assert CsvSchema.validate_datetime_format(dt) is True

    def test_validate_datetime_format_invalid(self):
        """無効な日時フォーマットを検出できる"""
        invalid_datetimes = [
            "invalid",              # 完全に不正
            "2025年10月01日",       # 日本語形式
            "abc123",               # ランダムな文字列
            "",                     # 空文字列
        ]
        
        for dt in invalid_datetimes:
            assert CsvSchema.validate_datetime_format(dt) is False
    
    def test_validate_datetime_format_flexible(self):
        """pandasが認識可能な様々な日時フォーマットを受け入れる"""
        flexible_datetimes = [
            "2025-10-01 10:00:00",  # ハイフン区切り（ISO 8601形式）
            "2025/10/01 10:30:00",  # 30分（毎正時でなくても可）
            "2025/10/01",           # 時刻なし（日付のみ）
            "10:00:00",             # 日付なし（時刻のみ、今日の日付が補完される）
            "2025-10-01T10:00:00",  # ISO 8601形式（T区切り）
        ]
        
        for dt in flexible_datetimes:
            assert CsvSchema.validate_datetime_format(dt) is True

    def test_validate_datetime_value_valid(self):
        """妥当な日付値を検証できる"""
        valid_datetimes = [
            "2025/10/18 10:00:00",
            "2024/02/29 00:00:00",  # うるう年
            "2023/12/31 23:00:00",
            "2020/01/01 00:00:00",
        ]
        
        for valid_dt in valid_datetimes:
            result = CsvSchema.validate_datetime_value(valid_dt)
            assert result is True, f"Expected True for {valid_dt}"

    def test_validate_datetime_value_invalid(self):
        """不正な日付値を検出できる（異常な年月日）"""
        invalid_datetimes = [
            "0002/10/12 00:00:00",  # 異常に古い年
            "9999/12/31 23:00:00",  # 異常に新しい年
            "2023/02/29 10:00:00",  # 平年の2月29日
            "2025/13/01 10:00:00",  # 13月
            "2025/04/31 10:00:00",  # 4月31日（存在しない）
            "2025/00/01 10:00:00",  # 0月
            "2025/01/00 10:00:00",  # 0日
        ]
        
        for invalid_dt in invalid_datetimes:
            result = CsvSchema.validate_datetime_value(invalid_dt)
            assert result is False, f"Expected False for {invalid_dt}"

    def test_validate_binary_flag_valid(self):
        """0/1の整数値を検証できる"""
        assert CsvSchema.validate_binary_flag(0) is True
        assert CsvSchema.validate_binary_flag(1) is True

    def test_validate_binary_flag_invalid(self):
        """0/1以外の値を検出できる"""
        assert CsvSchema.validate_binary_flag(2) is False
        assert CsvSchema.validate_binary_flag(-1) is False
        assert CsvSchema.validate_binary_flag(0.5) is False

    def test_get_column_type(self):
        """指定カラムの型を取得できる"""
        assert CsvSchema.get_column_type("No") == int
        assert CsvSchema.get_column_type("電圧") == int
        assert CsvSchema.get_column_type("工事フラグ") == int

    def test_expected_records_per_day(self):
        """1日あたりの期待レコード数が定義されている"""
        assert CsvSchema.EXPECTED_RECORDS_PER_DAY == 24

    def test_validate_daily_time_range_valid(self):
        """有効な1日分の時刻リストを検証できる"""
        # 00時〜23時の24レコード
        valid_datetimes = [
            f"2025/10/18 {hour:02d}:00:00" for hour in range(24)
        ]
        
        result = CsvSchema.validate_daily_time_range(valid_datetimes)
        
        assert result is True

    def test_validate_daily_time_range_missing_hour(self):
        """時刻が不足している場合を検出できる"""
        # 00時〜22時（23時が欠けている）
        incomplete_datetimes = [
            f"2025/10/18 {hour:02d}:00:00" for hour in range(23)
        ]
        
        result = CsvSchema.validate_daily_time_range(incomplete_datetimes)
        
        assert result is False

    def test_validate_daily_time_range_extra_hour(self):
        """余分な時刻がある場合を検出できる"""
        # 00時〜23時 + 重複
        extra_datetimes = [
            f"2025/10/18 {hour:02d}:00:00" for hour in range(24)
        ] + ["2025/10/18 10:00:00"]
        
        result = CsvSchema.validate_daily_time_range(extra_datetimes)
        
        assert result is False

    def test_validate_daily_time_range_wrong_start(self):
        """00時以外から始まる場合を検出できる"""
        # 01時〜23時（00時が欠けている）
        wrong_start = [
            f"2025/10/18 {hour:02d}:00:00" for hour in range(1, 24)
        ]
        
        result = CsvSchema.validate_daily_time_range(wrong_start)
        
        assert result is False

    def test_validate_daily_time_range_spans_multiple_days(self):
        """複数日にまたがる場合を検出できる"""
        # 2日分のデータ
        multi_day = [
            f"2025/10/18 {hour:02d}:00:00" for hour in range(24)
        ] + [f"2025/10/19 00:00:00"]
        
        result = CsvSchema.validate_daily_time_range(multi_day)
        
        assert result is False

    def test_validate_daily_time_range_different_dates(self):
        """異なる日付が混在する場合を検出できる"""
        mixed_dates = [
            "2025/10/18 00:00:00",
            "2025/10/18 01:00:00",
            "2025/10/19 02:00:00",  # 異なる日付
        ]
        
        result = CsvSchema.validate_daily_time_range(mixed_dates)
        
        assert result is False

