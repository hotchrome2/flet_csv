"""ヘッダーなしCSVで末尾カンマにより生成された全NaN列の除去テスト"""
from pathlib import Path

from infra.repositories.csv_repository import CsvRepository


def test_headerless_with_trailing_comma_drops_last_na_column(tmp_path: Path) -> None:
    """各行が末尾カンマで終わるヘッダーなしCSVを読み込み、
    末尾の全NaN列が除去されることを検証する。
    """
    csv_path = tmp_path / "trailing_comma.csv"
    lines = [
        f"2025/10/18 {hour:02d}:00:00,100,50,1000,0,\n" for hour in range(24)
    ]
    csv_path.write_text("".join(lines), encoding="utf-8")

    repo = CsvRepository()
    result = repo.load(csv_path)

    # 正規化後: 7列（No, 日時, 電圧, 周波数, パワー, 工事フラグ, 参照）
    assert result.row_count == 24
    assert result.column_count == 7
    assert "No" in result.column_names
    assert "参照" in result.column_names
    assert list(result.data["No"]) == list(range(1, 25))
    assert list(result.data["参照"]) == [0] * 24

