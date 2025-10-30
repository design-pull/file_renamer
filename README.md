# 複数ファイル名の一括置換ソフト

ファイル連番リネーマーは、選択したファイル群を指定したベース名と連番で一括リネームするシンプルなデスクトップ GUI ツールです。Windows 実行ファイル（exe）で配布でき、開発者はソースから実行とビルドが可能です。

<img src="https://design-pull.com/wp-content/uploads/2025/10/bandicam-2025-10-30-20-50-27-262.jpg" alt="複数ファイル名の一括置換ソフト">

## 目次
- 概要
- ダウンロード
- クイックスタート
- 開発者向け（実行とビルド）
- 注意事項と安全対策
- トラブルシュート
- ライセンスと連絡

---

## 概要
**主な機能**
- 複数ファイルの一括選択  
- ベース名、開始番号、桁数の指定  
- プレビュー表示で旧名と新名を確認  
- Dry Run による検証（実ファイルは変更しない）  
- 実行と Undo（最後のグループ操作を元に戻す）  
- 実行ログ rename_undo_log.csv による復元

---

## ダウンロード
- 最新の Windows 実行ファイル file_renamer_gui.exe は GitHub Releases から入手してください。  
- ダウンロードしたら exe をダブルクリックして起動します。スマートスクリーンやアンチウイルスで警告が出た場合は公開元と SHA256 ハッシュを確認してください。

SHA256 の確認例:
```powershell
certutil -hashfile file_renamer_gui.exe SHA256
```

---

## クイックスタート
1. 「ファイル選択」ボタンで対象ファイルを追加する  
2. 「ベース名」にリネーム後の先頭文字列を入力（例: `photo`）  
3. 「開始番号」と「桁数」を設定（例: 開始 1, 桁数 3 → `photo_001.jpg`）  
4. 「プレビュー」を押して旧名と新名を確認する  
5. 必要なら「Dry Run」で実ファイルを変更せず動作を検証する  
6. 問題なければ「実行」を押す。操作は undo ログに記録されるため「最後の操作を元に戻す」で直近グループを復元可能

重要な使い方の注意
- プレビューと Dry Run を必ず実行してから本処理を行ってください。  
- 同名ファイルが存在する場合は実行時にエラーになる可能性があります。  
- Undo はすべてのケースで復元できるわけではありません。ファイルが外部で移動や削除されていると復元できないことがあります。

---

## 開発者向け（実行とビルド）
要件
- Python 3.11 以上を推奨  
- 配布用ビルドに PyInstaller を使用

ソースをローカルで実行する例:
```powershell
cd C:\tools\file_renamer
python .\file_renamer_gui.py
```

配布用 exe を作る手順の例:
```powershell
cd C:\tools\file_renamer
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install pyinstaller
pyinstaller --onefile --windowed file_renamer_gui.py
# 出力は dist\file_renamer_gui.exe
```

自動ビルド
- `.github/workflows/release.yml` を用意すると push やタグ作成で自動ビルドと Release 添付が可能です。  
- Actions から Release を作成する場合は workflow に次を設定してください:
```yaml
permissions:
  contents: write
```

ビルド生成物について
- `build/` フォルダは PyInstaller の中間生成物です。配布には不要なので削除して問題ありません。  
- 配布対象は `dist/file_renamer_gui.exe` のみです。

---

## 注意事項と安全対策
- 重要ファイルは事前にバックアップしてください。リネーム処理はファイル名を直接変更します。  
- Undo ログ `rename_undo_log.csv` は既定で作業ディレクトリに保存されます。配布版ではユーザープロファイルに保存する変更を推奨します。  
- 未署名の exe はアンチウイルスに誤検知されやすいため、多数配布する場合はコード署名を検討してください。  
- exe をリポジトリに直接コミットしないでください。履歴肥大化を避けるため Releases に添付する方法を推奨します。

---

## トラブルシュート
- dist の exe が削除できない場合  
  - exe が実行中でロックされている可能性があります。タスクマネージャーで該当プロセスを終了してから再試行してください。  
- PyInstaller ビルドや Release 作成で 403 エラーが出る場合  
  - workflow に `permissions: contents: write` を追加してください。  
- Undo が失敗する場合  
  - 実行後にファイルが移動や削除されている可能性があります。`rename_undo_log.csv` を確認してください。

問題のログやエラーメッセージを貼っていただければ、具体的な対処方法を提示します。

---

## ライセンスと連絡
- ライセンスはリポジトリ内の LICENSE を参照してください。未設定なら MIT を推奨します。  
- バグ報告や要望は GitHub Issues に投稿してください。Issue タイトルに `bug:` や `feature:` を付けると見つけやすくなります。

---

## README をリポジトリに追加する手順
1. この内容を `README.md` として保存する  
2. 次を実行してリポジトリに反映する:
```bash
git add README.md
git commit -m "Add README"
git push origin main
```

---
