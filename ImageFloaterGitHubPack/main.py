import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMenu, QAction, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QIcon, QClipboard
from PyQt5.QtCore import Qt, QTimer
from PIL import Image

import json

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"directories": []}

class FloatingButton(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(60, 60)

        icon_path = "icons/floater.png"
        btn = QPushButton(self)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(self.size())
        btn.setFixedSize(self.size())
        btn.setStyleSheet("border: none; background: transparent;")
        btn.clicked.connect(self.toggle_window)
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(self.open_menu)

        self.image_window = None

    def toggle_window(self):
        if self.image_window and self.image_window.isVisible():
            self.image_window.hide()
        else:
            if not self.image_window:
                self.image_window = ImagePreviewWindow()
            self.image_window.show()

    def open_menu(self, pos):
        menu = QMenu(self)
        action = QAction("设置目录", self)
        action.triggered.connect(self.set_directories)
        menu.addAction(action)
        menu.exec_(self.mapToGlobal(pos))

    def set_directories(self):
        dirs = QFileDialog.getExistingDirectory(self, "选择目录", os.getcwd())
        if dirs:
            config = load_config()
            config["directories"] = [dirs]
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

class ImagePreviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片预览")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.load_images()

    def load_images(self):
        self.list_widget.clear()
        config = load_config()
        for folder in config.get("directories", []):
            for fname in os.listdir(folder):
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    full_path = os.path.join(folder, fname)
                    icon = QIcon(full_path)
                    item = QListWidgetItem(icon, fname)
                    item.setData(Qt.UserRole, full_path)
                    self.list_widget.addItem(item)
        self.list_widget.itemClicked.connect(self.copy_image)

    def copy_image(self, item):
        path = item.data(Qt.UserRole)
        img = Image.open(path)
        output = os.path.join(os.getcwd(), "_copy.png")
        img.save(output)
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap(output))