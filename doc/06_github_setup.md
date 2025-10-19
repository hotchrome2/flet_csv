# GitHubリポジトリ登録手順

このドキュメントは、ローカルのGitリポジトリをGitHubに登録する手順をまとめたものです。

**実施日**: 2025-10-19  
**対象リポジトリ**: https://github.com/hotchrome2/flet_csv

---

## 目次

1. [前提条件](#1-前提条件)
2. [GitHubでのリポジトリ作成](#2-githubでのリポジトリ作成)
3. [ローカルブランチの準備](#3-ローカルブランチの準備)
4. [リモートリポジトリの登録](#4-リモートリポジトリの登録)
5. [ブランチのプッシュ](#5-ブランチのプッシュ)
6. [README.mdの充実化](#6-readmemdの充実化)
7. [GitHub推奨設定](#7-github推奨設定)
8. [日常的な運用](#8-日常的な運用)

---

## 1. 前提条件

### 必要なもの

- ✅ GitHubアカウント
- ✅ ローカルにGitリポジトリが存在
- ✅ コミットが1つ以上存在
- ✅ Git認証情報の設定（HTTPSまたはSSH）

### ローカルの状態確認

```bash
# 現在のブランチとコミットを確認
git status
git log --oneline

# リモートリポジトリの確認（初回は何も表示されない）
git remote -v
```

---

## 2. GitHubでのリポジトリ作成

### 2.1 ブラウザでの作成手順

1. **GitHubにアクセス**
   - https://github.com にログイン

2. **新しいリポジトリを作成**
   - 右上の「+」→「New repository」をクリック

3. **リポジトリ情報を入力**
   - **Repository name**: `flet_csv`
   - **Description**: `複数の時系列CSVファイルを結合するWebアプリケーション`
   - **Visibility**: Public または Private
   - **Initialize this repository with**: すべてチェックを外す（重要！）
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   - 「Create repository」をクリック

### 2.2 なぜ初期化しないのか？

既存のローカルリポジトリをプッシュする場合、GitHubでの初期化は不要です。

**理由**:
- ローカルに既にコミット履歴がある
- GitHubで初期化すると、リモートとローカルの履歴が異なる
- マージの複雑さを避けるため

### 2.3 リポジトリURL

作成後、以下のようなURLが表示されます：

```
https://github.com/hotchrome2/flet_csv.git
```

このURLを次のステップで使用します。

---

## 3. ローカルブランチの準備

### 3.1 現在のブランチ確認

```bash
git branch -v
```

**実行例の出力**:
```
* develop 68b8e72 feat: Domain層とInfrastructure層の実装完了
```

### 3.2 開発ブランチの作成（未作成の場合）

```bash
# developブランチを作成して切り替え
git checkout -b develop
```

### 3.3 ブランチ戦略

このプロジェクトでは、以下のブランチ戦略を採用：

```
main (本番・安定版)
  └── develop (開発ブランチ)
       └── feature/* (機能ブランチ)
```

**各ブランチの役割**:
- `main`: 本番環境にデプロイ可能な安定版
- `develop`: 開発版（次のリリース候補）
- `feature/*`: 新機能開発用（developから分岐）

---

## 4. リモートリポジトリの登録

### 4.1 リモートを追加

```bash
git remote add origin https://github.com/hotchrome2/flet_csv.git
```

**コマンドの意味**:
- `git remote add`: リモートリポジトリを追加
- `origin`: リモートの名前（慣例的に`origin`を使用）
- `https://...`: GitHubリポジトリのURL

### 4.2 登録の確認

```bash
git remote -v
```

**期待される出力**:
```
origin	https://github.com/hotchrome2/flet_csv.git (fetch)
origin	https://github.com/hotchrome2/flet_csv.git (push)
```

### 4.3 SSH使用時

HTTPSではなくSSHを使用する場合：

```bash
git remote add origin git@github.com:hotchrome2/flet_csv.git
```

**メリット**:
- パスワード入力不要
- より安全
- トークンの有効期限を気にしなくて良い

---

## 5. ブランチのプッシュ

### 5.1 developブランチをプッシュ

```bash
# developブランチをプッシュ（上流ブランチとして設定）
git push -u origin develop
```

**コマンドの意味**:
- `git push`: リモートにプッシュ
- `-u`: 上流ブランチとして設定（以降は`git push`だけでOK）
- `origin`: リモート名
- `develop`: プッシュするブランチ名

**実行例の出力**:
```
branch 'develop' set up to track 'origin/develop'.
To https://github.com/hotchrome2/flet_csv.git
 * [new branch]      develop -> develop
```

### 5.2 mainブランチを作成してプッシュ

```bash
# developと同じ内容でmainブランチを作成
git checkout -b main

# mainブランチをプッシュ
git push -u origin main

# developブランチに戻る
git checkout develop
```

**実行例の出力**:
```
Switched to a new branch 'main'
To https://github.com/hotchrome2/flet_csv.git
 * [new branch]      main -> main
Switched to branch 'develop'
```

### 5.3 プッシュ結果の確認

```bash
# ローカルとリモートのブランチを表示
git branch -a
```

**期待される出力**:
```
* develop
  main
  remotes/origin/develop
  remotes/origin/main
```

---

## 6. README.mdの充実化

### 6.1 README.mdの重要性

GitHubのリポジトリページに最初に表示されるファイルです。

**含めるべき内容**:
- ✅ プロジェクト概要
- ✅ 主な特徴
- ✅ セットアップ手順
- ✅ 使い方
- ✅ ドキュメントへのリンク
- ✅ ライセンス情報

### 6.2 README.mdの作成

```bash
# エディタでREADME.mdを編集
# （内容は本プロジェクトのREADME.mdを参照）

# ステージング
git add README.md

# コミット
git commit -m "docs: README.mdを充実化"

# developブランチにプッシュ
git push origin develop
```

### 6.3 mainブランチにも反映

```bash
# mainブランチに切り替え
git checkout main

# developの変更をマージ
git merge develop

# mainブランチをプッシュ
git push origin main

# developに戻る
git checkout develop
```

---

## 7. GitHub推奨設定

### 7.1 リポジトリの基本情報

**Settings → General**

1. **Description（説明）**
   ```
   複数の時系列CSVファイルを結合するWebアプリケーション
   ```

2. **Website（ウェブサイト）**
   ```
   https://www.additengineer.info
   ```

3. **Topics（トピック）**
   ```
   python, csv, clean-architecture, tdd, flet, pandas
   ```

### 7.2 ブランチ保護ルール

**Settings → Branches → Add rule**

#### mainブランチの保護

- **Branch name pattern**: `main`
- **Protect matching branches**:
  - ✅ Require a pull request before merging
    - ✅ Require approvals (1以上)
  - ✅ Require status checks to pass before merging
    - ✅ Require branches to be up to date before merging
  - ✅ Do not allow bypassing the above settings

**効果**:
- mainブランチへの直接プッシュを禁止
- Pull Requestによるマージを必須化
- コードレビューを必須化

### 7.3 GitHub Actionsの設定（オプション）

**.github/workflows/test.yml** を作成：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run tests
        run: uv run pytest
```

**効果**:
- プッシュ時に自動テスト実行
- Pull Request時に自動テスト実行
- テスト結果をGitHubに表示

### 7.4 Issue・Pull Requestテンプレート（オプション）

**.github/PULL_REQUEST_TEMPLATE.md**:

```markdown
## 変更内容

<!-- このPRで何を変更したか -->

## 変更の種類

- [ ] 新機能追加
- [ ] バグ修正
- [ ] ドキュメント更新
- [ ] リファクタリング
- [ ] テスト追加

## チェックリスト

- [ ] テストを追加/更新した
- [ ] すべてのテストが通る
- [ ] ドキュメントを更新した
- [ ] コードレビューの準備ができている
```

---

## 8. 日常的な運用

### 8.1 開発の基本フロー

```bash
# 1. developブランチで作業
git checkout develop

# 2. 変更をコミット
git add .
git commit -m "feat: 新機能実装"

# 3. GitHubにプッシュ
git push origin develop
```

### 8.2 機能ブランチを使う場合（推奨）

```bash
# 1. 機能ブランチを作成
git checkout -b feature/usecase-layer

# 2. 開発してコミット
git add .
git commit -m "feat: UseCase層実装"

# 3. GitHubにプッシュ
git push origin feature/usecase-layer

# 4. GitHub上でPull Requestを作成
#    feature/usecase-layer → develop

# 5. レビュー・マージ後、ローカルを更新
git checkout develop
git pull origin develop

# 6. 機能ブランチを削除
git branch -d feature/usecase-layer
```

### 8.3 安定版リリース（developからmain）

```bash
# 1. developの内容をmainにマージ
git checkout main
git merge develop

# 2. タグを付ける（バージョン管理）
git tag -a v0.2.0 -m "UseCase層実装完了"

# 3. GitHubにプッシュ
git push origin main
git push origin v0.2.0

# 4. developに戻る
git checkout develop
```

### 8.4 他の開発者の変更を取り込む

```bash
# リモートの最新情報を取得
git fetch origin

# developブランチを更新
git checkout develop
git pull origin develop

# mainブランチを更新
git checkout main
git pull origin main
```

---

## 9. トラブルシューティング

### 9.1 認証エラー

**問題**: `remote: Support for password authentication was removed...`

**解決策**:
1. Personal Access Tokenを作成
   - GitHub → Settings → Developer settings → Personal access tokens → Generate new token
2. パスワードの代わりにトークンを使用

### 9.2 プッシュが拒否される

**問題**: `! [rejected] main -> main (fetch first)`

**原因**: リモートに自分の持っていない変更がある

**解決策**:
```bash
# リモートの変更を取得してマージ
git pull origin main

# コンフリクトがあれば解決してコミット
git add .
git commit

# 再度プッシュ
git push origin main
```

### 9.3 間違ったブランチにプッシュした

**解決策**:
```bash
# リモートブランチを削除
git push origin --delete wrong-branch-name

# 正しいブランチをプッシュ
git push origin correct-branch-name
```

---

## 10. ベストプラクティス

### 10.1 コミットメッセージ

**Conventional Commits形式を推奨**:

```
<type>: <subject>

<body>

<footer>
```

**type（タイプ）**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードスタイル変更（機能変更なし）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルド・設定変更

**例**:
```
feat: UseCase層の実装

- MergeCsvFilesUseCaseクラスを追加
- RepositoryとMergerを組み合わせた処理
- 統合テストを追加

Closes #12
```

### 10.2 プッシュ前のチェック

```bash
# 1. テストを実行
uv run pytest

# 2. コードフォーマット
uv run black .
uv run isort .

# 3. 型チェック
uv run mypy domain infra usecase

# 4. ステージング内容を確認
git diff --staged

# 5. プッシュ
git push origin develop
```

### 10.3 定期的なメンテナンス

```bash
# 不要なブランチを削除
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

# リモートで削除されたブランチをローカルからも削除
git fetch --prune

# リモートの状態を確認
git remote show origin
```

---

## まとめ

### 初回セットアップの流れ

1. ✅ GitHubでリポジトリ作成（初期化なし）
2. ✅ ローカルでdevelopブランチ作成
3. ✅ リモートリポジトリを登録（`git remote add origin`）
4. ✅ developブランチをプッシュ（`git push -u origin develop`）
5. ✅ mainブランチを作成してプッシュ
6. ✅ README.mdを充実化
7. ✅ GitHub設定（Description, Topics, Branch protection）

### 日常の運用

```
開発: developブランチで作業 → プッシュ
     ↓
機能: feature/*ブランチで開発 → Pull Request → developにマージ
     ↓
リリース: develop → main（タグ付き）
```

### 重要なポイント

- ✅ developで開発、mainで安定版管理
- ✅ Pull Requestでコードレビュー
- ✅ Conventional Commitsでメッセージ統一
- ✅ プッシュ前にテスト実行
- ✅ タグでバージョン管理

---

**作成日**: 2025-10-19  
**最終更新**: 2025-10-19  
**対象プロジェクト**: flet_csv

