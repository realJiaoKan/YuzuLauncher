import sys, enum
from dataclasses import dataclass

from PySide6.QtWidgets import (QMainWindow, QMessageBox, QListWidget, QListWidgetItem, QScrollArea,
                               QWidget, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel, QPushButton,
                               QLineEdit, QMenu, QSpacerItem, QSizePolicy)
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QPaintEvent
from PySide6.QtCore import Qt, QSize, QTimer, QRect

from setting import setting, SettingMenu

TEST_FLAG = True


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.takeAt(i).widget().setParent(None)


class Edge(enum.Flag):
    NoEdge: Qt.Edge = 0
    TopEdge: Qt.Edge = 1
    LeftEdge: Qt.Edge = 2
    RightEdge: Qt.Edge = 3
    BottomEdge: Qt.Edge = 4
    LeftTopEdge: Qt.Edge = 5
    RightTopEdge: Qt.Edge = 6
    LeftBottomEdge: Qt.Edge = 7
    RightBottomEdge: Qt.Edge = 8


@dataclass
class EdgePress:
    leftEdgePress: bool = False
    rightEdgePress: bool = False
    topEdgePress: bool = False
    bottomEdgePress: bool = False
    leftTopEdgePress: bool = False
    rightBottomEdgePress: bool = False
    leftBottomEdgePress: bool = False
    rightTopEdgePress: bool = False
    moveEdgePress: bool = False
    movePosition = None


class QMarqueeLabel(QLabel):
    def __init__(self, text="", parent=None, font='default', font_size=20, always_scroll=False):
        super().__init__(text, parent)
        self.always_scroll = always_scroll
        self.offset = 0
        self.setFont(QFont(setting.font[font], font_size))
        self.enableScroll = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_offset)
        self.timer.start(40)

        self.needScroll = self.fontMetrics().horizontalAdvance(self.text()) > (self.width() - 10)

    def setText(self, text):
        super().setText(text)
        self._update_offset()

    def enterEvent(self, event):
        if self.always_scroll:
            return
        self.enableScroll = True

    def leaveEvent(self, event):
        if self.always_scroll:
            return
        self.enableScroll = False

    def resizeEvent(self, event):
        super().resizeEvent(event)  # Ensure the base class resize event is called
        self.needScroll = self.fontMetrics().horizontalAdvance(self.text()) > (self.width() - 10)

    def _update_offset(self):
        if self.needScroll and (self.enableScroll or self.always_scroll):
            self.offset -= 1  # Adjust scrolling speed here
            if self.offset < -self.fontMetrics().horizontalAdvance(self.text()):
                self.offset = self.width()
            self.update()
            self.timer.start(40)
        else:
            self.offset = 0
            self.update()

    def paintEvent(self, event: QPaintEvent):
        if self.needScroll and (self.enableScroll or self.always_scroll):
            painter = QPainter(self)
            textWidth = self.fontMetrics().horizontalAdvance(self.text())
            painter.drawText(QRect(self.offset, 0, textWidth, self.height()), self.alignment(), self.text())
        else:
            super().paintEvent(event)


class FolderCard(QWidget):
    def __init__(self, id, title, icon_path, banner_path, font='default'):
        super().__init__()
        self.id = id
        self.title = title
        self.icon_path = icon_path
        self.banner_path = banner_path
        self.font = font
        self.layout = QHBoxLayout()
        self.subWindow = None

        # Icon
        self.iconLabel = QLabel()
        self.iconLabel.setFixedSize(70, 70)
        self.iconLabel.setPixmap(QIcon(icon_path).pixmap(self.iconLabel.size()))
        self.iconLabel.setAlignment(Qt.AlignCenter)

        # Divider
        self.divider = QLabel()
        self.divider.setFixedWidth(10)

        # Title
        self.titleLabel = QMarqueeLabel(title, self, 'default', setting.fontSize['folder_card'])
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

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

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        modify = contextMenu.addAction("Modify")
        remove = contextMenu.addAction("Remove")

        action = contextMenu.exec(self.mapToGlobal(event.pos()))

        if action == modify:
            self.modify()
        if action == remove:
            self.remove()

    def modify(self):
        self.subWindow = ModifyFolderWindow(self)
        self.subWindow.show()

    def remove(self):
        pass

    def clone(self):
        return FolderCard(self.id, self.title, self.icon_path, self.banner_path, self.font)


class AppCard(QWidget):
    def __init__(self, id, title, image_path, parent_folder_id, command, parameters, font='default'):
        super(AppCard, self).__init__()
        self.id = id
        self.title = title
        self.image_path = image_path
        self.parent_folder_id = parent_folder_id,
        self.command = command
        self.parameters = parameters
        self._font = font
        self.setFixedSize(300, 300)
        self.subWindow = None

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
        self.titleLabel = QMarqueeLabel(title, overlay, font, setting.fontSize['app_card'], True)
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

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        modify = contextMenu.addAction("Modify")
        remove = contextMenu.addAction("Remove")

        action = contextMenu.exec(self.mapToGlobal(event.pos()))

        if action == modify:
            self.modify()
        if action == remove:
            self.remove()

    def modify(self):
        self.subWindow = ModifyAppWindow(self)
        self.subWindow.show()

    def remove(self):
        pass

    def clone(self):
        return AppCard(self.id, self.title, self.image_path, self.parent_folder_id, self.command, self.parameters,
                       self._font)


class FolderList(QListWidget):
    content = []

    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet('''
        QListWidget {
            background-color: rgba(0, 0, 0, 0);
        }
        QListWidget::item {
            background-color: rgba(0, 0, 0, 0.5);
        }
        QListWidget::item:hover {
            background-color: rgba(252, 201, 185, 0.5);
        }
        QListWidget::item:selected {
            background-color: rgba(252, 201, 185, 0.5);
        }
        ''')

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
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

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
                background-color: rgba(0, 0, 0, 0.5);
            }
            QPushButton:hover {
                background-color: rgba(252, 201, 185, 0.5);
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
        self.pixmap = QPixmap(setting.background)
        self.resize_needed = True

        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.edge_size = 5
        self.xRadius = 5
        self.yRadius = 5
        self.min_width = 50
        self.min_height = 50
        self.edge_press = EdgePress()
        self.move_event_height = 40

        # Titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.titleBar = QWidget()
        self.titleLayout = QHBoxLayout()
        self.titleBar.setLayout(self.titleLayout)
        self.titleBar.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

        self.titleLabel = QLabel("Yuzu Launcher")
        self.titleBar.setStyleSheet(
            """
            QPushButton {
                border-radius: 8px;
            }
            """
        )
        self.closeButton = QPushButton()
        self.closeButton.setFixedSize(16, 16)
        self.closeButton.setStyleSheet("background-color: rgb(255, 59, 48);")
        self.fullScreenButton = QPushButton()
        self.fullScreenButton.setFixedSize(16, 16)
        self.fullScreenButton.setStyleSheet("background-color: rgb(255, 149, 0);")
        self.minimizeButton = QPushButton()
        self.minimizeButton.setFixedSize(16, 16)
        self.minimizeButton.setStyleSheet("background-color: rgb(76, 217, 0);")

        self.closeButton.clicked.connect(self.close)
        self.fullScreenButton.clicked.connect(self.toggleFullScreen)
        self.minimizeButton.clicked.connect(self.showMinimized)

        self.titleLayout.addWidget(self.closeButton)
        self.titleLayout.addWidget(self.fullScreenButton)
        self.titleLayout.addWidget(self.minimizeButton)
        self.titleLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addSpacing(self.closeButton.width() * 3)
        self.titleLayout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.setMenuWidget(self.titleBar)

        # Canvas
        self.canvas.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        self.folderList = FolderList()
        self.appList = AppList()

        # Menu
        self.menu = Menu()
        self.menu.addItem(MenuItem('+', 0, self))
        self.menu.addItem(MenuItem('📱', 1, self))
        self.menu.addItem(MenuItem('🗂️', 2, self))
        self.menu.addItem(MenuItem('⚙️', 3, self))

        self.menu.items[0].clicked.connect(self.menu.switch)
        self.menu.items[1].clicked.connect(self.addApp)
        self.menu.items[2].clicked.connect(self.addFolder)
        self.menu.items[3].clicked.connect(self.setting)

        if sys.platform == 'win32':
            self.menu.addItem(MenuItem('📥', 4, self))
            self.menu.items[4].clicked.connect(self.import_)

        self.menu.hide()

        # Layout
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.folderList)
        self.layout.addWidget(self.appList, 1)

        # Extra Stylesheet
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.backgroundMask = QWidget(self)
        self.backgroundMask.setGeometry(self.rect())
        self.backgroundMask.setStyleSheet(setting.background_mask)
        self.backgroundMask.lower()

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def addFolder(self):
        self.subWindow = AddFolderWindow()
        self.subWindow.show()

    def addApp(self):
        if self.folder_id is None:
            QMessageBox.warning(self, "Error", "Please select a folder first!")
            return
        self.subWindow = AddAppWindow()
        self.subWindow.show()

    def setting(self):
        self.subWindow = SettingMenu()
        self.subWindow.show()

    def import_(self):
        self.subWindow = Import()
        self.subWindow.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        bgPixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        startX = (self.width() - bgPixmap.width()) / 2
        startY = (self.height() - bgPixmap.height()) / 2

        painter.drawPixmap(startX, startY, bgPixmap)
        self.backgroundMask.setGeometry(self.rect())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.NoButton:
            pos = event.globalPosition().toPoint() - self.pos()
            edges = self._get_edges(pos)

            if edges == Edge.LeftEdge or edges == Edge.RightEdge:
                self.setCursor(Qt.SizeHorCursor)
            elif edges == Edge.TopEdge or edges == Edge.BottomEdge:
                self.setCursor(Qt.SizeVerCursor)
            elif edges == Edge.LeftTopEdge or edges == Edge.RightBottomEdge:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edges == Edge.LeftBottomEdge or edges == Edge.RightTopEdge:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        elif event.buttons() == Qt.MouseButton.LeftButton:
            if self.edge_press.moveEdgePress:
                self.move(event.globalPosition().toPoint() - self.edge_press.movePosition)
            elif self._get_edge_press() is not Edge.NoEdge:
                self._resize_window(event.globalPosition().toPoint() - self.pos())

    def mousePressEvent(self, event) -> None:
        pos = event.globalPosition().toPoint() - self.pos()
        edges = self._get_edges(pos)
        if edges == Edge.LeftEdge:
            self.edge_press.leftEdgePress = True
        elif edges == Edge.RightEdge:
            self.edge_press.rightEdgePress = True
        elif edges == Edge.TopEdge:
            self.edge_press.topEdgePress = True
        elif edges == Edge.BottomEdge:
            self.edge_press.bottomEdgePress = True
        elif edges == Edge.LeftTopEdge:
            self.edge_press.leftTopEdgePress = True
        elif edges == Edge.RightBottomEdge:
            self.edge_press.rightBottomEdgePress = True
        elif edges == Edge.LeftBottomEdge:
            self.edge_press.leftBottomEdgePress = True
        elif edges == Edge.RightTopEdge:
            self.edge_press.rightTopEdgePress = True
        else:
            if self._get_move_edges(pos):
                self.edge_press.moveEdgePress = True
                self.edge_press.movePosition = event.globalPosition().toPoint() - self.pos()
                self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseReleaseEvent(self, event) -> None:
        self.edge_press.leftEdgePress = False
        self.edge_press.rightEdgePress = False
        self.edge_press.topEdgePress = False
        self.edge_press.bottomEdgePress = False
        self.edge_press.leftTopEdgePress = False
        self.edge_press.rightBottomEdgePress = False
        self.edge_press.leftBottomEdgePress = False
        self.edge_press.rightTopEdgePress = False
        self.edge_press.moveEdgePress = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _get_move_edges(self, pos):
        in_move_edge: bool = pos.y() <= self.move_event_height
        not_in_edges: bool = self._get_edges(pos) == Edge.NoEdge
        return in_move_edge and not_in_edges

    def _get_edges(self, pos):
        edges = Edge.NoEdge

        in_left_edge: bool = pos.x() <= self.edge_size  # 左
        in_right_edge: bool = pos.x() >= (self.width() - self.edge_size)  # 右
        in_top_edge: bool = pos.y() <= self.edge_size  # 上
        in_bottom_edge: bool = pos.y() >= (self.height() - self.edge_size)  # 下

        size = len([i for i in [in_left_edge, in_right_edge, in_top_edge, in_bottom_edge] if i])

        if size == 0:
            return edges
        if size == 1:
            if in_left_edge:
                return Edge.LeftEdge
            if in_right_edge:
                return Edge.RightEdge
            if in_top_edge:
                return Edge.TopEdge
            if in_bottom_edge:
                return Edge.BottomEdge
        if size == 2:
            if in_left_edge and in_top_edge:
                return Edge.LeftTopEdge
            if in_left_edge and in_bottom_edge:
                return Edge.LeftBottomEdge
            if in_right_edge and in_top_edge:
                return Edge.RightTopEdge
            if in_right_edge and in_bottom_edge:
                return Edge.RightBottomEdge

    def _get_edge_press(self):
        if self.edge_press.leftEdgePress:
            return Edge.LeftEdge
        elif self.edge_press.rightEdgePress:
            return Edge.RightEdge
        elif self.edge_press.topEdgePress:
            return Edge.TopEdge
        elif self.edge_press.bottomEdgePress:
            return Edge.BottomEdge
        elif self.edge_press.leftTopEdgePress:
            return Edge.LeftTopEdge
        elif self.edge_press.rightBottomEdgePress:
            return Edge.RightBottomEdge
        elif self.edge_press.leftBottomEdgePress:
            return Edge.LeftBottomEdge
        elif self.edge_press.rightTopEdgePress:
            return Edge.RightTopEdge
        else:
            return Edge.NoEdge

    def _resize_window(self, pos):
        edges = self._get_edge_press()
        geo = self.frameGeometry()
        x, y, width, height = geo.x(), geo.y(), geo.width(), geo.height()
        if edges is Edge.LeftEdge:
            width -= pos.x()
            if width <= self.min_width:
                return
            else:
                x += pos.x()
        elif edges is Edge.RightEdge:
            width = pos.x()
            if width <= self.min_width:
                return
        elif edges is Edge.TopEdge:
            height -= pos.y()
            if height <= self.min_height:
                return
            else:
                y += pos.y()
        elif edges is Edge.BottomEdge:
            height = pos.y()
            if height <= self.min_height:
                return
        elif edges is Edge.LeftTopEdge:
            width -= pos.x()
            if width <= self.min_width:
                width = geo.width()
            else:
                x += pos.x()
            height -= pos.y()
            if height <= self.min_height:
                height = geo.height()
            else:
                y += pos.y()
        elif edges is Edge.LeftBottomEdge:
            width -= pos.x()
            if width <= self.min_width:
                width = geo.width()
            else:
                x += pos.x()
            height = pos.y()
            if height <= self.min_height:
                height = geo.height()
        elif edges is Edge.RightTopEdge:
            width = pos.x()
            if width <= self.min_width:
                width = geo.width()
            height -= pos.y()
            if height <= self.min_height:
                height = geo.height()
            else:
                y += pos.y()
        elif edges is Edge.RightBottomEdge:
            width = pos.x()
            if width <= self.min_width:
                width = geo.width()
            height = pos.y()
            if height <= self.min_height:
                height = geo.height()
        self.setGeometry(x, y, width, height)

    def resizeEvent(self, event):
        self.menu.updatePosition()
        self.setCursor(Qt.CursorShape.ArrowCursor)


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
        self.title4 = QLabel("Parameters")
        self.title1.setFixedWidth(150)
        self.title2.setFixedWidth(300)
        self.title3.setFixedWidth(300)
        self.title4.setFixedWidth(300)
        self.titles.addWidget(self.title1)
        self.titles.addWidget(self.title2)
        self.titles.addWidget(self.title3)
        self.titles.addWidget(self.title4)

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
        column4 = QLineEdit()
        column1.setFixedWidth(150)
        column2.setFixedWidth(300)
        column3.setFixedWidth(300)
        column4.setFixedWidth(300)
        row.addWidget(column1)
        row.addWidget(column2)
        row.addWidget(column3)
        row.addWidget(column4)
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


class Import(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Import")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("Path: ")
        self.path = QLineEdit()
        self.path.setFixedWidth(300)
        self.saveButton = QPushButton("Save")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.path)
        self.layout.addWidget(self.saveButton)

        self.saveButton.clicked.connect(self.saveData)

    def saveData(self):
        pass  # To be modified in slots.py


class ModifyFolderWindow(QWidget):
    def __init__(self, parent: FolderCard):
        super().__init__()
        self.setWindowTitle("Add Folder")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.id = parent.id

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

        # LineEdits
        self.lineEdits = QHBoxLayout()
        self.column1 = QLineEdit(parent.title if parent.title else '')
        self.column2 = QLineEdit(parent.icon_path if parent.icon_path else '')
        self.column3 = QLineEdit(parent.banner_path if parent.banner_path else '')
        self.column1.setFixedWidth(150)
        self.column2.setFixedWidth(300)
        self.column3.setFixedWidth(300)
        self.lineEdits.addWidget(self.column1)
        self.lineEdits.addWidget(self.column2)
        self.lineEdits.addWidget(self.column3)

        # Buttons
        self.buttons = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.buttons.addStretch()
        self.buttons.addWidget(self.saveButton)

        self.saveButton.clicked.connect(self.saveData)

        # Layout
        self.layout.addLayout(self.titles)
        self.layout.addLayout(self.lineEdits)
        self.layout.addLayout(self.buttons)

    def saveData(self):
        pass  # To be modified in slots.py


class ModifyAppWindow(QWidget):
    def __init__(self, parent: AppCard):
        super().__init__()
        self.setWindowTitle("Add App")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.id = parent.id

        # Titles
        self.titles = QHBoxLayout()
        self.title1 = QLabel("Name")
        self.title2 = QLabel("Background Path")
        self.title3 = QLabel("Command")
        self.title4 = QLabel("Parameters")
        self.title1.setFixedWidth(150)
        self.title2.setFixedWidth(300)
        self.title3.setFixedWidth(300)
        self.title4.setFixedWidth(300)
        self.titles.addWidget(self.title1)
        self.titles.addWidget(self.title2)
        self.titles.addWidget(self.title3)
        self.titles.addWidget(self.title4)

        # LineEdits
        self.lineEdits = QHBoxLayout()
        self.column1 = QLineEdit(parent.title)
        self.column2 = QLineEdit(parent.image_path if parent.image_path else '')
        self.column3 = QLineEdit(' '.join(parent.command) if parent.command else '')
        self.column4 = QLineEdit(' '.join(parent.parameters) if parent.parameters else '')
        self.column1.setFixedWidth(150)
        self.column2.setFixedWidth(300)
        self.column3.setFixedWidth(300)
        self.column4.setFixedWidth(300)
        self.lineEdits.addWidget(self.column1)
        self.lineEdits.addWidget(self.column2)
        self.lineEdits.addWidget(self.column3)
        self.lineEdits.addWidget(self.column4)

        # Buttons
        self.buttons = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.buttons.addStretch()
        self.buttons.addWidget(self.saveButton)

        self.saveButton.clicked.connect(self.saveData)

        # Layout
        self.layout.addLayout(self.titles)
        self.layout.addLayout(self.lineEdits)
        self.layout.addLayout(self.buttons)

    def saveData(self):
        pass  # To be modified in slots.py
