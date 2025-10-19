# 機能仕様書（全体）

このドキュメントは、flet-csvアプリケーション全体のアーキテクチャと共通ルールを定義します。
**各層の詳細仕様は、個別のドキュメントを参照してください。**

---

## 📚 仕様書の構成

| ドキュメント | 内容 | 対応するテスト | 状態 |
|------------|------|--------------|------|
| **03_specification.md**（本書） | 全体アーキテクチャ、共通ルール | - | ✅ 完成 |
| **04_domain_specification.md** | Domain層の詳細仕様 | `tests/unit/domain/**` | ✅ 完成 |
| **05_infrastructure_specification.md** | Infrastructure層の詳細仕様 | `tests/unit/infra/**` | ✅ 完成 |
| **08_usecase_specification.md** | UseCase層の詳細仕様 | `tests/unit/usecase/**` | ✅ 完成 |
| **09_cli_specification.md** | CLIエントリーポイントの詳細仕様 | `tests/e2e/**` | ✅ 完成 |

---

## 1. プロジェクト概要

### 1.1 目的

複数の時系列CSVファイルを結合し、1つのCSVファイルとして出力する。

### 1.2 主要機能

1. **CSVファイルの読み込み**
   - 多様なフォーマットに対応（ヘッダー有無、文字コードなど）
   - データの自動正規化

2. **データ検証**
   - 日時の妥当性チェック
   - 詳細なエラーメッセージの生成

3. **CSV結合**
   - 複数ファイルの結合
   - 時系列順ソート
   - 重複検出

4. **CSVファイルの出力**
   - UTF-8エンコーディング
   - 統一されたフォーマット

---

## 2. アーキテクチャ

### 2.1 クリーンアーキテクチャ

```
┌─────────────────────────────────────────┐
│        Presentation Layer (UI)          │  ← 将来実装
│              (Flet)                     │
├─────────────────────────────────────────┤
│        UseCase Layer                    │  ✅ 完成
│    (merge_csv_files.py)                 │
├─────────────────────────────────────────┤
│        Domain Layer                     │  ✅ 完成
│    (models, services, exceptions)       │
├─────────────────────────────────────────┤
│        Infrastructure Layer             │  ✅ 完成
│    (repositories)                       │
└─────────────────────────────────────────┘
```

### 2.2 依存関係のルール

- **外側の層は内側の層に依存できる**
- **内側の層は外側の層に依存してはいけない**

```
Presentation → UseCase → Domain ← Infrastructure
```

### 2.3 レイヤーの責務

#### Domain層（ビジネスロジック）
- **Models**: エンティティと値オブジェクト
- **Services**: ドメインサービス（結合ロジック）
- **Exceptions**: ドメイン固有の例外

**詳細**: [04_domain_specification.md](./04_domain_specification.md)

#### Infrastructure層（外部依存）
- **Repositories**: ファイルI/O、データの正規化

**詳細**: [05_infrastructure_specification.md](./05_infrastructure_specification.md)

#### UseCase層（アプリケーションロジック）
- 複数の層を組み合わせたユースケース
- CSV結合の一連の処理を統括

**詳細**: [08_usecase_specification.md](./08_usecase_specification.md)

#### Presentation層（UI）
- Fletを使用したユーザーインターフェース
- **未実装**（UIチーム担当）

---

## 3. 共通データ構造

### 3.1 CSVスキーマ

すべてのCSVファイルは、以下の7列を含みます：

| 列名 | データ型 | 説明 |
|------|---------|------|
| No | int | データ番号 |
| 日時 | datetime_string | YYYY/MM/DD HH:00:00 形式 |
| 電圧 | int | 電圧値 |
| 周波数 | int | 周波数値 |
| パワー | int | パワー値 |
| 工事フラグ | int | 0 または 1 |
| 参照 | int | 0 または 1 |

**詳細**: [04_domain_specification.md](./04_domain_specification.md#1-csvスキーマ仕様)

---

## 4. エラーハンドリング戦略

### 4.1 例外階層

```
CsvMergerError（基底例外）
├── InvalidCsvFormatError（フォーマット不正）
├── CsvFileNotFoundError（ファイル未存在）
├── MergeError（結合エラー）
└── EmptyDataError（データ空）
```

### 4.2 エラーメッセージ設計原則

1. **具体性**: 何が問題かを明確に
2. **場所の特定**: ファイル名、行番号を含む
3. **ユーザーフレンドリー**: 開発者でなくても理解できる
4. **アクション指向**: どうすれば解決できるかのヒント

**良い例**:
```
invalid_dates.csv: 不正な日時が検出されました（3行目、5行目から6行目、8行目）
```

**悪い例**:
```
ValueError: invalid literal for int() with base 10
```

**詳細**: [04_domain_specification.md](./04_domain_specification.md#5-エラーハンドリング)

---

## 5. TDD開発フロー

### 5.1 基本フロー

```
[仕様確認] → [Red] → [Green] → [Refactor] → [仕様書更新] → [レビュー]
     ↓
該当する仕様書を参照
```

### 5.2 仕様書の選び方

| 実装対象 | 参照する仕様書 |
|---------|--------------|
| Domain層のモデル・サービス | `04_domain_specification.md` |
| Infrastructure層のリポジトリ | `05_infrastructure_specification.md` |
| UseCase層 | `06_usecase_specification.md`（将来） |
| 全体的なルール・アーキテクチャ | `03_specification.md`（本書） |

---

## 6. コーディング規約

### 6.1 Python標準

- **PEP 8準拠**（black で自動整形）
- **型ヒント必須**（Python 3.13形式、mypy でチェック）
- **import順序**（isort で統一）

### 6.2 型ヒント

```python
# Python 3.13形式を使用
def load(self, file_path: str | Path) -> CsvFile:  # ✅
def load(self, file_path: Union[str, Path]) -> CsvFile:  # ❌ 古い

def merge(self, files: list[CsvFile]) -> CsvFile:  # ✅
def merge(self, files: List[CsvFile]) -> CsvFile:  # ❌ 古い
```

### 6.3 Docstrings

Google形式を使用：

```python
def merge(self, csv_files: list[CsvFile]) -> CsvFile:
    """複数のCSVファイルを1つに結合
    
    Args:
        csv_files: 結合するCSVファイルのリスト
        
    Returns:
        結合後の新しいCsvFileオブジェクト
        
    Raises:
        ValueError: 空リストが渡された場合
        MergeError: 日時の重複がある場合
    """
```

---

## 7. テスト戦略

### 7.1 テストの種類

| テスト種別 | 対象 | ディレクトリ |
|-----------|------|------------|
| **単体テスト** | 各クラス・関数の動作 | `tests/unit/` |
| **統合テスト** | 複数のクラスの連携 | `tests/integration/`（将来） |
| **E2Eテスト** | アプリ全体の動作 | `tests/e2e/`（将来） |

### 7.2 テストカバレッジ目標

- **単体テスト**: 100%（Domain層・Infrastructure層）
- **統合テスト**: 主要なユースケースをカバー
- **E2Eテスト**: ハッピーパスと主要なエラーケース

### 7.3 テストフィクスチャ

共通のテストデータは `tests/fixtures/` に配置：

```
tests/fixtures/
└── csv/
    ├── full_format.csv          # 完全フォーマット
    ├── no_column_missing.csv    # No列なし
    ├── no_header.csv            # ヘッダーなし
    ├── shift_jis.csv            # Shift-JIS
    ├── quoted.csv               # クォート付き
    ├── wrong_order.csv          # カラム順序違い
    └── invalid_dates.csv        # 不正な日時
```

---

## 8. 将来の拡張性

### 8.1 フォーマット変更への対応

**現在**: `YYYY/MM/DD HH:00:00`

**対応済み**:
- ✅ `pd.to_datetime()` で自動パース
- ✅ datetime型でソート

**将来の変更例**:
- `DD/MM/YYYY HH:00:00`
- `YYYY-MM-DD HH:00:00`
- ISO 8601形式

### 8.2 データ検証の拡張

現在は日時のみ検証していますが、同じパターンで拡張可能：

```python
# 将来の拡張例
def _validate_data(self, df: pd.DataFrame, file_name: str) -> None:
    self._validate_datetime_column(df, file_name)
    self._validate_voltage_column(df, file_name)  # NEW
    self._validate_flag_columns(df, file_name)    # NEW
```

### 8.3 新しいデータ型への対応

現在の7列から拡張する場合：

1. `CsvSchema.REQUIRED_COLUMNS` に追加
2. `CsvSchema.COLUMN_TYPES` で型を定義
3. 検証ロジックを追加（必要に応じて）
4. テストを追加
5. 仕様書を更新

---

## 9. UIチーム向けガイド

### 9.1 API概要

#### 基本的な使い方

```python
from infra.repositories.csv_repository import CsvRepository
from domain.services.csv_merger import CsvMerger

# リポジトリとサービスを初期化
repository = CsvRepository()
merger = CsvMerger()

# CSVファイルを読み込む
csv_files = []
for path in file_paths:
    csv_file = repository.load(path)
    csv_files.append(csv_file)

# 結合する
result = merger.merge(csv_files)

# 保存する
repository.save(result, "static/downloads")
```

### 9.2 エラーハンドリング

```python
from domain.exceptions import (
    InvalidCsvFormatError,
    CsvFileNotFoundError,
    MergeError,
    CsvMergerError,
)

try:
    csv_file = repository.load(path)
except CsvFileNotFoundError as e:
    # ファイルが見つかりません
    show_error_dialog(f"エラー: {e}")
except InvalidCsvFormatError as e:
    # フォーマットが不正です（詳細な行番号情報あり）
    show_error_dialog(f"エラー: {e}")
except CsvMergerError as e:
    # その他のエラー
    show_error_dialog(f"エラー: {e}")
```

### 9.3 プログレス表示

```python
total_files = len(file_paths)

# 読み込みフェーズ（0% - 70%）
for i, path in enumerate(file_paths):
    progress = int((i + 1) / total_files * 70)
    update_progress(progress, f"読み込み中: {path}")
    csv_file = repository.load(path)
    csv_files.append(csv_file)

# 結合フェーズ（70% - 90%）
update_progress(80, "結合中...")
result = merger.merge(csv_files)

# 保存フェーズ（90% - 100%）
update_progress(95, "保存中...")
output_path = repository.save(result, "static/downloads")
update_progress(100, "完了!")
```

**詳細なAPI仕様は各層の仕様書を参照してください。**

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2025-10-19 | 1.1.0 | 仕様書を階層化 - 全体仕様と詳細仕様を分離 |
| 2025-10-19 | 1.0.0 | 初版作成 - 全機能の仕様を統合 |
