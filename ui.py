# ui.py
import random
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QHeaderView, QAction, QMenuBar
)
from PyQt5.QtGui import QKeySequence, QFont, QFontDatabase, QPainter, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, QPointF

class FloatingPixelsWidget(QWidget):
    def __init__(self, parent=None, pixel_count=100):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.pixels = []
        self.pixel_count = pixel_count
        self.init_pixels()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def init_pixels(self):
        self.pixels = []
        w = self.width() or 800
        h = self.height() or 480
        for _ in range(self.pixel_count):
            pos = QPointF(random.uniform(0, w), random.uniform(0, h))
            vel = QPointF(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3))
            size = random.uniform(1, 3)
            alpha = random.uniform(0.3, 1.0)
            self.pixels.append({'pos': pos, 'vel': vel, 'size': size, 'alpha': alpha})

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.init_pixels()

    def animate(self):
        w = self.width()
        h = self.height()
        for p in self.pixels:
            p['pos'] += p['vel']
            if p['pos'].x() < 0 or p['pos'].x() > w:
                p['vel'].setX(-p['vel'].x())
            if p['pos'].y() < 0 or p['pos'].y() > h:
                p['vel'].setY(-p['vel'].y())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.black)
        painter.setPen(Qt.NoPen)
        for p in self.pixels:
            color = QColor(255, 255, 255)
            color.setAlphaF(p['alpha'])
            painter.setBrush(color)
            painter.drawEllipse(p['pos'], p['size'], p['size'])

class Ui_LeaderboardPro(object):
    def setupUi(self, LeaderboardPro):
        LeaderboardPro.setWindowTitle("Chaotic Neutral's 'Leaderboard Manager' [Pro Edition]")
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        LeaderboardPro.setWindowIcon(QIcon(icon_path))
        LeaderboardPro.setGeometry(100, 100, 1400, 800)

        self.centralWidget = QWidget(LeaderboardPro)
        LeaderboardPro.setCentralWidget(self.centralWidget)
        self.main_layout = QHBoxLayout(self.centralWidget)

        self.bg = FloatingPixelsWidget(LeaderboardPro)
        self.bg.lower()
        self.bg.setGeometry(LeaderboardPro.rect())
        self.bg.show()

        self.left_layout = QVBoxLayout()

        # Top controls for page and view selectors
        self.top_controls = QHBoxLayout()
        self.top_controls.addStretch()
        self.page_selector = QComboBox()
        self.page_selector.setFont(QFont("Verdana", 18))  # Larger font for page selector
        self.top_controls.addWidget(self.page_selector)
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Table", "Chart"])
        self.view_selector.setFont(QFont("Verdana", 12))  # Smaller font for view selector
        self.top_controls.addWidget(self.view_selector)
        self.chart_type_selector = QComboBox()
        self.chart_type_selector.addItems(["Bar", "Horizontal Bar", "Line", "Scatter"])
        self.chart_type_selector.setFont(QFont("Verdana", 12))
        self.top_controls.addWidget(self.chart_type_selector)
        self.top_controls.addStretch()
        self.left_layout.addLayout(self.top_controls)

        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setSortingEnabled(True)
        self.left_layout.addWidget(self.table)

        self.figure, self.ax = plt.subplots(figsize=(9, 5))
        self.figure.patch.set_facecolor("#000")
        self.ax.set_facecolor("#000")
        self.canvas = FigureCanvas(self.figure)
        self.left_layout.addWidget(self.canvas)

        # Bottom controls for add/remove model
        self.bottom_controls = QHBoxLayout()
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("New Model Name")
        self.bottom_controls.addWidget(self.model_input)
        self.add_btn = QPushButton("Add Model")
        self.bottom_controls.addWidget(self.add_btn)
        self.remove_btn = QPushButton("Remove Selected Model")
        self.bottom_controls.addWidget(self.remove_btn)
        self.left_layout.addLayout(self.bottom_controls)

        self.left_widget = QWidget(LeaderboardPro)
        self.left_widget.setLayout(self.left_layout)
        self.main_layout.addWidget(self.left_widget, 3)

        self.control_layout = QVBoxLayout()

        self.right_widget = QWidget(LeaderboardPro)
        self.right_widget.setLayout(self.control_layout)
        self.main_layout.addWidget(self.right_widget, 1)

        self.menubar = LeaderboardPro.menuBar()
        self.customize_menu = self.menubar.addMenu("Customize")
        self.set_formula_action = QAction("Set Column Formula")
        self.customize_menu.addAction(self.set_formula_action)
        self.score_tiers_action = QAction("Manage Column Tiers")
        self.customize_menu.addAction(self.score_tiers_action)
        self.font_size_action = QAction("Change Font Size")
        self.customize_menu.addAction(self.font_size_action)
        self.font_family_action = QAction("Change Font Family")
        self.customize_menu.addAction(self.font_family_action)