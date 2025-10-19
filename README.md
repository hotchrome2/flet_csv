# flet_csv

複数の時系列CSVファイルを1つに結合するWebアプリケーション

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-96%20passed-success.svg)](./tests)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📋 概要

このアプリケーションは、複数の時系列CSVファイルを読み込み、日時順に結合して1つのCSVファイルとして出力します。
多様なCSVフォーマットに対応し、文字コードの自動判定や詳細なエラーメッセージなど、実用的な機能を備えています。

### 主な特徴

- ✅ **クリーンアーキテクチャ**: 保守性・拡張性の高い設計
- ✅ **TDD（テスト駆動開発）**: 96個のテストで品質保証
- ✅ **多様なCSVフォーマット対応**: ヘッダー有無、列の欠損など
- ✅ **文字コード自動判定**: UTF-8, CP932, Shift-JISに対応
- ✅ **詳細なエラーメッセージ**: 不正な行番号を範囲形式で表示
- ✅ **CLIインターフェース**: コマンドラインから簡単に実行可能
- ✅ **Python 3.13**: 最新の型ヒント構文を使用

---

## 🏗️ アーキテクチャ

クリーンアーキテクチャに基づいた4層構造：

```
┌─────────────────────────────────────────┐
│     Presentation Layer (UI)             │  ⏳ 未実装
│           (Flet)                        │
├─────────────────────────────────────────┤
│     CLI Entrypoint                      │  ✅ 完成
│         (main.py)                       │
├─────────────────────────────────────────┤
│     UseCase Layer                       │  ✅ 完成
│   (merge_csv_files.py)                  │
├─────────────────────────────────────────┤
│     Domain Layer                        │  ✅ 完成
│  (models, services, exceptions)         │
├─────────────────────────────────────────┤
│     Infrastructure Layer                │  ✅ 完成
│   (repositories)                        │
└─────────────────────────────────────────┘
```

### 開発状況

| 層 | 状態 | 説明 |
|---|-----|------|
| **Domain層** | ✅ 完成 | CsvFile, MergeResult, CsvMerger, 例外クラス |
| **Infrastructure層** | ✅ 完成 | CsvRepository（多様なCSV対応、文字コード自動判定） |
| **UseCase層** | ✅ 完成 | MergeCsvFilesUseCase（CSV結合ロジック） |
| **CLI Entrypoint** | ✅ 完成 | main.py（コマンドライン実行、ログ出力） |
| **Presentation層** | ⏳ 未着手 | Flet UIコンポーネント |

---

## 🚀 セットアップ

### 必要な環境

- Python 3.13+
- uv（パッケージマネージャー）

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/hotchrome2/flet_csv.git
cd flet_csv

# 依存関係のインストール（uvを使用）
uv sync
```

---

## 🧪 テスト実行

```bash
# すべてのテストを実行
uv run pytest

# カバレッジ付きで実行
uv run pytest --cov=domain --cov=infra --cov=usecase

# 特定の層のみテスト
uv run pytest tests/unit/domain/     # Domain層
uv run pytest tests/unit/infra/      # Infrastructure層
uv run pytest tests/unit/usecase/    # UseCase層
uv run pytest tests/e2e/             # エンドツーエンドテスト
```

### テスト結果

```
96 passed in 7.54s ✅
```

### テスト構成

| テストタイプ | テスト数 | 内容 |
|------------|---------|------|
| Domain層 | 58テスト | モデル、サービス、例外のロジック |
| Infrastructure層 | 21テスト | CSV読み書き、正規化、エンコーディング |
| UseCase層 | 10テスト | 結合ユースケースのロジック |
| エンドツーエンド | 7テスト | CLIからの完全な実行フロー |

---

## 🚀 使用方法

### CLIから実行

```bash
# デフォルトディレクトリで実行（time_case/ → static/downloads/）
python main.py

# カスタムディレクトリで実行
python main.py --input my_data --output results

# ヘルプを表示
python main.py --help
```

### 実行例

```bash
$ python main.py
2025-10-19 16:00:00 - __main__ - INFO - ============================================================
2025-10-19 16:00:00 - __main__ - INFO - CSVファイル結合処理を開始します
2025-10-19 16:00:00 - __main__ - INFO - ============================================================
2025-10-19 16:00:00 - __main__ - INFO - 入力ディレクトリ: time_case
2025-10-19 16:00:00 - __main__ - INFO - 出力ディレクトリ: static/downloads
2025-10-19 16:00:00 - __main__ - INFO - 入力CSVファイル数: 3
2025-10-19 16:00:00 - __main__ - INFO -   1. file1.csv
2025-10-19 16:00:00 - __main__ - INFO -   2. file2.csv
2025-10-19 16:00:00 - __main__ - INFO -   3. file3.csv
2025-10-19 16:00:00 - __main__ - INFO - ------------------------------------------------------------
2025-10-19 16:00:00 - __main__ - INFO - 結合処理を実行中...
2025-10-19 16:00:00 - __main__ - INFO - ------------------------------------------------------------
2025-10-19 16:00:00 - __main__ - INFO - [成功] 結合処理が成功しました！
2025-10-19 16:00:00 - __main__ - INFO -    出力ファイル: static/downloads/merged_20251019_160000.csv
2025-10-19 16:00:00 - __main__ - INFO -    結合ファイル数: 3
2025-10-19 16:00:00 - __main__ - INFO -    総行数: 72
2025-10-19 16:00:00 - __main__ - INFO - ============================================================
成功: 3ファイルを結合しました（72行）
出力: static/downloads/merged_20251019_160000.csv
```

---

## 📚 ドキュメント

詳細な仕様は `doc/` ディレクトリを参照してください：

| ドキュメント | 内容 | 状態 |
|------------|------|------|
| [01_plan.md](./doc/01_plan.md) | プロジェクトプラン | ✅ |
| [01_1_design_decisions.md](./doc/01_1_design_decisions.md) | 重要な設計判断とその理由 | ✅ |
| [02_history_summary.md](./doc/02_history_summary.md) | 開発履歴サマリー | ✅ |
| [03_specification.md](./doc/03_specification.md) | 全体仕様（アーキテクチャ、共通ルール） | ✅ |
| [04_domain_specification.md](./doc/04_domain_specification.md) | Domain層の詳細仕様 | ✅ |
| [05_infrastructure_specification.md](./doc/05_infrastructure_specification.md) | Infrastructure層の詳細仕様 | ✅ |
| [06_github_setup.md](./doc/06_github_setup.md) | GitHubリポジトリ登録手順 | ✅ |
| [07_git_workflow.md](./doc/07_git_workflow.md) | Git開発ワークフロー | ✅ |
| [08_usecase_specification.md](./doc/08_usecase_specification.md) | UseCase層の詳細仕様 | ✅ |
| [09_cli_specification.md](./doc/09_cli_specification.md) | CLIエントリーポイントの詳細仕様 | ✅ |

---

## 🔧 使用技術

### フレームワーク・ライブラリ

- **Flet**: Webアプリケーションフレームワーク
- **pandas**: データ処理
- **pytest**: テストフレームワーク

### 開発ツール

- **uv**: パッケージマネージャー
- **black**: コードフォーマッター
- **isort**: import順序整理
- **mypy**: 型チェック

---

## 📖 主要機能

### 1. 多様なCSVフォーマット対応

以下のすべてのパターンを自動的に正規化します：

- ✅ ヘッダーあり/なし
- ✅ No列あり/なし
- ✅ 参照列あり/なし
- ✅ クォート付き/なし
- ✅ カラム順序の違い

### 2. 文字コード自動判定

Windows日本語環境で使われる典型的なエンコーディングを順番に試行：

1. UTF-8 BOM付き
2. UTF-8
3. CP932
4. Shift-JIS

### 3. 詳細なエラーメッセージ

不正な日時が検出された場合、ファイル名と行番号を詳細に表示：

```
invalid_dates.csv: 不正な日時が検出されました（3行目、5行目から6行目、8行目）
```

連続する行番号は範囲形式でまとめて表示します。

---

## 🎯 今後の開発予定

### ✅ 完了（v0.4.0）

- [x] Domain層の実装
- [x] Infrastructure層の実装
- [x] UseCase層の実装
- [x] CLIエントリーポイントの実装
- [x] エンドツーエンドテストの追加
- [x] ドキュメント整備

### 中期（v0.5.0）

- [ ] Flet UIの実装
- [ ] プログレスバー表示
- [ ] ファイル選択ダイアログ
- [ ] エラーダイアログ

### 長期（v1.0.0）

- [ ] プレビュー機能
- [ ] 設定保存機能
- [ ] 実行履歴管理
- [ ] Webサーバーとしてデプロイ

---

## 🤝 コントリビューション

このプロジェクトは現在開発中です。
バグ報告や機能提案は、GitHubのIssuesでお願いします。

### 開発フロー

1. `develop`ブランチから`feature/*`ブランチを作成
2. TDDでテストを書いてから実装
3. すべてのテストが通ることを確認
4. Pull Requestを作成
5. レビュー後、`develop`にマージ

---

## 📄 ライセンス

このプロジェクトは開発中のため、ライセンスは未定です。

---

## 📧 連絡先

- GitHub: [@hotchrome2](https://github.com/hotchrome2)
- Website: https://www.additengineer.info

---

**Last Updated**: 2025-10-19 (v0.4.0)

