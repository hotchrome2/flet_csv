"""CSVファイルのスキーマ定義

このモジュールはアプリケーションで扱うCSVファイルの
カラム構造を定義します。
"""
from typing import Any
import pandas as pd

from domain.exceptions import InvalidCsvFormatError


class CsvSchema:
    """CSVファイルのスキーマ定義
    
    時系列データを扱うCSVファイルの必須カラムを定義します。
    
    必須カラム:
        - 日時: 時系列データの基準となるタイムスタンプ
        - No: データ番号
        - 電圧: 電圧値
        - 周波数: 周波数値
        - パワー: パワー値
        - 工事フラグ: 工事中を示すフラグ
        - 参照: 参照情報
    """

    # 時系列カラム（ソートの基準）
    TIMESTAMP_COLUMN: str = "日時"

    # 必須カラム（順序は問わない）
    REQUIRED_COLUMNS: list[str] = [
        "日時",
        "No",
        "電圧",
        "周波数",
        "パワー",
        "工事フラグ",
        "参照",
    ]

    # 各カラムのデータ型定義
    # "datetime_string"は特殊な型で、pandasが認識できる日時文字列を示す
    COLUMN_TYPES: dict[str, type | str] = {
        "日時": "datetime_string",  # pandasが認識可能な日時文字列（例: YYYY/MM/DD HH:00:00, YYYY-MM-DD HH:MM:SS など）
        "No": int,
        "電圧": int,
        "周波数": int,
        "パワー": int,
        "工事フラグ": int,  # 0 または 1
        "参照": int,  # 0 または 1
    }

    # 1日あたりの期待レコード数（00時〜23時の24時間）
    EXPECTED_RECORDS_PER_DAY: int = 24

    @classmethod
    def validate_columns(cls, columns: list[str]) -> bool:
        """カラムの妥当性を検証
        
        Args:
            columns: 検証するカラム名のリスト
            
        Returns:
            全ての必須カラムが存在する場合True、それ以外はFalse
        """
        return all(required_col in columns for required_col in cls.REQUIRED_COLUMNS)

    @classmethod
    def get_missing_columns(cls, columns: list[str]) -> list[str]:
        """不足しているカラムのリストを取得
        
        Args:
            columns: チェックするカラム名のリスト
            
        Returns:
            不足している必須カラムのリスト
        """
        return [col for col in cls.REQUIRED_COLUMNS if col not in columns]

    @classmethod
    def validate_and_raise(cls, columns: list[str]) -> None:
        """カラムを検証し、不正な場合は例外を発生
        
        Args:
            columns: 検証するカラム名のリスト
            
        Raises:
            InvalidCsvFormatError: 必須カラムが不足している場合
        """
        if not cls.validate_columns(columns):
            missing = cls.get_missing_columns(columns)
            missing_str = "、".join(missing)
            raise InvalidCsvFormatError(
                f"CSVファイルに必須カラムが不足しています。不足カラム: {missing_str}"
            )

    @classmethod
    def is_timestamp_column(cls, column_name: str) -> bool:
        """指定されたカラムが時系列カラムかどうかを判定
        
        Args:
            column_name: 判定するカラム名
            
        Returns:
            時系列カラムの場合True、それ以外はFalse
        """
        return column_name == cls.TIMESTAMP_COLUMN

    @classmethod
    def column_count(cls) -> int:
        """必須カラムの数を取得
        
        Returns:
            必須カラムの数
        """
        return len(cls.REQUIRED_COLUMNS)

    @classmethod
    def validate_datetime_format(cls, datetime_str: str) -> bool:
        """日時フォーマットを検証
        
        pandasが認識可能な日時文字列かを確認します。
        フォーマットは固定されておらず、pandasが解釈できれば有効とみなします。
        
        Args:
            datetime_str: 検証する日時文字列
            
        Returns:
            pandasが認識できる日時フォーマットの場合True、それ以外はFalse
        """
        if not isinstance(datetime_str, str):
            return False
        
        # 空文字列は無効
        if not datetime_str.strip():
            return False
        
        try:
            # pandasでパースできるか試す
            pd.to_datetime(datetime_str)
            return True
        except (ValueError, pd.errors.ParserError, Exception):
            return False

    @classmethod
    def validate_datetime_value(cls, datetime_str: str) -> bool:
        """日付値の妥当性を検証
        
        フォーマットだけでなく、実際の日付として妥当かをチェックします。
        - pandasで認識可能な日時文字列か
        - 実在する日付か（2月30日、13月など存在しない日付を検出）
        - 妥当な年の範囲か（1900年〜2100年）
        
        Args:
            datetime_str: 検証する日時文字列（pandasが認識可能な形式）
            
        Returns:
            妥当な日付値の場合True、それ以外はFalse
        """
        # まずフォーマットをチェック（pandasでパースできるか）
        if not cls.validate_datetime_format(datetime_str):
            return False
        
        try:
            # pd.to_datetime()で変換
            dt = pd.to_datetime(datetime_str)
            
            # 年の範囲をチェック（1900年〜2100年）
            if dt.year < 1900 or dt.year > 2100:
                return False
            
            return True
        except (ValueError, pd.errors.ParserError, Exception):
            # パースに失敗した場合は不正な日付
            return False

    @classmethod
    def validate_binary_flag(cls, value: Any) -> bool:
        """0/1のフラグ値を検証
        
        Args:
            value: 検証する値
            
        Returns:
            0または1の場合True、それ以外はFalse
        """
        return value in (0, 1)

    @classmethod
    def get_column_type(cls, column_name: str) -> type | str:
        """指定されたカラムのデータ型を取得
        
        Args:
            column_name: カラム名
            
        Returns:
            カラムのデータ型（intまたは"datetime_string"）
        """
        return cls.COLUMN_TYPES.get(column_name, object)

    @classmethod
    def validate_daily_time_range(cls, datetime_strings: list[str]) -> bool:
        """1日分の時刻範囲を検証
        
        以下の条件をチェックします：
        - レコード数が24個（00時〜23時）
        - すべて同じ日付
        - 時刻が00時から23時まで連続している
        - 重複がない
        
        Args:
            datetime_strings: 日時文字列のリスト（pandasが認識可能な形式）
            
        Returns:
            有効な1日分のデータの場合True、それ以外はFalse
        """
        # レコード数チェック
        if len(datetime_strings) != cls.EXPECTED_RECORDS_PER_DAY:
            return False
        
        # 日時フォーマットの検証と日付・時刻の抽出
        dates = set()
        hours = set()
        
        for dt_str in datetime_strings:
            if not cls.validate_datetime_format(dt_str):
                return False
            
            try:
                # pandasでパース
                dt = pd.to_datetime(dt_str)
                
                # 日付部分を抽出（年月日）
                date_part = dt.date()
                
                # 時刻部分を抽出
                hour = dt.hour
                
                dates.add(date_part)
                hours.add(hour)
            except (ValueError, pd.errors.ParserError, Exception):
                return False
        
        # すべて同じ日付かチェック
        if len(dates) != 1:
            return False
        
        # 00時から23時まで全て揃っているかチェック
        expected_hours = set(range(24))
        if hours != expected_hours:
            return False
        
        return True

