# Infrastructure層 詳細仕様書

このドキュメントは、Infrastructure層（外部依存・I/O処理）の詳細な仕様を定義します。

**対応するテスト**: `tests/unit/infra/**`

---

## 目次

1. [CsvRepository仕様](#1-csvrepository仕様)
2. [多様なCSVフォーマット対応](#2-多様なcsvフォーマット対応)
3. [文字コード自動判定](#3-文字コード自動判定)
4. [正規化処理](#4-正規化処理)
5. [データ検証](#5-データ検証)

---

## 1. CsvRepository仕様

**ファイル**: `infra/repositories/csv_repository.py`  
**テスト**: `tests/unit/infra/repositories/test_csv_repository.py`

### 1.1 責務

CSVファイルの読み書きを担当するリポジトリ。

- 多様なCSVフォーマットの読み込み
- 文字コードの自動判定
- データの正規化（7列統一）
- データの妥当性検証
- CSVファイルの保存

### 1.2 load()メソッド

```python
def load(self, file_path: str | Path) -> CsvFile:
```

#### 処理フロー

1. **ファイル存在チェック**
   - ファイルが存在しない → `CsvFileNotFoundError`

2. **文字コード自動判定**
   - UTF-8 BOM, UTF-8, CP932, Shift-JISを順次試行

3. **CSVファイル読み込み**
   - ヘッダー有無を自動判定
   - pandas.read_csv()で読み込み

4. **正規化処理**
   - 7列統一（No列・参照列の補完）
   - カラム順序の統一

5. **データ検証**
   - 日時カラムの各行をチェック
   - 不正な値があれば`InvalidCsvFormatError`

6. **CsvFileオブジェクト生成**
   - Domain層の`CsvFile`を返す

### 1.3 save()メソッド

```python
def save(self, csv_file: CsvFile, output_path: str | Path) -> None:
```

#### 処理内容

1. **出力ディレクトリの作成**（存在しない場合）
2. **CSVファイルの保存**
   - UTF-8エンコーディング
   - index=False（行番号を含めない）

---

### 1.4 ZIP入力対応（撤廃）

要件変更により、ZIP入力のサポートは撤廃しました。現在は、ディレクトリ内のCSVファイルを直接指定して読み込みます。

---

## 2. 多様なCSVフォーマット対応

### 2.1 対応パターン

Infrastructure層は、以下のすべてのパターンを自動的に正規化します：

| パターン | ヘッダー | No列 | 参照列 | 例 |
|---------|---------|------|-------|-----|
| 完全フォーマット | あり | あり | あり | `full_format.csv` |
| No列なし | あり | **なし** | あり | `no_column_missing.csv` |
| ヘッダーなし | **なし** | **なし** | **なし** | `no_header.csv` |
| クォート付き | あり | あり | あり | `quoted.csv` |
| カラム順序違い | あり | あり | あり | `wrong_order.csv` |

**テストフィクスチャ**: `tests/fixtures/csv/`

### 2.2 ヘッダー有無の判定

#### 判定ロジック

```python
def _read_csv(self, file_path: Path, encoding: str) -> pd.DataFrame:
    # まずヘッダーありとして読み込む
    df_with_header = pd.read_csv(file_path, encoding=encoding)
    
    # 最初のカラム名が日時フォーマットなら → ヘッダーなし
    first_col_name = str(df_with_header.columns[0])
    if CsvSchema.validate_datetime_format(first_col_name):
        # ヘッダーなしとして再読み込み
        df = pd.read_csv(file_path, encoding=encoding, header=None)
        return df
    else:
        # ヘッダーありと判断
        return df_with_header
```

#### 判定例

| 1行目 | 判定 |
|------|------|
| `No,日時,電圧,...` | ヘッダーあり |
| `2025/10/18 00:00:00,100,...` | ヘッダーなし |

### 2.3 クォーテーション対応

pandas.read_csv()が自動的に処理します：

| 入力 | 読み込み結果 |
|------|------------|
| `"No","日時"` | `No`, `日時` |
| `No,日時` | `No`, `日時` |

---

## 3. 文字コード自動判定

### 3.1 対応エンコーディング

以下のエンコーディングを**順番に試行**します：

| 順序 | エンコーディング | 説明 |
|------|----------------|------|
| 1 | `utf-8-sig` | BOM付きUTF-8 |
| 2 | `utf-8` | UTF-8 |
| 3 | `cp932` | Windows日本語（Shift-JISの拡張） |
| 4 | `shift_jis` | Shift-JIS |

**デフォルト**: すべて失敗した場合は`utf-8`

### 3.2 判定ロジック

```python
def _detect_encoding(self, file_path: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                f.read()  # 全体を読み込んでエラーが発生しないか確認
            return encoding  # 成功したらこのエンコーディングを使用
        except (UnicodeDecodeError, LookupError):
            continue  # 次を試す
    
    return "utf-8"  # デフォルト
```

### 3.3 設計方針

- **標準ライブラリのみ使用**: `chardet`などの外部ライブラリは使わない
- **Windows環境に最適化**: 日本語Windowsで使われる典型的なエンコーディングを優先
- **試行順序が重要**: UTF-8系を先に試すことで、モダンなファイルに対応

---

## 4. 正規化処理

### 4.1 正規化の目的

多様なCSVフォーマットを、**統一された7列フォーマット**に変換してDomain層に渡す。

**統一フォーマット**:
- 7列: `No`, `日時`, `電圧`, `周波数`, `パワー`, `工事フラグ`, `参照`
- ヘッダーあり
- No列は1から連番
- 参照列は0で埋める（ない場合）

### 4.2 _normalize()メソッド

#### 処理フロー

1. **ヘッダーなしの場合**: 列数に応じてヘッダーを追加
2. **No列がない場合**: 1から連番で追加
3. **参照列がない場合**: 0で埋める
4. **カラム数検証**: 7列であることを確認
5. **カラム順序統一**: 必ず`No`, `日時`, ... の順に

### 4.3 _normalize_headerless()メソッド

ヘッダーなしCSVの列数別処理：

| 列数 | パターン | 処理 |
|------|---------|------|
| 5列 | 日時,電圧,周波数,パワー,工事フラグ | No列・参照列を追加 |
| 6列 | 日時,電圧,周波数,パワー,工事フラグ,参照 | No列を追加 |
| 7列 | No,日時,電圧,周波数,パワー,工事フラグ,参照 | ヘッダーのみ追加 |

**その他の列数**: `InvalidCsvFormatError`

### 4.4 正規化例

#### 例1: No列なし、ヘッダーあり

**入力**:
```
日時,電圧,周波数,パワー,工事フラグ,参照
2025/10/18 00:00:00,100,50,1000,0,1
```

**正規化後**:
```
No,日時,電圧,周波数,パワー,工事フラグ,参照
1,2025/10/18 00:00:00,100,50,1000,0,1
```

#### 例2: ヘッダーなし（5列）

**入力**:
```
2025/10/18 00:00:00,100,50,1000,0
```

**正規化後**:
```
No,日時,電圧,周波数,パワー,工事フラグ,参照
1,2025/10/18 00:00:00,100,50,1000,0,0
```

#### 例3: カラム順序違い

**入力**:
```
日時,電圧,No,周波数,パワー,参照,工事フラグ
2025/10/18 00:00:00,100,1,50,1000,1,0
```

**正規化後**:
```
No,日時,電圧,周波数,パワー,工事フラグ,参照
1,2025/10/18 00:00:00,100,50,1000,0,1
```

---

## 5. データ検証

### 5.1 _validate_data()メソッド

```python
def _validate_data(self, df: pd.DataFrame, file_name: str) -> None:
```

#### 検証内容

正規化後、各行の日時カラムをチェックします：

1. **日時フォーマット検証**: `CsvSchema.validate_datetime_format()`
2. **日付値の妥当性検証**: `CsvSchema.validate_datetime_value()`
   - 年の範囲（1900〜2100年）
   - 実在する日付（2月30日などを検出）
   - pd.to_datetime()で変換可能か

#### エラー生成

不正な行が見つかった場合：

```python
raise InvalidCsvFormatError.with_invalid_lines(
    file_name=file_name,
    invalid_lines=[3, 5, 6, 8],  # 不正な行番号（2行目から数える）
    error_type="不正な日時"
)
```

**生成されるメッセージ**:
```
invalid_dates.csv: 不正な日時が検出されました（3行目、5行目から6行目、8行目）
```

### 5.2 行番号の数え方

- **1行目**: ヘッダー
- **2行目以降**: データ行

```python
for idx, datetime_value in enumerate(df[CsvSchema.TIMESTAMP_COLUMN], start=2):
    # idx は 2, 3, 4, ... となる
```

### 5.3 検証タイミング

**load()メソッド内で自動実行**:

```
ファイル読み込み
  ↓
正規化
  ↓
データ検証 ← ここで不正な日時を検出
  ↓
CsvFile生成
```

---

## 6. テストフィクスチャ

### 6.1 配置場所

`tests/fixtures/csv/`

### 6.2 フィクスチャ一覧

| ファイル | パターン | 説明 |
|---------|---------|------|
| `full_format.csv` | 完全フォーマット | ヘッダーあり、No列あり、UTF-8 |
| `no_column_missing.csv` | No列なし | ヘッダーあり、No列なし |
| `no_header.csv` | ヘッダーなし | ヘッダーなし、No列なし、参照列なし |
| `shift_jis.csv` | Shift-JIS | Shift-JISエンコーディング |
| `quoted.csv` | クォート付き | すべての値が`""`で囲まれている |
| `wrong_order.csv` | カラム順序違い | No列が3番目にある |
| `invalid_dates.csv` | 不正な日時 | 0002年、9999年などを含む |

### 6.3 フィクスチャの使い方

```python
@pytest.fixture
def fixtures_dir(self):
    """テストフィクスチャディレクトリのパスを提供"""
    return Path(__file__).parent.parent.parent.parent / "fixtures" / "csv"

def test_load_csv(self, csv_repository, fixtures_dir):
    csv_path = fixtures_dir / "full_format.csv"
    result = csv_repository.load(csv_path)
    assert result.row_count == 24
```

---

## 7. エラーケース

### 7.1 ファイル未存在

```python
try:
    csv_file = repository.load("nonexistent.csv")
except CsvFileNotFoundError as e:
    # "CSVファイルが見つかりません: nonexistent.csv"
```

### 7.2 不正なフォーマット

```python
try:
    csv_file = repository.load("invalid_dates.csv")
except InvalidCsvFormatError as e:
    # "invalid_dates.csv: 不正な日時が検出されました（3行目、5行目から6行目、8行目）"
```

### 7.3 列数不正

ヘッダーなしで5列・6列・7列以外の場合：

```python
# 4列のCSVファイル
# → InvalidCsvFormatError: "ヘッダーなしCSVは5列、6列、または7列である必要があります（実際: 4列）"
```

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-10-20 | 1.1.0 | ZIP入力対応 `load_from_zip()` の仕様を追記 |
| 2025-10-19 | 1.0.0 | 初版作成 - Infrastructure層の詳細仕様を文書化 |

