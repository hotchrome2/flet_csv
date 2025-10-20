"""CsvRepository の ZIP入力対応テスト"""
from pathlib import Path
import tempfile
import zipfile

import pytest

from infra.repositories.csv_repository import CsvRepository
from domain.exceptions import CsvFileNotFoundError, InvalidCsvFormatError


class TestCsvRepositoryZip:
    @pytest.fixture
    def csv_repository(self):
        return CsvRepository()

    @pytest.fixture
    def fixtures_dir(self):
        # tests/unit/infra/repositories/ から tests/fixtures/csv/ へのパス
        return Path(__file__).parent.parent.parent.parent / "fixtures" / "csv"

    def _create_zip_with_files(self, src_files: list[Path]) -> Path:
        tmp_dir = Path(tempfile.mkdtemp())
        zip_path = tmp_dir / "inputs.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in src_files:
                # ZIP内ではファイル名のみで格納
                zf.write(p, arcname=p.name)
        return zip_path

    def test_load_from_zip_reads_multiple_csvs(self, csv_repository, fixtures_dir):
        """ZIP内の複数CSVを読み込める"""
        # 既存のフィクスチャから2つ選ぶ
        file1 = fixtures_dir / "full_format.csv"
        file2 = fixtures_dir / "no_column_missing.csv"
        zip_path = self._create_zip_with_files([file1, file2])

        csv_files = csv_repository.load_from_zip(zip_path)

        assert isinstance(csv_files, list)
        assert len(csv_files) == 2
        for f in csv_files:
            assert f.row_count == 24
            assert f.column_count == 7

    def test_load_from_zip_nonexistent_zip_raises(self, csv_repository):
        """存在しないZIPはエラー"""
        with pytest.raises(CsvFileNotFoundError):
            csv_repository.load_from_zip(Path("no_such.zip"))

    def test_load_from_zip_with_invalid_dates_raises(self, csv_repository, fixtures_dir):
        """ZIP内に不正CSVが含まれる場合は詳細エラーを伝播"""
        invalid_csv = fixtures_dir / "invalid_dates.csv"
        zip_path = self._create_zip_with_files([invalid_csv])

        with pytest.raises(InvalidCsvFormatError) as exc_info:
            csv_repository.load_from_zip(zip_path)

        assert "invalid_dates.csv" in str(exc_info.value)


