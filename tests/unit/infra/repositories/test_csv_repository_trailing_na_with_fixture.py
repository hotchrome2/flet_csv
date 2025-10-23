"""フィクスチャCSVを使った末尾NaN列削除の検証"""
from pathlib import Path

from infra.repositories.csv_repository import CsvRepository


def test_headerless_fixture_trailing_comma(tmp_path: Path) -> None:
    """フィクスチャのヘッダーなしCSV（末尾カンマ）を読み込み、最終NaN列が除去され正規化される。"""
    fixtures_dir = Path(__file__).parent.parent.parent.parent / "fixtures" / "csv"
    csv_path = fixtures_dir / "headerless_trailing_comma.csv"

    repo = CsvRepository()
    result = repo.load(csv_path)

    # 正規化後: 7列（No, 日時, 電圧, 周波数, パワー, 工事フラグ, 参照）
    assert result.row_count == 24
    assert result.column_count == 7
    assert list(result.data.columns) == ["No", "日時", "電圧", "周波数", "パワー", "工事フラグ", "参照"]
    assert list(result.data["No"]) == list(range(1, 25))
    assert all(result.data["参照"] == 0)

