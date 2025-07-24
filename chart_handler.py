# chart_handler.py
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import colors

class ChartHandler:
    def __init__(self, main):
        self.main = main
        self.main.view_selector.currentTextChanged.connect(self.change_view)

    def change_view(self, view):
        self.main.current_view = view
        if view == "Table":
            self.main.table.show()
            self.main.canvas.hide()
            self.main.legend_widget.show()
            self.main.abnormal_legend_widget.show()
        else:
            self.main.table.hide()
            self.main.canvas.show()
            self.main.legend_widget.hide()
            self.main.abnormal_legend_widget.hide()
            self.update_chart()

    def update_chart(self):
        title_fontsize = self.main.chart_base_font_size + 2
        tick_fontsize = self.main.chart_base_font_size - 1
        legend_fontsize = self.main.chart_base_font_size - 2

        self.main.ax.clear()
        self.main.ax.set_facecolor("#000")
        self.main.figure.patch.set_facecolor("#000")

        if not self.main.data_model.df.empty:
            # Sort df by Overall for consistent ordering
            sorted_df = self.main.data_model.df.sort_values(by=self.main.data_model.overall_col, ascending=False)

            if self.main.current_view == "Bar Chart":
                bar_width = 0.4
                x = range(len(sorted_df))
                retrieval_colors = [colors.get_color_for_score(row[self.main.data_model.overall_col]).name() for _, row in sorted_df.iterrows()]
                abnormal_colors = [colors.get_color_for_abnormal(row[self.main.data_model.abnormal_col]).name() for _, row in sorted_df.iterrows()]
                self.main.ax.bar(x, sorted_df[self.main.data_model.retrieval_col], width=bar_width, color=retrieval_colors)
                self.main.ax.bar([i + bar_width for i in x], sorted_df[self.main.data_model.abnormal_col], width=bar_width, color=abnormal_colors)
                self.main.ax.set_xticks([i + bar_width / 2 for i in x])
                self.main.ax.set_xticklabels(sorted_df["Model"], rotation=35, ha="right", color="white", fontsize=tick_fontsize)
                self.main.ax.set_title("Model Scores (Left: Retrieval, Right: Abnormal Behavior)", color="white", fontsize=title_fontsize)

                # Useful legend for tiers, more vertical and thinner
                handles = [
                    Patch(color='#EE82EE', label='Leviathan Overall (>=90)'),
                    Patch(color='#D3D3D3', label='N/A Abnormal Behavior (=0)'),
                    Patch(color='#FFD700', label='Gold Overall (>=75)'),
                    Patch(color='#40A040', label='Minimal Abnormal Behavior (1-5)'),
                    Patch(color='#C0C0C0', label='Silver Overall (>=50)'),
                    Patch(color='#0028FF', label='Low Abnormal Behavior (6-10)'),
                    Patch(color='#CD7F32', label='Bronze Overall (>=25)'),
                    Patch(color='#808080', label='Moderate Abnormal Behavior (11-15)'),
                    Patch(color='#8B4513', label='Subpar Overall (Rest)'),
                    Patch(color='#3280CD', label='High Abnormal Behavior (16-20)'),
                    Patch(color='#74BAEC', label='Severe Abnormal Behavior (>20)')
                ]
                self.main.ax.legend(handles=handles, bbox_to_anchor=(1.02, 1), loc='upper left', facecolor="#000", edgecolor="#FFFFFF", labelcolor="#FFFFFF", fontsize=legend_fontsize, ncol=1)

            self.main.ax.tick_params(axis='both', colors='white', labelsize=tick_fontsize)

        self.main.figure.tight_layout()
        self.main.canvas.draw()