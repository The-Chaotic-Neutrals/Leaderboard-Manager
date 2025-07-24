# shortcuts.py
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

def setup_shortcuts(window):
    window.undo_action = QAction("Undo", window)
    window.undo_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z))
    window.undo_action.triggered.connect(window.undo)
    window.addAction(window.undo_action)

    window.open_action = QAction("Open", window)
    window.open_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
    window.open_action.triggered.connect(window.import_data)
    window.addAction(window.open_action)

    window.save_action = QAction("Save", window)
    window.save_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
    window.save_action.triggered.connect(window.save_session_manually)
    window.addAction(window.save_action)

    window.reload_action = QAction("Reload", window)
    window.reload_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
    window.reload_action.triggered.connect(window.reload_session)
    window.addAction(window.reload_action)