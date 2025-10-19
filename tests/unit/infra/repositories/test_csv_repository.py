"""CsvRepository のテスト"""
import pytest
from pathlib import Path
import tempfile
import shutil

from infra.repositories.csv_repository import CsvRepository
from domain.models.csv_file import CsvFile
from domain.exceptions import CsvFileNotFoundError, InvalidCsvFormatError


class TestCsvRepository:
    """CsvRepositoryのテスト"""

    @pytest.fixture
    def csv_repository(self):
        """CsvRepositoryインスタンスを提供"""
        return CsvRepository()

    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを提供"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def fixtures_dir(self):
        """テストフィクスチャディレクトリのパスを提供"""
        # tests/unit/infra/repositories/ から tests/fixtures/csv/ へのパス
        return Path(__file__).parent.parent.parent.parent / "fixtures" / "csv"

    def test_load_csv_with_full_format_utf8(self, csv_repository, fixtures_dir):
        """完全フォーマット（ヘッダーあり、No列あり）のUTF-8 CSVを読み込める"""
        # Arrange
        csv_path = fixtures_dir / "full_format.csv"
        
        # Act
        result = csv_repository.load(csv_path)
        
        # Assert
        assert isinstance(result, CsvFile)
        assert result.row_count == 24
        assert result.column_count == 7
        assert "No" in result.column_names
        assert "日時" in result.column_names

    def test_load_csv_without_no_column(self, csv_repository, fixtures_dir):
        """No列なし（ヘッダーあり）のCSVを読み込んでNo列を自動採番できる"""
        # Arrange
        csv_path = fixtures_dir / "no_column_missing.csv"
        
        # Act
        result = csv_repository.load(csv_path)
        
        # Assert
        assert result.row_count == 24
        assert result.column_count == 7
        assert "No" in result.column_names
        # No列が1から連番で採番されている
        assert list(result.data["No"]) == list(range(1, 25))

    def test_load_csv_without_header(self, csv_repository, fixtures_dir):
        """ヘッダーなし（No列・参照列なし）のCSVを読み込んで正規化できる"""
        # Arrange
        csv_path = fixtures_dir / "no_header.csv"
        
        # Act
        result = csv_repository.load(csv_path)
        
        # Assert
        assert result.row_count == 24
        assert result.column_count == 7
        assert "No" in result.column_names
        assert "参照" in result.column_names
        # No列が1から連番で採番されている
        assert list(result.data["No"]) == list(range(1, 25))
        # 参照列が0で埋められている
        assert all(result.data["参照"] == 0)

    def test_load_csv_with_shift_jis_encoding(self, csv_repository, fixtures_dir):
        """Shift-JIS エンコーディングのCSVを読み込める"""
        # Arrange
        csv_path = fixtures_dir / "shift_jis.csv"
        
        # Act
        result = csv_repository.load(csv_path)
        
        # Assert
        assert result.row_count == 24
        assert result.column_count == 7
        assert "日時" in result.column_names

    def test_load_csv_with_quoted_values(self, csv_repository, fixtures_dir):
        """クォーテーション付きのCSVを読み込める"""
        # Arrange
        csv_path = fixtures_dir / "quoted.csv"
        
        # Act
        result = csv_repository.load(csv_path)
        
        # Assert
        assert result.row_count == 24
        assert result.column_count == 7

    def test_load_nonexistent_file_raises_error(self, csv_repository):
        """存在しないファイルを読み込もうとするとエラー"""
        # Arrange
        nonexistent_path = Path("nonexistent.csv")
        
        # Act & Assert
        with pytest.raises(CsvFileNotFoundError) as exc_info:
            csv_repository.load(nonexistent_path)
        
        assert "見つかりません" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_save_csv_file(self, csv_repository, temp_dir):
        """CsvFileを指定ディレクトリに保存できる"""
        # Arrange: 保存するCsvFileを作成
        import pandas as pd
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
        csv_file = CsvFile(file_path="test.csv", data=data)
        output_dir = temp_dir / "output"
        
        # Act
        output_path = csv_repository.save(csv_file, output_dir)
        
        # Assert
        assert output_path.exists()
        assert output_path.parent == output_dir
        assert output_path.name.startswith("merged_")
        assert output_path.suffix == ".csv"
        # 保存されたファイルを読み込んで検証
        loaded = csv_repository.load(output_path)
        assert loaded.row_count == 24
        assert loaded.column_count == 7

    def test_normalize_columns_order(self, csv_repository, fixtures_dir):
        """カラムの順番が正規化される（No, 日時, 電圧, ...の順）"""
        # Arrange
        csv_path = fixtures_dir / "wrong_order.csv"
        
        # Act
        result = csv_repository.load(csv_path)
        
        # Assert
        expected_order = ["No", "日時", "電圧", "周波数", "パワー", "工事フラグ", "参照"]
        assert list(result.data.columns) == expected_order

    def test_load_csv_with_invalid_dates_raises_detailed_error(self, csv_repository, fixtures_dir):
        """不正な日時を含むCSVは詳細なエラーメッセージで検出される"""
        # Arrange
        csv_path = fixtures_dir / "invalid_dates.csv"
        
        # Act & Assert
        with pytest.raises(InvalidCsvFormatError) as exc_info:
            csv_repository.load(csv_path)
        
        error_message = str(exc_info.value)
        # ファイル名が含まれる
        assert "invalid_dates.csv" in error_message
        # エラーの種類が含まれる
        assert "不正な日時" in error_message
        # 不正な行番号が含まれる（データ行は2行目から、ヘッダーは1行目）
        assert "3行目" in error_message  # 0002/10/12
        assert "5行目" in error_message  # 13月
        assert "6行目" in error_message  # 4月31日
        assert "8行目" in error_message  # 9999年
