# CLIエントリーポイント 詳細仕様

**ファイル**: `doc/09_cli_specification.md`  
**作成日**: 2025-10-19  
**最終更新**: 2025-10-19

このドキュメントは、CLIエントリーポイント（main.py）の詳細仕様を記載します。

---

## 目次

1. [概要](#1-概要)
2. [main.py仕様](#2-mainpy仕様)
3. [テスト仕様](#3-テスト仕様)
4. [使用例](#4-使用例)
5. [トラブルシューティング](#5-トラブルシューティング)

---

## 1. 概要

### 1.1 責務

CLIエントリーポイント（main.py）は、コマンドラインからCSV結合処理を実行するためのインターフェースを提供します。

- コマンドライン引数の解析
- CSVファイルの自動検出
- UseCaseの実行
- 詳細なログ出力
- 結果の表示

### 1.2 依存関係

```
main.py
    ↓ 使用
MergeCsvFilesUseCase (UseCase層)
    ↓ 使用
CsvRepository (Infrastructure層)
CsvMerger (Domain層)
```

---

## 2. main.py仕様

**ファイル**: `main.py`  
**テスト**: `tests/e2e/test_main.py`

### 2.1 主要機能

#### コマンドライン引数

```python
def parse_arguments() -> argparse.Namespace:
```

| 引数 | 型 | デフォルト | 説明 |
|-----|---|----------|------|
| `--input` | str | `time_case` | 入力CSVファイルが格納されているディレクトリ |
| `--output` | str | `static/downloads` | 結合後のCSVファイルを保存するディレクトリ |
| `--help` | - | - | ヘルプメッセージを表示 |

**使用例**:
```bash
python main.py                                           # デフォルト
python main.py --input my_data --output results          # カスタム
python main.py --help                                    # ヘルプ
```

#### CSVファイル自動検出

```python
def get_csv_files(input_dir: Path) -> list[Path]:
```

**機能**:
- 指定ディレクトリ内の`*.csv`ファイルを自動検出
- ファイル名でソート
- ディレクトリの存在確認
- CSVファイルの存在確認

**例外**:
- `FileNotFoundError`: ディレクトリが存在しない
- `ValueError`: CSVファイルが見つからない

#### メイン処理

```python
def main() -> int:
```

**処理フロー**:

```
1. コマンドライン引数を解析
   ↓
2. 入力/出力ディレクトリのPathを作成
   ↓
3. 出力ディレクトリを作成（存在しない場合）
   ↓
4. CSVファイルを自動検出
   ↓
5. MergeCsvFilesUseCaseを実行
   ↓
6. 結果を表示（標準出力/標準エラー出力）
   ↓
7. 終了コードを返す（成功: 0、失敗: 1）
```

**エラーハンドリング**:

| 例外 | メッセージ | 終了コード |
|------|----------|----------|
| `FileNotFoundError` | "ファイルが見つかりません" | 1 |
| `ValueError` | "入力エラー" | 1 |
| `Exception` | "予期しないエラーが発生しました" | 1 |

### 2.2 ログ出力

**ログレベル**:
- `INFO`: 処理の進行状況、成功メッセージ
- `ERROR`: エラーメッセージ

**ログフォーマット**:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**出力例**:
```
2025-10-19 16:00:00 - __main__ - INFO - ============================================================
2025-10-19 16:00:00 - __main__ - INFO - CSVファイル結合処理を開始します
2025-10-19 16:00:00 - __main__ - INFO - ============================================================
2025-10-19 16:00:00 - __main__ - INFO - 入力ディレクトリ: C:\...\time_case
2025-10-19 16:00:00 - __main__ - INFO - 出力ディレクトリ: C:\...\static\downloads
2025-10-19 16:00:00 - __main__ - INFO - 出力ディレクトリを準備しました: C:\...\static\downloads
2025-10-19 16:00:00 - __main__ - INFO - 入力CSVファイル数: 3
2025-10-19 16:00:00 - __main__ - INFO -   1. file1.csv
2025-10-19 16:00:00 - __main__ - INFO -   2. file2.csv
2025-10-19 16:00:00 - __main__ - INFO -   3. file3.csv
2025-10-19 16:00:00 - __main__ - INFO - ------------------------------------------------------------
2025-10-19 16:00:00 - __main__ - INFO - 結合処理を実行中...
2025-10-19 16:00:00 - __main__ - INFO - ------------------------------------------------------------
2025-10-19 16:00:00 - __main__ - INFO - [成功] 結合処理が成功しました！
2025-10-19 16:00:00 - __main__ - INFO -    出力ファイル: C:\...\static\downloads\merged_20251019_160000.csv
2025-10-19 16:00:00 - __main__ - INFO -    結合ファイル数: 3
2025-10-19 16:00:00 - __main__ - INFO -    総行数: 72
2025-10-19 16:00:00 - __main__ - INFO - ============================================================
```

### 2.3 標準出力/標準エラー出力

**成功時（標準出力）**:
```
成功: 3ファイルを結合しました（72行）
出力: C:\...\static\downloads\merged_20251019_160000.csv
```

**失敗時（標準エラー出力）**:
```
エラー: ファイルが見つかりません: 入力ディレクトリが見つかりません: nonexistent
```

### 2.4 終了コード

| コード | 意味 | 説明 |
|-------|------|------|
| 0 | 成功 | CSV結合処理が正常に完了 |
| 1 | 失敗 | エラーが発生（ファイル未存在、CSVエラーなど） |

---

## 3. テスト仕様

**テストファイル**: `tests/e2e/test_main.py`

### 3.1 テスト戦略

**エンドツーエンドテストの特徴**:
- **実際のCLI実行**: `subprocess.run()`でmain.pyを実行
- **完全な統合テスト**: すべての層を通した実行
- **実ファイル使用**: 一時ディレクトリに実際のCSVファイルを作成

### 3.2 テストケース一覧

#### 正常系テスト（3テスト）

| テスト名 | 説明 | 検証内容 |
|---------|------|---------|
| `test_main_success_with_default_directories` | デフォルトのディレクトリを使用して正常に実行できる | ・終了コード0 |
| `test_main_success_with_custom_directories` | カスタムディレクトリを指定して正常に実行できる | ・終了コード0<br>・成功メッセージが含まれる<br>・出力ファイルが作成される<br>・出力ファイルの内容が正しい（49行） |
| `test_main_shows_result_information` | 結果情報（ファイル数、行数）を表示する | ・終了コード0<br>・"2"が含まれる（2ファイル）<br>・"48"が含まれる（48行） |

#### 異常系テスト（3テスト）

| テスト名 | 説明 | 検証内容 |
|---------|------|---------|
| `test_main_failure_with_nonexistent_input_directory` | 存在しない入力ディレクトリを指定すると失敗する | ・終了コード≠0<br>・エラーメッセージが含まれる |
| `test_main_failure_with_empty_input_directory` | 空の入力ディレクトリを指定すると失敗する | ・終了コード≠0<br>・エラーメッセージが含まれる |
| `test_main_handles_invalid_csv_format` | 不正なCSVフォーマットの場合、適切なエラーメッセージを表示する | ・終了コード≠0<br>・"フォーマット"または"不正"が含まれる |

#### ヘルプテスト（1テスト）

| テスト名 | 説明 | 検証内容 |
|---------|------|---------|
| `test_main_shows_help_message` | ヘルプメッセージを表示できる | ・終了コード0<br>・"--input"が含まれる<br>・"--output"が含まれる<br>・"usage"が含まれる |

### 3.3 テストフィクスチャ

#### サンプルCSVファイル作成

```python
@pytest.fixture
def sample_csv_files(self, input_dir):
    """テスト用のサンプルCSVファイルを作成"""
    # ファイル1: 2025/01/01の24時間分
    csv1 = input_dir / "file1.csv"
    lines1 = ["No,日時,電圧,周波数,パワー,工事フラグ,参照\n"]
    for i in range(24):
        lines1.append(f"{i+1},2025/01/01 {i:02d}:00:00,100,50,1000,0,0\n")
    csv1.write_text("".join(lines1), encoding="utf-8")
    
    # ファイル2: 2025/01/02の24時間分
    # ...
```

#### 一時ディレクトリ

```python
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
```

### 3.4 テスト実行

```bash
# エンドツーエンドテストのみ実行
uv run pytest tests/e2e/ -v

# 全テスト実行
uv run pytest tests/ -q

# 特定のテストのみ実行
uv run pytest tests/e2e/test_main.py::TestMainCLI::test_main_success_with_custom_directories -v
```

**期待される結果**:
```
tests/e2e/test_main.py::TestMainCLI::test_main_success_with_default_directories PASSED
tests/e2e/test_main.py::TestMainCLI::test_main_success_with_custom_directories PASSED
tests/e2e/test_main.py::TestMainCLI::test_main_shows_result_information PASSED
tests/e2e/test_main.py::TestMainCLI::test_main_failure_with_nonexistent_input_directory PASSED
tests/e2e/test_main.py::TestMainCLI::test_main_failure_with_empty_input_directory PASSED
tests/e2e/test_main.py::TestMainCLI::test_main_shows_help_message PASSED
tests/e2e/test_main.py::TestMainCLI::test_main_handles_invalid_csv_format PASSED

7 passed in 6.72s
```

---

## 4. 使用例

### 4.1 基本的な使い方

```bash
# デフォルトディレクトリで実行
python main.py
```

**実行結果**:
- `time_case/`ディレクトリ内のすべての`.csv`ファイルを結合
- `static/downloads/`ディレクトリに`merged_YYYYMMDD_HHMMSS.csv`を作成
- 成功メッセージを標準出力に表示
- 終了コード0を返す

### 4.2 カスタムディレクトリの指定

```bash
# 入力と出力を明示的に指定
python main.py --input data/csv_files --output results
```

**実行結果**:
- `data/csv_files/`ディレクトリ内のCSVファイルを結合
- `results/`ディレクトリに出力
- 出力ディレクトリが存在しない場合は自動作成

### 4.3 ヘルプの表示

```bash
python main.py --help
```

**出力**:
```
usage: main.py [-h] [--input INPUT] [--output OUTPUT]

複数のCSVファイルを結合します

options:
  -h, --help       show this help message and exit
  --input INPUT    入力CSVファイルが格納されているディレクトリ（デフォルト: time_case）
  --output OUTPUT  結合後のCSVファイルを保存するディレクトリ（デフォルト: static/downloads）

使用例:
  python main.py
  python main.py --input time_case --output static/downloads
  python main.py --help
```

### 4.4 シェルスクリプトからの実行

**Windows (PowerShell)**:
```powershell
# 実行
python main.py --input .\input_data --output .\output_data

# 終了コードをチェック
if ($LASTEXITCODE -eq 0) {
    Write-Host "成功しました"
} else {
    Write-Host "失敗しました"
}
```

**Linux/Mac (Bash)**:
```bash
# 実行
python main.py --input ./input_data --output ./output_data

# 終了コードをチェック
if [ $? -eq 0 ]; then
    echo "成功しました"
else
    echo "失敗しました"
fi
```

### 4.5 バッチ処理

```bash
# 複数のディレクトリを順次処理
for dir in data1 data2 data3; do
    python main.py --input "$dir" --output "results/$dir"
done
```

---

## 5. トラブルシューティング

### 5.1 よくあるエラー

#### エラー1: ディレクトリが見つからない

**症状**:
```
エラー: 入力ディレクトリが見つかりません: my_data
```

**原因**: 指定したディレクトリが存在しない

**解決策**:
```bash
# ディレクトリの存在を確認
ls -la my_data  # Linux/Mac
dir my_data     # Windows

# ディレクトリを作成
mkdir -p my_data  # Linux/Mac
mkdir my_data     # Windows
```

#### エラー2: CSVファイルが見つからない

**症状**:
```
エラー: CSVファイルが見つかりませんでした: time_case
```

**原因**: ディレクトリ内にCSVファイルがない

**解決策**:
```bash
# ディレクトリ内のファイルを確認
ls time_case/*.csv

# CSVファイルを配置
cp my_files/*.csv time_case/
```

#### エラー3: CSVフォーマットエラー

**症状**:
```
エラー: CSVフォーマットが不正です: 必須カラムが不足しています
```

**原因**: CSVファイルが要求されるスキーマに合っていない

**解決策**:
- 必須カラムを確認: No, 日時, 電圧, 周波数, パワー, 工事フラグ, 参照
- 日時フォーマットを確認: YYYY/MM/DD HH:00:00
- CSVファイルの修正

#### エラー4: 日時の重複

**症状**:
```
エラー: 結合処理でエラーが発生しました: 日時の重複が検出されました
```

**原因**: 複数のCSVファイルに同じ日時のデータが含まれている

**解決策**:
- 各CSVファイルが異なる日時範囲のデータを含むことを確認
- 重複する日時のデータを持つファイルを除外

### 5.2 デバッグ方法

#### ログレベルの変更

```python
# main.pyのログレベルをDEBUGに変更
logging.basicConfig(
    level=logging.DEBUG,  # INFO → DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
```

#### 詳細なエラー情報の取得

```bash
# Python実行時に詳細なエラー情報を表示
python -u main.py --input my_data --output results 2>&1 | tee error.log
```

---

## 変更履歴

| 日付 | バージョン | 変更内容 | 著者 |
|------|-----------|---------|------|
| 2025-10-19 | 1.0.0 | 初版作成 - CLIエントリーポイント仕様、テスト仕様 | - |

---

**関連ドキュメント**:
- [01_plan.md](./01_plan.md) - プロジェクトプラン
- [02_history_summary.md](./02_history_summary.md) - 開発履歴サマリー
- [03_specification.md](./03_specification.md) - 全体仕様
- [08_usecase_specification.md](./08_usecase_specification.md) - UseCase層詳細仕様

