"""Domain層の例外クラス定義

このモジュールはflet-csvアプリケーションのドメイン固有の例外を定義します。
すべてのドメイン例外はCsvMergerErrorを基底クラスとして継承します。
"""


class CsvMergerError(Exception):
    """CSV結合処理に関する基底例外クラス
    
    すべてのドメイン固有の例外はこのクラスを継承します。
    これにより、ドメイン層のすべてのエラーを一括でキャッチできます。
    """
    pass


class InvalidCsvFormatError(CsvMergerError):
    """CSVフォーマットが不正な場合の例外
    
    以下の場合に発生します：
    - ファイルがCSVフォーマットでない
    - カラム構造が期待と異なる
    - データ型が不正
    """
    
    @classmethod
    def with_invalid_lines(
        cls,
        file_name: str,
        invalid_lines: list[int],
        error_type: str = "不正な値"
    ) -> "InvalidCsvFormatError":
        """行番号情報を含むInvalidCsvFormatErrorを生成
        
        Args:
            file_name: ファイル名
            invalid_lines: 不正な行番号のリスト（1始まり）
            error_type: エラーの種類（例：「不正な日時」「不正なフォーマット」）
            
        Returns:
            詳細なエラーメッセージを含むInvalidCsvFormatError
        """
        if not invalid_lines:
            return cls(f"{file_name}: {error_type}が検出されました")
        
        # 行番号をソート
        sorted_lines = sorted(invalid_lines)
        
        # 連続する行番号を範囲にまとめる
        ranges = cls._compress_line_numbers(sorted_lines)
        
        # エラーメッセージを生成
        ranges_str = "、".join(ranges)
        message = f"{file_name}: {error_type}が検出されました（{ranges_str}）"
        
        return cls(message)
    
    @staticmethod
    def _compress_line_numbers(line_numbers: list[int]) -> list[str]:
        """連続する行番号を範囲形式にまとめる
        
        例：[1, 2, 3, 5, 7, 8, 9] → ["1行目から3行目", "5行目", "7行目から9行目"]
        
        Args:
            line_numbers: ソート済みの行番号リスト
            
        Returns:
            範囲形式の文字列リスト
        """
        if not line_numbers:
            return []
        
        ranges = []
        start = line_numbers[0]
        end = line_numbers[0]
        
        for i in range(1, len(line_numbers)):
            if line_numbers[i] == end + 1:
                # 連続している
                end = line_numbers[i]
            else:
                # 連続が途切れた
                if start == end:
                    ranges.append(f"{start}行目")
                else:
                    ranges.append(f"{start}行目から{end}行目")
                start = line_numbers[i]
                end = line_numbers[i]
        
        # 最後の範囲を追加
        if start == end:
            ranges.append(f"{start}行目")
        else:
            ranges.append(f"{start}行目から{end}行目")
        
        return ranges


class CsvFileNotFoundError(CsvMergerError):
    """CSVファイルが見つからない場合の例外
    
    指定されたパスにCSVファイルが存在しない場合に発生します。
    """
    pass


class MergeError(CsvMergerError):
    """CSV結合処理中のエラー
    
    以下の場合に発生します：
    - カラム名が一致しない
    - データ型の不整合
    - 結合ロジックのエラー
    """
    pass


class EmptyDataError(CsvMergerError):
    """データが空の場合の例外
    
    以下の場合に発生します：
    - CSVファイルが空
    - ヘッダーのみでデータ行がない
    - 結合対象のファイルが0件
    """
    pass

