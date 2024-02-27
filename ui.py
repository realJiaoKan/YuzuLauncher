from PySide6.QtWidgets import (QMainWindow, QMessageBox, QListWidget, QListWidgetItem, QScrollArea,
                               QWidget, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit)
from PySide6.QtGui import QIcon, QFont, QEnterEvent, QPixmap, QPainter, QPaintEvent
from PySide6.QtCore import Qt, QSize, QTimer, QRect, QEvent

from setting import setting

TEST_FLAG = True


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.takeAt(i).widget().setParent(None)


class QMarqueeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_offset)
        self.needScrolling = False
        self.checkNeedForScrolling()

    def setText(self, text):
        super().setText(text)
        self.checkNeedForScrolling()

    def resizeEvent(self, event):
        super().resizeEvent(event)  # Ensure the base class resize event is called
        self.checkNeedForScrolling()

    def checkNeedForScrolling(self):
        self.needScrolling = self.fontMetrics().horizontalAdvance(self.text()) > self.width()
        if self.needScrolling:
            self.timer.start(40)
        else:
            self.timer.stop()
            self.offset = 0
            self.update()

    def _update_offset(self):
        self.offset -= 1  # Adjust scrolling speed here
        if self.offset < -self.fontMetrics().horizontalAdvance(self.text()):
            self.offset = self.width()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        if self.needScrolling:
            painter = QPainter(self)
            textWidth = self.fontMetrics().horizontalAdvance(self.text())
            painter.drawText(QRect(self.offset, 0, textWidth, self.height()), self.alignment(), self.text())
        else:
            super().paintEvent(event)


class FolderCard(QWidget):
    def __init__(self, id, title, icon_path, banner_path):
        super().__init__()
        self.id = id
        self.title = title
        self.icon_path = icon_path
        self.banner_path = banner_path
        self.layout = QHBoxLayout()
        self.setStyleSheet("background-color: none;")

        # Icon
        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(70, 70)
        self.iconLabel.setPixmap(QIcon(icon_path).pixmap(self.iconLabel.size()))
        self.iconLabel.setAlignment(Qt.AlignCenter)

        # Divider
        self.divider = QLabel()
        self.divider.setFixedWidth(10)
        self.divider.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        # Title
        self.titleLabel = QLabel(title)
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setFont(QFont("Arial", setting.fontSize['folder_card']))

        # Layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.iconLabel)
        self.layout.addWidget(self.divider)
        self.layout.addWidget(self.titleLabel, 1)
        self.setLayout(self.layout)

    def clicked(self):
        pass  # To be modified dynamically in slots.py

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked()
        super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent):
        self.setStyleSheet("background-color: rgb(30, 30, 30);")
        self.divider.setStyleSheet("background-color: rgb(30, 30, 30);")

    def leaveEvent(self, event: QEnterEvent):
        self.setStyleSheet("background-color: none;")
        self.divider.setStyleSheet("background-color: none;")

    def clone(self):
        return FolderCard(self.id, self.title, self.icon_path, self.banner_path)


class AppCard(QWidget):
    def __init__(self, title, image_path, parent_folder_id, command, parameters):
        super(AppCard, self).__init__()
        self.title = title
        self.image_path = image_path
        self.parent_folder_id = parent_folder_id,
        self.command = command
        self.parameters = parameters
        self.setFixedSize(300, 300)

        # Background image
        self.backgroundLabel = QLabel(self)
        try:
            pixmap = QPixmap(image_path).scaled(300, 300, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.backgroundLabel.setPixmap(pixmap)
        except Exception as e:
            pixmap = QPixmap('default_icon.png').scaled(300, 300, Qt.KeepAspectRatioByExpanding,
                                                        Qt.SmoothTransformation)
            self.backgroundLabel.setPixmap(pixmap)
        self.backgroundLabel.setGeometry(0, 0, 300, 300)

        # Overlay
        overlay = QLabel(self)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        overlay.setGeometry(0, 200, 300, 100)

        # Title
        self.titleLabel = QMarqueeLabel(title, overlay)
        self.titleLabel.setGeometry(10, 0, 280, 100)
        self.titleLabel.setStyleSheet(f"color: white;"
                                      f"font-size: {setting.fontSize['app_card']}px;"
                                      f"background-color: rgba(0, 0, 0, 0);")

    def clicked(self):
        pass  # To be modified dynamically in slots.py

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked()
        super().mousePressEvent(event)

    def clone(self):
        return AppCard(self.title, self.image_path, self.parent_folder_id, self.command, self.parameters)


class FolderList(QListWidget):
    content = []

    def __init__(self):
        super().__init__()
        self.setFixedWidth(280)

    def refresh(self, folderCards=None):
        if folderCards is None:
            folderCards = self.content
        self.clear()
        self.content = [i.clone() for i in folderCards]
        for i in self.content:
            item = QListWidgetItem(self)
            item.setSizeHint(QSize(0, 70))
            item.id = i.id
            self.addItem(item)
            self.setItemWidget(item, i)


class AppList(QScrollArea):
    content = []

    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(30, 30, 30, 200)

        # Layout
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.layout.setSpacing(50)

    def refresh(self, appCards=None):
        if appCards is None:
            appCards = self.content
        clear_layout(self.layout)
        self.content = [i.clone() for i in appCards]
        if len(self.content) == 0:
            return
        num_per_row = self.width() // (self.content[0].width() + self.layout.spacing())
        for i, appCard in enumerate(self.content):
            self.layout.addWidget(appCard, i // num_per_row, i % num_per_row)
        self.widget.setLayout(self.layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(100, self.refresh)  # Idk why but without this is will be strange ()


class MenuItem(QPushButton):
    def __init__(self, content, offset, stage):
        super().__init__(content, stage)
        self.offset = offset
        self.stage = stage
        self.setGeometry(0, 0, 50, 50)
        self.setFont(QFont("Arial", 20))
        self.setStyleSheet(
            """
            QPushButton {
                border-radius: 25px;
                background-color: grey;
            }
            QPushButton:hover {
                background-color: rgba(252,201,185,0.5);
            }
            """
        )

    def updatePosition(self):
        x = self.stage.width() - self.width() - 20
        y = self.stage.height() - self.height() - 20 - self.offset * 70
        self.move(x, y)


class Menu:
    def __init__(self):
        self.items = []
        self.expended = False

    def addItem(self, menuItem: MenuItem):
        self.items.append(menuItem)

    def updatePosition(self):
        for i in self.items:
            i.updatePosition()

    def show(self):
        for i in self.items[1:]:
            i.show()
            self.expended = True

    def hide(self):
        for i in self.items[1:]:
            i.hide()
            self.expended = False

    def switch(self):
        if self.expended:
            self.hide()
        else:
            self.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_id = None
        self.setWindowTitle("Yuzu Launcher")
        self.setGeometry(50, 50, 1600, 900)
        self.canvas = QWidget()
        self.setCentralWidget(self.canvas)
        self.layout = QHBoxLayout(self.canvas)
        self.subWindow = None

        # Canvas
        self.folderList = FolderList()
        self.appList = AppList()

        # Menu
        self.menu = Menu()
        self.menu.addItem(MenuItem('+', 0, self))
        self.menu.addItem(MenuItem('📱', 1, self))
        self.menu.addItem(MenuItem('🗂️', 2, self))

        self.menu.items[0].clicked.connect(self.menu.switch)
        self.menu.items[1].clicked.connect(self.addApp)
        self.menu.items[2].clicked.connect(self.addFolder)
        self.menu.hide()

        # Layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.folderList)
        self.layout.addWidget(self.appList, 1)

    def addFolder(self):
        self.subWindow = AddFolderWindow()
        self.subWindow.show()

    def addApp(self):
        if self.folder_id is None:
            QMessageBox.warning(self, "Error", "Please select a folder first!")
            return
        self.subWindow = AddAppWindow()
        self.subWindow.show()

    def resizeEvent(self, event):
        self.menu.updatePosition()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and self.isExpanded:
            pass
        return super().eventFilter(obj, event)


class AddFolderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Folder")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Titles
        self.titles = QHBoxLayout()
        self.title1 = QLabel("Name")
        self.title2 = QLabel("Icon Path")
        self.title3 = QLabel("Banner Path")
        self.title1.setFixedWidth(150)
        self.title2.setFixedWidth(300)
        self.title3.setFixedWidth(300)
        self.titles.addWidget(self.title1)
        self.titles.addWidget(self.title2)
        self.titles.addWidget(self.title3)

        # Rows
        self.rows = []

        # Buttons
        self.buttons = QHBoxLayout()
        self.addButton = QPushButton("Add a Row")
        self.removeButton = QPushButton("Delete a Row")
        self.saveButton = QPushButton("Save")
        self.addButton.setFixedWidth(150)
        self.removeButton.setFixedWidth(300)
        self.saveButton.setFixedWidth(300)
        self.buttons.addWidget(self.addButton)
        self.buttons.addWidget(self.removeButton)
        self.buttons.addWidget(self.saveButton)

        self.addButton.clicked.connect(self.addRow)
        self.removeButton.clicked.connect(self.removeRow)
        self.saveButton.clicked.connect(self.saveData)

        # Layout
        self.layout.addLayout(self.titles)
        self.layout.addLayout(self.buttons)
        self.addRow()

    def addRow(self):
        row = QHBoxLayout()
        column1 = QLineEdit()
        column2 = QLineEdit()
        column3 = QLineEdit()
        column1.setFixedWidth(150)
        column2.setFixedWidth(300)
        column3.setFixedWidth(300)
        row.addWidget(column1)
        row.addWidget(column2)
        row.addWidget(column3)
        self.layout.insertLayout(self.layout.count() - 1, row)
        self.rows.append(row)

    def removeRow(self):
        if self.rows:
            row = self.rows.pop()
            while row.count():
                item = row.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.layout.removeItem(row)

    def saveData(self):
        pass  # To be modified in slots.py


class AddAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add App")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Titles
        self.titles = QHBoxLayout()
        self.title1 = QLabel("Name")
        self.title2 = QLabel("Background Path")
        self.title3 = QLabel("Command")
        self.title1.setFixedWidth(150)
        self.title2.setFixedWidth(300)
        self.title3.setFixedWidth(300)
        self.titles.addWidget(self.title1)
        self.titles.addWidget(self.title2)
        self.titles.addWidget(self.title3)

        # Rows
        self.rows = []

        # Buttons
        self.buttons = QHBoxLayout()
        self.addButton = QPushButton("Add a Row")
        self.removeButton = QPushButton("Delete a Row")
        self.saveButton = QPushButton("Save")
        self.addButton.setFixedWidth(150)
        self.removeButton.setFixedWidth(300)
        self.saveButton.setFixedWidth(300)
        self.buttons.addWidget(self.addButton)
        self.buttons.addWidget(self.removeButton)
        self.buttons.addWidget(self.saveButton)

        self.addButton.clicked.connect(self.addRow)
        self.removeButton.clicked.connect(self.removeRow)
        self.saveButton.clicked.connect(self.saveData)

        # Layout
        self.layout.addLayout(self.titles)
        self.layout.addLayout(self.buttons)
        self.addRow()

    def addRow(self):
        row = QHBoxLayout()
        column1 = QLineEdit()
        column2 = QLineEdit()
        column3 = QLineEdit()
        column1.setFixedWidth(150)
        column2.setFixedWidth(300)
        column3.setFixedWidth(300)
        row.addWidget(column1)
        row.addWidget(column2)
        row.addWidget(column3)
        self.layout.insertLayout(self.layout.count() - 1, row)
        self.rows.append(row)

    def removeRow(self):
        if self.rows:
            row = self.rows.pop()
            while row.count():
                item = row.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.layout.removeItem(row)

    def saveData(self):
        pass  # To be modified in slots.py
