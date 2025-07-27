# leaderboard_pro.py
import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QLabel, QMenu, QAction, QDialog, QVBoxLayout, QCheckBox, QPushButton, QListWidget, QListWidgetItem, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
from ui import Ui_LeaderboardPro
import data_model
import shortcuts
from table_handler import TableHandler
from style_handler import StyleHandler
from chart_handler import ChartHandler
from action_handler import ActionHandler
from file_io import load_multi, save_multi


class LeaderboardPro(QMainWindow, Ui_LeaderboardPro):
    DF_ROW_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.font_size = 16
        self.font_family = "Verdana"
        self.chart_base_font_size = 12
        self.current_view = "Table"
        self.has_been_sorted = False
        self.current_sort_col = 0
        self.current_sort_order = Qt.AscendingOrder
        self.show_legends = True

        self.data_models = load_multi(data_model.DataModel.SESSION_FILE) if os.path.exists(data_model.DataModel.SESSION_FILE) else [data_model.DataModel()]

        for dm in self.data_models:
            dm.all_data_models = self.data_models
            self.page_selector.addItem(dm.page_name)

        # Recompute after all models are loaded and all_data_models is set
        if self.data_models:
            self.data_models[0].recompute_all_computed()

        self.current_page = 0
        self.page_selector.setCurrentIndex(0)
        self.data_model = self.data_models[self.current_page]

        self.style_handler = StyleHandler(self)
        self.table_handler = TableHandler(self)
        self.chart_handler = ChartHandler(self)
        self.action_handler = ActionHandler(self)

        self.page_selector.currentIndexChanged.connect(self.change_page)
        self.chart_type_selector.currentTextChanged.connect(self.update_chart)
        self.chart_type_selector.hide()  # Hide initially
        self.apply_styles()
        self.refresh_table()
        self.change_view(self.current_view)
        self.update_legends()

        self.undo_action = QAction("Undo", self)
        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)
        self.reload_action = QAction("Reload", self)
        self.new_session_action = QAction("New Session", self)

        # Set action texts
        self.open_action.setText("Import Data (CSV/Excel)")
        self.save_action.setText("Save Session")
        self.reload_action.setText("Reload Session")
        self.new_session_action.setText("New Session")

        # Create export action
        self.export_action = QAction("Export Current Session", self)
        self.export_action.triggered.connect(self.export_session)

        # Add File menu
        self.file_menu = QMenu("File", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.file_menu)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.export_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.undo_action)
        self.file_menu.addAction(self.reload_action)
        self.file_menu.addAction(self.new_session_action)

        # Add Model menu
        self.model_menu = QMenu("Model", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.model_menu)
        self.add_model_action = QAction("Add Model", self)
        self.add_model_action.triggered.connect(self.action_handler.add_model)
        self.model_menu.addAction(self.add_model_action)
        self.remove_model_action = QAction("Remove Selected", self)
        self.remove_model_action.triggered.connect(self.action_handler.remove_selected)
        self.model_menu.addAction(self.remove_model_action)

        # Add View menu
        self.view_menu = QMenu("View", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.view_menu)
        self.table_view_action = QAction("Table", self)
        self.table_view_action.triggered.connect(lambda: self.view_selector.setCurrentText("Table"))
        self.view_menu.addAction(self.table_view_action)
        self.chart_view_action = QAction("Chart", self)
        self.chart_view_action.triggered.connect(lambda: self.view_selector.setCurrentText("Chart"))
        self.view_menu.addAction(self.chart_view_action)
        self.toggle_legends_action = QAction("Show Legends", self)
        self.toggle_legends_action.setCheckable(True)
        self.toggle_legends_action.setChecked(True)
        self.toggle_legends_action.triggered.connect(self.toggle_legends)
        self.view_menu.addAction(self.toggle_legends_action)

        # Add Page menu
        self.page_menu = QMenu("Page", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.page_menu)
        self.add_page_action = QAction("Add Page", self)
        self.add_page_action.triggered.connect(self.action_handler.add_page)
        self.page_menu.addAction(self.add_page_action)
        self.rename_page_action = QAction("Rename Page", self)
        self.rename_page_action.triggered.connect(self.action_handler.rename_page)
        self.page_menu.addAction(self.rename_page_action)
        self.delete_page_action = QAction("Delete Page", self)
        self.delete_page_action.triggered.connect(self.action_handler.delete_page)
        self.page_menu.addAction(self.delete_page_action)

        # Add Column menu
        self.column_menu = QMenu("Column", self)
        self.menuBar().insertMenu(self.customize_menu.menuAction(), self.column_menu)
        self.add_column_action = QAction("Add Column", self)
        self.add_column_action.triggered.connect(self.action_handler.add_column)
        self.column_menu.addAction(self.add_column_action)
        self.rename_column_action = QAction("Rename Column", self)
        self.rename_column_action.triggered.connect(self.action_handler.rename_column)
        self.column_menu.addAction(self.rename_column_action)
        self.change_type_action = QAction("Change Column Type", self)
        self.change_type_action.triggered.connect(self.action_handler.change_column_type)
        self.column_menu.addAction(self.change_type_action)
        self.delete_column_action = QAction("Delete Column", self)
        self.delete_column_action.triggered.connect(self.action_handler.delete_column)
        self.column_menu.addAction(self.delete_column_action)

        # Add Plot menu
        self.plot_menu = QMenu("Plot", self)
        self.menuBar().addMenu(self.plot_menu)
        self.select_plot_columns_action = QAction("Select Columns to Plot", self)
        self.select_plot_columns_action.triggered.connect(self.select_plot_columns)
        self.plot_menu.addAction(self.select_plot_columns_action)

        # Shortcuts
        shortcuts.setup_shortcuts(self)

    def select_plot_columns(self):
        numeric_cols = [col for col, typ in self.data_model.column_types.items() if typ in ["integer", "float", "boolean"]]
        dlg = QDialog(self)
        dlg.setWindowTitle("Select Columns to Plot")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.MultiSelection)
        for col in numeric_cols:
            item = QListWidgetItem(col)
            list_widget.addItem(item)
        if self.data_model.plot_columns:
            for i in range(list_widget.count()):
                if list_widget.item(i).text() in self.data_model.plot_columns:
                    list_widget.item(i).setSelected(True)
        layout.addWidget(list_widget)
        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dlg.accept)
        buttons.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dlg.reject)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        dlg.setLayout(layout)
        if dlg.exec_() == QDialog.Accepted:
            selected = [item.text() for item in list_widget.selectedItems()]
            self.data_model.plot_columns = selected
            self.update_chart()

    def toggle_legends(self, checked):
        self.show_legends = checked
        self.change_view(self.current_view)

    def change_page(self, index):
        self.current_page = index
        self.data_model = self.data_models[index]
        self.refresh_table()
        self.update_chart()
        self.update_legends()
        self.change_view(self.current_view)

    def apply_styles(self):
        self.style_handler.apply_styles()

    def refresh_table(self):
        self.table_handler.refresh_table()

    def update_table(self):
        self.table_handler.update_table()

    def update_chart(self):
        self.chart_handler.update_chart()

    def change_view(self, view):
        self.current_view = view
        if view == "Table":
            self.table.show()
            self.canvas.hide()
            self.chart_type_selector.hide()
            self.update_legends()
            if self.show_legends:
                self.right_widget.show()
            else:
                self.right_widget.hide()
        else:
            self.table.hide()
            self.canvas.show()
            self.chart_type_selector.show()
            self.right_widget.hide()
            self.update_chart()

    def reload_session(self):
        self.data_models = load_multi(data_model.DataModel.SESSION_FILE)
        for dm in self.data_models:
            dm.all_data_models = self.data_models
        self.page_selector.clear()
        for dm in self.data_models:
            self.page_selector.addItem(dm.page_name)
        self.current_page = 0
        self.page_selector.setCurrentIndex(0)
        self.change_page(0)
        self.update_legends()
        QMessageBox.information(self, "Reload Successful", "Session reloaded from file.")

    def new_session(self):
        reply = QMessageBox.question(self, "New Session", "Are you sure you want to start a new session? Unsaved changes will be lost.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.data_models = [data_model.DataModel()]
            for dm in self.data_models:
                dm.all_data_models = self.data_models
            self.page_selector.clear()
            self.page_selector.addItem("Default")
            self.current_page = 0
            self.page_selector.setCurrentIndex(0)
            self.change_page(0)
            self.update_legends()
            QMessageBox.information(self, "New Session", "New session started.")

    def save_session_manually(self):
        self.action_handler.save_session_manually()

    def undo(self):
        self.action_handler.undo()

    def import_data(self):
        self.action_handler.import_data()

    def export_session(self):
        self.action_handler.export_session()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(self.rect())

    def closeEvent(self, event):
        save_multi(self.data_models, data_model.DataModel.SESSION_FILE)
        event.accept()

    def change_font_size(self):
        self.style_handler.change_font_size()

    def change_font_family(self):
        self.style_handler.change_font_family()

    def update_legends(self):
        layout = self.control_layout
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for col in sorted(self.data_model.column_tiers.keys()):
            widget = QWidget()
            wlayout = QVBoxLayout(widget)
            title = QLabel(f"{col} Color Legend")
            title.setStyleSheet("color: #3498db; font-weight: bold;")
            wlayout.addWidget(title)
            is_min_threshold, tiers = self.data_model.column_tiers[col]
            if is_min_threshold:
                for _, text, color in tiers:
                    label = QLabel(text)
                    label.setStyleSheet(f"color: {color};")
                    wlayout.addWidget(label)
            else:
                for _, _, text, color in tiers:
                    label = QLabel(text)
                    label.setStyleSheet(f"color: {color};")
                    wlayout.addWidget(label)
            widget.setStyleSheet("background-color: rgba(17,17,17,128); border: 1px solid #3498db; border-radius: 5px;")
            layout.addWidget(widget)
        layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#000"))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    window = LeaderboardPro()
    window.show()
    sys.exit(app.exec_())
python

Collapse

Wrap

Run

Copy
# chart_handler.py
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import matplotlib.colors as mcolors

class ChartHandler:
    def __init__(self, main):
        self.main = main
        self.main.view_selector.currentTextChanged.connect(self.change_view)

    def change_view(self, view):
        self.main.change_view(view)

    def update_chart(self):
        type = self.main.chart_type_selector.currentText()
        title_fontsize = self.main.chart_base_font_size + 2
        tick_fontsize = self.main.chart_base_font_size - 1
        legend_fontsize = self.main.chart_base_font_size - 2

        # Clear previous plot
        for ax in self.main.figure.get_axes():
            ax.clear()
        self.main.figure.clear()
        self.main.figure.patch.set_facecolor("#000")

        plot_cols = self.main.data_model.plot_columns
        if plot_cols:
            # Sort df by first plot col if present
            sort_col = plot_cols[0] if plot_cols else self.main.data_model.model_col_name
            sorted_df = self.main.data_model.df.sort_values(by=sort_col, ascending=False)

            labels = sorted_df["Model"]
            x = range(len(sorted_df))
            y = list(range(len(sorted_df)))[::-1]  # for horizontal

            values_dict = {col: sorted_df[col] for col in plot_cols}
            colors_dict = {col: [self.main.data_model.get_column_color(col, v).name() for v in values_dict[col]] for col in plot_cols}
            has_colors_dict = {col: col in self.main.data_model.column_tiers for col in plot_cols}

            num_series = len(plot_cols)

            if num_series == 0:
                return

            default_colors = list(mcolors.TABLEAU_COLORS.values())

            subplots_types = ["Pie", "Histogram", "Boxplot"]
            if type in subplots_types and num_series > 1:
                self.main.ax = self.main.figure.subplots(1, num_series)
                axes = self.main.ax
            else:
                self.main.ax = self.main.figure.subplots()
                axes = [self.main.ax] * num_series

            for i, col in enumerate(plot_cols):
                ax = axes[i] if type in subplots_types and num_series > 1 else axes[0]
                values = values_dict[col]
                series_color = default_colors[i % len(default_colors)]
                colors = colors_dict[col] if has_colors_dict[col] else series_color

                if type == "Bar":
                    bar_width = 0.8 / num_series if num_series > 1 else 0.4
                    offset = (i - (num_series - 1) / 2) * bar_width
                    ax.bar([j + offset for j in x], values, width=bar_width, color=colors, label=col)

                elif type == "Horizontal Bar":
                    bar_height = 0.8 / num_series if num_series > 1 else 0.4
                    offset = (i - (num_series - 1) / 2) * bar_height
                    ax.barh([j + offset for j in y], values, height=bar_height, color=colors, label=col)

                elif type == "Line":
                    ax.plot(x, values, marker='o', label=col, color=series_color)

                elif type == "Scatter":
                    ax.scatter(x, values, label=col, color=series_color)

                elif type == "Pie":
                    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors if isinstance(colors, list) else None)
                    ax.set_title(col)

                elif type == "Histogram":
                    ax.hist(values, bins=10, color=series_color, alpha=0.7)
                    ax.set_title(col)

                elif type == "Boxplot":
                    ax.boxplot(values)
                    ax.set_title(col)

            if type not in subplots_types or num_series == 1:
                ax = axes[0]
                if type in ["Bar", "Line", "Scatter"]:
                    ax.set_xticks(x)
                    ax.set_xticklabels(labels, rotation=35, ha="right")
                if type == "Horizontal Bar":
                    ax.set_yticks(y)
                    ax.set_yticklabels(labels)
                if type in ["Bar", "Horizontal Bar", "Line", "Scatter"]:
                    ax.legend()

            # Add grid and customize spines
            for a in self.main.figure.get_axes():
                a.set_facecolor("#000")
                a.spines['right'].set_visible(False)
                a.spines['top'].set_visible(False)
                a.spines['left'].set_color('white')
                a.spines['bottom'].set_color('white')
                a.tick_params(axis='both', colors='white', labelsize=tick_fontsize)
                a.grid(True, linestyle='--', alpha=0.3, color='gray')

            if self.main.show_legends:
                handles = []
                for col in plot_cols:
                    if col in self.main.data_model.column_tiers:
                        is_min_threshold, tiers = self.main.data_model.column_tiers[col]
                        if is_min_threshold:
                            handles += [Patch(color=color, label=label) for minv, label, color in tiers]
                        else:
                            handles += [Patch(color=color, label=label) for minv, maxv, label, color in tiers]
                if handles:
                    legend_ax = self.main.figure.add_axes([0.9, 0.1, 0.1, 0.8])
                    legend_ax.axis('off')
                    legend_ax.legend(handles=handles, loc='center left', facecolor="#000", edgecolor="#FFFFFF", labelcolor="#FFFFFF", fontsize=legend_fontsize, ncol=1)

        self.main.figure.tight_layout(rect=[0, 0, 0.9, 1])
        self.main.canvas.draw()