vers 1

code

import sys
import os
import subprocess
import urllib.request
import re
from datetime import datetime
from PySide6.QtCore import (
    QUrl, Qt, QTimer, QSettings, QSize, QMimeData, QThread, Signal
)
from PySide6.QtGui import (
    QKeySequence, QShortcut, QAction, QDesktopServices, QIcon,
    QPixmap, QPainter, QColor, QFont, QBrush, QPen, QDrag
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QProgressBar, QToolBar,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QFrame,
    QDialog, QComboBox, QDialogButtonBox, QFormLayout
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineCertificateError,
    QWebEngineDownloadRequest, QWebEngineSettings
)


# ============================================================
# НАСТРОЙКИ ОБНОВЛЕНИЙ
# ============================================================
CURRENT_VERSION = 1

UPDATE_URL = "https://raw.githubusercontent.com/kartemser-crypto/updatedeepseek.py/refs/heads/main/update.py"


# ---------- ЯЗЫКИ ИНТЕРФЕЙСА ----------
TRANSLATIONS = {
    "ru": {
        "downloads": "⬇ Загрузки",
        "downloads_folder": "📂 Папка загрузок",
        "back": "← Назад",
        "reload": "↻ Обновить",
        "home": "🏠 DeepSeek",
        "check_updates": "🔄 Проверить обновление",
        "settings": "⚙ Настройки",
        "downloads_title": "📥 Загрузки",
        "downloads_empty": "Нет активных загрузок",
        "downloads_done": "Загрузка завершена",
        "download_in_progress": "Загрузка...",
        "open_folder": "📂 Папка",
        "clear": "🗑",
        "refresh": "🔄",
        "settings_title": "⚙ Настройки",
        "language": "Язык интерфейса:",
        "toolbar_color": "Цвет полосы:",
        "update_available_title": "Доступно обновление",
        "update_available_text": "Найдена новая версия: v{v1}\nВаша версия: v{v2}\n\nОбновить приложение?\n(Приложение закроется и запустится с новой версией)",
        "no_updates_title": "Обновлений нет",
        "no_updates_text": "У вас последняя версия (v{v}).",
        "update_error_title": "Ошибка проверки",
        "update_error_text": "Не удалось проверить обновления:\n{err}",
        "update_close_title": "Обновление",
        "update_close_text": "Приложение закроется и запустится с новой версией.",
        "update_apply_error": "Не удалось применить обновление:\n{e}\n\nПодробности в консоли.",
        "ok": "OK",
        "cancel": "Отмена",
        "save": "Сохранить",
        "file_open": "📂 Открыть",
        "file_show": "📁 Показать в папке",
        "file_delete": "🗑 Удалить",
    },
    "en": {
        "downloads": "⬇ Downloads",
        "downloads_folder": "📂 Downloads Folder",
        "back": "← Back",
        "reload": "↻ Reload",
        "home": "🏠 DeepSeek",
        "check_updates": "🔄 Check Updates",
        "settings": "⚙ Settings",
        "downloads_title": "📥 Downloads",
        "downloads_empty": "No active downloads",
        "downloads_done": "Download complete",
        "download_in_progress": "Downloading...",
        "open_folder": "📂 Folder",
        "clear": "🗑",
        "refresh": "🔄",
        "settings_title": "⚙ Settings",
        "language": "Interface language:",
        "toolbar_color": "Toolbar color:",
        "update_available_title": "Update Available",
        "update_available_text": "New version found: v{v1}\nYour version: v{v2}\n\nUpdate the app?\n(App will restart with the new version)",
        "no_updates_title": "No Updates",
        "no_updates_text": "You have the latest version (v{v}).",
        "update_error_title": "Check Error",
        "update_error_text": "Failed to check updates:\n{err}",
        "update_close_title": "Update",
        "update_close_text": "The app will close and restart with the new version.",
        "update_apply_error": "Failed to apply update:\n{e}\n\nDetails in console.",
        "ok": "OK",
        "cancel": "Cancel",
        "save": "Save",
        "file_open": "📂 Open",
        "file_show": "📁 Show in folder",
        "file_delete": "🗑 Delete",
    }
}

# Доступные цвета тулбара
TOOLBAR_COLORS = {
    "Тёмный (по умолчанию)": "#202123",
    "Синий": "#1a3a6e",
    "Зелёный": "#1a5a2a",
    "Красный": "#6e1a1a",
    "Фиолетовый": "#4a1a6e",
    "Оранжевый": "#6e4a1a",
    "Розовый": "#6e1a4a",
    "Бирюзовый": "#1a6e6e",
}

TOOLBAR_COLORS_EN = {
    "Dark (default)": "#202123",
    "Blue": "#1a3a6e",
    "Green": "#1a5a2a",
    "Red": "#6e1a1a",
    "Purple": "#4a1a6e",
    "Orange": "#6e4a1a",
    "Pink": "#6e1a4a",
    "Teal": "#1a6e6e",
}


# ---------- ПУТИ ----------
APP_DIR = os.path.join(os.path.expanduser("~"), ".deepseek_app")
DOWNLOADS_DIR = os.path.join(APP_DIR, "downloads")
STORAGE_DIR = os.path.join(APP_DIR, "storage")
CACHE_DIR = os.path.join(APP_DIR, "cache")
ICON_PATH = os.path.join(APP_DIR, "icon.png")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

ICON_URL = "https://avatars.mds.yandex.net/i?id=4fb8d73655c6808470befa2458d32f00_l-5279811-images-thumbs&n=13"

if getattr(sys, 'frozen', False):
    SCRIPT_PATH = sys.executable
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_PATH = os.path.abspath(__file__)
    SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

SCRIPT_NAME = os.path.basename(SCRIPT_PATH)

BAT_PATH = os.path.join(SCRIPT_DIR, "update.bat")
NEW_CODE_PATH = os.path.join(SCRIPT_DIR, "deepseek_new.py")

# Глобальные настройки (загружаются позже)
settings = QSettings("DeepSeekApp", "Config")

# Текущий язык
current_lang = settings.value("language", "ru")
if current_lang not in TRANSLATIONS:
    current_lang = "ru"

# Текущий цвет тулбара
current_color_hex = settings.value("toolbar_color", "#202123")


def t(key):
    """Перевод по ключу."""
    return TRANSLATIONS.get(current_lang, TRANSLATIONS["ru"]).get(key, key)


print(f"Папка приложения: {APP_DIR}")
print(f"Загрузки: {DOWNLOADS_DIR}")
print(f"Файл приложения: {SCRIPT_PATH}")
print(f"Текущая версия: {CURRENT_VERSION}")
print(f"Язык: {current_lang}")


# ============================================================
# ПАРСИНГ ФОРМАТА ПАСТЫ
# ============================================================
def parse_paste(content):
    version_match = re.search(r'^\s*vers\s+(\d+)\s*$', content, re.MULTILINE)
    if not version_match:
        return None, None
    version = int(version_match.group(1))

    code_match = re.search(r'^\s*code\s*$', content, re.MULTILINE)
    if not code_match:
        return None, None

    code = content[code_match.end():].lstrip('\n')
    if len(code) < 100:
        return None, None

    return version, code


# ============================================================
# ПРОВЕРКА БАТНИКА ПРИ СТАРТЕ
# ============================================================
def check_pending_update():
    if os.path.exists(BAT_PATH):
        print(f"[обновление] Найден update.bat — применяю")
        try:
            if sys.platform == "win32":
                os.startfile(BAT_PATH)
            else:
                subprocess.Popen(["/bin/bash", BAT_PATH])
            print("[обновление] Батник запущен, закрываюсь")
            sys.exit(0)
        except Exception as e:
            print(f"[обновление] Ошибка запуска батника: {e}")
            try:
                os.remove(BAT_PATH)
            except Exception:
                pass


check_pending_update()


# ---------- ПОТОК ПРОВЕРКИ + СКАЧИВАНИЯ ----------
class UpdateChecker(QThread):
    update_available = Signal(int, str)
    no_update = Signal()
    error = Signal(str)

    def run(self):
        try:
            url = UPDATE_URL + "?t=" + str(int(datetime.now().timestamp()))
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode("utf-8")

            remote_version, new_code = parse_paste(content)
            if remote_version is None:
                self.error.emit("Не удалось распарсить файл (нужны строки 'vers N' и 'code')")
                return

            print(f"[обновление] Версия с GitHub: {remote_version}")
            print(f"[обновление] Длина кода: {len(new_code)} символов")

            if remote_version > CURRENT_VERSION:
                self.update_available.emit(remote_version, new_code)
            else:
                self.no_update.emit()

        except Exception as e:
            self.error.emit(str(e))


# ---------- ИКОНКА ----------
def generate_default_icon(path):
    pixmap = QPixmap(256, 256)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    from PySide6.QtGui import QRadialGradient
    gradient = QRadialGradient(128, 100, 150)
    gradient.setColorAt(0, QColor(90, 160, 255))
    gradient.setColorAt(1, QColor(30, 90, 200))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(10, 10, 236, 236)

    painter.setPen(QPen(QColor(255, 255, 255)))
    font = QFont("Arial", 130, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "D")

    painter.end()
    pixmap.save(path, "PNG")


def ensure_icon():
    if os.path.exists(ICON_PATH) and os.path.getsize(ICON_PATH) > 0:
        return
    try:
        req = urllib.request.Request(ICON_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            if len(data) > 0:
                with open(ICON_PATH, "wb") as f:
                    f.write(data)
                return
    except Exception as e:
        print(f"Не удалось скачать иконку: {e}")
    generate_default_icon(ICON_PATH)


ensure_icon()


# ---------- ВНЕШНЯЯ СТРАНИЦА ----------
class ExternalPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.urlChanged.connect(self.open_external)

    def open_external(self, url):
        if url.isValid():
            QDesktopServices.openUrl(url)
        self.deleteLater()


# ---------- СТРАНИЦА ----------
class MyPage(QWebEnginePage):
    def certificateError(self, error: QWebEngineCertificateError) -> bool:
        print(f"Игнорирую ошибку сертификата: {error.description()}")
        return True

    def javaScriptConsoleMessage(self, level, message, line, source):
        print(f"[JS] {message} (строка {line})")

    def featurePermissionRequested(self, securityOrigin, feature):
        if feature in (
            QWebEnginePage.Feature.ClipboardReadWrite,
            QWebEnginePage.Feature.ClipboardSanitizedWrite,
        ):
            self.setFeaturePermission(
                securityOrigin, feature,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )
        else:
            self.setFeaturePermission(
                securityOrigin, feature,
                QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
            )

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            host = url.host()
            if "deepseek.com" not in host and host != "":
                QDesktopServices.openUrl(url)
                return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def createWindow(self, _type):
        return ExternalPage(self.profile(), self)


# ---------- ОКНО НАСТРОЕК ----------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("settings_title"))
        self.resize(450, 250)

        self.setStyleSheet("""
            QDialog {
                background: #2a2a2a;
                color: #ddd;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { color: #ddd; font-size: 13px; }
            QComboBox {
                background: #3a3a3a; color: #fff;
                border: 1px solid #555; border-radius: 6px;
                padding: 8px 12px; font-size: 13px; min-height: 20px;
            }
            QComboBox:hover { border: 1px solid #4a90e2; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView {
                background: #3a3a3a; color: #fff;
                selection-background-color: #4a90e2;
                border: 1px solid #555;
            }
            QPushButton {
                background: #4a90e2; color: #fff;
                border: none; border-radius: 6px;
                padding: 8px 16px; font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover { background: #5eb3ff; }
            QPushButton:pressed { background: #3a7ac2; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        form = QFormLayout()
        form.setSpacing(15)

        # Выбор языка
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🇷🇺 Русский", "ru")
        self.lang_combo.addItem("🇬🇧 English", "en")

        # Устанавливаем текущий язык
        idx = self.lang_combo.findData(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

        form.addRow(t("language"), self.lang_combo)

        # Выбор цвета тулбара
        self.color_combo = QComboBox()
        colors_dict = TOOLBAR_COLORS if current_lang == "ru" else TOOLBAR_COLORS_EN
        for name, hex_color in colors_dict.items():
            self.color_combo.addItem(name, hex_color)

        # Устанавливаем текущий цвет
        idx = self.color_combo.findData(current_color_hex)
        if idx >= 0:
            self.color_combo.setCurrentIndex(idx)

        form.addRow(t("toolbar_color"), self.color_combo)

        layout.addLayout(form)
        layout.addStretch()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton(t("save"))
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton(t("cancel"))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #555; color: #fff;
                border: none; border-radius: 6px;
                padding: 8px 16px; font-size: 13px; min-width: 100px;
            }
            QPushButton:hover { background: #666; }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def get_language(self):
        return self.lang_combo.currentData()

    def get_color(self):
        return self.color_combo.currentData()


# ---------- КАРТОЧКА ФАЙЛА ----------
class FileCardWidget(QWidget):
    def __init__(self, filename, meta, path, is_downloading=False, parent=None):
        super().__init__(parent)
        self.file_path = path
        self.setStyleSheet("""
            FileCardWidget {
                background: #2a2a2a;
                border-radius: 8px;
            }
            FileCardWidget:hover {
                background: #333333;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        self.setLayout(layout)

        icon_label = QLabel("📥" if is_downloading else "📄")
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setFixedWidth(32)
        layout.addWidget(icon_label)

        info = QVBoxLayout()
        info.setSpacing(2)

        name_label = QLabel(filename)
        name_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold;")
        info.addWidget(name_label)

        meta_label = QLabel(meta)
        meta_label.setStyleSheet("color: #888; font-size: 11px;")
        info.addWidget(meta_label)

        layout.addLayout(info)
        layout.addStretch()


# ---------- СПИСОК ФАЙЛОВ ----------
class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item is None:
            return
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if not file_path or not os.path.exists(file_path):
            return

        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(file_path)])
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)


# ---------- ОКНО ЗАГРУЗОК ----------
class DownloadsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("downloads_title"))
        self.resize(700, 550)
        self.downloads = {}

        self.setStyleSheet("""
            QWidget {
                background: #1e1e1e;
                color: #ddd;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { color: #ddd; }
            QPushButton {
                background: #333; color: #fff;
                border: none; border-radius: 6px;
                padding: 8px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #444; }
            QPushButton:pressed { background: #555; }
            QListWidget {
                background: #1e1e1e; border: none; outline: none;
            }
            QListWidget::item {
                background: transparent; border: none; padding: 0px;
            }
            QListWidget::item:selected { background: transparent; }
            QProgressBar {
                background: #2a2a2a; border: none; border-radius: 4px;
                height: 8px; text-align: center; color: transparent;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a90e2, stop:1 #5eb3ff);
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.setLayout(layout)

        header = QHBoxLayout()
        title = QLabel(t("downloads_title"))
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #fff;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton(t("refresh"))
        refresh_btn.setFixedSize(36, 36)
        refresh_btn.clicked.connect(self.refresh_from_folder)
        header.addWidget(refresh_btn)

        open_btn = QPushButton(t("open_folder"))
        open_btn.clicked.connect(self.open_downloads_folder)
        header.addWidget(open_btn)

        clear_btn = QPushButton(t("clear"))
        clear_btn.setFixedSize(36, 36)
        clear_btn.clicked.connect(self.clear_list)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        path_frame = QFrame()
        path_frame.setStyleSheet("background: #252525; border-radius: 6px; padding: 8px;")
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(10, 6, 10, 6)
        path_frame.setLayout(path_layout)

        path_icon = QLabel("📁")
        path_icon.setStyleSheet("font-size: 14px;")
        path_layout.addWidget(path_icon)

        path_label = QLabel(DOWNLOADS_DIR)
        path_label.setStyleSheet("color: #888; font-size: 11px;")
        path_label.setWordWrap(True)
        path_layout.addWidget(path_label, 1)

        layout.addWidget(path_frame)

        self.list_widget = FileListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_click)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget, 1)

        self.progress_container = QFrame()
        self.progress_container.setStyleSheet("background: #252525; border-radius: 8px; padding: 8px;")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(10, 8, 10, 8)
        progress_layout.setSpacing(6)
        self.progress_container.setLayout(progress_layout)

        self.progress_label = QLabel(t("downloads_empty"))
        self.progress_label.setStyleSheet("color: #888; font-size: 11px;")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_container.setVisible(False)
        layout.addWidget(self.progress_container)

        self.refresh_from_folder()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_from_folder()

    def refresh_from_folder(self):
        self.list_widget.clear()
        self.downloads.clear()

        if not os.path.exists(DOWNLOADS_DIR):
            return

        files = []
        for f in os.listdir(DOWNLOADS_DIR):
            full_path = os.path.join(DOWNLOADS_DIR, f)
            if os.path.isfile(full_path):
                files.append((full_path, os.path.getmtime(full_path)))

        files.sort(key=lambda x: x[1], reverse=True)
        for path, mtime in files:
            self.add_file_to_list(path)

    def add_file_to_list(self, path):
        filename = os.path.basename(path)
        size = os.path.getsize(path)
        size_str = self.format_size(size)
        date_str = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d.%m.%Y %H:%M")

        card = FileCardWidget(filename, f"{size_str}  •  {date_str}", path, is_downloading=False)
        item = QListWidgetItem(self.list_widget)
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setSizeHint(QSize(0, 60))

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, card)

    def on_item_double_click(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path and os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #2a2a2a; color: #ddd;
                border: 1px solid #444; border-radius: 6px; padding: 4px;
            }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background: #444; }
        """)

        open_action = menu.addAction(t("file_open"))
        folder_action = menu.addAction(t("file_show"))
        menu.addSeparator()
        delete_action = menu.addAction(t("file_delete"))

        action = menu.exec(self.list_widget.mapToGlobal(pos))

        if action == open_action:
            self.on_item_double_click(item)
        elif action == folder_action:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        elif action == delete_action:
            reply = QMessageBox.question(
                self, "?", f"{os.path.basename(path)}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(path)
                    self.list_widget.takeItem(self.list_widget.row(item))
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"{e}")

    def add_download(self, download: QWebEngineDownloadRequest, path: str):
        filename = os.path.basename(path)

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == path:
                self.list_widget.takeItem(i)
                break

        card = FileCardWidget(filename, t("download_in_progress"), path, is_downloading=True)
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setSizeHint(QSize(0, 60))
        self.list_widget.insertItem(0, item)
        self.list_widget.setItemWidget(item, card)

        self.downloads[download] = (item, card, path)

        self.progress_container.setVisible(True)
        self.progress_label.setText(f"📥 {filename}")

        download.receivedBytesChanged.connect(lambda d=download: self.update_progress(d))
        download.isFinishedChanged.connect(lambda d=download: self.finish_download(d))

    def update_progress(self, download):
        if download in self.downloads:
            item, card, path = self.downloads[download]
            received = download.receivedBytes()
            total = download.totalBytes()

            if total > 0:
                percent = int(received * 100 / total)
                self.progress_bar.setValue(percent)

                info_layout = card.layout().itemAt(1).layout()
                if info_layout and info_layout.count() >= 2:
                    meta = info_layout.itemAt(1).widget()
                    if meta:
                        meta.setText(
                            f"{self.format_size(received)} / "
                            f"{self.format_size(total)}  •  {percent}%"
                        )

    def finish_download(self, download):
        if download in self.downloads:
            item, card, path = self.downloads[download]
            if download.isFinished():
                total = download.totalBytes()

                info_layout = card.layout().itemAt(1).layout()
                if info_layout and info_layout.count() >= 2:
                    meta = info_layout.itemAt(1).widget()
                    if meta:
                        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                        meta.setText(f"{self.format_size(total)}  •  {date_str}")

                icon_label = card.layout().itemAt(0).widget()
                if icon_label:
                    icon_label.setText("📄")

                self.progress_container.setVisible(False)
                self.progress_label.setText(t("downloads_done"))

    def format_size(self, bytes_size):
        if bytes_size < 1024:
            return f"{bytes_size} Б"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} КБ"
        else:
            return f"{bytes_size / (1024 * 1024):.1f} МБ"

    def open_downloads_folder(self):
        if sys.platform == "win32":
            os.startfile(DOWNLOADS_DIR)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", DOWNLOADS_DIR])
        else:
            subprocess.Popen(["xdg-open", DOWNLOADS_DIR])

    def clear_list(self):
        self.list_widget.clear()
        self.downloads.clear()
        self.progress_container.setVisible(False)


# ---------- ГЛАВНОЕ ОКНО ----------
class DeepSeekApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")
        self.resize(1200, 800)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.settings = QSettings("DeepSeekApp", "Config")

        # Профиль
        self.profile = QWebEngineProfile("deepseek_profile_main", self)
        self.profile.setPersistentStoragePath(STORAGE_DIR)
        self.profile.setCachePath(CACHE_DIR)
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.downloadRequested.connect(self.on_download_requested)

        self.download_window = DownloadsWindow()
        self.download_count = 0

        # Страница
        self.page = MyPage(self.profile, self)
        settings_q = self.page.settings()
        settings_q.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings_q.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings_q.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)
        settings_q.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings_q.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Браузер
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl("https://chat.deepseek.com/"))
        self.setCentralWidget(self.browser)
        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

        # Тулбар
        self.toolbar = None
        self.toolbar_actions = {}
        self.setup_toolbar()

        # Горячие клавиши
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(
            lambda: self.page.triggerAction(QWebEnginePage.WebAction.Copy)
        )
        QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(
            lambda: self.page.triggerAction(QWebEnginePage.WebAction.Paste)
        )
        QShortcut(QKeySequence("Ctrl+X"), self).activated.connect(
            lambda: self.page.triggerAction(QWebEnginePage.WebAction.Cut)
        )
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(
            lambda: self.page.triggerAction(QWebEnginePage.WebAction.SelectAll)
        )
        QShortcut(QKeySequence("Ctrl+J"), self).activated.connect(self.show_downloads)

        # Автопроверка обновлений через 3 секунды
        QTimer.singleShot(3000, lambda: self.check_updates(manual=False))

    def setup_toolbar(self):
        self.toolbar = QToolBar("Панель")
        self.toolbar.setMovable(False)
        self.apply_toolbar_style()

        self.addToolBar(self.toolbar)

        # Кнопки тулбара (сохраняем ссылки, чтобы менять текст при смене языка)
        self.toolbar_actions["downloads"] = QAction(f"{t('downloads')} (0)", self)
        self.toolbar_actions["downloads"].triggered.connect(self.show_downloads)
        self.toolbar.addAction(self.toolbar_actions["downloads"])

        self.toolbar_actions["folder"] = QAction(t("downloads_folder"), self)
        self.toolbar_actions["folder"].triggered.connect(self.open_downloads_folder)
        self.toolbar.addAction(self.toolbar_actions["folder"])

        self.toolbar_actions["back"] = QAction(t("back"), self)
        self.toolbar_actions["back"].triggered.connect(self.browser.back)
        self.toolbar.addAction(self.toolbar_actions["back"])

        self.toolbar_actions["reload"] = QAction(t("reload"), self)
        self.toolbar_actions["reload"].triggered.connect(self.browser.reload)
        self.toolbar.addAction(self.toolbar_actions["reload"])

        self.toolbar_actions["home"] = QAction(t("home"), self)
        self.toolbar_actions["home"].triggered.connect(
            lambda: self.browser.setUrl(QUrl("https://chat.deepseek.com/"))
        )
        self.toolbar.addAction(self.toolbar_actions["home"])

        self.toolbar_actions["update"] = QAction(t("check_updates"), self)
        self.toolbar_actions["update"].triggered.connect(lambda: self.check_updates(manual=True))
        self.toolbar.addAction(self.toolbar_actions["update"])

        self.toolbar_actions["settings"] = QAction(t("settings"), self)
        self.toolbar_actions["settings"].triggered.connect(self.open_settings)
        self.toolbar.addAction(self.toolbar_actions["settings"])

    def apply_toolbar_style(self):
        """Применяет цвет тулбара."""
        self.toolbar.setStyleSheet(f"""
            QToolBar {{ background: {current_color_hex}; border-bottom: 1px solid #444; padding: 4px; }}
            QToolButton {{ color: #fff; padding: 6px 12px; border-radius: 4px; }}
            QToolButton:hover {{ background: #444; }}
        """)

    def refresh_toolbar_text(self):
        """Обновляет текст кнопок после смены языка."""
        self.toolbar_actions["downloads"].setText(f"{t('downloads')} ({self.download_count})")
        self.toolbar_actions["folder"].setText(t("downloads_folder"))
        self.toolbar_actions["back"].setText(t("back"))
        self.toolbar_actions["reload"].setText(t("reload"))
        self.toolbar_actions["home"].setText(t("home"))
        self.toolbar_actions["update"].setText(t("check_updates"))
        self.toolbar_actions["settings"].setText(t("settings"))

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_lang = dlg.get_language()
            new_color = dlg.get_color()

            self.settings.setValue("language", new_lang)
            self.settings.setValue("toolbar_color", new_color)

            # Применяем сразу
            global current_lang, current_color_hex
            current_lang = new_lang
            current_color_hex = new_color

            self.apply_toolbar_style()
            self.refresh_toolbar_text()

            QMessageBox.information(
                self, "OK" if current_lang == "en" else "Готово",
                "Settings saved. Some elements will update after restart."
                if current_lang == "en"
                else "Настройки сохранены. Некоторые элементы обновятся после перезапуска."
            )

    # ---------- ПРОВЕРКА ОБНОВЛЕНИЙ ----------
    def check_updates(self, manual=False):
        if manual:
            self.setWindowTitle("DeepSeek App — проверка обновлений...")

        self.update_checker = UpdateChecker()
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_update.connect(lambda: self.on_no_update(manual))
        self.update_checker.error.connect(lambda err: self.on_update_error(err, manual))
        self.update_checker.start()

    def on_update_available(self, new_version, new_code):
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")

        reply = QMessageBox.question(
            self,
            t("update_available_title"),
            t("update_available_text").format(v1=new_version, v2=CURRENT_VERSION),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.apply_update(new_code)

    def on_no_update(self, manual):
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")
        if manual:
            QMessageBox.information(
                self, t("no_updates_title"),
                t("no_updates_text").format(v=CURRENT_VERSION)
            )

    def on_update_error(self, err, manual):
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")
        print(f"[обновление] ошибка: {err}")
        if manual:
            QMessageBox.warning(
                self, t("update_error_title"),
                t("update_error_text").format(err=err)
            )

    def apply_update(self, new_code):
        print(f"[обновление] Применяю обновление, длина кода: {len(new_code)}")

        try:
            with open(NEW_CODE_PATH, "w", encoding="utf-8") as f:
                f.write(new_code)
            print(f"[обновление] Новый код сохранён: {NEW_CODE_PATH}")

            python_exe = sys.executable
            print(f"[обновление] Python: {python_exe}")

            bat_content = f'''@echo off
chcp 65001 > nul
timeout /t 3 /nobreak > nul
del "{SCRIPT_PATH}"
move "{NEW_CODE_PATH}" "{SCRIPT_PATH}"
start "" "{python_exe}" "{SCRIPT_PATH}"
del "%~f0"
'''
            with open(BAT_PATH, "w", encoding="cp866") as f:
                f.write(bat_content)

            print(f"[обновление] Батник создан: {BAT_PATH}")

            QMessageBox.information(self, t("update_close_title"), t("update_close_text"))

            if sys.platform == "win32":
                os.startfile(BAT_PATH)
            else:
                subprocess.Popen(["/bin/bash", BAT_PATH])

            QApplication.instance().quit()

        except Exception as e:
            import traceback
            print(f"[обновление] ОШИБКА:\n{traceback.format_exc()}")
            QMessageBox.critical(
                self, "Ошибка",
                t("update_apply_error").format(e=e)
            )

    # ---------- ОКНО ЗАГРУЗОК ----------
    def show_downloads(self):
        geom = self.settings.value("downloads_window_geometry")
        if geom:
            self.download_window.restoreGeometry(geom)

        self.download_window.show()
        self.download_window.raise_()
        self.download_window.activateWindow()
        self.download_window.refresh_from_folder()

    def open_downloads_folder(self):
        if sys.platform == "win32":
            os.startfile(DOWNLOADS_DIR)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", DOWNLOADS_DIR])
        else:
            subprocess.Popen(["xdg-open", DOWNLOADS_DIR])

    # ---------- ЗАГРУЗКИ ----------
    def on_download_requested(self, download: QWebEngineDownloadRequest):
        filename = download.downloadFileName() or "file"
        save_path = os.path.join(DOWNLOADS_DIR, filename)

        download.setDownloadDirectory(DOWNLOADS_DIR)
        download.setDownloadFileName(filename)
        download.accept()

        print(f"Скачивание: {filename} → {DOWNLOADS_DIR}")

        self.download_count += 1
        self.toolbar_actions["downloads"].setText(f"{t('downloads')} ({self.download_count})")

        self.download_window.add_download(download, save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    window = DeepSeekApp()
    window.show()
    sys.exit(app.exec())
