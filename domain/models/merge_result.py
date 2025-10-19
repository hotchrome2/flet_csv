"""結合処理の結果を表現するドメインモデル

このモジュールはCSV結合処理の結果を表現するモデルを定義します。
"""
from pathlib import Path


class MergeResult:
    """CSV結合処理の結果を表現するドメインモデル
    
    結合処理の成功/失敗、出力ファイルパス、統計情報などを保持します。
    
    Attributes:
        success: 処理が成功したかどうか
        output_path: 出力ファイルのパス（失敗時はNone）
        merged_file_count: 結合したファイル数
        total_rows: 結合後の総行数
        message: 処理結果メッセージ
        error_message: エラーメッセージ（エラー時のみ）
    """

    def __init__(
        self,
        success: bool,
        output_path: str | Path | None,
        merged_file_count: int,
        total_rows: int,
        message: str | None = None,
        error_message: str | None = None
    ):
        """MergeResultを初期化
        
        Args:
            success: 処理が成功したかどうか
            output_path: 出力ファイルのパス
            merged_file_count: 結合したファイル数
            total_rows: 結合後の総行数
            message: 処理結果メッセージ
            error_message: エラーメッセージ（エラー時のみ）
        """
        self._success = success
        self._output_path = Path(output_path) if output_path and isinstance(output_path, str) else output_path
        self._merged_file_count = merged_file_count
        self._total_rows = total_rows
        self._message = message or self._generate_default_message()
        self._error_message = error_message

    def _generate_default_message(self) -> str:
        """デフォルトメッセージを生成"""
        if self._success:
            return f"{self._merged_file_count}個のファイルを結合しました（総行数: {self._total_rows}）"
        else:
            return "CSV結合処理に失敗しました"

    @property
    def success(self) -> bool:
        """処理が成功したかどうか"""
        return self._success

    @property
    def output_path(self) -> Path | None:
        """出力ファイルのパス"""
        return self._output_path

    @property
    def merged_file_count(self) -> int:
        """結合したファイル数"""
        return self._merged_file_count

    @property
    def total_rows(self) -> int:
        """結合後の総行数"""
        return self._total_rows

    @property
    def message(self) -> str:
        """処理結果メッセージ"""
        return self._message

    @property
    def error_message(self) -> str | None:
        """エラーメッセージ"""
        return self._error_message

    @property
    def is_successful(self) -> bool:
        """処理が成功したかどうか（successのエイリアス）"""
        return self._success

    @property
    def has_error(self) -> bool:
        """エラーが発生したかどうか"""
        return self._error_message is not None

    @property
    def output_file_name(self) -> str | None:
        """出力ファイル名を取得"""
        return self._output_path.name if self._output_path else None

    @classmethod
    def create_success(
        cls,
        output_path: str | Path,
        merged_file_count: int,
        total_rows: int,
        message: str | None = None
    ) -> "MergeResult":
        """成功した結合結果を作成するファクトリメソッド
        
        Args:
            output_path: 出力ファイルのパス
            merged_file_count: 結合したファイル数
            total_rows: 結合後の総行数
            message: カスタムメッセージ
            
        Returns:
            成功を示すMergeResultインスタンス
        """
        return cls(
            success=True,
            output_path=output_path,
            merged_file_count=merged_file_count,
            total_rows=total_rows,
            message=message,
            error_message=None
        )

    @classmethod
    def create_failure(
        cls,
        error_message: str,
        merged_file_count: int = 0,
        message: str | None = None
    ) -> "MergeResult":
        """失敗した結合結果を作成するファクトリメソッド
        
        Args:
            error_message: エラーメッセージ
            merged_file_count: 処理できたファイル数
            message: カスタムメッセージ
            
        Returns:
            失敗を示すMergeResultインスタンス
        """
        return cls(
            success=False,
            output_path=None,
            merged_file_count=merged_file_count,
            total_rows=0,
            message=message,
            error_message=error_message
        )

    def __str__(self) -> str:
        """文字列表現"""
        if self._success:
            return f"成功: {self._merged_file_count}ファイル結合, {self._total_rows}行 -> {self.output_file_name}"
        else:
            return f"失敗: {self._error_message or self._message}"

    def __repr__(self) -> str:
        """repr表現"""
        return (
            f"MergeResult(success={self._success}, "
            f"output_path={self._output_path!r}, "
            f"merged_file_count={self._merged_file_count}, "
            f"total_rows={self._total_rows})"
        )

