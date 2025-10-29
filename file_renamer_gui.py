# file_renamer_gui.py
# パス C:\tools\file_renamer
# 実行: python .\file_renamer_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import csv
from datetime import datetime

UNDO_LOG = "rename_undo_log.csv"

def select_files():
    paths = filedialog.askopenfilenames(title="ファイルを選択")
    listbox_files.delete(0, tk.END)
    for p in paths:
        listbox_files.insert(tk.END, p)

def build_preview():
    files = listbox_files.get(0, tk.END)
    if not files:
        messagebox.showinfo("情報", "ファイルを選択してください")
        return []
    base = entry_base.get().strip()
    if not base:
        messagebox.showinfo("情報", "ベース名を入力してください")
        return []
    try:
        start = int(entry_start.get())
        width = int(entry_width.get())
    except ValueError:
        messagebox.showinfo("情報", "開始番号と桁数は整数にしてください")
        return []
    preview = []
    i = start
    for f in files:
        dirpath, fname = os.path.split(f)
        ext = os.path.splitext(fname)[1]
        newname = f"{base}_{str(i).zfill(width)}{ext}"
        preview.append((f, os.path.join(dirpath, newname)))
        i += 1
    # 表示
    tree_preview.delete(*tree_preview.get_children())
    for old, new in preview:
        tree_preview.insert("", tk.END, values=(old, new))
    return preview

def execute_rename(dry_run=False):
    preview = build_preview()
    if not preview:
        return
    confirm = messagebox.askyesno("確認", f"{len(preview)} 件をリネームします。続行しますか？")
    if not confirm:
        return
    log_entries = []
    errors = []
    for old, new in preview:
        if dry_run:
            continue
        try:
            if os.path.exists(new):
                raise FileExistsError(f"ターゲットが既に存在します: {new}")
            os.rename(old, new)
            log_entries.append([datetime.utcnow().isoformat(), old, new])
        except Exception as e:
            errors.append(f"{old} -> {new} : {e}")
    if log_entries:
        write_undo_log(log_entries)
    if dry_run:
        messagebox.showinfo("Dry Run", "Dry-run モード: 実際のリネームは行われませんでした")
    else:
        if errors:
            messagebox.showwarning("一部失敗", "\n".join(errors))
        else:
            messagebox.showinfo("完了", f"{len(log_entries)} 件をリネームしました")

def write_undo_log(entries):
    header = ["timestamp", "old_path", "new_path"]
    write_header = not os.path.exists(UNDO_LOG)
    with open(UNDO_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerows(entries)

def undo_last():
    if not os.path.exists(UNDO_LOG):
        messagebox.showinfo("情報", "undo ログが見つかりません")
        return
    with open(UNDO_LOG, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        messagebox.showinfo("情報", "undo ログが空です")
        return
    last_ts = rows[-1]["timestamp"]
    to_undo = [r for r in reversed(rows) if r["timestamp"] == last_ts]
    errors = []
    undone = 0
    for r in to_undo:
        old = r["old_path"]
        new = r["new_path"]
        if os.path.exists(new) and not os.path.exists(old):
            try:
                os.rename(new, old)
                undone += 1
            except Exception as e:
                errors.append(f"{new} -> {old} : {e}")
        else:
            errors.append(f"期待されるファイルが存在しません: {new}")
    remaining = [r for r in rows if r["timestamp"] != last_ts]
    with open(UNDO_LOG, "w", newline="", encoding="utf-8") as f:
        if remaining:
            w = csv.DictWriter(f, fieldnames=["timestamp", "old_path", "new_path"])
            w.writeheader()
            w.writerows(remaining)
    if errors:
        messagebox.showwarning("一部失敗", "\n".join(errors))
    else:
        messagebox.showinfo("完了", f"{undone} 件を元に戻しました")

# UI build
root = tk.Tk()
root.title("ファイル連番リネーマー")

# 初期ウィンドウサイズ（必要なら調整）
root.geometry("1000x600")

frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill=tk.BOTH, expand=True)

# File select button and listbox
btn_select = ttk.Button(frame_top, text="ファイル選択", command=select_files)
btn_select.grid(row=0, column=0, sticky="w", padx=(0,6))

listbox_files = tk.Listbox(frame_top, width=80, height=6)
listbox_files.grid(row=1, column=0, columnspan=4, pady=6, sticky="ew")

# Controls
ttk.Label(frame_top, text="ベース名").grid(row=2, column=0, sticky="w")
entry_base = ttk.Entry(frame_top, width=20)
entry_base.grid(row=2, column=1, sticky="w")
entry_base.insert(0, "name")

ttk.Label(frame_top, text="開始番号").grid(row=2, column=2, sticky="w")
entry_start = ttk.Entry(frame_top, width=6)
entry_start.grid(row=2, column=3, sticky="w")
entry_start.insert(0, "1")

ttk.Label(frame_top, text="桁数").grid(row=3, column=0, sticky="w")
entry_width = ttk.Entry(frame_top, width=6)
entry_width.grid(row=3, column=1, sticky="w")
entry_width.insert(0, "3")

btn_preview = ttk.Button(frame_top, text="プレビュー", command=build_preview)
btn_preview.grid(row=3, column=2, sticky="w")
btn_execute = ttk.Button(frame_top, text="実行", command=lambda: execute_rename(dry_run=False))
btn_execute.grid(row=3, column=3, sticky="w")
btn_dry = ttk.Button(frame_top, text="Dry Run", command=lambda: execute_rename(dry_run=True))
btn_dry.grid(row=4, column=3, sticky="w")

# Treeview を作成（自動リサイズ対応）
tree_preview = ttk.Treeview(frame_top, columns=("old", "new"), show="headings", height=8)
tree_preview.heading("old", text="元ファイル")
tree_preview.heading("new", text="新しい名前")

# グリッド配置（frame_top のグリッドを伸縮可能にする）
tree_preview.grid(row=5, column=0, columnspan=4, pady=8, sticky="nsew")
frame_top.grid_columnconfigure(0, weight=1)
frame_top.grid_columnconfigure(1, weight=0)
frame_top.grid_columnconfigure(2, weight=0)
frame_top.grid_columnconfigure(3, weight=0)
frame_top.grid_rowconfigure(5, weight=1)

# 初期幅・最小幅・伸縮可否の設定
tree_preview.column("old", width=700, minwidth=150, stretch=True)
tree_preview.column("new", width=300, minwidth=150, stretch=True)

# リサイズ時に列幅を割合で再計算するハンドラ
def _on_frame_resize(event):
    try:
        total = event.width
        # 列幅割合（調整可）
        left = max(int(total * 0.65), 150)
        right = max(int(total * 0.32), 150)
        tree_preview.column("old", width=left)
        tree_preview.column("new", width=right)
    except Exception:
        pass

# frame_top のサイズ変更イベントにバインドする
frame_top.bind("<Configure>", _on_frame_resize)

btn_undo = ttk.Button(frame_top, text="最後の操作を元に戻す", command=undo_last)
btn_undo.grid(row=6, column=0, sticky="w", pady=6)

root.mainloop()
