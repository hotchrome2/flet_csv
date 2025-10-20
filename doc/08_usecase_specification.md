# UseCase層 詳細仕様

**ファイル**: `doc/08_usecase_specification.md`  
**作成日**: 2025-10-19  
**最終更新**: 2025-10-19

このドキュメントは、UseCase層の詳細仕様を記載します。

---

## 目次

1. [概要](#1-概要)
2. [MergeCsvFilesUseCase仕様](#2-mergecsvfilesusecase仕様)
3. [エラーハンドリング](#3-エラーハンドリング)
4. [テスト仕様](#4-テスト仕様)
5. [使用例](#5-使用例)

---

## 1. 概要

### 1.1 責務

UseCase層は、**アプリケーション固有のユースケース**を実装します。

- 複数の層（Domain、Infrastructure）を組み合わせた処理フロー
- ドメイン例外を適切にハンドリング
- ユーザーフレンドリーな結果を返す

### 1.2 依存関係

```
UseCase層
    ↓ 依存
Domain層（models, services, exceptions）
Infrastructure層（repositories）
```

**重要**: UseCase層はDomain層とInfrastructure層に依存しますが、Presentation層からは依存されます。

### 1.3 実装ファイル

| ファイル | 説明 | テストファイル |
|---------|------|--------------|
| `usecase/merge_csv_files.py` | CSV結合ユースケース | `tests/unit/usecase/test_merge_csv_files.py` |

---

## 2. MergeCsvFilesUseCase仕様

**ファイル**: `usecase/merge_csv_files.py`  
**テスト**: `tests/unit/usecase/test_merge_csv_files.py`

### 2.1 クラス定義

```python
class MergeCsvFilesUseCase:
    """CSV結合ユースケース
    
    複数のCSVファイルを読み込み、結合して保存するユースケースを実行します。
    """
    
    def __init__(
        self,
        repository: CsvRepository | None = None,
        merger: CsvMerger | None = None
    ):
        """初期化
        
        Args:
            repository: CSVリポジトリ（Noneの場合は新規作成）
            merger: CSVマージャー（Noneの場合は新規作成）
        """
```

**ポイント**:
- 依存性注入（DI）をサポート
- `repository`と`merger`が`None`の場合、デフォルトインスタンスを作成
- テスト時はモックオブジェクトを注入可能

### 2.2 execute()メソッド

```python
def execute(
    self,
    input_paths: list[str | Path],
    output_dir: str | Path
) -> MergeResult:
    """CSV結合ユースケースを実行
    
    Args:
        input_paths: 入力CSVファイルのパスリスト
        output_dir: 出力先ディレクトリ
        
    Returns:
        結合結果を表すMergeResultオブジェクト
    """
```

#### 処理フロー

```
1. 入力ファイルリストの検証
   ↓
2. ファイルを読み込み (CsvRepository.load)
   ↓
3. CSVファイルを結合 (CsvMerger.merge)
   ↓
4. 結合結果を保存 (CsvRepository.save)
   ↓
5. 成功結果を返す (MergeResult.create_success)
```

**エラー発生時**:
```
例外をキャッチ
   ↓
適切なエラーメッセージを生成
   ↓
失敗結果を返す (MergeResult.create_failure)
```

#### 入力検証

**空リストチェック**:
```python
if not input_paths:
    return MergeResult.create_failure(
        error_message="入力ファイルが指定されていません。"
    )
```

#### ファイル読み込み

```python
csv_files = []
for path in input_paths:
    csv_file = self.repository.load(path)
    csv_files.append(csv_file)
```

**特徴**:
- 各ファイルを順次読み込み
- `CsvRepository.load()`を使用
- 読み込んだファイルは`CsvFile`モデルとして保持

#### 結合処理

```python
merged_file = self.merger.merge(csv_files)
```

**特徴**:
- `CsvMerger.merge()`に委譲
- ドメインサービスがビジネスロジックを担当

#### 保存処理

```python
output_path = self.repository.save(merged_file, output_dir)
```

**特徴**:
- `CsvRepository.save()`を使用
- タイムスタンプ付きファイル名で保存
- 実際の保存パスが返される

#### 成功結果の返却

```python
return MergeResult.create_success(
    output_path=output_path,
    merged_file_count=len(csv_files),
    total_rows=len(merged_file.data),
    message=f"CSVファイルの結合が完了しました。出力: {output_path}"
)
```

**含まれる情報**:
- 出力ファイルパス
- 結合したファイル数
- 総行数
- カスタムメッセージ

---

### 2.3 execute_from_zip()メソッド（NEW）

```python
def execute_from_zip(
    self,
    zip_path: str | Path,
    output_dir: str | Path
) -> MergeResult:
    """ZIP内のCSVを読み込み結合するユースケース"""
```

#### 目的

1つのZIPファイルにまとめられた複数のCSVファイルを読み込み、正規化・結合して保存する。ファイルシステムへの恒久的展開は行わず、Infrastructure層が一時ディレクトリを用いて処理する。

#### 処理フロー

```
1. ZIPからCSV群を読み込み (CsvRepository.load_from_zip)
   ↓
2. CSVファイルを結合 (CsvMerger.merge)
   ↓
3. 結合結果を保存 (CsvRepository.save)
   ↓
4. 成功結果を返す (MergeResult.create_success)
```

#### 入力検証

- ZIP内にCSVが1つもない場合は失敗とする。
  - エラーメッセージ: "ZIPファイル内にCSVファイルがありません"

#### 例外マッピング

- `CsvFileNotFoundError` → "ファイルが見つかりません: ..."（ZIP未存在 等）
- `InvalidCsvFormatError` → "CSVフォーマットが不正です: ..."（ZIP内CSVの不正）
- `MergeError` → "結合処理でエラーが発生しました: ..."
- `EmptyDataError` → "データが空です: ..."
- `CsvMergerError` → "CSV結合エラー: ..."
- `Exception` → "予期しないエラーが発生しました: ..."

#### 成功結果の返却

```python
return MergeResult.create_success(
    output_path=output_path,
    merged_file_count=len(csv_files),
    total_rows=len(merged_file.data),
    message=f"CSVファイルの結合が完了しました。出力: {output_path}"
)
```

---

## 3. エラーハンドリング

### 3.1 エラーハンドリング戦略

UseCase層は、すべてのドメイン例外をキャッチし、ユーザーフレンドリーなエラーメッセージに変換します。

### 3.2 例外マッピング

| ドメイン例外 | エラーメッセージ | 説明 |
|------------|----------------|------|
| `CsvFileNotFoundError` | "ファイルが見つかりません: ..." | 入力ファイルが存在しない |
| `InvalidCsvFormatError` | "CSVフォーマットが不正です: ..." | CSVフォーマットエラー |
| `MergeError` | "結合処理でエラーが発生しました: ..." | 結合時のエラー（重複など） |
| `EmptyDataError` | "データが空です: ..." | 空のCSVファイル |
| `CsvMergerError` | "CSV結合エラー: ..." | その他のドメインエラー |
| `Exception` | "予期しないエラーが発生しました: ..." | 予期しないエラー |

### 3.3 エラーハンドリングの実装

```python
try:
    # 処理...
    
except CsvFileNotFoundError as e:
    return MergeResult.create_failure(
        error_message=f"ファイルが見つかりません: {str(e)}"
    )

except InvalidCsvFormatError as e:
    return MergeResult.create_failure(
        error_message=f"CSVフォーマットが不正です: {str(e)}"
    )

# ... その他の例外ハンドリング
```

**ポイント**:
- 例外は**握りつぶさない**（すべてMergeResultとして返す）
- エラーメッセージは**元の例外情報を含む**
- 失敗時も**必ずMergeResultを返す**

---

## 4. テスト仕様

**テストファイル**: `tests/unit/usecase/test_merge_csv_files.py`

### 4.1 テスト戦略

**単体テストの特徴**:
- **モックの活用**: `CsvRepository`と`CsvMerger`をモック化
- **外部依存の分離**: ファイルシステムやドメインロジックに依存しない
- **高速なテスト**: モックにより高速に実行可能

### 4.2 テストケース一覧

#### 正常系テスト（4テスト）

| テスト名 | 説明 | 検証内容 |
|---------|------|---------|
| `test_successful_merge_with_two_files` | 2つのCSVファイルを正常に結合 | ・`is_successful`が`True`<br>・`output_path`が正しい<br>・`load`が2回呼ばれる<br>・`merge`が1回呼ばれる<br>・`save`が1回呼ばれる |
| `test_successful_merge_with_single_file` | 1つのCSVファイルでも正常に処理 | ・`is_successful`が`True`<br>・`output_path`が正しい |
| `test_multiple_files_merge` | 複数ファイル（3つ以上）を正常に結合 | ・`is_successful`が`True`<br>・`load`が3回呼ばれる<br>・`merge`に3つのファイルが渡される |
| `test_returns_merge_result_object` | MergeResultオブジェクトを返す | ・戻り値が`MergeResult`インスタンス |

#### 異常系テスト（5テスト）

| テスト名 | 説明 | 検証内容 |
|---------|------|---------|
| `test_failure_when_file_not_found` | ファイルが見つからない場合、失敗を返す | ・`is_successful`が`False`<br>・エラーメッセージに"ファイルが見つかりません"が含まれる<br>・ファイル名が含まれる |
| `test_failure_when_invalid_csv_format` | CSVフォーマットが不正な場合、失敗を返す | ・`is_successful`が`False`<br>・エラーメッセージに"CSVフォーマットが不正です"が含まれる<br>・ファイル名が含まれる |
| `test_failure_when_merge_error_occurs` | 結合時にエラーが発生した場合、失敗を返す | ・`is_successful`が`False`<br>・エラーメッセージに"結合処理でエラーが発生しました"が含まれる<br>・"日時の重複"が含まれる |
| `test_failure_when_empty_data` | 空のCSVファイルの場合、失敗を返す | ・`is_successful`が`False`<br>・エラーメッセージに"データが空です"が含まれる |
| `test_failure_when_empty_file_list` | 入力ファイルリストが空の場合、失敗を返す | ・`is_successful`が`False`<br>・エラーメッセージに"入力ファイルが指定されていません"が含まれる |

#### ZIP入力テスト（3テスト）

| テスト名 | 説明 | 検証内容 |
|---------|------|---------|
| `test_execute_from_zip_success` | ZIPから複数CSVを読み込み結合 | ・`is_successful`が`True`<br>・`load_from_zip`が1回呼ばれる<br>・`save`が1回呼ばれる |
| `test_execute_from_zip_nonexistent_zip` | 存在しないZIPは失敗 | ・`is_successful`が`False`<br>・"ファイルが見つかりません"を含む |
| `test_execute_from_zip_invalid_csv_in_zip` | ZIP内CSVが不正なら失敗 | ・`is_successful`が`False`<br>・"CSVフォーマットが不正です"を含む |

### 4.3 モックの設定

**CsvRepositoryのモック**:
```python
mock_repository = Mock()
mock_repository.load.side_effect = [mock_csv_file1, mock_csv_file2]
mock_repository.save.return_value = mock_output_path
```

**CsvMergerのモック**:
```python
mock_merger = Mock()
mock_merger.merge.return_value = mock_merged_file
```

**CsvFileのモック**:
```python
mock_csv_file = Mock(spec=CsvFile)
mock_csv_file.data = [1, 2, 3]  # データ行数を設定
```

### 4.4 テストフィクスチャ

```python
@pytest.fixture
def mock_repository():
    """モックリポジトリのフィクスチャ"""
    return Mock()

@pytest.fixture
def mock_merger():
    """モックマージャーのフィクスチャ"""
    return Mock()

@pytest.fixture
def usecase(mock_repository, mock_merger):
    """UseCaseインスタンスのフィクスチャ"""
    return MergeCsvFilesUseCase(
        repository=mock_repository,
        merger=mock_merger
    )
```

### 4.5 テスト実行

```bash
# UseCase層のテストのみ実行
uv run pytest tests/unit/usecase/ -v

# 全テスト実行
uv run pytest tests/unit/ -q
```

**期待される結果**:
```
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_successful_merge_with_two_files PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_successful_merge_with_single_file PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_failure_when_file_not_found PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_failure_when_invalid_csv_format PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_failure_when_merge_error_occurs PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_failure_when_empty_data PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_failure_when_empty_file_list PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_returns_merge_result_object PASSED
tests/unit/usecase/test_merge_csv_files.py::TestMergeCsvFilesUseCase::test_multiple_files_merge PASSED

9 passed in 0.99s
```

---

## 5. 使用例

### 5.1 基本的な使い方

```python
from pathlib import Path
from usecase.merge_csv_files import MergeCsvFilesUseCase

# UseCaseインスタンスを作成
usecase = MergeCsvFilesUseCase()

# 入力ファイルパスを指定
input_paths = [
    Path("time_case/file1.csv"),
    Path("time_case/file2.csv"),
    Path("time_case/file3.csv"),
]

# 出力ディレクトリを指定
output_dir = Path("static/downloads")

# ユースケースを実行
result = usecase.execute(input_paths, output_dir)

# 結果を確認
if result.is_successful:
    print(f"成功: {result.message}")
    print(f"出力ファイル: {result.output_path}")
    print(f"結合ファイル数: {result.merged_file_count}")
    print(f"総行数: {result.total_rows}")
else:
    print(f"失敗: {result.error_message}")
```

### 5.2 カスタムリポジトリを使用する場合

```python
from usecase.merge_csv_files import MergeCsvFilesUseCase
from infra.repositories.csv_repository import CsvRepository
from domain.services.csv_merger import CsvMerger

# カスタムリポジトリとマージャーを作成
repository = CsvRepository()
merger = CsvMerger()

# UseCaseインスタンスに注入
usecase = MergeCsvFilesUseCase(
    repository=repository,
    merger=merger
)

# 実行
result = usecase.execute(input_paths, output_dir)
```

### 5.3 エラーハンドリング

```python
result = usecase.execute(input_paths, output_dir)

if result.is_successful:
    # 成功時の処理
    print(f"✅ 成功: {result.output_path}")
else:
    # 失敗時の処理
    print(f"❌ エラー: {result.error_message}")
    
    # エラーメッセージに応じた処理
    if "ファイルが見つかりません" in result.error_message:
        print("入力ファイルのパスを確認してください。")
    elif "CSVフォーマットが不正です" in result.error_message:
        print("CSVファイルの形式を確認してください。")
    elif "結合処理でエラーが発生しました" in result.error_message:
        print("日時の重複などがないか確認してください。")
```

### 5.4 Presentation層からの呼び出し（将来）

```python
# main.py または Presentation層から
from usecase.merge_csv_files import MergeCsvFilesUseCase

def merge_csv_files_command(input_paths: list[str], output_dir: str):
    """CLI コマンド"""
    usecase = MergeCsvFilesUseCase()
    result = usecase.execute(input_paths, output_dir)
    
    if result.is_successful:
        print(f"✅ {result.message}")
        return 0  # 成功
    else:
        print(f"❌ {result.error_message}")
        return 1  # 失敗
```

---

## 変更履歴

| 日付 | バージョン | 変更内容 | 著者 |
|------|-----------|---------|------|
| 2025-10-20 | 1.1.0 | execute_from_zip() 仕様とZIPテスト仕様を追加 | - |
| 2025-10-19 | 1.0.0 | 初版作成 - MergeCsvFilesUseCase仕様、テスト仕様 | - |

---

**関連ドキュメント**:
- [03_specification.md](./03_specification.md) - 全体仕様
- [04_domain_specification.md](./04_domain_specification.md) - Domain層詳細仕様
- [05_infrastructure_specification.md](./05_infrastructure_specification.md) - Infrastructure層詳細仕様
- [02_history_summary.md](./02_history_summary.md) - 開発履歴サマリー

