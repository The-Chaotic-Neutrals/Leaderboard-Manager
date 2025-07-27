# shortcuts.py
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

def setup_shortcuts(window):
    window.undo_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z))
    window.undo_action.triggered.connect(window.undo)
    window.addAction(window.undo_action)

    window.open_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
    window.open_action.triggered.connect(window.import_data)
    window.addAction(window.open_action)

    window.save_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
    window.save_action.triggered.connect(window.save_session_manually)
    window.addAction(window.save_action)

    window.reload_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
    window.reload_action.triggered.connect(window.reload_session)
    window.addAction(window.reload_action)

    window.new_session_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_R))
    window.new_session_action.triggered.connect(window.new_session)
    window.addAction(window.new_session_action)

    window.export_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_E))

    window.add_model_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_M))

    window.remove_model_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Delete))

    window.table_view_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_T))

    window.chart_view_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_B))

    window.add_page_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))

    window.rename_page_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N))

    window.delete_page_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_D))

    window.add_column_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_A))

    window.rename_column_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_R))

    window.delete_column_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Delete))

    window.change_type_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_T))

    window.set_formula_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_F))
    window.score_tiers_action.setShortcut(QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_T))
    window.font_size_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_S))
    window.font_family_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F))

    window.toggle_legends_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
    window.addAction(window.toggle_legends_action)