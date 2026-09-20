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
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QFrame
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

# ⚠️ ЗАМЕНИ ЭТУ ССЫЛКУ НА СВОЮ ИЗ PASTEBIN (кнопка "raw") ⚠️
# Формат пасты:
#   vers 1
#
#   code
#
#   import sys
#   ...весь код...
UPDATE_URL = "https://pastebin.com/raw/ЗАМЕНИ_НА_ССЫЛКУ"


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

print(f"Папка приложения: {APP_DIR}")
print(f"Загрузки: {DOWNLOADS_DIR}")
print(f"Файл приложения: {SCRIPT_PATH}")
print(f"Текущая версия: {CURRENT_VERSION}")


# ============================================================
# ПАРСИНГ ФОРМАТА ПАСТЫ
# ============================================================
def parse_paste(content):
    """
    Парсит текст пасты в формате:
        vers N
        code
        <код>
    Возвращает (версия: int, код: str) или (None, None) при ошибке.
    """
    # Ищем строку "vers N"
    version_match = re.search(r'^\s*vers\s+(\d+)\s*$', content, re.MULTILINE)
    if not version_match:
        return None, None
    version = int(version_match.group(1))

    # Ищем строку "code" (отдельное слово на строке)
    code_match = re.search(r'^\s*code\s*$', content, re.MULTILINE)
    if not code_match:
        return None, None

    # Всё после "code" — это код
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
                subprocess.Popen(
                    ["cmd", "/c", BAT_PATH],
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS,
                    cwd=SCRIPT_DIR
                )
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
    """Скачивает пасту, парсит версию и код."""
    update_available = Signal(int, str)   # (версия, код)
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
                self.error.emit("Не удалось распарсить пасту (нужны строки 'vers N' и 'code')")
                return

            print(f"[обновление] Версия с Pastebin: {remote_version}")
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
        req = urllib.request.Request(
            ICON_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
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
        name_label.setStyleSheet(
            "color: #ffffff; font-size: 13px; font-weight: bold;"
        )
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
        self.setWindowTitle("Загрузки")
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
        title = QLabel("📥 Загрузки")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #fff;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Обновить")
        refresh_btn.setFixedSize(36, 36)
        refresh_btn.clicked.connect(self.refresh_from_folder)
        header.addWidget(refresh_btn)

        open_btn = QPushButton("📂 Папка")
        open_btn.clicked.connect(self.open_downloads_folder)
        header.addWidget(open_btn)

        clear_btn = QPushButton("🗑")
        clear_btn.setToolTip("Очистить список")
        clear_btn.setFixedSize(36, 36)
        clear_btn.clicked.connect(self.clear_list)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        path_frame = QFrame()
        path_frame.setStyleSheet(
            "background: #252525; border-radius: 6px; padding: 8px;"
        )
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
        self.progress_container.setStyleSheet(
            "background: #252525; border-radius: 8px; padding: 8px;"
        )
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(10, 8, 10, 8)
        progress_layout.setSpacing(6)
        self.progress_container.setLayout(progress_layout)

        self.progress_label = QLabel("Нет активных загрузок")
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
        date_str = datetime.fromtimestamp(
            os.path.getmtime(path)
        ).strftime("%d.%m.%Y %H:%M")

        card = FileCardWidget(
            filename,
            f"{size_str}  •  {date_str}",
            path,
            is_downloading=False
        )

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

        open_action = menu.addAction("📂 Открыть")
        folder_action = menu.addAction("📁 Показать в папке")
        menu.addSeparator()
        delete_action = menu.addAction("🗑 Удалить")

        action = menu.exec(self.list_widget.mapToGlobal(pos))

        if action == open_action:
            self.on_item_double_click(item)
        elif action == folder_action:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        elif action == delete_action:
            reply = QMessageBox.question(
                self, "Удаление",
                f"Удалить файл?\n{os.path.basename(path)}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(path)
                    self.list_widget.takeItem(self.list_widget.row(item))
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось удалить:\n{e}")

    def add_download(self, download: QWebEngineDownloadRequest, path: str):
        filename = os.path.basename(path)

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == path:
                self.list_widget.takeItem(i)
                break

        card = FileCardWidget(filename, "Загрузка...", path, is_downloading=True)
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setSizeHint(QSize(0, 60))
        self.list_widget.insertItem(0, item)
        self.list_widget.setItemWidget(item, card)

        self.downloads[download] = (item, card, path)

        self.progress_container.setVisible(True)
        self.progress_label.setText(f"📥 {filename}")

        download.receivedBytesChanged.connect(
            lambda d=download: self.update_progress(d)
        )
        download.isFinishedChanged.connect(
            lambda d=download: self.finish_download(d)
        )

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
                self.progress_label.setText("Загрузка завершена")

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
        self.profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.DiskHttpCache
        )
        self.profile.downloadRequested.connect(self.on_download_requested)

        self.download_window = DownloadsWindow()
        self.download_count = 0

        # Страница
        self.page = MyPage(self.profile, self)
        settings = self.page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Браузер
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl("https://chat.deepseek.com/"))
        self.setCentralWidget(self.browser)
        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

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
        toolbar = QToolBar("Панель")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar { background: #202123; border-bottom: 1px solid #444; padding: 4px; }
            QToolButton { color: #fff; padding: 6px 12px; border-radius: 4px; }
            QToolButton:hover { background: #444; }
        """)
        self.addToolBar(toolbar)

        self.downloads_action = QAction("⬇ Загрузки (0)", self)
        self.downloads_action.triggered.connect(self.show_downloads)
        toolbar.addAction(self.downloads_action)

        open_folder_action = QAction("📂 Папка загрузок", self)
        open_folder_action.triggered.connect(self.open_downloads_folder)
        toolbar.addAction(open_folder_action)

        back_action = QAction("← Назад", self)
        back_action.triggered.connect(self.browser.back)
        toolbar.addAction(back_action)

        reload_action = QAction("↻ Обновить", self)
        reload_action.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_action)

        home_action = QAction("🏠 DeepSeek", self)
        home_action.triggered.connect(
            lambda: self.browser.setUrl(QUrl("https://chat.deepseek.com/"))
        )
        toolbar.addAction(home_action)

        update_action = QAction("🔄 Проверить обновление", self)
        update_action.triggered.connect(lambda: self.check_updates(manual=True))
        toolbar.addAction(update_action)

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
            "Доступно обновление",
            f"Найдена новая версия: v{new_version}\n"
            f"Ваша версия: v{CURRENT_VERSION}\n\n"
            f"Обновить приложение?\n"
            f"(Приложение закроется и запустится с новой версией)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.apply_update(new_code)

    def on_no_update(self, manual):
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")
        if manual:
            QMessageBox.information(
                self, "Обновлений нет",
                f"У вас последняя версия (v{CURRENT_VERSION})."
            )

    def on_update_error(self, err, manual):
        self.setWindowTitle(f"DeepSeek App — v{CURRENT_VERSION}")
        print(f"[обновление] ошибка: {err}")
        if manual:
            QMessageBox.warning(
                self, "Ошибка проверки",
                f"Не удалось проверить обновления:\n{err}"
            )

    def apply_update(self, new_code):
        """Сохраняем новый код, создаём батник, перезапускаемся."""
        print(f"[обновление] Применяю обновление, длина кода: {len(new_code)}")

        try:
            with open(NEW_CODE_PATH, "w", encoding="utf-8") as f:
                f.write(new_code)

            bat_content = f"""@echo off
chcp 65001 > nul
timeout /t 2 /nobreak > nul
del "{SCRIPT_PATH}"
move "{NEW_CODE_PATH}" "{SCRIPT_PATH}"
start "" pythonw "{SCRIPT_PATH}"
del "%~f0"
"""
            with open(BAT_PATH, "w", encoding="cp866") as f:
                f.write(bat_content)

            print(f"[обновление] Батник создан: {BAT_PATH}")
            print(f"[обновление] Новый код: {NEW_CODE_PATH}")

            QMessageBox.information(
                self, "Обновление",
                "Приложение закроется и запустится с новой версией."
            )

            if sys.platform == "win32":
                subprocess.Popen(
                    ["cmd", "/c", BAT_PATH],
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS,
                    cwd=SCRIPT_DIR
                )
            else:
                subprocess.Popen(["/bin/bash", BAT_PATH])

            QApplication.instance().quit()

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось применить обновление:\n{e}"
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
        self.downloads_action.setText(f"⬇ Загрузки ({self.download_count})")

        self.download_window.add_download(download, save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    window = DeepSeekApp()
    window.show()
    sys.exit(app.exec())
