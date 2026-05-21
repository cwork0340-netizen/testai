"""LINE 相片整理小工具 — 拖曳照片進視窗，自動分類上傳到 Google Drive。"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import traceback
from datetime import date
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from drive_client import DriveClient

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic"}


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def sanitize(name: str) -> str:
    """Strip characters that are illegal in Windows/Drive file names."""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip()
    return cleaned or "未命名"


class UploadWorker(QObject):
    progress = Signal(int, int)  # done, total
    finished = Signal(str)        # share link
    failed = Signal(str)          # error message

    def __init__(
        self,
        files: list[Path],
        group: str,
        activity: str,
        the_date: date,
        cfg: dict,
    ) -> None:
        super().__init__()
        self.files = files
        self.group = group
        self.activity = activity
        self.date = the_date
        self.cfg = cfg

    def run(self) -> None:
        tmp_dir: Path | None = None
        try:
            client = DriveClient()
            root_id = client.get_or_create_folder(self.cfg["drive_root_folder"])
            group_id = client.get_or_create_folder(self.group, parent_id=root_id)
            date_str = self.date.strftime(self.cfg["date_format"])
            subfolder = sanitize(f"{date_str}_{self.activity}")
            target_id = client.get_or_create_folder(subfolder, parent_id=group_id)

            # Stage renamed copies in a temp dir so originals stay untouched.
            tmp_dir = Path(tempfile.mkdtemp(prefix="line_photo_"))
            pattern = self.cfg["filename_pattern"]
            group_clean = sanitize(self.group)
            activity_clean = sanitize(self.activity)

            total = len(self.files)
            for i, src in enumerate(self.files, start=1):
                stem = pattern.format(
                    date=date_str,
                    group=group_clean,
                    activity=activity_clean,
                    seq=i,
                )
                dst_name = f"{sanitize(stem)}{src.suffix.lower()}"
                staged = tmp_dir / dst_name
                shutil.copy2(src, staged)
                client.upload_file(str(staged), target_id, dst_name)
                self.progress.emit(i, total)

            link = (
                client.make_folder_link_shareable(target_id)
                if self.cfg.get("make_link_anyone_with_link", True)
                else f"https://drive.google.com/drive/folders/{target_id}"
            )
            self.finished.emit(link)
        except Exception:
            self.failed.emit(traceback.format_exc())
        finally:
            if tmp_dir and tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.cfg = load_config()
        self.pending_files: list[Path] = []
        self.thread: QThread | None = None
        self.worker: UploadWorker | None = None

        self.setWindowTitle("LINE 相片整理工具")
        self.setAcceptDrops(True)
        self.resize(520, 460)
        self._build_ui()
        self._refresh_drop_label()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.drop_label = QLabel()
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setMinimumHeight(160)
        self.drop_label.setStyleSheet(
            "QLabel {"
            "  border: 2px dashed #888;"
            "  border-radius: 12px;"
            "  background-color: #fafafa;"
            "  font-size: 16px;"
            "  color: #555;"
            "}"
        )
        layout.addWidget(self.drop_label)

        form = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(date.today())
        form.addRow("日期：", self.date_edit)

        group_row = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.setEditable(False)
        self.group_combo.addItems(self.cfg.get("groups", []))
        group_row.addWidget(self.group_combo, 1)
        add_group_btn = QPushButton("＋ 新增群組")
        add_group_btn.clicked.connect(self._add_group)
        group_row.addWidget(add_group_btn)
        form.addRow("群組：", group_row)

        self.activity_edit = QLineEdit()
        self.activity_edit.setPlaceholderText("例如：年終尾牙、5月份例會")
        form.addRow("活動：", self.activity_edit)

        layout.addLayout(form)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        button_row = QHBoxLayout()
        self.pick_btn = QPushButton("選擇檔案…")
        self.pick_btn.clicked.connect(self._pick_files)
        button_row.addWidget(self.pick_btn)
        button_row.addStretch(1)
        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self._clear_pending)
        button_row.addWidget(self.clear_btn)
        self.upload_btn = QPushButton("📤 上傳")
        self.upload_btn.setDefault(True)
        self.upload_btn.clicked.connect(self._start_upload)
        button_row.addWidget(self.upload_btn)
        layout.addLayout(button_row)

    def _refresh_drop_label(self) -> None:
        if self.pending_files:
            self.drop_label.setText(
                f"📸 已準備 {len(self.pending_files)} 張照片\n"
                "（可再拖更多進來追加，或按下方「清除」重來）"
            )
        else:
            self.drop_label.setText(
                "📥 把 LINE 的照片拖到這裡\n"
                "（在 LINE 群組裡 Shift + 點選範圍 → 拖進來）"
            )

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        added = 0
        for url in event.mimeData().urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXT:
                if path not in self.pending_files:
                    self.pending_files.append(path)
                    added += 1
        if added == 0:
            QMessageBox.warning(self, "沒有可用的照片", "拖進來的檔案沒有支援的圖片格式。")
        self._refresh_drop_label()

    def _pick_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "選擇照片",
            "",
            "圖片 (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.heic)",
        )
        for f in files:
            path = Path(f)
            if path not in self.pending_files:
                self.pending_files.append(path)
        self._refresh_drop_label()

    def _clear_pending(self) -> None:
        self.pending_files.clear()
        self._refresh_drop_label()

    def _add_group(self) -> None:
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "新增群組", "群組名稱：")
        name = name.strip()
        if not ok or not name:
            return
        groups = self.cfg.setdefault("groups", [])
        if name in groups:
            QMessageBox.information(self, "已存在", "這個群組名稱已經在清單裡了。")
        else:
            groups.append(name)
            save_config(self.cfg)
            self.group_combo.addItem(name)
        self.group_combo.setCurrentText(name)

    def _start_upload(self) -> None:
        if not self.pending_files:
            QMessageBox.warning(self, "沒有照片", "請先把照片拖進視窗或用「選擇檔案」加入。")
            return
        group = self.group_combo.currentText().strip()
        activity = self.activity_edit.text().strip()
        if not group:
            QMessageBox.warning(self, "缺少群組", "請選擇或新增一個群組名稱。")
            return
        if not activity:
            QMessageBox.warning(self, "缺少活動名稱", "請輸入活動名稱（會用在資料夾與檔名）。")
            return

        the_date = self.date_edit.date().toPython()
        self._set_busy(True)
        self.progress.setVisible(True)
        self.progress.setRange(0, len(self.pending_files))
        self.progress.setValue(0)

        self.thread = QThread(self)
        self.worker = UploadWorker(
            list(self.pending_files), group, activity, the_date, self.cfg
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_thread)
        self.thread.start()

    def _on_progress(self, done: int, total: int) -> None:
        self.progress.setValue(done)
        self.drop_label.setText(f"⬆️ 上傳中… {done} / {total}")

    def _on_finished(self, link: str) -> None:
        QGuiApplication.clipboard().setText(link)
        QMessageBox.information(
            self,
            "上傳完成",
            f"✅ 已上傳 {len(self.pending_files)} 張照片\n\n"
            f"連結（已複製到剪貼簿，可直接貼回 LINE）：\n{link}",
        )
        self.pending_files.clear()
        self.activity_edit.clear()
        self.progress.setVisible(False)
        self._refresh_drop_label()
        self._set_busy(False)

    def _on_failed(self, message: str) -> None:
        self.progress.setVisible(False)
        self._refresh_drop_label()
        self._set_busy(False)
        QMessageBox.critical(self, "上傳失敗", message)

    def _cleanup_thread(self) -> None:
        if self.thread:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None

    def _set_busy(self, busy: bool) -> None:
        for w in (self.upload_btn, self.pick_btn, self.clear_btn,
                  self.date_edit, self.group_combo, self.activity_edit):
            w.setEnabled(not busy)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
