#!/usr/bin/env python3
"""
ArchLatam Welcome — estilo inspirado en omabox.app
App de bienvenida para la ISO live.
"""

import configparser
import os
import re
import shlex
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QProcess, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QIcon,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "ArchLatam Welcome"
ICON_NAME = "archlatam-welcome"
ICON_BG = "#33421c"  # verde musgo oscuro del icono
ASSET_DIR = Path(__file__).resolve().parent
ICON_SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)

# Colores estilo omabox
BG = "#0b0c13"
BG_ELEVATED = "#12141c"
BG_CARD = "#151822"
BORDER = "rgba(255, 255, 255, 0.10)"
BORDER_STRONG = "rgba(255, 255, 255, 0.16)"
TEXT = "#e8eaf0"
TEXT_MUTED = "#8b90a0"
TEXT_DIM = "#5c6170"
ACCENT = "#b8f55a"
ACCENT_HOVER = "#c8ff6e"
ACCENT_SOFT = "rgba(184, 245, 90, 0.12)"

LINKS = {
    "web": "https://archlatam.github.io",
    "docs": "https://archlatam.github.io",
    "repo": "https://github.com/archlatam",
}

TEXT = {
    "es": {
        "subtitle": "Tu sistema, listo para comenzar.",
        "description": (
            "Instalá ArchLatam en tu equipo o explorá el sistema "
            "desde la sesión Live."
        ),
        "install": "Instalar ArchLatam",
        "live": "Seguir probando el sistema",
        "docs": "Documentación",
        "web": "Sitio web",
        "repo": "Código fuente",
        "language": "Idioma",
        "missing": "No se encontró una entrada de Calamares.",
        "failed": "No se pudo iniciar Calamares.",
        "title": "Bienvenido a ArchLatam",
        "badge": "ISO Live",
    },
    "en": {
        "subtitle": "Your system, ready to get started.",
        "description": (
            "Install ArchLatam on your computer or explore "
            "the system in the Live session."
        ),
        "install": "Install ArchLatam",
        "live": "Continue testing the system",
        "docs": "Documentation",
        "web": "Website",
        "repo": "Source code",
        "language": "Language",
        "missing": "No Calamares desktop entry was found.",
        "failed": "Could not start Calamares.",
        "title": "Welcome to ArchLatam",
        "badge": "Live ISO",
    },
    "pt": {
        "subtitle": "Seu sistema, pronto para começar.",
        "description": (
            "Instale o ArchLatam no seu computador ou explore "
            "o sistema na sessão Live."
        ),
        "install": "Instalar ArchLatam",
        "live": "Continuar testando o sistema",
        "docs": "Documentação",
        "web": "Site",
        "repo": "Código-fonte",
        "language": "Idioma",
        "missing": "Não foi encontrada uma entrada do Calamares.",
        "failed": "Não foi possível iniciar o Calamares.",
        "title": "Bem-vindo ao ArchLatam",
        "badge": "ISO Live",
    },
}


def find_calamares_entry():
    override = os.environ.get("CALAMARES_DESKTOP_FILE")
    candidates = ([Path(override)] if override else []) + [
        Path("/usr/share/applications/calamares.desktop"),
        Path("/usr/local/share/applications/calamares.desktop"),
    ]

    for path in candidates:
        if not path.is_file():
            continue

        parser = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            parser.read(path, encoding="utf-8")
            entry = parser["Desktop Entry"]
            if entry.get("Hidden", "false").lower() == "true":
                continue
            if entry.get("NoDisplay", "false").lower() == "true":
                continue
            if entry.get("Type", "Application") != "Application":
                continue

            command = entry.get("Exec", "").strip()
            if not command:
                continue

            command = re.sub(r"%[fFuUdDnNickvm]", "", command)
            parts = shlex.split(command)
            if not parts:
                continue

            executable = parts[0]
            if not (executable.startswith("/") or shutil.which(executable)):
                continue

            return executable, parts[1:]
        except (OSError, KeyError, ValueError):
            continue

    return None


def load_preferred_font(families, size, weight=QFont.Weight.Normal):
    """Intenta cargar una fuente; si no está, usa la del sistema."""
    available = set(QFontDatabase.families())
    for name in families:
        if name in available:
            return QFont(name, size, weight)
    return QFont("Sans Serif", size, weight)


def draw_app_icon(size=512):
    """Dibuja la marca en runtime (fallback si no hay archivos de icono)."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    scale = size / 512
    inset = 28 * scale
    stroke = 56 * scale
    radius = 112 * scale

    painter.setPen(QPen(QColor(ACCENT), stroke))
    painter.setBrush(QColor(ICON_BG))
    painter.drawRoundedRect(
        QRectF(inset, inset, size - 2 * inset, size - 2 * inset),
        radius,
        radius,
    )
    painter.end()

    return pixmap


def app_icon():
    """Icono de la app: archivos junto al script, tema de iconos o runtime."""
    candidates = [
        ASSET_DIR / f"{ICON_NAME}.svg",
        ASSET_DIR / "assets" / f"{ICON_NAME}.svg",
        ASSET_DIR / f"{ICON_NAME}-256.png",
        ASSET_DIR / "assets" / f"{ICON_NAME}-256.png",
        Path(f"/usr/share/icons/hicolor/256x256/apps/{ICON_NAME}.png"),
        Path(f"/usr/share/icons/hicolor/scalable/apps/{ICON_NAME}.svg"),
        Path(f"/usr/share/pixmaps/{ICON_NAME}.png"),
    ]

    for path in candidates:
        if not path.is_file():
            continue
        icon = QIcon(str(path))
        if not icon.isNull():
            return icon

    icon = QIcon()
    for size in ICON_SIZES:
        icon.addPixmap(draw_app_icon(size))
    return icon


def desktop_entry_available():
    """¿Existe un .desktop válido con nuestro app id?

    Sin él, el portal no puede registrar la app y Qt escupe
    "App info not found for 'archlatam-welcome'". Solo lo asociamos cuando
    está realmente instalado.
    """
    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    data_dirs = os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share"

    directories = [data_home] + [Path(d) for d in data_dirs.split(":") if d]
    for directory in directories:
        entry = directory / "applications" / f"{ICON_NAME}.desktop"
        try:
            if "[Desktop Entry]" in entry.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            continue

    return False


class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "en"
        self.setMinimumSize(560, 520)
        self.resize(720, 580)
        self.setWindowTitle(APP_NAME)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(40, 28, 40, 28)
        root.setSpacing(0)

        # —— Barra superior ——
        top = QHBoxLayout()
        top.setSpacing(12)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        # Logo mark (cuadrado con punto)
        self.logo_mark = QLabel()
        self.logo_mark.setFixedSize(18, 18)
        self.logo_mark.setStyleSheet(f"""
            background-color: transparent;
            border: 2px solid {ACCENT};
            border-radius: 4px;
        """)
        # Punto interior con otro label superpuesto no es trivial en Qt;
        # usamos un estilo simple.
        brand_row.addWidget(self.logo_mark)

        self.brand = QLabel("archlatam")
        self.brand.setFont(load_preferred_font(
            ["Chakra Petch", "Inter", "Segoe UI"], 14, QFont.Weight.DemiBold
        ))
        self.brand.setStyleSheet(f"color: {TEXT}; letter-spacing: -0.3px;")
        brand_row.addWidget(self.brand)
        top.addLayout(brand_row)

        top.addStretch()

        self.language_label = QLabel()
        self.language_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px;")
        top.addWidget(self.language_label)

        self.language_box = QComboBox()
        self.language_box.addItem("English", "en")
        self.language_box.addItem("Español", "es")
        self.language_box.addItem("Português", "pt")
        self.language_box.setCurrentIndex(0)
        self.language_box.setMinimumWidth(120)
        self.language_box.currentIndexChanged.connect(self.change_language)
        top.addWidget(self.language_box)

        root.addLayout(top)
        root.addSpacing(36)

        # —— Badge ——
        self.badge = QLabel()
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setStyleSheet(f"""
            QLabel {{
                color: {ACCENT};
                background-color: {ACCENT_SOFT};
                border: 1px solid rgba(184, 245, 90, 0.28);
                border-radius: 999px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 500;
            }}
        """)
        self.badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        badge_wrap = QHBoxLayout()
        badge_wrap.addStretch()
        badge_wrap.addWidget(self.badge)
        badge_wrap.addStretch()
        root.addLayout(badge_wrap)
        root.addSpacing(20)

        # —— Título y textos ——
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(load_preferred_font(
            ["Chakra Petch", "Inter", "Segoe UI"], 28, QFont.Weight.DemiBold
        ))
        self.title_label.setStyleSheet(
            f"color: {TEXT}; letter-spacing: -0.8px; line-height: 1.15;"
        )
        self.title_label.setWordWrap(True)
        root.addWidget(self.title_label)
        root.addSpacing(10)

        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(
            f"color: {ACCENT}; font-size: 15px; font-weight: 500;"
        )
        root.addWidget(self.subtitle_label)
        root.addSpacing(12)

        self.description_label = QLabel()
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 14.5px; line-height: 1.5;"
        )
        self.description_label.setMaximumWidth(460)
        # Centrar el label con ancho máximo
        desc_wrap = QHBoxLayout()
        desc_wrap.addStretch()
        desc_wrap.addWidget(self.description_label)
        desc_wrap.addStretch()
        root.addLayout(desc_wrap)

        root.addSpacing(28)

        # —— Botones principales ——
        self.install_button = QPushButton()
        self.install_button.setMinimumHeight(48)
        self.install_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: {BG};
                border: none;
                border-radius: 999px;
                font-size: 15px;
                font-weight: 600;
                padding: 10px 28px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #a8e04a;
            }}
        """)
        self.install_button.clicked.connect(self.launch_calamares)

        self.live_button = QPushButton()
        self.live_button.setMinimumHeight(48)
        self.live_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.live_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT};
                border: 1px solid {BORDER_STRONG};
                border-radius: 999px;
                font-size: 14px;
                font-weight: 500;
                padding: 10px 24px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.04);
                border-color: rgba(255, 255, 255, 0.24);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.07);
            }}
        """)
        self.live_button.clicked.connect(self.close)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(10)
        btn_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for btn in (self.install_button, self.live_button):
            btn.setMinimumWidth(280)
            btn.setMaximumWidth(340)
            wrap = QHBoxLayout()
            wrap.addStretch()
            wrap.addWidget(btn)
            wrap.addStretch()
            btn_col.addLayout(wrap)

        root.addLayout(btn_col)
        root.addStretch(1)
        root.addSpacing(16)

        # —— Separador ——
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"color: {BORDER}; background-color: {BORDER}; max-height: 1px;")
        root.addWidget(separator)
        root.addSpacing(16)

        # —— Enlaces ——
        links = QHBoxLayout()
        links.setSpacing(8)
        links.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.link_buttons = {}
        for key in ("docs", "web", "repo"):
            button = QPushButton()
            button.setFlat(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(f"""
                QPushButton {{
                    color: {TEXT_MUTED};
                    background: transparent;
                    border: none;
                    font-size: 13px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    color: {TEXT};
                }}
            """)
            button.clicked.connect(lambda checked=False, k=key: self.open_link(k))
            links.addWidget(button)
            self.link_buttons[key] = button

        root.addLayout(links)

        # Estilo global de la ventana
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {BG};
                color: {TEXT};
            }}
            QComboBox {{
                background-color: {BG_ELEVATED};
                color: {TEXT};
                border: 1px solid {BORDER_STRONG};
                border-radius: 0px;
                padding: 6px 10px;
                font-size: 13px;
                min-height: 18px;
            }}
            QComboBox:hover {{
                border: 1px solid rgba(255, 255, 255, 0.24);
            }}
            QComboBox::drop-down {{
                border: none;
                width: 22px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_ELEVATED};
                color: {TEXT};
                border: 1px solid {BORDER_STRONG};
                selection-background-color: {ACCENT_SOFT};
                selection-color: {ACCENT};
                outline: none;
            }}
            QMessageBox {{
                background-color: {BG_ELEVATED};
                color: {TEXT};
            }}
            QMessageBox QPushButton {{
                background-color: {BG_CARD};
                color: {TEXT};
                border: 1px solid {BORDER_STRONG};
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 70px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.06);
            }}
        """)

        self.change_language()

    def change_language(self, *_):
        selected = self.language_box.currentData()
        if selected:
            self.language = selected

        t = TEXT[self.language]
        self.setWindowTitle(APP_NAME)
        self.title_label.setText(t["title"])
        self.subtitle_label.setText(t["subtitle"])
        self.description_label.setText(t["description"])
        self.install_button.setText(t["install"])
        self.live_button.setText(t["live"])
        self.language_label.setText(t["language"] + ":")
        self.badge.setText("●  " + t["badge"])

        for key, button in self.link_buttons.items():
            button.setText(t[key])

    def launch_calamares(self):
        entry = find_calamares_entry()
        if not entry:
            QMessageBox.warning(self, APP_NAME, TEXT[self.language]["missing"])
            return

        program, arguments = entry
        ok, _pid = QProcess.startDetached(program, arguments)
        if ok:
            self.hide()
        else:
            QMessageBox.critical(self, APP_NAME, TEXT[self.language]["failed"])

    def open_link(self, key):
        url = QUrl(LINKS[key])
        if url.scheme() == "https" and url.host():
            QDesktopServices.openUrl(url)


def main():
    # Mejor renderizado en pantallas HiDPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName("ArchLatam")
    app.setStyle("Fusion")  # estilo base limpio

    # Icono de ventana y asociación con el .desktop instalado (app_id en
    # Wayland / barra de tareas de KDE Plasma). Solo si el .desktop existe,
    # para no disparar el aviso del portal al correr la app suelta.
    if desktop_entry_available():
        app.setDesktopFileName(ICON_NAME)
    app.setWindowIcon(app_icon())

    window = WelcomeWindow()
    window.show()

    exit_code = app.exec()

    # PySide6 6.12 + Python 3.14: si la ventana sobrevive a la QApplication,
    # el cleanup de Shiboken termina en SIGSEGV al salir. Borramos en orden.
    window.deleteLater()
    app.processEvents()
    del window, app

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
