#!/usr/bin/env python3

import configparser
import os
import shlex
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtCore import Qt, QProcess, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "ArchLatam Welcome"

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

        parser = configparser.ConfigParser(
            interpolation=None,
            strict=False,
        )
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

            # Remove freedesktop field codes, e.g. %f and %U.
            command = __import__("re").sub(
                r"%[fFuUdDnNickvm]",
                "",
                command,
            )
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


class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "es"
        self.setMinimumSize(540, 500)
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(36, 30, 36, 30)
        layout.setSpacing(18)

        top = QHBoxLayout()
        self.brand = QLabel("ARCHLATAM")
        self.brand.setFont(QFont("Sans Serif", 13, QFont.Weight.Bold))
        top.addWidget(self.brand)
        top.addStretch()

        self.language_label = QLabel()
        top.addWidget(self.language_label)

        self.language_box = QComboBox()
        self.language_box.addItem("Español", "es")
        self.language_box.addItem("English", "en")
        self.language_box.addItem("Português", "pt")
        self.language_box.currentIndexChanged.connect(self.change_language)
        top.addWidget(self.language_box)
        layout.addLayout(top)

        layout.addStretch(1)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Sans Serif", 25, QFont.Weight.Bold))
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #7aa2f7;")
        layout.addWidget(self.subtitle_label)

        self.description_label = QLabel()
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        layout.addSpacing(12)

        self.install_button = QPushButton()
        self.install_button.setMinimumHeight(52)
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #7aa2f7;
                color: #16161e;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover { background-color: #89b4fa; }
        """)
        self.install_button.clicked.connect(self.launch_calamares)
        layout.addWidget(self.install_button)

        self.live_button = QPushButton()
        self.live_button.setMinimumHeight(42)
        self.live_button.clicked.connect(self.close)
        layout.addWidget(self.live_button)

        layout.addStretch(1)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)

        links = QHBoxLayout()
        self.link_buttons = {}
        for key in ("docs", "web", "repo"):
            button = QPushButton()
            button.setFlat(True)
            button.clicked.connect(lambda checked=False, k=key: self.open_link(k))
            links.addWidget(button)
            self.link_buttons[key] = button
        layout.addLayout(links)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1b26;
                color: #c0caf5;
            }
            QPushButton {
                border: 1px solid #414868;
                border-radius: 7px;
                padding: 8px;
            }
            QPushButton:hover { background-color: #292e42; }
            QComboBox {
                padding: 6px;
                border: 1px solid #414868;
                border-radius: 6px;
            }
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
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("ArchLatam")

    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
