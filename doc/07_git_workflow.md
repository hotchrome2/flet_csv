# Git開発ワークフロー

このドキュメントは、featureブランチを使った日常的な開発フローを詳細に記載します。

**対象**: 日常的な機能開発からGitHubへの反映まで

---

## 目次

1. [基本的なブランチ戦略](#1-基本的なブランチ戦略)
2. [featureブランチでの開発フロー](#2-featureブランチでの開発フロー)
3. [developへの反映](#3-developへの反映)
4. [mainへの反映](#4-mainへの反映)
5. [GitHubへの反映](#5-githubへの反映)
6. [ブランチのクリーンアップ](#6-ブランチのクリーンアップ)
7. [完全な実行例](#7-完全な実行例)
8. [トラブルシューティング](#8-トラブルシューティング)

---

## 1. 基本的なブランチ戦略

このプロジェクトでは、**Git Flow**を簡略化した戦略を採用します。

```
main (本番・安定版)
  └── develop (開発統合ブランチ)
       └── feature/* (機能開発ブランチ)
```

### ブランチの役割

| ブランチ | 役割 | 更新タイミング |
|---------|------|--------------|
| **main** | 本番環境にデプロイ可能な安定版 | developから定期的にマージ |
| **develop** | 開発版（次のリリース候補） | featureブランチからマージ |
| **feature/** | 新機能開発 | 開発中は頻繁にコミット |

---

## 2. featureブランチでの開発フロー

### ステップ1: 最新のdevelopを取得

```bash
# developブランチに移動
git checkout develop

# リモートの最新を取得
git pull origin develop
```

**確認**:
```bash
git log --oneline -3
```

**期待される出力**:
```
238a863 docs: GitHub登録手順を既存ブランチ前提に修正
1b8b202 docs: GitHubリポジトリ登録手順をドキュメント化
b56cbc5 docs: README.mdを充実化
```

### ステップ2: featureブランチを作成

```bash
# 新しいfeatureブランチを作成して切り替え
git checkout -b feature/usecase-layer
```

**ブランチ命名規則**:
- `feature/機能名` の形式
- 機能名は小文字、ハイフン区切り
- 例:
  - `feature/usecase-layer`
  - `feature/csv-validation`
  - `feature/error-handling`

**確認**:
```bash
git branch
```

**期待される出力**:
```
  develop
* feature/usecase-layer
  main
```

### ステップ3: 開発作業

```bash
# ファイルを作成・編集
# 例: UseCase層を実装

# 1. ディレクトリ作成（必要な場合）
mkdir -p usecase
mkdir -p tests/unit/usecase

# 2. ファイル編集
# （エディタで実装作業）

# 3. ステータス確認
git status
```

**期待される出力**:
```
On branch feature/usecase-layer
Untracked files:
  usecase/merge_csv_files.py
  tests/unit/usecase/test_merge_csv_files.py
```

### ステップ4: 変更をコミット

```bash
# ファイルをステージング
git add usecase/merge_csv_files.py
git add tests/unit/usecase/test_merge_csv_files.py

# コミット（Conventional Commits形式）
git commit -m "feat: UseCase層の実装

- MergeCsvFilesUseCaseクラスを追加
- RepositoryとMergerを組み合わせた処理
- 統合テストを追加

Refs: #12"
```

**コミットメッセージのガイドライン**:

```
<type>: <subject>

<body>

<footer>
```

**type（タイプ）**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `test`: テスト追加・修正
- `refactor`: リファクタリング
- `style`: コードスタイル変更
- `chore`: ビルド・設定変更

### ステップ5: テスト実行

```bash
# すべてのテストを実行
uv run pytest

# 特定のテストのみ実行
uv run pytest tests/unit/usecase/
```

**期待される出力**:
```
======================== test session starts ========================
collected 85 items

tests/unit/usecase/test_merge_csv_files.py .....                [100%]

======================== 85 passed in 1.52s ========================
```

### ステップ6: 追加の変更（必要に応じて）

開発中は複数回コミットしてOKです。

```bash
# さらに変更
git add .
git commit -m "test: UseCase層のエッジケースを追加"

# ログを確認
git log --oneline -5
```

**期待される出力**:
```
def5678 test: UseCase層のエッジケースを追加
abc1234 feat: UseCase層の実装
238a863 docs: GitHub登録手順を既存ブランチ前提に修正
...
```

---

## 3. developへの反映

featureブランチでの開発が完了したら、developにマージします。

### ステップ1: developを最新化

```bash
# developブランチに切り替え
git checkout develop

# リモートの最新を取得
git pull origin develop
```

**重要**: 他のメンバーの変更がある可能性があるため、必ず最新化

### ステップ2: featureブランチをマージ

```bash
# featureブランチをdevelopにマージ
git merge feature/usecase-layer
```

**期待される出力（Fast-forward）**:
```
Updating 238a863..def5678
Fast-forward
 usecase/merge_csv_files.py                   | 150 ++++++++++++++++
 tests/unit/usecase/test_merge_csv_files.py   | 180 +++++++++++++++++++
 2 files changed, 330 insertions(+)
```

**もしコンフリクトが発生した場合**:
```
Auto-merging usecase/merge_csv_files.py
CONFLICT (content): Merge conflict in usecase/merge_csv_files.py
Automatic merge failed; fix conflicts and then commit the result.
```

**コンフリクト解決手順**:
```bash
# 1. コンフリクトファイルを編集（エディタで）
# <<<<<<< HEAD
# =======
# >>>>>>> feature/usecase-layer
# の部分を手動で修正

# 2. 解決したファイルをステージング
git add usecase/merge_csv_files.py

# 3. マージを完了
git commit -m "Merge branch 'feature/usecase-layer' into develop"
```

### ステップ3: テスト実行（重要！）

```bash
# マージ後、必ずテストを実行
uv run pytest
```

### ステップ4: developにプッシュ

```bash
# developブランチをGitHubにプッシュ
git push origin develop
```

**期待される出力**:
```
To https://github.com/hotchrome2/flet_csv.git
   238a863..def5678  develop -> develop
```

---

## 4. mainへの反映

developで統合・テストが完了したら、mainに反映します。

### ステップ1: mainを最新化

```bash
# mainブランチに切り替え
git checkout main

# リモートの最新を取得
git pull origin main
```

### ステップ2: developをmainにマージ

```bash
# developをmainにマージ
git merge develop
```

**期待される出力（Fast-forward）**:
```
Updating 238a863..def5678
Fast-forward
 usecase/merge_csv_files.py                   | 150 ++++++++++++++++
 tests/unit/usecase/test_merge_csv_files.py   | 180 +++++++++++++++++++
 2 files changed, 330 insertions(+)
```

### ステップ3: タグ付け（オプション・推奨）

リリースのマイルストーンにタグを付けます。

```bash
# タグを作成（バージョン管理）
git tag -a v0.2.0 -m "UseCase層実装完了

- CSV結合ユースケース実装
- 統合テスト完備
- 全85テスト成功"

# タグを確認
git tag -l
```

**期待される出力**:
```
v0.1.0
v0.2.0
```

### ステップ4: mainにプッシュ

```bash
# mainブランチをGitHubにプッシュ
git push origin main

# タグもプッシュ
git push origin v0.2.0
```

**期待される出力**:
```
To https://github.com/hotchrome2/flet_csv.git
   238a863..def5678  main -> main
To https://github.com/hotchrome2/flet_csv.git
 * [new tag]         v0.2.0 -> v0.2.0
```

### ステップ5: mainの変更をdevelopに反映（重要！）

mainにマージした後、必ずdevelopにも反映させます。

```bash
# developブランチに切り替え
git checkout develop

# mainをdevelopにマージ（同期）
git merge main

# developにプッシュ
git push origin develop
```

**なぜ必要？**:
- mainとdevelopの履歴を同期
- 次のfeatureブランチ作成時、mainの最新を含む
- タグ情報もdevelopに反映

---

## 5. GitHubへの反映

ここまでの操作で、GitHub上のすべてのブランチが最新になります。

### 確認: GitHubの状態

ブラウザで https://github.com/hotchrome2/flet_csv を開いて確認：

**mainブランチ**:
- ✅ 最新のコミット: `def5678 test: UseCase層のエッジケースを追加`
- ✅ タグ: `v0.2.0`

**developブランチ**:
- ✅ 最新のコミット: mainと同じ
- ✅ mainと同期済み

### ローカルとリモートの状態確認

```bash
# すべてのブランチとリモートの状態を表示
git branch -a -v
```

**期待される出力**:
```
* develop                  def5678 test: UseCase層のエッジケースを追加
  feature/usecase-layer    def5678 test: UseCase層のエッジケースを追加
  main                     def5678 test: UseCase層のエッジケースを追加
  remotes/origin/develop   def5678 test: UseCase層のエッジケースを追加
  remotes/origin/main      def5678 test: UseCase層のエッジケースを追加
```

**ポイント**:
- develop, main, origin/develop, origin/main が同じコミットを指している ✅
- featureブランチはまだローカルにのみ存在

---

## 6. ブランチのクリーンアップ

featureブランチの役割が終わったら、削除してクリーンな状態を保ちます。

### ローカルのfeatureブランチ削除

```bash
# developブランチにいることを確認
git branch

# featureブランチを削除
git branch -d feature/usecase-layer
```

**期待される出力**:
```
Deleted branch feature/usecase-layer (was def5678).
```

**もし未マージの変更がある場合**:
```
error: The branch 'feature/usecase-layer' is not fully merged.
If you are sure you want to delete it, run 'git branch -D feature/usecase-layer'.
```

**強制削除（注意！）**:
```bash
# 未マージでも削除（変更が失われます）
git branch -D feature/usecase-layer
```

### リモートのfeatureブランチ削除（プッシュした場合）

もしfeatureブランチをGitHubにプッシュしていた場合：

```bash
# リモートのfeatureブランチを削除
git push origin --delete feature/usecase-layer
```

### ブランチ一覧確認

```bash
git branch -a
```

**期待される出力**:
```
* develop
  main
  remotes/origin/develop
  remotes/origin/main
```

featureブランチがクリーンに削除されました ✅

---

## 7. 完全な実行例

実際のコマンドを順番に並べた完全な例です。

```bash
# ========================================
# 1. featureブランチで開発開始
# ========================================

# developの最新を取得
git checkout develop
git pull origin develop

# featureブランチを作成
git checkout -b feature/usecase-layer

# ========================================
# 2. 開発作業
# ========================================

# ファイルを作成・編集（エディタで作業）
# ...

# 変更をコミット
git add usecase/merge_csv_files.py tests/unit/usecase/test_merge_csv_files.py
git commit -m "feat: UseCase層の実装

- MergeCsvFilesUseCaseクラスを追加
- RepositoryとMergerを組み合わせた処理
- 統合テストを追加"

# テスト実行
uv run pytest

# 追加の変更（必要に応じて）
git add .
git commit -m "test: UseCase層のエッジケースを追加"

# ========================================
# 3. developに反映
# ========================================

# developを最新化
git checkout develop
git pull origin develop

# featureブランチをマージ
git merge feature/usecase-layer

# テスト実行（重要！）
uv run pytest

# developにプッシュ
git push origin develop

# ========================================
# 4. mainに反映
# ========================================

# mainを最新化
git checkout main
git pull origin main

# developをマージ
git merge develop

# タグ付け（オプション）
git tag -a v0.2.0 -m "UseCase層実装完了"

# mainとタグをプッシュ
git push origin main
git push origin v0.2.0

# ========================================
# 5. mainの変更をdevelopに同期
# ========================================

# developに切り替え
git checkout develop

# mainをマージ
git merge main

# developにプッシュ
git push origin develop

# ========================================
# 6. ブランチのクリーンアップ
# ========================================

# featureブランチを削除
git branch -d feature/usecase-layer

# 確認
git branch -a

# ========================================
# 完了！
# ========================================

echo "✅ 開発フロー完了"
git log --oneline --graph --all --decorate -5
```

---

## 8. トラブルシューティング

### 問題1: マージコンフリクト

**症状**:
```
Auto-merging usecase/merge_csv_files.py
CONFLICT (content): Merge conflict in usecase/merge_csv_files.py
Automatic merge failed; fix conflicts and then commit the result.
```

**解決策**:
```bash
# 1. コンフリクトファイルを確認
git status

# 2. エディタでファイルを開いて手動修正
# <<<<<<< HEAD
# （現在のブランチの内容）
# =======
# （マージしようとしているブランチの内容）
# >>>>>>> feature/usecase-layer

# 3. 不要な行（<<<<<<<, =======, >>>>>>>）を削除
# 4. 正しい内容に修正

# 5. 解決したファイルをステージング
git add usecase/merge_csv_files.py

# 6. マージを完了
git commit

# 7. テスト実行
uv run pytest
```

### 問題2: 間違ったブランチで作業してしまった

**症状**:
developで作業すべきところ、mainで作業してしまった

**解決策**:
```bash
# 1. 現在の変更を退避
git stash

# 2. 正しいブランチに切り替え
git checkout develop

# 3. 変更を復元
git stash pop

# 4. コミット
git add .
git commit -m "feat: ..."
```

### 問題3: コミットメッセージを間違えた

**症状**:
最後のコミットメッセージを修正したい

**解決策（まだプッシュしていない場合）**:
```bash
# 最後のコミットメッセージを修正
git commit --amend -m "正しいメッセージ"
```

**注意**: プッシュ済みの場合は修正しない！

### 問題4: プッシュが拒否される

**症状**:
```
! [rejected]        develop -> develop (fetch first)
error: failed to push some refs
```

**原因**: リモートに自分が持っていない変更がある

**解決策**:
```bash
# 1. リモートの変更を取得
git pull origin develop

# 2. 再度プッシュ
git push origin develop
```

---

## まとめ

### 標準的な開発フロー

```
1. develop から feature ブランチを作成
   ↓
2. feature ブランチで開発・コミット
   ↓
3. feature → develop にマージ
   ↓
4. develop → main にマージ（リリース時）
   ↓
5. main → develop にマージ（同期）
   ↓
6. feature ブランチを削除
```

### 重要なポイント

✅ **常にdevelopから最新を取得してからfeatureを作成**  
✅ **マージ後は必ずテスト実行**  
✅ **mainに反映した後、developに同期を忘れない**  
✅ **使い終わったfeatureブランチは削除**  
✅ **リリース時はタグを付ける**

### コマンドのチートシート

| 操作 | コマンド |
|------|---------|
| featureブランチ作成 | `git checkout -b feature/xxx` |
| developにマージ | `git merge feature/xxx` |
| mainにマージ | `git merge develop` |
| mainをdevelopに同期 | `git checkout develop && git merge main` |
| featureブランチ削除 | `git branch -d feature/xxx` |
| タグ作成 | `git tag -a v0.2.0 -m "..."` |
| プッシュ（ブランチ） | `git push origin <branch>` |
| プッシュ（タグ） | `git push origin <tag>` |

---

**作成日**: 2025-10-19  
**最終更新**: 2025-10-19  
**対象プロジェクト**: flet_csv

