# Domain層 詳細仕様書

このドキュメントは、Domain層（ビジネスロジック）の詳細な仕様を定義します。

**対応するテスト**: `tests/unit/domain/**`

---

## 目次

1. [CSVスキーマ仕様](#1-csvスキーマ仕様)
2. [CsvFileモデル仕様](#2-csvfileモデル仕様)
3. [MergeResultモデル仕様](#3-mergeresultモデル仕様)
4. [CsvMergerサービス仕様](#4-csvmergerサービス仕様)
5. [エラーハンドリング仕様](#5-エラーハンドリング仕様)

---

## 1. CSVスキーマ仕様

**ファイル**: `domain/models/csv_schema.py`  
**テスト**: `tests/unit/domain/models/test_csv_schema.py`

### 1.1 必須カラム

| 列名 | データ型 | 説明 | 制約 |
|------|---------|------|------|
| No | int | データ番号 | 1以上の整数 |
| 日時 | datetime_string | 時系列データの基準 | YYYY/MM/DD HH:00:00 形式 |
| 電圧 | int | 電圧値 | 整数 |
| 周波数 | int | 周波数値 | 整数 |
| パワー | int | パワー値 | 整数 |
| 工事フラグ | int | 工事中フラグ | 0 または 1 |
| 参照 | int | 参照情報 | 0 または 1 |

**カラム順序**: `No`, `日時`, `電圧`, `周波数`, `パワー`, `工事フラグ`, `参照`

### 1.2 日時フォーマット

#### 形式
- **フォーマット**: `YYYY/MM/DD HH:00:00`
- **例**: `2025/10/18 10:00:00`
- **時刻**: 毎正時（00分00秒）のみ
- **時間範囲**: 00時〜23時

**正規表現**: `^\d{4}/\d{2}/\d{2} ([01]\d|2[0-3]):00:00$`

#### 妥当性検証
- **年の範囲**: 1900年〜2100年
- **実在する日付**: 2月30日、13月などは不正
- **うるう年**: 正しく判定（2024/02/29は有効）
- **pd.to_datetime()互換性**: 結合処理で使用するため、pd.to_datetime()でパース可能である必要がある

**検証メソッド**:
- `validate_datetime_format(datetime_str)`: フォーマット検証
- `validate_datetime_value(datetime_str)`: 値の妥当性検証

### 1.3 1日分データ制約

各入力CSVファイルは、**1日分のデータ**を含む必要があります。

#### 条件
- **レコード数**: 24個（00時〜23時）
- **日付**: すべて同じ日付
- **時刻**: 00時から23時まで全て存在
- **重複**: 同じ時刻が重複しない
- **順序**: 時刻の順序は問わない（読み込み時は順不同でもOK）

**検証メソッド**: `validate_daily_time_range(datetime_strings)`

#### エラーケース
- レコード数が24でない
- 同じ日付でない（例：2025/10/18と2025/10/19が混在）
- 時刻が欠けている（例：05時のデータがない）
- 時刻が重複している（例：10時が2回ある）

---

## 2. CsvFileモデル仕様

**ファイル**: `domain/models/csv_file.py`  
**テスト**: `tests/unit/domain/models/test_csv_file.py`

### 2.1 責務

CSVファイルを表現するドメインモデル。

- CSVデータ（pandas.DataFrame）を保持
- ファイルパス情報を保持
- スキーマ検証を実行
- 1日分データ制約の検証（オプション）

### 2.2 初期化

```python
def __init__(
    self,
    file_path: str | Path,
    data: pd.DataFrame,
    skip_daily_validation: bool = False
):
```

#### 引数
- `file_path`: CSVファイルのパス
- `data`: CSVデータ（pandas.DataFrame）
- `skip_daily_validation`: 1日分データ検証をスキップするか（結合後のファイル用）

#### 検証
1. **空データチェック**: dataが空の場合 → `EmptyDataError`
2. **スキーマ検証**: 必須カラムが揃っているか → `InvalidCsvFormatError`
3. **1日分データ検証**（`skip_daily_validation=False`の場合）: 24時間分のデータか → `InvalidCsvFormatError`

### 2.3 プロパティ

| プロパティ | 型 | 説明 |
|----------|-----|------|
| `file_path` | Path | ファイルパス |
| `data` | pd.DataFrame | CSVデータ |
| `row_count` | int | 行数 |
| `column_count` | int | 列数 |
| `column_names` | list[str] | カラム名リスト |
| `file_name` | str | ファイル名（パスのみ） |
| `is_empty` | bool | データが空かどうか |

### 2.4 使用例

```python
# 正常なケース
data = pd.DataFrame({...})  # 24行、7列
csv_file = CsvFile("data.csv", data)

# 結合後のデータ（複数日分）
merged_data = pd.DataFrame({...})  # 48行、7列
csv_file = CsvFile("merged.csv", merged_data, skip_daily_validation=True)
```

---

## 3. MergeResultモデル仕様

**ファイル**: `domain/models/merge_result.py`  
**テスト**: `tests/unit/domain/models/test_merge_result.py`

### 3.1 責務

CSV結合処理の結果を表現するドメインモデル。

- 成功/失敗の状態を保持
- 結合後のCSVファイルを保持（成功時）
- エラー情報を保持（失敗時）

### 3.2 初期化

```python
def __init__(
    self,
    is_successful: bool,
    merged_file: CsvFile | None = None,
    error_message: str = "",
    output_file_path: Path | None = None
):
```

#### 引数
- `is_successful`: 結合が成功したかどうか
- `merged_file`: 結合後のCSVファイル（成功時のみ）
- `error_message`: エラーメッセージ（失敗時）
- `output_file_path`: 出力ファイルのパス

### 3.3 ファクトリメソッド

#### 成功ケース
```python
@classmethod
def success(
    cls,
    merged_file: CsvFile,
    output_file_path: str | Path,
    message: str = "結合処理が成功しました。"
) -> "MergeResult":
```

#### 失敗ケース
```python
@classmethod
def failure(
    cls,
    error_message: str
) -> "MergeResult":
```

### 3.4 プロパティ

| プロパティ | 型 | 説明 |
|----------|-----|------|
| `is_successful` | bool | 成功したかどうか |
| `has_error` | bool | エラーがあるかどうか（`not is_successful`） |
| `merged_file` | CsvFile \| None | 結合後のファイル |
| `error_message` | str | エラーメッセージ |
| `output_file_path` | Path \| None | 出力ファイルパス |
| `output_file_name` | str | 出力ファイル名 |

### 3.5 使用例

```python
# 成功ケース
result = MergeResult.success(
    merged_file=csv_file,
    output_file_path=Path("output/merged.csv")
)

# 失敗ケース
result = MergeResult.failure(
    error_message="日時の重複が検出されました"
)
```

---

## 4. CsvMergerサービス仕様

**ファイル**: `domain/services/csv_merger.py`  
**テスト**: `tests/unit/domain/services/test_csv_merger.py`

### 4.1 責務

複数のCSVファイルを結合するドメインサービス。

### 4.2 merge()メソッド

```python
def merge(self, csv_files: list[CsvFile]) -> CsvFile:
```

#### 処理フロー

1. **入力検証**: 空リストの場合 → `ValueError`
2. **1ファイルのみの場合**: No列を再採番して返す
3. **複数ファイルの場合**:
   - すべてのDataFrameを`pd.concat()`で結合
   - 日時カラムで昇順ソート（**datetime型に変換してソート**）
   - 日時の重複チェック → 重複があれば`MergeError`
   - No列を1から連番で再採番
   - 新しい`CsvFile`オブジェクトを生成（`skip_daily_validation=True`）

#### ソート仕様（重要）

**datetime型でソート**（将来のフォーマット変更に対応）：

```python
# datetime型に変換
merged_df[timestamp_col] = pd.to_datetime(merged_df[timestamp_col])
# ソート
merged_df = merged_df.sort_values(by=timestamp_col).reset_index(drop=True)
# 元の文字列フォーマットに戻す
merged_df[timestamp_col] = merged_df[timestamp_col].dt.strftime("%Y/%m/%d %H:%M:%S")
```

**理由**:
- 文字列ソートはフォーマット依存
- datetime型ソートは必ず時系列順になる

### 4.3 重複検出

同じ日時が複数のファイルに存在する場合、`MergeError`を発生。

**エラーメッセージ例**:
```
日時の重複が検出されました: 2025/10/18 10:00:00, 2025/10/18 15:00:00
```

**最大表示数**: 5件（それ以上は`...`で省略）

### 4.4 No列再採番

結合後、No列は必ず1から連番で再採番されます。

**例**:
```
入力1: No=1,2,3
入力2: No=1,2,3
結合後: No=1,2,3,4,5,6
```

### 4.5 使用例

```python
merger = CsvMerger()

# 2つのファイルを結合
result = merger.merge([csv_file1, csv_file2])

# 複数ファイルを結合
result = merger.merge([csv_file1, csv_file2, csv_file3])

# エラーケース
try:
    result = merger.merge([csv_with_duplicate])
except MergeError as e:
    print(f"エラー: {e}")
```

---

## 5. エラーハンドリング仕様

**ファイル**: `domain/exceptions.py`  
**テスト**: `tests/unit/domain/test_exceptions.py`

### 5.1 例外階層

```
CsvMergerError（基底例外）
├── InvalidCsvFormatError（フォーマット不正）
├── CsvFileNotFoundError（ファイル未存在）
├── MergeError（結合エラー）
└── EmptyDataError（データ空）
```

### 5.2 InvalidCsvFormatError

#### 基本的な使い方

```python
raise InvalidCsvFormatError("CSVファイルのフォーマットが不正です。")
```

#### 行番号情報付きエラー（推奨）

```python
error = InvalidCsvFormatError.with_invalid_lines(
    file_name="invalid_dates.csv",
    invalid_lines=[3, 5, 6, 8],
    error_type="不正な日時"
)
raise error
```

**生成されるメッセージ**:
```
invalid_dates.csv: 不正な日時が検出されました（3行目、5行目から6行目、8行目）
```

#### 行番号の範囲圧縮アルゴリズム

連続する行番号は範囲形式で表示：

| 入力 | 出力 |
|------|------|
| `[1, 2, 3]` | `"1行目から3行目"` |
| `[5]` | `"5行目"` |
| `[7, 8, 9]` | `"7行目から9行目"` |
| `[1, 2, 3, 5, 7, 8, 9]` | `"1行目から3行目、5行目、7行目から9行目"` |

### 5.3 各例外の使用場面

#### InvalidCsvFormatError
**発生条件**:
- CSVフォーマットが不正
- カラム構造が期待と異なる
- データ型が不正
- 日時値が不正

**使用場所**:
- `CsvFile.__init__()`: スキーマ検証、1日分データ検証
- `CsvRepository._validate_data()`: 日時値の検証

#### CsvFileNotFoundError
**発生条件**:
- 指定されたパスにCSVファイルが存在しない

**使用場所**:
- `CsvRepository.load()`: ファイル存在チェック

#### MergeError
**発生条件**:
- 日時の重複
- 結合処理中の一般的なエラー

**使用場所**:
- `CsvMerger.merge()`: 重複検出時

#### EmptyDataError
**発生条件**:
- CSVファイルが空
- ヘッダーのみでデータ行がない
- 結合対象のファイルが0件

**使用場所**:
- `CsvFile.__init__()`: 空データチェック
- `CsvMerger.merge()`: 空リストチェック

### 5.4 エラーハンドリングのベストプラクティス

```python
from domain.exceptions import CsvMergerError, InvalidCsvFormatError

try:
    csv_file = CsvFile(path, data)
except InvalidCsvFormatError as e:
    # 具体的なエラーをキャッチ
    print(f"フォーマットエラー: {e}")
except CsvMergerError as e:
    # 基底例外でキャッチ
    print(f"一般的なエラー: {e}")
```

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-10-19 | 1.0.0 | 初版作成 - Domain層の詳細仕様を文書化 |

