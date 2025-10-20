# 設計判断記録（Design Decisions）

**ファイル**: `doc/01_1_design_decisions.md`  
**作成日**: 2025-10-19  
**最終更新**: 2025-10-19

このドキュメントは、プロジェクトにおける重要な設計判断の理由と背景を記録します。

---

## 目次

1. [概要](#1-概要)
2. [Domain層の設計判断](#2-domain層の設計判断)
3. [Infrastructure層の設計判断](#3-infrastructure層の設計判断)
4. [UseCase層の設計判断](#4-usecase層の設計判断)
5. [その他の設計判断](#5-その他の設計判断)

---

## 1. 概要

### 1.1 このドキュメントの目的

- **設計判断の記録**: なぜその設計を選択したのか、理由を明確にする
- **代替案の検討**: 他の選択肢とその却下理由を記録する
- **将来の参考**: 将来の変更時に過去の判断を振り返る材料とする
- **チーム共有**: 設計の意図をチームメンバーに伝える

### 1.2 記録の方針

- **重要な設計判断のみ記録**: 些細な実装の詳細は記録しない
- **理由を明確に**: 「なぜ」を重視する
- **代替案を示す**: 検討した他の選択肢を記録する
- **将来の見直しポイントを示す**: どうなったら再検討すべきかを明示する

---

## 2. Domain層の設計判断

### 2.1 CsvSchemaで`@dataclass`を使わなかった理由

**判断日**: 2025-10-18  
**関連ファイル**: `domain/models/csv_schema.py`

#### 2.1.1 現在の実装

```python
class CsvSchema:
    """CSVファイルのスキーマ定義（ルール集）"""
    
    # クラス変数で「ルール」を定義
    TIMESTAMP_COLUMN: str = "日時"
    REQUIRED_COLUMNS: list[str] = ["日時", "No", "電圧", ...]
    COLUMN_TYPES: dict[str, type | str] = {"日時": "datetime_string", ...}
    
    @classmethod
    def validate_columns(cls, df: pd.DataFrame) -> None:
        """カラム検証"""
        ...
    
    @classmethod
    def validate_datetime_value(cls, value: str) -> bool:
        """日時検証"""
        ...
```

#### 2.1.2 検討した代替案

##### 代替案A: レコード型としての`@dataclass`

```python
from dataclasses import dataclass

@dataclass
class CsvRecord:
    """1行のCSVデータを表現"""
    日時: str
    No: int
    電圧: int
    周波数: int
    パワー: int
    工事フラグ: int
    参照: int
```

**却下理由**:
1. **Pandasを使用**: DataFrameが行データを管理するため、個別レコードクラスは冗長
2. **パフォーマンス**: 数千行のデータを個別オブジェクトに変換するのは非効率
3. **不要な抽象化**: DataFrameで十分な表現力がある

##### 代替案B: スキーマ設定型としての`@dataclass`

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class CsvSchema:
    """スキーマを「値」として扱う"""
    required_columns: list[str] = field(default_factory=lambda: ["日時", "No", ...])
    column_types: dict[str, type] = field(default_factory=dict)
    timestamp_column: str = "日時"
    
    def validate_columns(self, df: pd.DataFrame) -> None:
        """検証メソッド"""
        pass
```

**却下理由**:
1. **スキーマは1つだけ**: 複数のスキーマを動的に切り替える要件がない
2. **静的な定義で十分**: ハードコードされたルールで問題ない
3. **シンプルさ優先**: 不要な複雑さを避ける（YAGNI原則）

#### 2.1.3 採用した設計の理由

1. **スキーマは「値」ではなく「ルール」**
   - データを保持するのではなく、検証ルールを定義する
   - 静的な定義で十分

2. **Pandasとの統合**
   - DataFrameが行データを管理
   - 個別レコードクラスは不要

3. **シンプルさ優先**
   - クラス変数 + クラスメソッドで十分な表現力
   - インスタンス化のオーバーヘッドなし

4. **パフォーマンス**
   - 静的なクラス定義で高速
   - 大量データを扱う場合に有利

#### 2.1.4 設計比較表

| 項目 | 現在の設計<br>（クラス変数） | dataclass<br>（レコード型） | dataclass<br>（スキーマ値型） |
|------|------------------------|--------------------------|----------------------------|
| **用途** | ルール定義・検証 | 個別レコード表現 | スキーマ設定管理 |
| **インスタンス化** | 不要 | 必要（各行） | 必要（スキーマごと） |
| **データ保持** | なし（ルールのみ） | あり（1行分） | あり（設定） |
| **型安全性** | △ | ◎ | ◎ |
| **パフォーマンス** | ◎ | △ (大量データで×) | ○ |
| **拡張性** | △ | ○ | ◎ |
| **シンプルさ** | ◎ | ○ | △ |
| **今回の用途** | ✅ 最適 | ❌ 不要 | ❌ オーバーエンジニアリング |

#### 2.1.5 将来の見直しポイント

以下の要件が発生した場合、`@dataclass`の採用を再検討する：

1. **複数のスキーマを動的に切り替えたい**
   ```python
   schema_v1 = CsvSchema(required_columns=[...])
   schema_v2 = CsvSchema(required_columns=[...])
   schema = schema_v1 if condition else schema_v2
   ```

2. **DataFrameを使わず、個別オブジェクトで管理したい**
   ```python
   records: list[CsvRecord] = [
       CsvRecord(日時="2025/01/01 00:00:00", No=1, ...),
       ...
   ]
   ```

3. **スキーマ設定を外部から読み込みたい**
   ```python
   schema = CsvSchema.from_yaml("schema.yaml")
   schema = CsvSchema.from_json("schema.json")
   ```

4. **複数のCSV形式を同時にサポートしたい**
   ```python
   legacy_schema = CsvSchema(required_columns=[...])
   new_schema = CsvSchema(required_columns=[...])
   ```

#### 2.1.6 教訓

> **「データを保持するか、ルールを定義するか」を見極める**

- **データを保持** → `@dataclass`が適切
  - 例: ユーザー情報、注文データ、商品情報
- **ルールを定義** → 通常のクラスで十分
  - 例: バリデーションルール、変換ルール、制約定義

今回は「CSVのルール定義」という用途なので、`@dataclass`は不要と判断しました。

---

### 2.2 CsvFileでpandas.DataFrameを内部保持した理由

**判断日**: 2025-10-18  
**関連ファイル**: `domain/models/csv_file.py`

#### 2.2.1 現在の実装

```python
class CsvFile:
    """CSVファイルを表現するドメインモデル
    
    pandas.DataFrameを内部に保持し、CSV検証とデータアクセスを提供
    """
    
    def __init__(self, data: pd.DataFrame, file_path: str | Path | None = None, ...):
        self._data = data
        self._file_path = Path(file_path) if file_path else None
        # 検証
        CsvSchema.validate_columns(self._data)
        ...
```

#### 2.2.2 検討した代替案

##### 代替案A: リスト+辞書で保持

```python
class CsvFile:
    def __init__(self, records: list[dict[str, Any]], ...):
        self._records = records
```

**却下理由**:
1. **パフォーマンス**: 大量データの処理が遅い
2. **機能不足**: ソート、フィルタ、集計が面倒
3. **再発明**: pandasで既に解決済みの問題

##### 代替案B: CsvRecordのリスト

```python
@dataclass
class CsvRecord:
    日時: str
    No: int
    ...

class CsvFile:
    def __init__(self, records: list[CsvRecord], ...):
        self._records = records
```

**却下理由**:
1. **パフォーマンス**: 数千のオブジェクト作成は重い
2. **DataFrame変換**: 結局、保存時にDataFrameに変換する必要がある
3. **複雑化**: 不要な抽象化層が増える

#### 2.2.3 採用した設計の理由

1. **pandasの強力な機能を活用**
   - ソート、結合、フィルタリングが簡単
   - CSV読み書きが高速

2. **パフォーマンス**
   - 大量データの処理に最適化されている
   - NumPyベースで高速

3. **実用性**
   - CSV処理の標準的な選択肢
   - Infrastructure層との統合が容易

4. **クリーンアーキテクチャとの両立**
   - `CsvFile`クラスでラップすることでDomain層の抽象化を維持
   - 外部ライブラリへの依存は隠蔽されている

#### 2.2.4 懸念点と対策

**懸念**: pandasへの依存がDomain層に入り込む

**対策**:
- `CsvFile`クラスで適切にカプセル化
- 公開プロパティを通じてのみアクセス
- 将来、pandas以外のバックエンドに切り替え可能な設計

#### 2.2.5 将来の見直しポイント

以下の状況になった場合、DataFrameの使用を再検討する：

1. **pandasの依存が重すぎる**: 軽量化が必要な環境（組み込みなど）
2. **別のデータ処理ライブラリが主流になる**: Polarsなど
3. **純粋なPythonオブジェクトが必要**: ORM連携など

---

## 3. Infrastructure層の設計判断

### 3.1 文字コード検出でchardetを使わなかった理由

**判断日**: 2025-10-19  
**関連ファイル**: `infra/repositories/csv_repository.py`

#### 3.1.1 現在の実装

```python
def _detect_encoding(self, file_path: Path) -> str:
    """エンコーディングを自動検出
    
    標準ライブラリのみを使用し、一般的なエンコーディングを順に試す
    """
    encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    raise InvalidCsvFormatError(...)
```

#### 3.1.2 検討した代替案

##### 代替案: chardetライブラリを使用

```python
import chardet

def _detect_encoding(self, file_path: Path) -> str:
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result['encoding']
```

**却下理由**:
1. **依存関係の増加**: 新しい外部ライブラリの追加
2. **精度の問題**: 日本語の小さなファイルでは誤検出が多い
3. **不要な複雑さ**: 既知のエンコーディングを試す方が確実
4. **ユーザーからの明示的な要請**: "基本的に新たなパッケージはインストールしないでください"

#### 3.1.3 採用した設計の理由

1. **標準ライブラリのみ使用**
   - 追加の依存なし
   - シンプルで理解しやすい

2. **確実性**
   - Windows日本語環境で使われる典型的なエンコーディングを優先順位付け
   - 試行錯誤方式で確実に読み込める

3. **十分な実用性**
   - 対象のエンコーディングは限定的（UTF-8, CP932, Shift-JIS）
   - 自動検出の精度は十分

#### 3.1.4 エンコーディングの優先順位

| 順位 | エンコーディング | 理由 |
|------|----------------|------|
| 1 | `utf-8-sig` | BOM付きUTF-8（Excelなど） |
| 2 | `utf-8` | 最も一般的な現代的エンコーディング |
| 3 | `cp932` | Windows日本語環境の標準 |
| 4 | `shift_jis` | レガシーな日本語エンコーディング |

**削除したエンコーディング**:
- ~~`euc-jp`~~: 使用頻度が低い（ユーザー要請で削除）
- ~~`iso-2022-jp`~~: メール用、CSV使用は稀（ユーザー要請で削除）

#### 3.1.5 将来の見直しポイント

以下の状況になった場合、再検討する：

1. **多様なエンコーディングのサポートが必要**: ヨーロッパ言語、中国語など
2. **自動検出の精度向上が必要**: より高度な推論が必要な場合
3. **標準ライブラリに文字コード検出機能が追加**: Python標準で提供された場合

---

## 4. UseCase層の設計判断

### 4.1 MergeCsvFilesUseCaseで例外を変換する理由

**判断日**: 2025-10-19  
**関連ファイル**: `usecase/merge_csv_files.py`

#### 4.1.1 現在の実装

```python
def execute(self, input_paths: list[str | Path], output_dir: str | Path) -> MergeResult:
    try:
        # ... 処理 ...
        return MergeResult.create_success(...)
    
    except CsvFileNotFoundError as e:
        return MergeResult.create_failure(
            error_message=f"ファイルが見つかりません: {str(e)}"
        )
    
    except InvalidCsvFormatError as e:
        return MergeResult.create_failure(
            error_message=f"CSVフォーマットが不正です: {str(e)}"
        )
    
    # ... 他の例外処理 ...
    
    except Exception as e:
        return MergeResult.create_failure(
            error_message=f"予期しないエラーが発生しました: {str(e)}"
        )
```

#### 4.1.2 検討した代替案

##### 代替案: 例外をそのまま伝播

```python
def execute(self, input_paths: list[str | Path], output_dir: str | Path) -> MergeResult:
    # 例外はそのまま上位に投げる
    csv_files = [self.repository.load(path) for path in input_paths]
    merged_file = self.merger.merge(csv_files)
    output_path = self.repository.save(merged_file, output_dir)
    return MergeResult.create_success(...)
```

**却下理由**:
1. **責務の不明確化**: 呼び出し側がドメイン例外を知る必要がある
2. **依存関係の逆転違反**: Presentation層がDomain層に依存する
3. **エラーハンドリングの分散**: 各呼び出し元で重複したtry-catch

#### 4.1.3 採用した設計の理由

1. **クリーンアーキテクチャの原則**
   - UseCase層がドメイン例外を吸収
   - 上位層（Presentation層）はドメイン例外を知らなくて良い

2. **統一されたインターフェース**
   - 常に`MergeResult`を返す
   - 成功/失敗が明確

3. **エラー情報の集約**
   - 各例外を適切なメッセージに変換
   - ユーザーフレンドリーなメッセージを提供

4. **テストの容易性**
   - 例外をキャッチしない設計より、戻り値でテストする方が簡単
   - モックの設定がシンプル

#### 4.1.4 教訓

> **UseCaseは「境界」として機能する**

- **内側（Domain, Infrastructure）**: 例外を投げる
- **外側（Presentation）**: 結果オブジェクトを受け取る
- **UseCase**: 例外を結果オブジェクトに変換する

---

## 5. その他の設計判断

### 5.1 型ヒントでPython 3.13構文を採用した理由

**判断日**: 2025-10-18  
**関連ファイル**: プロジェクト全体

#### 5.1.1 現在の実装

```python
# Python 3.13+ の新しい構文
def load(self, file_path: str | Path) -> CsvFile:
    ...

def merge(self, csv_files: list[CsvFile]) -> CsvFile:
    ...
```

#### 5.1.2 検討した代替案

##### 代替案: typing モジュールを使用

```python
from typing import List, Union
from pathlib import Path

def load(self, file_path: Union[str, Path]) -> CsvFile:
    ...

def merge(self, csv_files: List[CsvFile]) -> CsvFile:
    ...
```

**却下理由**:
1. **冗長**: `Union[str, Path]` より `str | Path` が簡潔
2. **古い構文**: Python 3.10+で新構文が利用可能
3. **可読性**: より自然な記述

#### 5.1.3 採用した設計の理由

1. **シンプルさ**: より短く、読みやすい
2. **最新のベストプラクティス**: Python 3.10+の推奨構文
3. **一貫性**: プロジェクト全体で統一

#### 5.1.4 注意点

- **Python 3.9以下との互換性なし**: プロジェクトは3.13を要求
- **`.python-version`で明示**: `3.13`

---

### 5.2 CsvRepository.save()がディレクトリを受け取る理由

**判断日**: 2025-10-19  
**関連ファイル**: `infra/repositories/csv_repository.py`

#### 5.2.1 現在の実装

```python
def save(self, csv_file: CsvFile, output_dir: str | Path) -> Path:
    """CsvFileを指定ディレクトリに保存
    
    タイムスタンプ付きのファイル名を自動生成
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_name = f"merged_{timestamp}.csv"
    output_path = output_dir_path / output_file_name
    
    csv_file.data.to_csv(output_path, index=False, encoding="utf-8")
    return output_path
```

#### 5.2.2 以前の実装（変更前）

```python
def save(self, csv_file: CsvFile, output_path: str | Path) -> None:
    """CsvFileを指定パスに保存"""
    path = Path(output_path)
    csv_file.data.to_csv(path, index=False, encoding="utf-8")
```

#### 5.2.3 変更した理由

1. **ファイル名の衝突回避**
   - タイムスタンプ付きで一意のファイル名を生成
   - 複数回実行しても上書きされない

2. **テストの容易性**
   - 一時ディレクトリを指定するだけで良い
   - ファイル名を気にしなくて良い

3. **実用性**
   - 実行ごとに異なるファイルが作成される
   - 実行履歴を保持できる

4. **戻り値の追加**
   - 作成されたファイルのパスを返す
   - 呼び出し側が結果を確認できる

#### 5.2.4 トレードオフ

**メリット**:
- ✅ ファイル名衝突の回避
- ✅ 実行履歴の保持
- ✅ テストの簡素化

**デメリット**:
- ❌ ファイル名を指定できない（カスタマイズ性の低下）
- ❌ 固定のファイル名形式（`merged_YYYYMMDD_HHMMSS.csv`）

**判断**: メリットがデメリットを上回ると判断

---

### 5.3 日時フォーマットを固定せずpandas認識可能形式とした理由

**判断日**: 2025-10-19  
**関連ファイル**: `domain/models/csv_schema.py`, `tests/unit/domain/models/test_csv_schema.py`

#### 5.3.1 以前の実装（変更前）

```python
class CsvSchema:
    # 日時フォーマットの正規表現パターン
    # YYYY/MM/DD HH:00:00 形式、HHは00〜23
    _DATETIME_PATTERN = re.compile(
        r"^\d{4}/\d{2}/\d{2} ([01]\d|2[0-3]):00:00$"
    )
    
    @classmethod
    def validate_datetime_format(cls, datetime_str: str) -> bool:
        """日時フォーマットを検証（固定フォーマット）"""
        if not isinstance(datetime_str, str):
            return False
        return cls._DATETIME_PATTERN.match(datetime_str) is not None
```

**問題点**:
- 固定フォーマット `YYYY/MM/DD HH:00:00` のみ受け入れる
- `datetime.strptime()` で固定フォーマットを想定
- 文字列分割で日付・時刻を抽出

#### 5.3.2 現在の実装（変更後）

```python
class CsvSchema:
    # 日時フォーマットの正規表現は削除
    
    @classmethod
    def validate_datetime_format(cls, datetime_str: str) -> bool:
        """日時フォーマットを検証
        
        pandasが認識可能な日時文字列かを確認します。
        フォーマットは固定されておらず、pandasが解釈できれば有効とみなします。
        """
        if not isinstance(datetime_str, str):
            return False
        
        # 空文字列は無効
        if not datetime_str.strip():
            return False
        
        try:
            # pandasでパースできるか試す
            pd.to_datetime(datetime_str)
            return True
        except (ValueError, pd.errors.ParserError, Exception):
            return False
```

#### 5.3.3 変更した理由

**ユーザーからのフィードバック**:
> "日時の文字列のフォーマットはpandasにて日時として認識可能な何でも変更になる可能性がある。日時の文字列のフォーマットが固定である事を前提とした処理は修正する必要があります。"

**採用した設計の理由**:

1. **将来の変更に対応**
   - フォーマットが変更されても、コードの修正が不要
   - pandasが認識できる様々な形式に対応

2. **柔軟性の向上**
   - ISO 8601形式（`2025-10-01 10:00:00`）
   - ハイフン区切り（`2025-10-01T10:00:00`）
   - スラッシュ区切り（`2025/10/01 10:00:00`）
   - 日付のみ（`2025/10/01`）
   - 時刻のみ（`10:00:00`）
   - 分・秒の多様性（`10:30:45`も可）

3. **実装の簡素化**
   - 正規表現パターンが不要
   - `re`モジュールのインポートが不要
   - `datetime.strptime()`の固定フォーマットが不要

4. **一貫性**
   - 検証と処理（ソート）で同じpandas機能を使用
   - 検証で通ったフォーマットは必ず処理でも成功

#### 5.3.4 影響を受けた処理

**変更した処理**:

1. **`validate_datetime_format()`**
   - 正規表現 → `pd.to_datetime()` での検証

2. **`validate_datetime_value()`**
   - `datetime.strptime(固定フォーマット)` → `pd.to_datetime()` での検証

3. **`validate_daily_time_range()`**
   - 文字列分割 → `pd.to_datetime()` でパース後、datetimeオブジェクトで検証

4. **テストケース**
   - 新しいテスト `test_validate_datetime_format_flexible()` を追加
   - 様々なフォーマットが受け入れられることを確認

#### 5.3.5 受け入れる日時フォーマット例

| フォーマット | 例 | 説明 |
|------------|---|------|
| スラッシュ区切り | `2025/10/01 10:00:00` | 従来の形式（後方互換性） |
| ハイフン区切り | `2025-10-01 10:00:00` | ISO 8601形式 |
| T区切り | `2025-10-01T10:00:00` | ISO 8601形式（厳密） |
| 日付のみ | `2025/10/01` | 時刻は00:00:00と解釈 |
| 時刻のみ | `10:00:00` | 今日の日付が補完される |
| 分・秒あり | `2025/10/01 10:30:45` | 毎正時でなくても可 |

#### 5.3.6 制約事項

以下の制約は維持されます：

1. **1日分のデータ制約**:
   - 24レコード（00時〜23時）
   - すべて同じ日付
   - 時刻が00時から23時まで揃っている

2. **年の範囲**:
   - 1900年〜2100年

#### 5.3.7 教訓

> **「フォーマットを固定しない」という選択**

- **データ検証**: フォーマットではなく、処理可能性で検証
- **将来の柔軟性**: 実装の変更なしに新しいフォーマットに対応
- **一貫性**: 検証と処理で同じライブラリ（pandas）を使用

**トレードオフ**:
- ✅ 柔軟性: 様々なフォーマットに対応
- ✅ 保守性: フォーマット変更時の修正不要
- ❌ 制約の緩和: 毎正時（HH:00:00）でなくても受け入れる
  - ただし、1日24レコードの制約は維持されるため、実用上問題なし

---

## 変更履歴

| 日付 | バージョン | 変更内容 | 著者 |
|------|-----------|---------|------|
| 2025-10-19 | 1.1.0 | 日時フォーマットの柔軟化 - 固定フォーマットからpandas認識可能形式へ変更 | - |
| 2025-10-19 | 1.0.0 | 初版作成 - @dataclass不採用の理由など5つの設計判断を記録 | - |

---

**関連ドキュメント**:
- [01_plan.md](./01_plan.md) - プロジェクトプラン
- [03_specification.md](./03_specification.md) - 全体仕様
- [04_domain_specification.md](./04_domain_specification.md) - Domain層詳細仕様

