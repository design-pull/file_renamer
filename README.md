# file_renamer

ファイル連番リネーマーは、選択したファイル群を指定したベース名と連番で一括リネームするシンプルなデスクトップ GUI ツールです。Windows 実行ファイル（exe）で配布でき、開発者はソース（Python + tkinter）から実行・ビルドできます。

## 目次
- 概要
- ダウンロード
- クイックスタート（ユーザー向け）
- 開発者向け（実行・ビルド）
- 注意事項と安全対策
- トラブルシュート
- ライセンス・連絡
- スクリーンショット

---

## 概要
**主な機能**
- 複数ファイルの一括選択
- ベース名 / 開始番号 / 桁数 の指定
- プレビュー表示（旧名 → 新名）
- Dry Run（実ファイル変更なしで確認）
- 実行（リネーム）と Undo（最後のグループ操作を元に戻す）
- 実行ログ（rename_undo_log.csv）による復元

---

## ダウンロード
- 最新の Windows 実行ファイル（file_renamer_gui.exe）は GitHub Releases をご確認ください。  
- ダウンロード後、exe をダブルクリックして起動します。Windows のスマートスクリーンやアンチウイルスに警告される場合は、公開元と SHA256 を確認してください。

SHA256 の確認例（Windows の certutil を使用）:
```powershell
certutil -hashfile file_renamer_gui.exe SHA256

クイックスタート（ユーザー向け）
「ファイル選択」ボタンで対象ファイルを選ぶ。

「ベース名」にリネーム後の先頭文字列を入力（例: photo）。

「開始番号」「桁数」を設定（例: 開始 1, 桁数 3 → photo_001.jpg）。

「プレビュー」を押して旧名→新名を確認。

必要なら「Dry Run」で実操作なしに確認。

問題なければ「実行」を押す。操作は undo ログに記録されるので「最後の操作を元に戻す」で直近グループを復元可能。

重要:

プレビューと Dry Run を必ず利用してください。既に同名ファイルが存在する場合は実行時にエラーになります。

Undo が必ず成功するわけではありません（外部でファイルが移動・削除された場合など）。

開発者向け（実行・ビルド）
要件: Python 3.11 以上（推奨）、PyInstaller（配布用ビルド）

ソースをローカルで実行する:

powershell
cd C:\tools\file_renamer
python .\file_renamer_gui.py
仮想環境を使ったビルド手順（例）:

powershell
cd C:\tools\file_renamer
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install pyinstaller
pyinstaller --onefile --windowed file_renamer_gui.py
# 出力: dist\file_renamer_gui.exe
GitHub Actions による自動ビルド:

.github/workflows/release.yml を利用すると push / タグ作成で Windows exe をビルドして Release に添付できます。

Release 作成に必要な権限を付与するため、workflow に permissions: contents: write を設定してください。

ビルド時の中間生成物:

build/ フォルダは中間生成物です。配布に不要なので削除して問題ありません。

配布対象は dist/file_renamer_gui.exe のみです。

注意事項と安全対策
リネーム処理はファイル名を直接操作します。重要なファイルは事前にバックアップしてください。

Undo ログ（rename_undo_log.csv）は既定で作業ディレクトリに保存されます。配布版ではユーザープロファイルへ保存する変更を推奨します。

未署名の exe は一部のアンチウイルスで誤検知されやすいです。不特定多数へ配布する場合はコード署名を検討してください。

バージョン管理と配布は GitHub Releases を使うのが推奨です（exe はリポジトリ履歴に直接コミットしないでください）。

トラブルシュート（よくある事例）
dist の exe が削除できない / 上書きできない

exe が実行中でロックされている可能性があります。タスクマネージャーでプロセスを終了してから削除してください。

PyInstaller のビルドで 403 / Release 作成エラー

workflow に permissions: contents: write を追加してください。

Undo が失敗する

実行後にファイルが別の場所に移動・削除された可能性があります。undo ログ（rename_undo_log.csv）を確認してください。

追加のログやエラー出力を貼っていただければ具体的な対処を提示します。
