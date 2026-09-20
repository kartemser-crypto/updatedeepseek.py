vers 8

code

import sys
import os
import shutil
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
    QDialog, QComboBox, QFormLayout, QSplitter, QFileDialog,
    QCheckBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineCertificateError,
    QWebEngineDownloadRequest, QWebEngineSettings
)


# ============================================================
# НАСТРОЙКИ ОБНОВЛЕНИЙ
# ============================================================
CURRENT_VERSION = 8

UPDATE_URL = "https://raw.githubusercontent.com/kartemser-crypto/updatedeepseek.py/refs/heads/main/update.py"


# ---------- ЯЗЫКИ ----------
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
        "downloads_empty": "Нет загрузок",
        "downloads_done": "Загрузка завершена",
        "download_in_progress": "Загрузка...",
        "open_folder": "📂 Папка",
        "clear": "🗑",
        "refresh": "🔄",
        "settings_title": "⚙ Настройки",
        "language": "Язык интерфейса:",
        "toolbar_color": "Цвет полосы:",
        "downloads_panel_pos": "Панель загрузок:",
        "mods": "Моды (.py файлы):",
        "load_mod": "📂 Загрузить мод",
        "mods_empty": "Нет загруженных модов",
        "mod_run": "▶ Запустить",
        "mod_delete": "🗑 Удалить",
        "mod_show_folder": "📁 Показать в папке",
        "mod_activate": "✅ Активировать",
        "mod_deactivate": "⛔ Деактивировать",
        "mod_applied": "Мод применён!",
        "mod_error": "Ошибка в моде '{name}':\n{e}",
        "mod_loaded": "Мод загружен: {name}",
        "mod_deleted": "Мод удалён: {name}",
        "restart_needed_title": "Требуется перезагрузка",
        "restart_needed_text": "Изменения в модах вступят в силу после перезапуска приложения.\n\nПерезапустить сейчас?",
        "restart_now": "🔄 Перезапустить сейчас",
        "restart_later": "Позже",
        "restarting": "Перезапуск...",
        "update_available_title": "Доступно обновление",
        "update_available_text": "Найдена новая версия: v{v1}\nВаша версия: v{v2}\n\nОбновить приложение?\n(Приложение закроется и запустится с новой версией)",
        "no_updates_title": "Обновлений нет",
        "no_updates_text": "У вас последняя версия (v{v}).",
        "update_error_title": "Ошибка проверки",
        "update_error_text": "Не удалось проверить обновления:\n{err}",
        "update_close_title": "Обновление",
        "update_close_text": "Приложение закроется и запустится с новой версией.",
        "update_apply_error": "Не удалось применить обновление:\n{e}",
        "save": "Сохранить",
        "cancel": "Отмена",
        "file_open": "📂 Открыть",
        "file_show": "📁 Показать в папке",
        "file_delete": "🗑 Удалить",
    },
    "en": {
        "downloads": "⬇ Downloads",
        "downloads_folder": "📂 Folder",
        "back": "← Back",
        "reload": "↻ Reload",
        "home": "🏠 DeepSeek",
        "check_updates": "🔄 Check Updates",
        "settings": "⚙ Settings",
        "downloads_title": "📥 Downloads",
        "downloads_empty": "No downloads",
        "downloads_done": "Download complete",
        "download_in_progress": "Downloading...",
        "open_folder": "📂 Folder",
        "clear": "🗑",
        "refresh": "🔄",
        "settings_title": "⚙ Settings",
        "language": "Interface language:",
        "toolbar_color": "Toolbar color:",
        "downloads_panel_pos": "Downloads panel:",
        "mods": "Mods (.py files):",
        "load_mod": "📂 Load mod",
        "mods_empty": "No mods loaded",
        "mod_run": "▶ Run",
        "mod_delete": "🗑 Delete",
        "mod_show_folder": "📁 Show in folder",
        "mod_activate": "✅ Activate",
        "mod_deactivate": "⛔ Deactivate",
        "mod_applied": "Mod applied!",
        "mod_error": "Mod error '{name}':\n{e}",
        "mod_loaded": "Mod loaded: {name}",
        "mod_deleted": "Mod deleted: {name}",
        "restart_needed_title": "Restart required",
        "restart_needed_text": "Mod changes will take effect after restart.\n\nRestart now?",
        "restart_now": "🔄 Restart now",
        "restart_later": "Later",
        "restarting": "Restarting...",
        "update_available_title": "Update Available",
        "update_available_text": "New version: v{v1}\nYour version: v{v2}\n\nUpdate now?",
        "no_updates_title": "No Updates",
        "no_updates_text": "Latest version (v{v}).",
        "update_error_title": "Error",
        "update_error_text": "Failed to check updates:\n{err}",
        "update_close_title": "Update",
        "update_close_text": "The app will restart.",
        "update_apply_error": "Failed:\n{e}",
        "save": "Save",
        "cancel": "Cancel",
        "file_open": "📂 Open",
        "file_show": "📁 Show in folder",
        "file_delete": "🗑 Delete",
    }
}

TOOLBAR_COLORS = {
    "Тёмный (по умолчанию)": "#202123",
    "Белый": "#f0f0f0",
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
    "White": "#f0f0f0",
    "Blue": "#1a3a6e",
    "Green": "#1a5a2a",
    "Red": "#6e1a1a",
    "Purple": "#4a1a6e",
    "Orange": "#6e4a1a",
    "Pink": "#6e1a4a",
    "Teal": "#1a6e6e",
}

PANEL_POSITIONS = {
    "left": "Слева (закреплено)",
    "bottom": "Снизу (закреплено)",
    "floating": "Отдельное окно",
    "hidden": "Скрыта",
}

PANEL_POSITIONS_EN = {
    "left": "Left (docked)",
    "bottom": "Bottom (docked)",
    "floating": "Floating window",
    "hidden": "Hidden",
}


# ---------- ИКОНКИ ФАЙЛОВ ----------
def get_file_icon(filename):
    ext = os.path.splitext(filename.lower())[1]
    icons = {
        ".py": "🐍", ".bat": "⚙", ".cmd": "⚙", ".exe": "💻",
        ".txt": "📄", ".md": "📝", ".pdf": "📕",
        ".doc": "📘", ".docx": "📘", ".xls": "📗", ".xlsx": "📗",
        ".ppt": "📙", ".pptx": "📙",
        ".png": "🖼", ".jpg": "🖼", ".jpeg": "🖼", ".gif": "🖼",
        ".bmp": "🖼", ".webp": "🖼", ".svg": "🖼",
        ".mp3": "🎵", ".wav": "🎵", ".ogg": "🎵", ".flac": "🎵",
        ".mp4": "🎬", ".avi": "🎬", ".mkv": "🎬", ".mov": "🎬",
        ".zip": "📦", ".rar": "📦", ".7z": "📦", ".tar": "📦", ".gz": "📦",
        ".json": "🔧", ".xml": "📋", ".html": "🌐", ".htm": "🌐",
        ".css": "🎨", ".js": "📜", ".csv": "📊",
    }
    return icons.get(ext, "📄")


# ---------- ПУТИ ----------
APP_DIR = os.path.join(os.path.expanduser("~"), ".deepseek_app")
DOWNLOADS_DIR = os.path.join(APP_DIR, "downloads")
STORAGE_DIR = os.path.join(APP_DIR, "storage")
CACHE_DIR = os.path.join(APP_DIR, "cache")
MODS_DIR = os.path.join(APP_DIR, "mods")
MODS_CONFIG = os.path.join(MODS_DIR, "active.txt")  # список активных модов
ICON_PATH = os.path.join(APP_DIR, "icon.png")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODS_DIR, exist_ok=True)

ICON_URL = "https://avatars.mds.yandex.net/i?id=4fb8d73655c6808470befa2458d32f00_l-5279811-images-thumbs&n=13"

if getattr(sys, 'frozen', False):
    SCRIPT_PATH = sys.executable
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_PATH = os.path.abspath(__file__)
    SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)

BAT_PATH = os.path.join(SCRIPT_DIR, "update.bat")
RESTART_BAT_PATH = os.path.join(SCRIPT_DIR, "restart.bat")
NEW_CODE_PATH = os.path.join(SCRIPT_DIR, "deepseek_new.py")

settings = QSettings("DeepSeekApp", "Config")

current_lang = settings.value("language", "ru")
if current_lang not in TRANSLATIONS:
    current_lang = "ru"

current_color_hex = settings.value("toolbar_color", "#202123")

current_panel_pos = settings.value("panel_position", "left")
if current_panel_pos not in PANEL_POSITIONS:
    current_panel_pos = "left"


def t(key):
    return TRANSLATIONS.get(current_lang, TRANSLATIONS["ru"]).get(key, key)


# ---------- УПРАВЛЕНИЕ АКТИВНЫМИ МОДАМИ ----------
def load_active_mods():
    """Возвращает множество имён активных модов."""
    if not os.path.exists(MODS_CONFIG):
        return set()
    try:
        with open(MODS_CONFIG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception:
        return set()


def save_active_mods(active_set):
    """Сохраняет список активных модов."""
    try:
        with open(MODS_CONFIG, "w", encoding="utf-8") as f:
            for name in sorted(active_set):
                f.write(name + "\n")
    except Exception as e:
        print(f"[моды] Ошибка сохранения: {e}")


def run_mod_file(file_path, app_instance):
    """Запускает .py файл мода. Возвращает (успех, ошибка)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return False, f"Не удалось прочитать: {e}"

    try:
        exec_globals = {
            "app": app_instance,
            "window": app_instance,
            "settings": settings,
            "print": print,
            "QMessageBox": QMessageBox,
            "QAction": QAction,
            "__file__": file_path,
            "__name__": "__mod__",
        }
        exec(code, exec_globals)
        return True, None
    except Exception as e:
        import traceback
        return False, traceback.format_exc()


print(f"Папка приложения: {APP_DIR}")
print(f"Загрузки: {DOWNLOADS_DIR}")
print(f"Моды: {MODS_DIR}")
print(f"Текущая версия: {CURRENT_VERSION}")


# ============================================================
# ПАРСИНГ
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
# БАТНИК ПРИ СТАРТЕ
# ============================================================
def check_pending_update():
    if os.path.exists(BAT_PATH):
        print(f"[обновление] Найден update.bat")
        try:
            if sys.platform == "win32":
                os.startfile(BAT_PATH)
            else:
                subprocess.Popen(["/bin/bash", BAT_PATH])
            sys.exit(0)
        except Exception as e:
            print(f"[обновление] Ошибка: {e}")
            try:
                os.remove(BAT_PATH)
            except Exception:
                pass


check_pending_update()


# ---------- ПОТОК ПРОВЕРКИ ----------
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
                self.error.emit("Не удалось распарсить файл")
                return

            print(f"[обновление] Версия с GitHub: {remote_version}")

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


# ---------- ПЕРЕЗАПУСК ПРИЛОЖЕНИЯ ----------
def restart_application():
    """Перезапускает приложение через временный bat-файл."""
    try:
        python_exe = sys.executable

        bat_content = f'''@echo off
chcp 65001 > nul
timeout /t 2 /nobreak > nul
start "" "{python_exe}" "{SCRIPT_PATH}"
del "%~f0"
'''
        with open(RESTART_BAT_PATH, "w", encoding="cp866") as f:
            f.write(bat_content)

        if sys.platform == "win32":
            os.startfile(RESTART_BAT_PATH)
        else:
            subprocess.Popen(["/bin/bash", RESTART_BAT_PATH])

        QApplication.instance().quit()
        return True
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Не удалось перезапустить:\n{e}")
        return False


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
        return True

    def javaScriptConsoleMessage(self, level, message, line, source):
        pass

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


# ---------- МОД-КАРТОЧКА (в списке) ----------
class ModItemWidget(QWidget):
    """Виджет-карточка мода с чекбоксом."""
    def __init__(self, filename, file_path, active=False, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.file_path = file_path
        self.setStyleSheet("""
            ModItemWidget { background: #2a2a2a; border-radius: 6px; }
            ModItemWidget:hover { background: #333; }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(active)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 2px solid #666; border-radius: 4px;
                background: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background: #4a90e2; border: 2px solid #4a90e2;
            }
        """)
        layout.addWidget(self.checkbox)

        icon_label = QLabel("🐍")
        icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_label)

        name_label = QLabel(filename)
        name_label.setStyleSheet("color: #fff; font-size: 12px;")
        layout.addWidget(name_label, 1)


# ---------- ОКНО НАСТРОЕК ----------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("settings_title"))
        self.resize(600, 620)

        # Флаг: были ли изменения в модах (активация/деактивация/загрузка/удаление)
        self.mods_changed = False

        self.setStyleSheet("""
            QDialog { background: #2a2a2a; color: #ddd; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: #ddd; font-size: 13px; }
            QComboBox {
                background: #3a3a3a; color: #fff;
                border: 1px solid #555; border-radius: 6px;
                padding: 8px 12px; font-size: 13px; min-height: 20px;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QPushButton {
                background: #4a90e2; color: #fff;
                border: none; border-radius: 6px;
                padding: 8px 16px; font-size: 13px; min-width: 100px;
            }
            QPushButton:hover { background: #5eb3ff; }
            QListWidget {
                background: #1e1e1e; border: 1px solid #444;
                border-radius: 6px; outline: none;
            }
            QListWidget::item {
                background: transparent; border: none; padding: 0px;
            }
            QListWidget::item:selected { background: transparent; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        self.setLayout(layout)

        form = QFormLayout()
        form.setSpacing(10)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🇷🇺 Русский", "ru")
        self.lang_combo.addItem("🇬🇧 English", "en")
        idx = self.lang_combo.findData(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        form.addRow(t("language"), self.lang_combo)

        self.color_combo = QComboBox()
        colors_dict = TOOLBAR_COLORS if current_lang == "ru" else TOOLBAR_COLORS_EN
        for name, hex_color in colors_dict.items():
            self.color_combo.addItem(name, hex_color)
        idx = self.color_combo.findData(current_color_hex)
        if idx >= 0:
            self.color_combo.setCurrentIndex(idx)
        form.addRow(t("toolbar_color"), self.color_combo)

        self.panel_combo = QComboBox()
        positions_dict = PANEL_POSITIONS if current_lang == "ru" else PANEL_POSITIONS_EN
        for key, label in positions_dict.items():
            self.panel_combo.addItem(label, key)
        idx = self.panel_combo.findData(current_panel_pos)
        if idx >= 0:
            self.panel_combo.setCurrentIndex(idx)
        form.addRow(t("downloads_panel_pos"), self.panel_combo)

        layout.addLayout(form)

        # ---- МОДЫ ----
        mods_label = QLabel(t("mods"))
        mods_label.setStyleSheet("font-size: 13px; padding-top: 6px; font-weight: bold;")
        layout.addWidget(mods_label)

        # Кнопка "Загрузить мод"
        load_mod_btn = QPushButton(t("load_mod"))
        load_mod_btn.clicked.connect(self.load_mod_file)
        layout.addWidget(load_mod_btn)

        # Список модов
        self.mods_list = QListWidget()
        self.mods_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.mods_list.customContextMenuRequested.connect(self.show_mod_context_menu)
        self.mods_list.itemClicked.connect(self.on_mod_clicked)
        layout.addWidget(self.mods_list, 1)

        # Загружаем список модов
        self.refresh_mods_list()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton(t("cancel"))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #555; color: #fff;
                border: none; border-radius: 6px;
                padding: 8px 16px; font-size: 13px; min-width: 100px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton(t("save"))
        save_btn.clicked.connect(self.on_save_clicked)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def on_save_clicked(self):
        """Сохраняет настройки и предлагает перезапуск, если моды изменились."""
        self.accept()

        # После accept диалог закрывается, показываем запрос на перезапуск
        if self.mods_changed:
            reply = QMessageBox.question(
                self.parent(),
                t("restart_needed_title"),
                t("restart_needed_text"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                restart_application()

    def refresh_mods_list(self):
        """Обновляет список модов из папки MODS_DIR."""
        self.mods_list.clear()
        active = load_active_mods()

        if not os.path.exists(MODS_DIR):
            return

        mods = []
        for f in os.listdir(MODS_DIR):
            if f.endswith(".py"):
                mods.append(f)

        mods.sort()

        if not mods:
            item = QListWidgetItem(t("mods_empty"))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.mods_list.addItem(item)
            return

        for filename in mods:
            file_path = os.path.join(MODS_DIR, filename)
            is_active = filename in active

            widget = ModItemWidget(filename, file_path, active=is_active)
            widget.checkbox.stateChanged.connect(
                lambda state, fn=filename: self.on_mod_toggle(fn, state)
            )

            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, filename)
            item.setSizeHint(QSize(0, 36))
            self.mods_list.addItem(item)
            self.mods_list.setItemWidget(item, widget)

    def on_mod_toggle(self, filename, state):
        """Обработчик чекбокса активации мода."""
        active = load_active_mods()
        if state == Qt.CheckState.Checked.value or state == 2:
            if filename not in active:
                active.add(filename)
                self.mods_changed = True
        else:
            if filename in active:
                active.discard(filename)
                self.mods_changed = True
        save_active_mods(active)

    def on_mod_clicked(self, item):
        """Клик по моду — переключение чекбокса."""
        filename = item.data(Qt.ItemDataRole.UserRole)
        if not filename:
            return
        widget = self.mods_list.itemWidget(item)
        if widget and hasattr(widget, "checkbox"):
            widget.checkbox.toggle()

    def show_mod_context_menu(self, pos):
        """ПКМ по моду — меню действий."""
        item = self.mods_list.itemAt(pos)
        if item is None:
            return
        filename = item.data(Qt.ItemDataRole.UserRole)
        if not filename:
            return

        file_path = os.path.join(MODS_DIR, filename)
        active = load_active_mods()
        is_active = filename in active

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: #2a2a2a; color: #ddd; border: 1px solid #444; border-radius: 6px; padding: 4px; }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background: #444; }
        """)

        if is_active:
            toggle_action = menu.addAction(t("mod_deactivate"))
        else:
            toggle_action = menu.addAction(t("mod_activate"))

        run_action = menu.addAction(t("mod_run"))
        show_action = menu.addAction(t("mod_show_folder"))
        menu.addSeparator()
        delete_action = menu.addAction(t("mod_delete"))

        action = menu.exec(self.mods_list.mapToGlobal(pos))

        if action == toggle_action:
            if is_active:
                active.discard(filename)
            else:
                active.add(filename)
            save_active_mods(active)
            self.mods_changed = True
            self.refresh_mods_list()

        elif action == run_action:
            app_instance = self.parent()
            ok, err = run_mod_file(file_path, app_instance)
            if ok:
                QMessageBox.information(self, "Мод", t("mod_applied"))
            else:
                QMessageBox.critical(self, "Ошибка мода", err)

        elif action == show_action:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(file_path)])

        elif action == delete_action:
            reply = QMessageBox.question(
                self, "?", f"{filename}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(file_path)
                    active.discard(filename)
                    save_active_mods(active)
                    self.mods_changed = True
                    self.refresh_mods_list()
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"{e}")

    def load_mod_file(self):
        """Загружает .py файл мода (копирует в папку модов)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, t("load_mod"),
            os.path.expanduser("~"),
            "Python файлы (*.py);;Все файлы (*.*)"
        )
        if not file_path:
            return

        filename = os.path.basename(file_path)
        dest_path = os.path.join(MODS_DIR, filename)

        try:
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.copy2(file_path, dest_path)
            self.mods_changed = True
            self.refresh_mods_list()
            QMessageBox.information(self, "OK", t("mod_loaded").format(name=filename))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить:\n{e}")

    def get_language(self):
        return self.lang_combo.currentData()

    def get_color(self):
        return self.color_combo.currentData()

    def get_panel_pos(self):
        return self.panel_combo.currentData()


# ---------- КАРТОЧКА ФАЙЛА ----------
class FileCardWidget(QWidget):
    def __init__(self, filename, meta, path, is_downloading=False, parent=None):
        super().__init__(parent)
        self.file_path = path
        self.setStyleSheet("""
            FileCardWidget { background: #2a2a2a; border-radius: 8px; }
            FileCardWidget:hover { background: #333333; }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        self.setLayout(layout)

        icon_text = "📥" if is_downloading else get_file_icon(filename)
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 22px;")
        icon_label.setFixedWidth(28)
        layout.addWidget(icon_label)

        info = QVBoxLayout()
        info.setSpacing(2)

        name_label = QLabel(filename)
        name_label.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold;")
        name_label.setWordWrap(True)
        info.addWidget(name_label)

        meta_label = QLabel(meta)
        meta_label.setStyleSheet("color: #888; font-size: 10px;")
        meta_label.setWordWrap(True)
        info.addWidget(meta_label)

        layout.addLayout(info)
        layout.addStretch()


# ---------- СПИСОК ФАЙЛОВ (drag-and-drop) ----------
class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)

    def startDrag(self, supportedActions):
        items = self.selectedItems()
        if not items:
            return

        mime_data = QMimeData()
        urls = []
        for item in items:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path and os.path.exists(file_path):
                urls.append(QUrl.fromLocalFile(file_path))

        if not urls:
            return

        mime_data.setUrls(urls)

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI Emoji", 32))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "📄")
        painter.end()
        drag.setPixmap(pixmap)

        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)


# ---------- ПАНЕЛЬ ЗАГРУЗОК ----------
class DownloadsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloads = {}
        self.setMinimumWidth(250)

        self.setStyleSheet("""
            QWidget { background: #1e1e1e; color: #ddd; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: #ddd; }
            QPushButton {
                background: #333; color: #fff;
                border: none; border-radius: 6px;
                padding: 6px 10px; font-size: 11px;
            }
            QPushButton:hover { background: #444; }
            QListWidget { background: #1e1e1e; border: none; outline: none; }
            QListWidget::item { background: transparent; border: none; padding: 0px; }
            QListWidget::item:selected { background: #333; border-radius: 6px; }
            QProgressBar {
                background: #2a2a2a; border: none; border-radius: 4px;
                height: 6px; text-align: center; color: transparent;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a90e2, stop:1 #5eb3ff);
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)

        header = QHBoxLayout()

        title = QLabel(t("downloads_title"))
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton(t("refresh"))
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setToolTip("Обновить")
        refresh_btn.clicked.connect(self.refresh_from_folder)
        header.addWidget(refresh_btn)

        clear_btn = QPushButton(t("clear"))
        clear_btn.setFixedSize(30, 30)
        clear_btn.setToolTip("Очистить список")
        clear_btn.clicked.connect(self.clear_list)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        open_btn = QPushButton(t("open_folder"))
        open_btn.clicked.connect(self.open_downloads_folder)
        layout.addWidget(open_btn)

        self.list_widget = FileListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_click)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget, 1)

        self.progress_container = QFrame()
        self.progress_container.setStyleSheet("background: #252525; border-radius: 6px; padding: 6px;")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(8, 6, 8, 6)
        progress_layout.setSpacing(4)
        self.progress_container.setLayout(progress_layout)

        self.progress_label = QLabel(t("downloads_empty"))
        self.progress_label.setStyleSheet("color: #888; font-size: 10px;")
        self.progress_label.setWordWrap(True)
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_container.setVisible(False)
        layout.addWidget(self.progress_container)

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
        date_str = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d.%m %H:%M")

        card = FileCardWidget(filename, f"{size_str}  •  {date_str}", path, is_downloading=False)
        item = QListWidgetItem(self.list_widget)
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setSizeHint(QSize(0, 50))

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
            QMenu { background: #2a2a2a; color: #ddd; border: 1px solid #444; border-radius: 6px; padding: 4px; }
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
        item.setSizeHint(QSize(0, 50))
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
                filename = os.path.basename(path)

                icon_label = card.layout().itemAt(0).widget()
                if icon_label:
                    icon_label.setText(get_file_icon(filename))

                info_layout = card.layout().itemAt(1).layout()
                if info_layout and info_layout.count() >= 2:
                    meta = info_layout.itemAt(1).widget()
                    if meta:
                        date_str = datetime.now().strftime("%d.%m %H:%M")
                        meta.setText(f"{self.format_size(total)}  •  {date_str}")

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
        self.resize(1400, 850)

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
        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

        # Панель загрузок
        self.downloads_panel = DownloadsPanel(self)
        self.downloads_panel.setVisible(False)

        # Сплиттер
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle { background: #333; width: 4px; height: 4px; }
            QSplitter::handle:hover { background: #4a90e2; }
        """)

        # Применяем позицию панели
        self.apply_panel_position(current_panel_pos)

        # Тулбар
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
        QShortcut(QKeySequence("Ctrl+J"), self).activated.connect(self.toggle_downloads)

        # Автопроверка обновлений
        QTimer.singleShot(3000, lambda: self.check_updates(manual=False))

        # Автозагрузка активных модов через 1 секунду
        QTimer.singleShot(1000, self.load_active_mods_on_start)

    def load_active_mods_on_start(self):
        """Запускает все активные моды при старте."""
        active = load_active_mods()
        if not active:
            return

        print(f"[моды] Активированных модов: {len(active)}")
        for mod_name in active:
            mod_path = os.path.join(MODS_DIR, mod_name)
            if not os.path.exists(mod_path):
                print(f"[моды] Не найден: {mod_name}")
                continue

            print(f"[моды] Запускаю: {mod_name}")
            ok, err = run_mod_file(mod_path, self)
            if ok:
                print(f"[моды] ✅ {mod_name} загружен")
            else:
                print(f"[моды] ❌ {mod_name}:\n{err}")

    def apply_panel_position(self, pos):
        """Применяет позицию панели загрузок."""
        global current_panel_pos
        current_panel_pos = pos

        while self.splitter.count() > 0:
            w = self.splitter.widget(0)
            w.setParent(None)

        if pos == "left":
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.addWidget(self.downloads_panel)
            self.splitter.addWidget(self.browser)
            self.splitter.setSizes([320, 1080])
            self.downloads_panel.setVisible(False)
        elif pos == "bottom":
            self.splitter.setOrientation(Qt.Orientation.Vertical)
            self.splitter.addWidget(self.browser)
            self.splitter.addWidget(self.downloads_panel)
            self.splitter.setSizes([600, 250])
            self.downloads_panel.setVisible(False)
        elif pos == "floating":
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.addWidget(self.browser)
            self.downloads_panel.setParent(None)
            self.downloads_panel.setWindowTitle(t("downloads_title"))
            self.downloads_panel.setVisible(False)
        else:
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            self.splitter.addWidget(self.browser)
            self.downloads_panel.setVisible(False)

        self.setCentralWidget(self.splitter)

    def setup_toolbar(self):
        self.toolbar = QToolBar("Панель")
        self.toolbar.setMovable(False)
        self.apply_toolbar_style()
        self.addToolBar(self.toolbar)

        self.toolbar_actions = {}

        self.toolbar_actions["downloads"] = QAction(f"{t('downloads')} (0)", self)
        self.toolbar_actions["downloads"].triggered.connect(self.toggle_downloads)
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
        text_color = "#000" if current_color_hex.lower() in ("#f0f0f0", "#ffffff", "#fff") else "#fff"
        hover_color = "#d0d0d0" if text_color == "#000" else "#444"

        self.toolbar.setStyleSheet(f"""
            QToolBar {{ background: {current_color_hex}; border-bottom: 1px solid #444; padding: 4px; }}
            QToolButton {{ color: {text_color}; padding: 6px 12px; border-radius: 4px; }}
            QToolButton:hover {{ background: {hover_color}; }}
        """)

    def refresh_toolbar_text(self):
        self.toolbar_actions["downloads"].setText(f"{t('downloads')} ({self.download_count})")
        self.toolbar_actions["folder"].setText(t("downloads_folder"))
        self.toolbar_actions["back"].setText(t("back"))
        self.toolbar_actions["reload"].setText(t("reload"))
        self.toolbar_actions["home"].setText(t("home"))
        self.toolbar_actions["update"].setText(t("check_updates"))
        self.toolbar_actions["settings"].setText(t("settings"))

    def toggle_downloads(self):
        if current_panel_pos == "floating":
            self.downloads_panel.setVisible(not self.downloads_panel.isVisible())
            if self.downloads_panel.isVisible():
                self.downloads_panel.refresh_from_folder()
            return

        visible = self.downloads_panel.isVisible()
        self.downloads_panel.setVisible(not visible)
        if not visible:
            self.downloads_panel.refresh_from_folder()

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_lang = dlg.get_language()
            new_color = dlg.get_color()
            new_panel_pos = dlg.get_panel_pos()

            self.settings.setValue("language", new_lang)
            self.settings.setValue("toolbar_color", new_color)
            self.settings.setValue("panel_position", new_panel_pos)

            global current_lang, current_color_hex
            current_lang = new_lang
            current_color_hex = new_color

            self.apply_toolbar_style()
            self.refresh_toolbar_text()

            if new_panel_pos != current_panel_pos:
                self.apply_panel_position(new_panel_pos)

            QMessageBox.information(self, "OK", "Настройки сохранены.")

    # ---------- ОБНОВЛЕНИЯ ----------
    def check_updates(self, manual=False):
        if manual:
            self.setWindowTitle("DeepSeek App — проверка...")
        self.update_checker = UpdateChecker()
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_update.connect(lambda: self.on_no_update(manual))
        self.update_checker.error.connect(lambda err: self.on_update_error(err, manual))
        self.update_checker.start()

    def on_update_available(self, new_version, new_code):
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")
        reply = QMessageBox.question(
            self, t("update_available_title"),
            t("update_available_text").format(v1=new_version, v2=CURRENT_VERSION),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
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
        if manual:
            QMessageBox.warning(
                self, t("update_error_title"),
                t("update_error_text").format(err=err)
            )

    def apply_update(self, new_code):
        try:
            with open(NEW_CODE_PATH, "w", encoding="utf-8") as f:
                f.write(new_code)

            python_exe = sys.executable
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

            QMessageBox.information(self, t("update_close_title"), t("update_close_text"))

            if sys.platform == "win32":
                os.startfile(BAT_PATH)
            else:
                subprocess.Popen(["/bin/bash", BAT_PATH])

            QApplication.instance().quit()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"{e}")

    # ---------- ПРОЧЕЕ ----------
    def open_downloads_folder(self):
        if sys.platform == "win32":
            os.startfile(DOWNLOADS_DIR)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", DOWNLOADS_DIR])
        else:
            subprocess.Popen(["xdg-open", DOWNLOADS_DIR])

    def on_download_requested(self, download: QWebEngineDownloadRequest):
        filename = download.downloadFileName() or "file"
        save_path = os.path.join(DOWNLOADS_DIR, filename)

        download.setDownloadDirectory(DOWNLOADS_DIR)
        download.setDownloadFileName(filename)
        download.accept()

        print(f"Скачивание: {filename} → {DOWNLOADS_DIR}")

        self.download_count += 1
        self.toolbar_actions["downloads"].setText(f"{t('downloads')} ({self.download_count})")

        self.downloads_panel.add_download(download, save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    window = DeepSeekApp()
    window.show()
    sys.exit(app.exec())
