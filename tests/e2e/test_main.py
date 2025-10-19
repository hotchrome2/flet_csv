"""main.pyのエンドツーエンドテスト

このモジュールは、main.pyのCLI機能のエンドツーエンドテストを提供します。
"""
from pathlib import Path
import subprocess
import sys
import pytest


class TestMainCLI:
    """main.pyのCLI機能のテスト"""

    @pytest.fixture
    def input_dir(self, tmp_path):
        """テスト用の入力ディレクトリを作成"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        return input_dir

    @pytest.fixture
    def output_dir(self, tmp_path):
        """テスト用の出力ディレクトリを作成"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return output_dir

    @pytest.fixture
    def sample_csv_files(self, input_dir):
        """テスト用のサンプルCSVファイルを作成"""
        # ファイル1: 2025/01/01の24時間分
        csv1 = input_dir / "file1.csv"
        lines1 = [
            "No,日時,電圧,周波数,パワー,工事フラグ,参照\n"
        ]
        for i in range(24):
            lines1.append(f"{i+1},2025/01/01 {i:02d}:00:00,100,50,1000,0,0\n")
        csv1.write_text("".join(lines1), encoding="utf-8")

        # ファイル2: 2025/01/02の24時間分
        csv2 = input_dir / "file2.csv"
        lines2 = [
            "No,日時,電圧,周波数,パワー,工事フラグ,参照\n"
        ]
        for i in range(24):
            lines2.append(f"{i+1},2025/01/02 {i:02d}:00:00,100,50,1000,0,0\n")
        csv2.write_text("".join(lines2), encoding="utf-8")

        return [csv1, csv2]

    def test_main_success_with_default_directories(self, sample_csv_files, monkeypatch, tmp_path):
        """デフォルトのディレクトリを使用して正常に実行できる"""
        # デフォルトのディレクトリをテスト用に変更
        monkeypatch.setattr(sys, "argv", ["main.py"])
        # 注: この実装はmain.pyがデフォルトで time_case/ を使用することを前提とする

    def test_main_success_with_custom_directories(self, sample_csv_files, input_dir, output_dir):
        """カスタムディレクトリを指定して正常に実行できる"""
        # main.pyを実行
        result = subprocess.run(
            [sys.executable, "main.py", "--input", str(input_dir), "--output", str(output_dir)],
            capture_output=True,
            text=True
        )

        # 正常終了を確認
        assert result.returncode == 0

        # 成功メッセージが含まれることを確認
        assert "成功" in result.stdout or "完了" in result.stdout

        # 出力ファイルが作成されていることを確認
        output_files = list(output_dir.glob("merged_*.csv"))
        assert len(output_files) == 1

        # 出力ファイルの内容を確認
        output_file = output_files[0]
        output_content = output_file.read_text(encoding="utf-8")
        lines = output_content.strip().split("\n")
        
        # ヘッダー + 48行（2ファイル × 24時間）
        assert len(lines) == 49

    def test_main_shows_result_information(self, sample_csv_files, input_dir, output_dir):
        """結果情報（ファイル数、行数）を表示する"""
        result = subprocess.run(
            [sys.executable, "main.py", "--input", str(input_dir), "--output", str(output_dir)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # 結果情報が含まれることを確認
        assert "2" in result.stdout  # 2ファイル結合
        assert "48" in result.stdout  # 48行

    def test_main_failure_with_nonexistent_input_directory(self, output_dir):
        """存在しない入力ディレクトリを指定すると失敗する"""
        nonexistent_dir = Path("nonexistent_directory")
        
        result = subprocess.run(
            [sys.executable, "main.py", "--input", str(nonexistent_dir), "--output", str(output_dir)],
            capture_output=True,
            text=True
        )

        # エラー終了を確認
        assert result.returncode != 0

        # エラーメッセージが含まれることを確認
        assert "エラー" in result.stderr or "失敗" in result.stderr or "見つかりません" in result.stderr

    def test_main_failure_with_empty_input_directory(self, tmp_path, output_dir):
        """空の入力ディレクトリを指定すると失敗する"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = subprocess.run(
            [sys.executable, "main.py", "--input", str(empty_dir), "--output", str(output_dir)],
            capture_output=True,
            text=True
        )

        # エラー終了を確認
        assert result.returncode != 0

        # エラーメッセージが含まれることを確認
        assert "エラー" in result.stderr or "失敗" in result.stderr or "ファイルが" in result.stderr

    def test_main_shows_help_message(self):
        """ヘルプメッセージを表示できる"""
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        # ヘルプメッセージが含まれることを確認
        assert "--input" in result.stdout
        assert "--output" in result.stdout
        assert "usage" in result.stdout.lower() or "使用方法" in result.stdout

    def test_main_handles_invalid_csv_format(self, tmp_path, output_dir):
        """不正なCSVフォーマットの場合、適切なエラーメッセージを表示する"""
        input_dir = tmp_path / "invalid_input"
        input_dir.mkdir()
        
        # 不正なCSVファイルを作成（カラム不足）
        invalid_csv = input_dir / "invalid.csv"
        invalid_csv.write_text("No,日時\n1,2025/01/01 00:00:00\n", encoding="utf-8")
        
        result = subprocess.run(
            [sys.executable, "main.py", "--input", str(input_dir), "--output", str(output_dir)],
            capture_output=True,
            text=True
        )

        # エラー終了を確認
        assert result.returncode != 0

        # CSVフォーマットエラーのメッセージが含まれることを確認
        output = result.stderr + result.stdout
        assert "フォーマット" in output or "不正" in output

