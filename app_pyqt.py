# app_pyqt.py
import sys, os, csv, re
from datetime import datetime
from PySide6 import QtWidgets, QtCore

UNDO_LOG = os.path.join(os.path.expanduser("~"), "file_renamer_undo.csv")

class RenameModel(QtCore.QAbstractTableModel):
    HEADERS = ["元パス","拡張子","新パス","状態"]
    def __init__(self, items=None):
        super().__init__()
        self.items = items or []  # list of dict {path, name, ext, newpath, status}
    def rowCount(self, parent=None): return len(self.items)
    def columnCount(self, parent=None): return 4
    def data(self, index, role):
        if not index.isValid(): return None
        r,c = index.row(), index.column()
        if role==QtCore.Qt.DisplayRole:
            it = self.items[r]
            if c==0: return it["path"]
            if c==1: return it["ext"]
            if c==2: return it.get("newpath","")
            if c==3: return it.get("status","")
    def headerData(self, section, orientation, role):
        if role==QtCore.Qt.DisplayRole and orientation==QtCore.Qt.Horizontal:
            return self.HEADERS[section]
    def set_items(self, items):
        self.beginResetModel()
        self.items = items
        self.endResetModel()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PowerRename")
        w = QtWidgets.QWidget()
        self.setCentralWidget(w)
        layout = QtWidgets.QVBoxLayout(w)

        # controls
        ctrl = QtWidgets.QHBoxLayout()
        self.base_edit = QtWidgets.QLineEdit("name")
        self.start_spin = QtWidgets.QSpinBox(); self.start_spin.setMinimum(0); self.start_spin.setValue(1)
        self.width_spin = QtWidgets.QSpinBox(); self.width_spin.setMinimum(1); self.width_spin.setValue(3)
        ctrl.addWidget(QtWidgets.QLabel("Base"))
        ctrl.addWidget(self.base_edit)
        ctrl.addWidget(QtWidgets.QLabel("Start"))
        ctrl.addWidget(self.start_spin)
        ctrl.addWidget(QtWidgets.QLabel("Width"))
        ctrl.addWidget(self.width_spin)
        layout.addLayout(ctrl)

        # replace / regex
        repl_layout = QtWidgets.QHBoxLayout()
        self.find_edit = QtWidgets.QLineEdit()
        self.repl_edit = QtWidgets.QLineEdit()
        self.regex_cb = QtWidgets.QCheckBox("Regex")
        repl_layout.addWidget(QtWidgets.QLabel("Find"))
        repl_layout.addWidget(self.find_edit)
        repl_layout.addWidget(QtWidgets.QLabel("Replace"))
        repl_layout.addWidget(self.repl_edit)
        repl_layout.addWidget(self.regex_cb)
        layout.addLayout(repl_layout)

        # file list / preview
        self.model = RenameModel([])
        self.view = QtWidgets.QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.view)

        # buttons
        btns = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add Files")
        self.preview_btn = QtWidgets.QPushButton("Preview")
        self.dry_btn = QtWidgets.QPushButton("Dry Run")
        self.run_btn = QtWidgets.QPushButton("Run")
        self.undo_btn = QtWidgets.QPushButton("Undo Last")
        btns.addWidget(self.add_btn); btns.addWidget(self.preview_btn); btns.addWidget(self.dry_btn)
        btns.addWidget(self.run_btn); btns.addWidget(self.undo_btn)
        layout.addLayout(btns)

        # signals
        self.add_btn.clicked.connect(self.add_files)
        self.preview_btn.clicked.connect(lambda: self.build_preview(dry=False))
        self.dry_btn.clicked.connect(lambda: self.build_preview(dry=True))
        self.run_btn.clicked.connect(lambda: self.execute(dry=False))
        self.undo_btn.clicked.connect(self.undo_last)

        self.files = []  # list of full paths

    def add_files(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Files")
        if paths:
            self.files.extend(paths)
            self.update_model_paths()

    def update_model_paths(self):
        items = []
        for p in self.files:
            name = os.path.basename(p)
            ext = os.path.splitext(name)[1]
            items.append({"path": p, "name": name, "ext": ext, "newpath": "", "status": ""})
        self.model.set_items(items)

    def build_preview(self, dry=False):
        items = self.model.items
        base = self.base_edit.text().strip()
        start = self.start_spin.value()
        width = self.width_spin.value()
        find = self.find_edit.text()
        repl = self.repl_edit.text()
        use_regex = self.regex_cb.isChecked()
        i = start
        for it in items:
            name = it["name"]
            newname = name
            # apply find/replace
            if find:
                try:
                    if use_regex:
                        newname = re.sub(find, repl, newname)
                    else:
                        newname = newname.replace(find, repl)
                except Exception as e:
                    it["status"] = f"ReplaceErr:{e}"
                    continue
            # apply base+index template if base provided
            if base:
                newname = f"{base}_{str(i).zfill(width)}{it['ext']}"
                i += 1
            it["newpath"] = os.path.join(os.path.dirname(it["path"]), newname)
            it["status"] = ("EXISTS" if os.path.exists(it["newpath"]) and it["newpath"]!=it["path"] else "OK")
        self.model.layoutChanged.emit()
        if dry:
            QtWidgets.QMessageBox.information(self, "Dry Run", "Dry run completed, no changes made")

    def execute(self, dry=False):
        self.build_preview(dry=True)  # always build preview first
        items = self.model.items
        to_rename = [it for it in items if it.get("newpath") and it["newpath"]!=it["path"]]
        if not to_rename:
            QtWidgets.QMessageBox.information(self, "Info", "No items to rename")
            return
        if not dry:
            res = QtWidgets.QMessageBox.question(self, "Confirm", f"Rename {len(to_rename)} files?")
            if res!=QtWidgets.QMessageBox.Yes:
                return
        log = []
        errors = []
        for it in to_rename:
            old = it["path"]; new = it["newpath"]
            try:
                if os.path.exists(new) and new!=old:
                    raise FileExistsError("target exists")
                if not dry:
                    os.rename(old, new)
                log.append([datetime.utcnow().isoformat(), old, new])
                it["status"] = "RENAMED" if not dry else "DRY_OK"
            except Exception as e:
                errors.append(f"{old} -> {new} : {e}")
                it["status"] = f"ERR:{e}"
        # write undo
        if log and not dry:
            write_header = not os.path.exists(UNDO_LOG)
            with open(UNDO_LOG, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if write_header:
                    w.writerow(["ts","old","new"])
                w.writerows(log)
        self.model.layoutChanged.emit()
        if errors:
            QtWidgets.QMessageBox.warning(self, "Some errors", "\n".join(errors))
        else:
            QtWidgets.QMessageBox.information(self, "Done", f"{len(log)} renamed")

    def undo_last(self):
        if not os.path.exists(UNDO_LOG):
            QtWidgets.QMessageBox.information(self, "Info", "No undo log")
            return
        with open(UNDO_LOG, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            QtWidgets.QMessageBox.information(self, "Info", "Undo log empty")
            return
        last_ts = rows[-1]["ts"]
        to_undo = [r for r in reversed(rows) if r["ts"]==last_ts]
        errors=[]; undone=0
        for r in to_undo:
            old, new = r["old"], r["new"]
            if os.path.exists(new) and not os.path.exists(old):
                try:
                    os.rename(new, old); undone+=1
                except Exception as e:
                    errors.append(str(e))
            else:
                errors.append(f"Missing {new}")
        remaining = [r for r in rows if r["ts"]!=last_ts]
        with open(UNDO_LOG, "w", newline="", encoding="utf-8") as f:
            if remaining:
                w = csv.DictWriter(f, fieldnames=["ts","old","new"])
                w.writeheader(); w.writerows(remaining)
        if errors:
            QtWidgets.QMessageBox.warning(self, "Undo done with errors", "\n".join(errors))
        else:
            QtWidgets.QMessageBox.information(self, "Undo", f"{undone} restored")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow(); mw.resize(900,500); mw.show()
    sys.exit(app.exec())
