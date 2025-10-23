# プロジェクトプラン

## 1. プロジェクト概要

### 1.1 プロジェクト名
**flet-csv** - 時系列CSVデータ結合アプリケーション

### 1.2 目的
複数の時系列CSVファイルを結合し、1つのCSVファイルとして出力するWebアプリケーションの開発

### 1.3 主要機能
- `time_case/` ディレクトリ内の複数CSVファイルの読み込み
- 時系列データとしての結合処理
- 結合済みCSVファイルの `static/downloads/` への保存

### 1.4 ユーザー層
- 社内の他部署メンバー
- ローカル環境での実行を想定

### 1.5 技術スタック
| カテゴリ | 技術 | バージョン |
|---------|------|-----------|
| 言語 | Python | 3.13+ |
| UIフレームワーク | Flet | 0.28.3 |
| データ処理 | pandas | 2.3.3 |
| 数値計算 | numpy | 2.3.4 |
| テスト | pytest | 8.4.2 |
| コード整形 | black, isort | latest |
| 型チェック | mypy | 1.18.2 |
| パッケージ管理 | uv | latest |

---

## 2. クリーンアーキテクチャ設計

### 2.1 レイヤー構成

本プロジェクトはクリーンアーキテクチャの原則に従い、依存関係を内側（ドメイン層）に向けます。

```
┌─────────────────────────────────────────┐
│        Presentation Layer (UI)          │  ← 将来UIチームが実装
│              (Flet)                     │
├─────────────────────────────────────────┤
│        UseCase Layer                    │  ← アプリケーションロジック
│    (merge_csv_files.py など)           │
├─────────────────────────────────────────┤
│        Domain Layer                     │  ← ビジネスロジック
│    (models, services, exceptions)       │
├─────────────────────────────────────────┤
│        Infrastructure Layer             │  ← 外部依存
│    (repositories, file_handler)         │
└─────────────────────────────────────────┘
```

### 2.2 ディレクトリ構造

```
flet_csv/
├── domain/                    # ドメイン層
│   ├── __init__.py
│   ├── models/                # エンティティ・値オブジェクト
│   │   ├── __init__.py
│   │   ├── csv_file.py        # CSVファイルのドメインモデル
│   │   ├── csv_schema.py      # CSVスキーマ定義（カラム・型）
│   │   └── merge_result.py    # 結合結果のモデル
│   ├── services/              # ドメインサービス
│   │   ├── __init__.py
│   │   └── csv_merger.py      # CSV結合のコアロジック
│   └── exceptions.py          # ドメイン固有の例外定義
│
├── usecase/                   # ユースケース層
│   ├── __init__.py
│   └── merge_csv_files.py     # CSV結合ユースケース
│
├── infra/                     # インフラ層
│   ├── __init__.py
│   └── repositories/
│       ├── __init__.py
│       └── csv_repository.py  # CSV読み書き（pandas利用）
│
├── static/
│   └── downloads/             # 出力先ディレクトリ
│
├── time_case/                 # 入力CSVファイル配置ディレクトリ
│
├── tests/                     # テストコード
│   ├── unit/                  # 単体テスト
│   ├── integration/           # 統合テスト
│   └── fixtures/              # テスト用データ
│
├── doc/                       # ドキュメント
│   ├── 01_plan.md            # プロジェクトプラン
│   ├── 02_history_summary.md # 開発履歴サマリー
│   ├── 03_specification.md   # 全体仕様（アーキテクチャ、共通ルール）
│   ├── 04_domain_specification.md     # Domain層詳細仕様
│   ├── 05_infrastructure_specification.md  # Infrastructure層詳細仕様
│   ├── 06_github_setup.md    # GitHubリポジトリ登録手順
│   ├── 07_git_workflow.md    # Git開発ワークフロー（feature→develop→main）
│   ├── 08_usecase_specification.md    # UseCase層詳細仕様
│   └── 09_cli_specification.md        # CLIエントリーポイント詳細仕様
│
├── scripts/                   # ユーティリティスクリプト
│
├── main.py                    # エントリーポイント
├── pyproject.toml             # プロジェクト設定
├── uv.lock                    # 依存関係ロック
└── README.md                  # プロジェクトREADME
```

### 2.3 各層の責務

#### Domain Layer（ドメイン層）
**責務**: ビジネスロジックの中核を定義  
**依存**: なし（他の層に依存しない）

- **models/csv_file.py**
  - CSVファイルの概念をモデル化
  - ファイルパス、データフレーム、メタデータを保持
  - スキーマバリデーション
  
- **models/csv_schema.py**
  - CSVファイルのスキーマ定義（ドメイン知識）
  - 必須カラム: 「日時」「No」「電圧」「周波数」「パワー」「工事フラグ」「参照」
  - データ型定義: 整数、pandasが認識可能な日時文字列
  - バリデーションルール: カラムの存在チェック、型チェック
  
- **models/merge_result.py**
  - 結合処理の結果を表現
  - 成功/失敗、結合行数、エラー情報など
  - ファクトリメソッド: create_success, create_failure
  
- **services/csv_merger.py**
  - CSV結合の核となるビジネスロジック
  - 時系列ソート、重複排除、データ整合性チェック
  - 連続日検証（最小日〜最大日が欠損なく連続していること）
  
- **exceptions.py**
  - ドメイン固有の例外クラス定義
  - `CsvMergerError`（基底）, `InvalidCsvFormatError`, `CsvFileNotFoundError`, `MergeError`, `EmptyDataError`

#### UseCase Layer（ユースケース層）
**責務**: アプリケーション固有の処理フローを定義  
**依存**: Domain Layer

- **merge_csv_files.py**
  - CSV結合の一連の処理を統括
  - 入力: ファイルパスのリスト、出力先パス
  - 処理: ファイル読込 → 検証 → 結合 → 保存
  - 出力: 結合結果（成功/失敗、メッセージ）

#### Infrastructure Layer（インフラ層）
**責務**: 外部システム（ファイルシステム、ライブラリ）との接続  
**依存**: Domain Layer

- **repositories/csv_repository.py**
  - CSVファイルの読み書きを抽象化
  - pandas の利用をこの層に限定
  - インターフェース定義により、テスト時にモック化可能

#### Presentation Layer（プレゼンテーション層）
**責務**: ユーザーインターフェース  
**依存**: UseCase Layer  
**状態**: 将来UIチームが実装予定

- 現段階では `main.py` でCLI実行のみ実装
- Flet UIは後フェーズで開発

### 2.4 データフロー

```
[ユーザー/CLI]
    ↓
[main.py] ← エントリーポイント
    ↓
[MergeCsvFilesUseCase] ← ユースケース実行
    ↓
[CsvRepository] → ファイル読み込み (pandas)
    ↓
[CsvFile Models] ← ドメインモデルに変換
    ↓
[CsvMergerService] ← ビジネスロジック実行
    ↓ (結合処理)
[MergeResult] ← 結果モデル
    ↓
[CsvRepository] → ファイル書き込み (pandas)
    ↓
[static/downloads/merged_xxx.csv] ← 出力
```

---

## 3. 開発タスク・進行フロー

### 3.1 フェーズ1: コアロジック開発（現フェーズ）

#### タスク1: プロジェクト構造のセットアップ
- [x] `.gitignore` の整備
- [x] プロジェクトプランドキュメントの作成
- [x] ディレクトリ構造の作成
- [x] `__init__.py` ファイルの配置

#### タスク2: Domain層の実装（TDDサイクル）✅ **完了**
- [x] **Red**: `domain/exceptions.py` のテスト作成
- [x] **Green**: `domain/exceptions.py` の実装
- [x] **Red**: `domain/models/csv_file.py` のテスト作成
- [x] **Green**: `domain/models/csv_file.py` の実装
- [x] **Red**: `domain/models/csv_schema.py` のテスト作成
- [x] **Green**: `domain/models/csv_schema.py` の実装
- [x] **Red**: `domain/models/merge_result.py` のテスト作成
- [x] **Green**: `domain/models/merge_result.py` の実装
- [x] **Refactor**: Domain層モデルのリファクタリング（Python 3.13型ヒント、スキーマ統合）
- [x] **Red**: `domain/services/csv_merger.py` のテスト作成
- [x] **Green**: `domain/services/csv_merger.py` の実装
- [x] **Refactor**: Domain層サービスのリファクタリング
- [x] **改善** (2025-10-19): datetime型ソートへの変更（将来のフォーマット変更に対応）

**完成状況**: 5モジュール、66テスト、100%成功 🎉

#### タスク3: Infrastructure層の実装（TDDサイクル）✅ **完了**
- [x] **Red**: `infra/repositories/csv_repository.py` のテスト作成
- [x] **Green**: `infra/repositories/csv_repository.py` の実装
  - 多様なCSVフォーマット対応（ヘッダーあり/なし、No列あり/なし、クォート付き）
  - 文字コード自動判定（UTF-8、UTF-8 BOM、Shift-JIS、CP932）※標準ライブラリのみ使用
  - 正規化処理（7列統一、No列・参照列補完、カラム順序統一）
- [x] **Refactor**: テストフィクスチャ化によるコード簡潔化（311行 → 155行、50%削減）

**完成状況**: 1モジュール、9テスト、100%成功 + 全体80テスト成功 🎉

**追加機能** (2025-10-19):
- [x] データ検証機能強化
  - 不正な日時の詳細エラー表示（ファイル名・行番号・範囲圧縮）
  - 日付妥当性検証（年の範囲、存在しない日付の検出）
  - CsvRepositoryでの自動検証
  - pd.to_datetime()での変換可能性チェック（検証と結合の一貫性確保）
  
**改善** (2025-10-23):
- ヘッダーなしCSV読み込み時、末尾が「全行NaN」の最終列を自動削除
- ヘッダーなし期待列数をスキーマから動的算出（マジックナンバー排除）

#### タスク4: UseCase層の実装（TDDサイクル）✅ **完了**
- [x] **Red**: `usecase/merge_csv_files.py` の統合テスト作成
- [x] **Green**: `usecase/merge_csv_files.py` の実装
- [x] **Refactor**: UseCase層のリファクタリング

**完成状況**: 1モジュール、9テスト、100%成功 + 全体89テスト成功 🎉

#### タスク5: エントリーポイントの実装 ✅ **完了**
- [x] `main.py` の実装（CLI版）
- [x] ログ出力の実装
- [x] エンドツーエンドテスト

**完成状況**: CLI実装、7エンドツーエンドテスト、全96テスト成功 🎉

#### タスク6: ドキュメント整備 ✅ **完了**
- [x] 仕様書の作成（03_specification.md）
- [x] 各層の詳細仕様書（04, 05, 08, 09）
- [x] GitHubセットアップガイド（06_github_setup.md）
- [x] Git開発ワークフロー（07_git_workflow.md）
- [x] CLIエントリーポイント仕様（09_cli_specification.md）
- [x] README.md の充実化
- [ ] UIチーム向けインテグレーションガイド作成（将来）

**完成状況**: 9つのドキュメント完成、テスト仕様書を含む包括的なドキュメント体系の構築 🎉

### 3.2 フェーズ2: UI開発（UIチーム担当）

#### タスク1: Flet UI設計
- [ ] UIモックアップ作成
- [ ] コンポーネント設計

#### タスク2: Presentation層の実装
- [ ] ファイル一覧表示画面
- [ ] 結合操作パネル
- [ ] 進捗表示・結果通知

#### タスク3: UI統合テスト
- [ ] UIテストの作成
- [ ] エンドユーザー向けテスト

### 3.3 フェーズ3: デプロイメント準備（将来）

- [ ] デプロイ方法の確定
- [ ] 環境構築手順書の作成
- [ ] 運用マニュアルの作成

### 3.4 開発フロー（TDD）

本プロジェクトは **TDD（Test-Driven Development）** で開発を進めます。

#### TDDサイクル（Red-Green-Refactor）

```
[要件確認] → [設計]
                ↓
         ┌─────────────┐
         │  Red Phase  │ ← テストを先に書く（失敗する）
         └─────┬───────┘
               ↓
         ┌─────────────┐
         │ Green Phase │ ← 最小限の実装でテストを通す
         └─────┬───────┘
               ↓
         ┌─────────────┐
         │   Refactor  │ ← コードをリファクタリング
         └─────┬───────┘
               ↓
         [レビュー] → [マージ]
               ↓
         [ドキュメント更新]
```

#### TDD開発手順

0. **仕様確認**: 機能仕様書を参照
   - `doc/03_specification.md` で実装する機能の仕様を確認
   - 期待される動作、制約、エッジケースを理解
   - テストケースの設計に活用

1. **Red Phase（赤）**: テストを書く
   - 仕様書に基づいてテストを先に作成
   - テストは失敗する（実装がないため）
   - テストケースで仕様を検証可能な形に

2. **Green Phase（緑）**: 最小限の実装
   - テストが通る最小限のコードを書く
   - 完璧である必要はない
   - とにかくテストを通すことが目標

3. **Refactor Phase（リファクタリング）**: 改善
   - コードの重複を排除
   - 可読性を向上
   - 設計原則に従った構造に改善
   - テストは引き続き成功することを確認

4. **仕様書更新**: 実装後に仕様書を更新（必要に応じて）
   - 実装中に発見した新しい制約や考慮事項を追記
   - 将来のメンバーのための知見を文書化

#### コーディング規約
- PEP 8 準拠（black で自動整形）
- 型ヒント必須（mypy でチェック）
- import 順序は isort で統一
- docstring は Google Style
- **テストファースト**: 実装前に必ずテストを書く

#### テスト方針
- **テスト駆動**: テストを先に書き、実装はテストに従う
- **単体テスト**: 各層ごとに実装（pytest）
- **カバレッジ目標**: 90%以上（TDDにより自然と高カバレッジに）
- **テストの独立性**: 各テストは独立して実行可能
- **モック活用**: pytest-mock で外部依存を分離
- **Given-When-Then**: テストはAAA（Arrange-Act-Assert）パターンで記述

#### Git運用
- main ブランチ: 安定版
- feature/xxx: 機能開発ブランチ
- コミットメッセージ: Conventional Commits 形式

---

## 4. 補足・方針

### 4.1 開発方針

#### TDD（Test-Driven Development）
本プロジェクトは **テスト駆動開発** を採用します。

**TDDの利点:**
- ✅ **設計の明確化**: テストを書く過程で仕様が明確になる
- ✅ **品質向上**: バグの早期発見、高いテストカバレッジ
- ✅ **リファクタリング容易性**: テストがあるため安心して改善できる
- ✅ **ドキュメント効果**: テストコードが使用例・仕様書として機能
- ✅ **回帰テスト**: 既存機能の破壊を即座に検出

**TDDの原則:**
1. 実装コードを書く前に、必ずテストを書く
2. 失敗するテストを書いてから実装を始める（Red）
3. テストを通す最小限のコードを書く（Green）
4. テストが通ったらリファクタリングする（Refactor）
5. 1つの機能につき、小さいサイクルを繰り返す

#### 段階的開発
- **Phase 1（現在）**: コアロジックに集中
  - UIは後回し、ロジックの品質を優先
  - TDDでテストと実装を同時進行
  - main.py でCLI実行により動作確認
  
- **Phase 2（将来）**: UIチームによるFlet UI開発
  - コアロジックは変更せず、UI層のみ実装
  - UseCase層のインターフェースを経由して統合
  - UIもTDDで開発（必要に応じて）

#### 疎結合設計
- 各層の依存関係を明確化
- インターフェース（抽象クラス）を活用
- UIチームがコアロジックに影響を与えずに開発可能
- TDDによりモック化・テスト容易性が向上

### 4.2 スコープ外の機能

以下の機能は現時点では実装しない（将来検討可能）：

- ❌ メモリ不足時の分割処理（巨大データを扱わない前提）
- ❌ プレビュー機能
- ❌ 実行履歴の保存
- ❌ 設定の保存・復元
- ❌ Excel等のCSV以外のフォーマット対応
- ❌ データクレンジング・変換機能
- ❌ ユーザー認証・権限管理

### 4.3 技術的な決定事項

#### CSVデータ仕様
- **必須カラム（7列）**:
  - 日時: YYYY/MM/DD HH:00:00 形式（HHは00〜23の毎正時）
  - No: 整数
  - 電圧: 整数
  - 周波数: 整数
  - パワー: 整数
  - 工事フラグ: 整数（0 または 1）
  - 参照: 整数（0 または 1）

- **時系列カラム**: 「日時」（結合時のソート基準）
- **スキーマバリデーション**: domain/models/csv_schema.pyで定義

#### Python 3.13 型ヒント
- 組み込み型を使用: `list[str]`, `dict[str, int]`
- Union型演算子: `str | Path | None`
- typing モジュールからのインポート最小化
- 型チェック: mypy で実施

#### pandas の利用
- CSV読み書きには pandas を使用
- Infrastructure層に閉じ込め、Domain層には pandas の型を持ち込まない
- データフレームをドメインモデルに変換して使用

#### エラーハンドリング
- ドメイン固有の例外を定義（CsvMergerError 階層）
- UseCase層でキャッチし、適切なメッセージを返す
- 開発者向けログは標準出力・標準エラー出力

#### ファイル命名規則
- 出力ファイル名: `merged_YYYYMMDD_HHMMSS.csv`
- タイムスタンプで一意性を保証

### 4.4 UIチームへの引き継ぎポイント

#### インターフェース
- `usecase/merge_csv_files.py` の `MergeCsvFilesUseCase` クラスを呼び出す
- 入力: ファイルパスのリスト
- 出力: `MergeResult` オブジェクト（成功/失敗、メッセージ、出力パス）

#### Flet統合時の注意点
- UseCase実行は非同期処理推奨（UIブロック防止）
- 進捗通知が必要な場合はコールバック機構を追加
- エラーメッセージは `MergeResult` から取得

#### ドキュメント
- 詳細なAPI仕様書を別途作成予定
- サンプルコードを提供予定

### 4.5 品質保証

#### コードレビュー
- Pull Request ベースで開発
- 最低1名のレビュー必須

#### 自動チェック
- GitHub Actions等でCI/CD構築検討
- テスト、Linter、型チェックを自動実行

#### テストデータ
- `tests/fixtures/` にサンプルCSVを配置
- 正常系・異常系のテストケースを網羅

---

## 変更履歴

| 日付 | バージョン | 変更内容 | 著者 |
|------|-----------|---------|------|
| 2025-10-18 | 1.3.0 | Domain層完成（全66テスト成功）、Infrastructure層タスク詳細化 | - |
| 2025-10-18 | 1.2.0 | CSVスキーマ定義追加、Python 3.13型ヒント採用、タスク進捗更新 | - |
| 2025-10-18 | 1.1.0 | TDD（Test-Driven Development）方針を追加 | - |
| 2025-10-18 | 1.0.0 | 初版作成 | - |


