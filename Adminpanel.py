import sys
import json
import datetime
import base64
import requests

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

# 🔐 CONFIG
GITHUB_TOKEN = "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"
USERNAME = "HotWheels-gtx-97"
REPO = "Shop"
FILE_PATH = "products.json"

CATEGORIES = ["bestseller", "mostwanted", "limited", "newarrival", "rare", "giftset"]
AVAILABILITY = ["in-stock", "low-stock", "sold-out"]

# LOAD FROM GITHUB
def load_data():
    try:
        url = f"https://api.github.com/repos/HotWheels-gtx-97/Shop/contents/products.json"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            raise Exception(res.json())

        data = res.json()
        content = base64.b64decode(data["content"]).decode()
        json_data = json.loads(content)

        return json_data.get("products", [])

    except Exception as e:
        QMessageBox.warning(None, "Error", f"Load failed:\n{e}")
        return []

# PUSH TO GITHUB
def push_data(data):
    try:
        url = f"https://api.github.com/repos/HotWheels-gtx-97/Shop/contents/products.json"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        res = requests.get(url, headers=headers)
        file_data = res.json()
        sha = file_data["sha"]

        new_json = json.dumps({"products": data}, indent=4)
        encoded = base64.b64encode(new_json.encode()).decode()

        payload = {
            "message": f"Admin Auto-Sync {datetime.datetime.now()}",
            "content": encoded,
            "sha": sha
        }

        res = requests.put(url, headers=headers, json=payload)

        return res.status_code in [200, 201]

    except Exception as e:
        QMessageBox.warning(None, "Error", f"Push failed:\n{e}")
        return False

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel")
        self.setGeometry(200, 160, 800, 600)

        self.data = load_data()
        self.unsaved_changes = False

        layout = QVBoxLayout()

        # TOP BAR
        top_bar = QHBoxLayout()

        self.status = QLabel("✅ Synced")
        self.status.setStyleSheet("color: green; font-weight: bold;")

        self.sync_btn = QPushButton("Send▶️")
        self.sync_btn.setFixedSize(60, 40)
        self.sync_btn.clicked.connect(self.sync_now)

        top_bar.addWidget(self.status)
        top_bar.addStretch()
        top_bar.addWidget(self.sync_btn)

        layout.addLayout(top_bar)

        # TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Price", "Image URL", "Info"])
        self.table.cellClicked.connect(self.load_selected)
        layout.addWidget(self.table)

        # INPUTS
        self.name = QLineEdit()
        self.price = QLineEdit()
        self.img = QLineEdit()
        self.info = QLineEdit()

        self.category = QComboBox()
        self.category.addItems(CATEGORIES)

        self.availability = QComboBox()
        self.availability.addItems(AVAILABILITY)

        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Price"))
        layout.addWidget(self.price)

        layout.addWidget(QLabel("Category"))
        layout.addWidget(self.category)

        layout.addWidget(QLabel("Availability"))
        layout.addWidget(self.availability)

        layout.addWidget(QLabel("Image URL"))
        layout.addWidget(self.img)

        layout.addWidget(QLabel("Info"))
        layout.addWidget(self.info)

        # BUTTONS
        btn_layout = QHBoxLayout()

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.clear_inputs)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)

        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self.update_item)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_item)

        move_up_btn = QPushButton("⬆")
        move_up_btn.clicked.connect(self.move_up)

        move_down_btn = QPushButton("⬇")
        move_down_btn.clicked.connect(self.move_down)

        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(move_up_btn)
        btn_layout.addWidget(move_down_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.refresh_table()

    def mark_unsaved(self):
        self.unsaved_changes = True
        self.status.setText("⚠️ Unsaved")
        self.status.setStyleSheet("color: orange; font-weight: bold;")

    # ✅ CONFIRMATION ADDED HERE
    def sync_now(self):
        if not self.unsaved_changes:
            QMessageBox.information(self, "Info", "No changes to sync")
            return

        if QMessageBox.question(self, "Confirm", "Send all changes to GitHub?") != QMessageBox.StandardButton.Yes:
            return

        if push_data(self.data):
            self.unsaved_changes = False
            self.status.setText("✅ Synced")
            self.status.setStyleSheet("color: green; font-weight: bold;")
            QMessageBox.information(self, "Success", "All changes pushed 🚀")
        else:
            QMessageBox.warning(self, "Error", "Sync failed")

    def refresh_table(self):
        self.table.setRowCount(len(self.data))
        for row, item in enumerate(self.data):
            self.table.setItem(row, 0, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.get("price", ""))))
            img = item.get("images", [""])
            self.table.setItem(row, 2, QTableWidgetItem(img[0]))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("description", "")))

    # ✅ CONFIRMATION ADDED
    def add_item(self):
        if QMessageBox.question(self, "Confirm", "Add this product?") != QMessageBox.StandardButton.Yes:
            return

        item = {
            "id": max([i.get("id", 0) for i in self.data], default=0) + 1,
            "name": self.name.text(),
            "price": int(self.price.text()) if self.price.text().isdigit() else 0,
            "category": self.category.currentText(),
            "availability": self.availability.currentText(),
            "images": [self.img.text()],
            "description": self.info.text()
        }

        self.data.insert(0, item)
        self.mark_unsaved()
        self.refresh_table()

    # ✅ CONFIRMATION ADDED
    def update_item(self):
        row = self.table.currentRow()
        if row < 0:
            return

        if QMessageBox.question(self, "Confirm", "Update this product?") != QMessageBox.StandardButton.Yes:
            return

        self.data[row]["name"] = self.name.text()
        self.data[row]["price"] = int(self.price.text()) if self.price.text().isdigit() else 0
        self.data[row]["category"] = self.category.currentText()
        self.data[row]["availability"] = self.availability.currentText()
        self.data[row]["images"] = [self.img.text()]
        self.data[row]["description"] = self.info.text()

        self.mark_unsaved()
        self.refresh_table()

    # ✅ CONFIRMATION ADDED
    def delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            return

        if QMessageBox.question(self, "Confirm", "Delete this product?") != QMessageBox.StandardButton.Yes:
            return

        self.data.pop(row)
        self.mark_unsaved()
        self.refresh_table()

    def move_up(self):
        row = self.table.currentRow()
        if row <= 0:
            return

        self.data[row], self.data[row - 1] = self.data[row - 1], self.data[row]
        self.mark_unsaved()
        self.refresh_table()
        self.table.selectRow(row - 1)

    def move_down(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.data) - 1:
            return

        self.data[row], self.data[row + 1] = self.data[row + 1], self.data[row]
        self.mark_unsaved()
        self.refresh_table()
        self.table.selectRow(row + 1)

    def load_selected(self, row, col):
        item = self.data[row]
        self.name.setText(item.get("name", ""))
        self.price.setText(str(item.get("price", "")))
        self.img.setText(item.get("images", [""])[0])
        self.info.setText(item.get("description", ""))

    def clear_inputs(self):
        self.name.clear()
        self.price.clear()
        self.img.clear()
        self.info.clear()

app = QApplication(sys.argv)
window = AdminPanel()
window.show()
sys.exit(app.exec())
