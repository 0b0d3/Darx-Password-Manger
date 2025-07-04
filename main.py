#
# main.py - DARX PASS™ Secure Password Manager
# Author: DARX Tech
#CREATED BY ABDULLAHUSIEN **0b0d3**
# Requirements:
# pip install PySide6 cryptography
#
# Optional for extended Windows clipboard functionality (not used in this cross-platform implementation):
# pip install pywin32
#
# Note on Fonts:
# This application attempts to use the "Inter" font. If not installed, it will fall back to
# system default sans-serif fonts like "Segoe UI". For the best visual experience,
# please install the Inter font family.
#

import sys
import os
import json
import time
import hashlib
import hmac
import re

from cryptography.fernet import Fernet, InvalidToken

from PySide6.QtCore import (
    Qt, QSize, QTimer, Slot
)
from PySide6.QtGui import (
    QIcon, QFont, QAction
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QFormLayout,
    QMessageBox, QGraphicsDropShadowEffect, QButtonGroup, QDialogButtonBox,
    QSpacerItem, QSizePolicy, QAbstractItemView
)

# --- Configuration Constants ---
VAULT_FILE = "vault_data.json"
KEY_FILE = "key.key"
MASTER_HASH_FILE = "master.hash"  # Stores the SHA-256 hash of the master password.
WINDOW_SIZE = QSize(1080, 720)
SIDEBAR_WIDTH = 220


# --- STYLESHEETS ---

def get_stylesheet(theme='dark'):
    """Returns the QSS stylesheet for the specified theme."""
    if theme == 'light':
        return """
        /* Light Theme */
        QWidget {
            background-color: #f0f0f0;
            color: #1e1e2e;
            font-family: Inter, Segoe UI, sans-serif;
            font-size: 10pt;
        }
        QMainWindow { background-color: #f0f0f0; }
        QFrame#Sidebar {
            background-color: #e9e9ed;
            border-right: 1px solid #d5d5d8;
        }
        QLabel { color: #1e1e2e; }
        QLabel#Header {
            font-size: 16pt;
            font-weight: bold;
        }
        QLabel#FooterLabel {
            font-size: 8pt;
            color: #6c757d; /* Muted gray for light bg */
        }
        /* Buttons */
        QPushButton {
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #ffffff;
        }
        QPushButton:hover { background-color: #f5f5f5; }
        QPushButton:pressed { background-color: #e0e0e0; }
        QPushButton#PrimaryButton {
            background-color: #0d6efd;
            color: #ffffff;
            font-weight: bold;
            border: none;
        }
        QPushButton#PrimaryButton:hover { background-color: #388bfd; }
        QPushButton#PrimaryButton:pressed { background-color: #0a58ca; }
        QPushButton#DangerButton {
            background-color: #dc3545;
            color: #ffffff;
            font-weight: bold;
            border: none;
        }
        QPushButton#DangerButton:hover { background-color: #e11d48; }
        QPushButton#DangerButton:pressed { background-color: #b02a37; }
        QPushButton#SidebarButton {
            background-color: transparent;
            border: none;
            padding: 12px;
            text-align: left;
            border-radius: 6px;
            color: #1e1e2e;
            font-size: 11pt;
        }
        QPushButton#SidebarButton:hover { background-color: #d8d8de; }
        QPushButton#SidebarButton:checked {
            background-color: #0d6efd;
            color: white;
            font-weight: bold;
        }
        /* Table */
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 6px;
            gridline-color: #e0e0e0;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            padding: 4px;
            border-style: none;
            border-bottom: 1px solid #cccccc;
            font-weight: bold;
        }
        QTableWidget::item { padding: 5px; }
        QTableWidget::item:selected {
            background-color: #0d6efd;
            color: #ffffff;
        }
        /* Inputs & Dialogs */
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 8px;
            border-radius: 6px;
        }
        QDialog { background-color: #f0f0f0; }
        /* ScrollBar */
        QScrollBar:vertical {
            border: none;
            background: #e0e0e0;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #b0b0b0;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        QToolTip {
            color: #ffffff;
            background-color: #1e1e2e;
            border: 1px solid #2a2a3f;
            border-radius: 4px;
            padding: 5px;
        }
        """

    # Dark Theme is default
    return """
    /* Dark Theme - DARX VAULT */
    QWidget {
        background-color: #1e1e2e;
        color: #c9c9d1; /* Softer white for text */
        font-family: Inter, Segoe UI, sans-serif;
        font-size: 10pt;
    }
    QMainWindow { background-color: #1e1e2e; }
    QFrame#Sidebar {
        background-color: #161625;
        border-right: 1px solid #2a2a3f;
    }
    QLabel { color: #c9c9d1; }
    QLabel#Header {
        font-size: 16pt;
        font-weight: bold;
        color: #ffffff;
    }
    QLabel#FooterLabel {
        font-size: 8pt;
        color: #6a6a7f; /* Muted gray for dark bg */
    }
    /* Buttons */
    QPushButton {
        border: 1px solid #3c3c5a;
        border-radius: 6px;
        padding: 8px 12px;
        background-color: #2e2e48;
    }
    QPushButton:hover { background-color: #383854; }
    QPushButton:pressed { background-color: #252538; }
    QPushButton#PrimaryButton {
        background-color: #1f6feb;
        color: #ffffff;
        font-weight: bold;
        border: 1px solid #1f6feb;
    }
    QPushButton#PrimaryButton:hover {
        background-color: #388bfd;
        border: 1px solid #388bfd;
    }
    QPushButton#PrimaryButton:pressed { background-color: #0d6efd; }
    QPushButton#DangerButton {
        background-color: #f43f5e;
        color: #ffffff;
        font-weight: bold;
        border: none;
    }
    QPushButton#DangerButton:hover { background-color: #e11d48; }
    QPushButton#DangerButton:pressed { background-color: #be123c; }
    QPushButton#SidebarButton {
        background-color: transparent;
        border: none;
        padding: 12px;
        color: #ffffff;
        text-align: left;
        border-radius: 6px;
        font-size: 11pt;
    }
    QPushButton#SidebarButton:hover { background-color: #2e2e48; }
    QPushButton#SidebarButton:checked {
        background-color: #1f6feb;
        font-weight: bold;
    }
    /* Table */
    QTableWidget {
        background-color: #161625;
        border: 1px solid #2a2a3f;
        border-radius: 6px;
        gridline-color: #2a2a3f;
    }
    QHeaderView::section {
        background-color: #2e2e48;
        padding: 4px;
        border-style: none;
        border-bottom: 1px solid #3c3c5a;
        font-weight: bold;
        color: #ffffff;
    }
    QTableWidget::item { padding: 5px; border-bottom: 1px solid #2a2a3f; }
    QTableWidget::item:selected {
        background-color: #1f6feb;
        color: #ffffff;
    }
    /* Inputs & Dialogs */
    QLineEdit {
        background-color: #2e2e48;
        border: 1px solid #3c3c5a;
        padding: 8px;
        border-radius: 6px;
        color: #c9c9d1;
    }
    QLineEdit:focus { border: 1px solid #1f6feb; }
    QDialog { background-color: #1e1e2e; }
    /* ScrollBar */
    QScrollBar:vertical {
        border: none;
        background: #161625;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #3c3c5a;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QToolTip {
        color: #ffffff;
        background-color: #161625;
        border: 1px solid #2a2a3f;
        border-radius: 4px;
        padding: 5px;
    }
    """


# --- Authentication Dialogs ---

class CreateMasterPasswordDialog(QDialog):
    """Dialog to create the initial master password."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Master Password")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.layout = QFormLayout(self)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)

        self.layout.addRow("New Master Password:", self.password_input)
        self.layout.addRow("Confirm Password:", self.confirm_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Create & Lock")
        buttons.accepted.connect(self.verify)
        buttons.rejected.connect(self.reject)
        self.layout.addRow(buttons)
        buttons.button(QDialogButtonBox.Ok).setObjectName("PrimaryButton")

    def verify(self):
        p1 = self.password_input.text()
        p2 = self.confirm_input.text()
        if not p1:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        self.accept()

    def get_password(self):
        return self.password_input.text()


class LoginDialog(QDialog):
    """Dialog to enter master password for login."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unlock DARX PASS™")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.layout = QFormLayout(self)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.layout.addRow("Master Password:", self.password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Unlock")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addRow(buttons)
        buttons.button(QDialogButtonBox.Ok).setObjectName("PrimaryButton")

    def get_password(self):
        return self.password_input.text()


# --- Add Password Dialog ---
class AddPasswordDialog(QDialog):
    """Dialog for adding a new password entry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Password")
        self.setMinimumWidth(400)
        self.setModal(True)

        self.layout = QFormLayout(self)
        self.site_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.check_password_strength)

        # Password visibility toggle
        self.password_visibility_action = self.password_input.addAction(
            QIcon(), QLineEdit.TrailingPosition)
        self.password_visibility_action.setToolTip("Show/Hide Password")
        self.password_visibility_action.setCheckable(True)
        self.password_visibility_action.toggled.connect(self.toggle_password_visibility)
        self.update_eye_icon()

        self.layout.addRow("Site URL/Name:", self.site_input)
        self.layout.addRow("Username/Email:", self.username_input)
        self.layout.addRow("Password:", self.password_input)

        # Password strength indicator
        self.strength_label = QLabel("")
        self.strength_label.setAlignment(Qt.AlignCenter)
        self.layout.addRow(self.strength_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Save).setObjectName("PrimaryButton")
        self.layout.addRow(buttons)

    def check_password_strength(self, password):
        """Checks password and updates strength indicator label."""
        score = 0
        if not password:
            self.strength_label.setText("")
            return

        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if re.search(r'[a-z]', password): score += 1
        if re.search(r'[A-Z]', password): score += 1
        if re.search(r'\d', password): score += 1
        if re.search(r'[^a-zA-Z0-9]', password): score += 1

        if score < 3:
            self.strength_label.setText("Weak")
            self.strength_label.setStyleSheet("color: #f43f5e; font-weight: bold;")
        elif score < 5:
            self.strength_label.setText("Medium")
            self.strength_label.setStyleSheet("color: #f97316; font-weight: bold;")  # Orange
        else:
            self.strength_label.setText("Strong")
            self.strength_label.setStyleSheet("color: #10b981; font-weight: bold;")  # Green

    def toggle_password_visibility(self, checked):
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.update_eye_icon()

    def update_eye_icon(self):
        icon_text = "👁️" if self.password_input.echoMode() == QLineEdit.Password else "🙈"
        self.password_visibility_action.setText(icon_text)

    def get_data(self):
        return {
            "site": self.site_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
        }


# --- Main Application Window ---
class MainWindow(QMainWindow):
    """The main application window for DARX PASS™."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DARX PASS™ – Secure Password Manager")
        self.setFixedSize(WINDOW_SIZE)

        self.is_dark_theme = True
        self.fernet = None
        self.passwords = []
        self.active_shadow_button = None

        self.init_crypto()
        self.init_ui()
        self.apply_stylesheet()
        self.load_passwords_to_table()

    def init_crypto(self):
        """Initializes the encryption service and loads vault data."""
        try:
            if os.path.exists(KEY_FILE):
                with open(KEY_FILE, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(KEY_FILE, 'wb') as f:
                    f.write(key)
            self.fernet = Fernet(key)
        except Exception as e:
            self.show_critical_error(f"Failed to load/generate security key: {e}")

        if not os.path.exists(KEY_FILE):
            self.show_critical_error(f"FATAL: Key file '{KEY_FILE}' not found and could not be created.")

        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, 'rb') as f:
                    encrypted_data = f.read()
                if not encrypted_data:
                    self.passwords = []
                    return
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.passwords = json.loads(decrypted_data)
            except InvalidToken:
                self.show_critical_error(
                    f"Decryption failed: key is invalid or data is corrupt. If you lost '{KEY_FILE}', your data is unrecoverable.")
            except Exception as e:
                self.show_critical_error(f"Failed to load vault: {e}")

    def save_vault_data(self):
        """Encrypts and saves the current passwords list to the vault file."""
        try:
            json_data = json.dumps(self.passwords, indent=4).encode('utf-8')
            encrypted_data = self.fernet.encrypt(json_data)
            with open(VAULT_FILE, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            self.show_critical_error(f"Could not save vault: {e}", fatal=False)

    def init_ui(self):
        """Sets up the main user interface."""
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.create_passwords_page()
        self.create_settings_page()
        main_layout.addWidget(self.pages)

        self.btn_passwords.setChecked(True)
        self.update_sidebar_shadow(self.btn_passwords)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        app_title = QLabel("DARX PASS™")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffffff; margin-bottom: 10px;")

        self.sidebar_button_group = QButtonGroup(self)
        self.sidebar_button_group.setExclusive(True)
        self.sidebar_button_group.idClicked.connect(self.switch_page)

        self.btn_passwords = self.create_sidebar_button("🔐 My Passwords", 0)
        btn_add = self.create_sidebar_button("➕ Add Password")
        btn_add.clicked.connect(self.open_add_password_dialog)

        btn_theme = self.create_sidebar_button("🎨 Change Theme")
        btn_theme.clicked.connect(self.toggle_theme)

        self.btn_settings = self.create_sidebar_button("⚙️ Settings", 1)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        btn_quit = self.create_sidebar_button("🚪 Quit")
        btn_quit.clicked.connect(self.close)

        self.footer_label = QLabel("DARX PASS™ – 2025 © | GitHub: @0b0d3")
        self.footer_label.setObjectName("FooterLabel")
        self.footer_label.setAlignment(Qt.AlignCenter)

        sidebar_layout.addWidget(app_title)
        sidebar_layout.addWidget(self.btn_passwords)
        sidebar_layout.addWidget(btn_add)
        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(btn_theme)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addSpacerItem(spacer)
        sidebar_layout.addWidget(btn_quit)
        self.footer_label.setWordWrap(True)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setContentsMargins(0, 10, 0, 0)
        sidebar_layout.addSpacing(5)
        sidebar_layout.addWidget(self.footer_label)
        return sidebar

    def create_sidebar_button(self, text, page_id=None):
        button = QPushButton(text)
        button.setObjectName("SidebarButton")
        button.setCheckable(page_id is not None)
        button.clicked.connect(lambda: self.update_sidebar_shadow(button))
        if page_id is not None:
            self.sidebar_button_group.addButton(button, page_id)
        return button

    @Slot(int)
    def switch_page(self, page_id):
        self.pages.setCurrentIndex(page_id)

    def create_passwords_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        header = QLabel("My Passwords")
        header.setObjectName("Header")
        layout.addWidget(header)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Site", "Username", "Password", "Copy", "Delete"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.table)
        self.pages.addWidget(page)

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        header = QLabel("Settings")
        header.setObjectName("Header")
        layout.addWidget(header)
        self.vault_info_label = QLabel()
        layout.addWidget(self.vault_info_label)
        danger_label = QLabel("🚨 Danger Zone")
        danger_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-top: 20px;")
        layout.addWidget(danger_label)
        btn_delete_all = QPushButton("Delete ALL Passwords")
        btn_delete_all.setObjectName("DangerButton")
        btn_delete_all.setFixedWidth(200)
        btn_delete_all.clicked.connect(self.delete_all_passwords)
        layout.addWidget(btn_delete_all)
        layout.addStretch()
        self.pages.addWidget(page)
        self.update_settings_info()

    def update_settings_info(self):
        count = len(self.passwords)
        self.vault_info_label.setText(
            f"<b>Vault Location:</b> {os.path.abspath(VAULT_FILE)}\n"
            f"<b>Number of Entries:</b> {count}"
        )

    def load_passwords_to_table(self):
        self.table.setRowCount(0)
        for idx, entry in enumerate(self.passwords):
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(entry["site"]))
            self.table.setItem(idx, 1, QTableWidgetItem(entry["username"]))
            self.table.setItem(idx, 2, QTableWidgetItem("******"))
            btn_copy = QPushButton("Copy")
            btn_copy.clicked.connect(lambda _, r=idx: self.copy_password(r))
            self.table.setCellWidget(idx, 3, btn_copy)
            btn_delete = QPushButton("Delete")
            btn_delete.setObjectName("DangerButton")
            btn_delete.clicked.connect(lambda _, r=idx: self.delete_password(r))
            self.table.setCellWidget(idx, 4, btn_delete)
        self.table.resizeColumnsToContents()
        for i in range(2): self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        self.update_settings_info()

    def copy_password(self, row_index):
        password = self.passwords[row_index]['password']
        QApplication.clipboard().setText(password)
        button = self.table.cellWidget(row_index, 3)
        if button:
            button.setText("Copied!")
            QTimer.singleShot(2000, lambda: button.setText("Copy"))
        QTimer.singleShot(10000, lambda: self.clear_clipboard_if_match(password))

    def clear_clipboard_if_match(self, p_to_clear):
        if QApplication.clipboard().text() == p_to_clear:
            QApplication.clipboard().clear()

    def delete_password(self, row_index):
        site = self.passwords[row_index]['site']
        reply = QMessageBox.warning(self, "Confirm Deletion", f"Delete password for <b>{site}</b>?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.passwords[row_index]
            self.save_vault_data()
            self.load_passwords_to_table()

    def open_add_password_dialog(self):
        dialog = AddPasswordDialog(self)
        dialog.setStyleSheet(self.styleSheet())  # Inherit theme
        if dialog.exec():
            data = dialog.get_data()
            if not all(data.values()):
                QMessageBox.warning(self, "Incomplete Data", "All fields are required.")
                return
            self.passwords.append(data)
            self.save_vault_data()
            self.load_passwords_to_table()
            self.pages.setCurrentIndex(0)
            self.btn_passwords.setChecked(True)
            self.update_sidebar_shadow(self.btn_passwords)

    def delete_all_passwords(self):
        reply = QMessageBox.critical(self, "DELETE ALL DATA",
                                     "<b>DANGER!</b> This is irreversible.<br>Delete ALL passwords in the vault?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.passwords.clear()
            self.save_vault_data()
            self.load_passwords_to_table()
            QMessageBox.information(self, "Success", "All passwords have been deleted.")

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_stylesheet()

    def apply_stylesheet(self):
        theme = 'dark' if self.is_dark_theme else 'light'
        self.setStyleSheet(get_stylesheet(theme))
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        shadow_color = "#1f6feb" if self.is_dark_theme else "#0a58ca"
        self.shadow_effect.setColor(shadow_color)
        self.shadow_effect.setOffset(0, 0)
        self.update_sidebar_shadow(self.active_shadow_button)

    def update_sidebar_shadow(self, button):
        if not hasattr(self, 'shadow_effect'): return
        if self.active_shadow_button:
            self.active_shadow_button.setGraphicsEffect(None)
        if button and button.isCheckable() and button.isChecked():
            button.setGraphicsEffect(self.shadow_effect)
            self.active_shadow_button = button
        else:
            self.active_shadow_button = None

    def show_critical_error(self, message, fatal=True):
        QMessageBox.critical(self, "Critical Error", message)
        if fatal:
            sys.exit(1)


# --- Application Startup and Authentication ---
def handle_authentication():
    """Manages the master password login flow."""
    authenticated = False

    # All auth dialogs default to the dark theme for consistency on startup.
    dialog_style = get_stylesheet('dark')

    if not os.path.exists(MASTER_HASH_FILE):
        # First-time setup
        create_dialog = CreateMasterPasswordDialog()
        create_dialog.setStyleSheet(dialog_style)
        if create_dialog.exec() == QDialog.Accepted:
            password = create_dialog.get_password()
            password_hash = hashlib.sha256(password.encode('utf-8')).digest()
            with open(MASTER_HASH_FILE, 'wb') as f:
                f.write(password_hash)
            authenticated = True
    else:
        # Existing user login
        with open(MASTER_HASH_FILE, 'rb') as f:
            stored_hash = f.read()

        login_dialog = LoginDialog()
        login_dialog.setStyleSheet(dialog_style)
        if login_dialog.exec() == QDialog.Accepted:
            password = login_dialog.get_password()
            entered_hash = hashlib.sha256(password.encode('utf-8')).digest()
            if hmac.compare_digest(stored_hash, entered_hash):
                authenticated = True
            else:
                msg_box = QMessageBox(QMessageBox.Critical, "Login Failed", "Incorrect master password.")
                msg_box.setStyleSheet(dialog_style)
                msg_box.exec()

    return authenticated


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    if not handle_authentication():
        sys.exit(0)  # Clean exit if authentication fails or is cancelled

    window = MainWindow()
    window.show()
    sys.exit(app.exec())