# chart_handler.py
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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
            # Sort df by score_col for consistent ordering
            sort_col = self.main.data_model.score_col if self.main.data_model.score_col else self.main.data_model.model_col_name
            sorted_df = self.main.data_model.df.sort_values(by=sort_col, ascending=False)

            if self.main.current_view == "Bar Chart":
                bar_width = 0.4
                x = range(len(sorted_df))
                score_colors = [self.main.data_model.get_score_color(row[self.main.data_model.score_col]).name() if self.main.data_model.score_col else "#FFFFFF" for _, row in sorted_df.iterrows()]
                penalty_colors = [self.main.data_model.get_penalty_color(row[self.main.data_model.penalty_col]).name() if self.main.data_model.penalty_col else "#FFFFFF" for _, row in sorted_df.iterrows()]
                score_values = sorted_df[self.main.data_model.score_col] if self.main.data_model.score_col else [0] * len(sorted_df)
                penalty_values = sorted_df[self.main.data_model.penalty_col] if self.main.data_model.penalty_col else [0] * len(sorted_df)
                self.main.ax.bar(x, score_values, width=bar_width, color=score_colors)
                self.main.ax.bar([i + bar_width for i in x], penalty_values, width=bar_width, color=penalty_colors)
                self.main.ax.set_xticks([i + bar_width / 2 for i in x])
                self.main.ax.set_xticklabels(sorted_df["Model"], rotation=35, ha="right", color="white", fontsize=tick_fontsize)
                score_name = self.main.data_model.score_col or "N/A"
                penalty_name = self.main.data_model.penalty_col or "N/A"
                self.main.ax.set_title(f"Model Scores (Left: {score_name}, Right: {penalty_name})", color="white", fontsize=title_fontsize)

                # Legend
                handles = [Patch(color=color, label=label) for _, label, color in self.main.data_model.score_tiers]
                handles += [Patch(color=color, label=label) for _, _, label, color in self.main.data_model.penalty_tiers]
                self.main.ax.legend(handles=handles, bbox_to_anchor=(1.02, 1), loc='upper left', facecolor="#000", edgecolor="#FFFFFF", labelcolor="#FFFFFF", fontsize=legend_fontsize, ncol=1)

            self.main.ax.tick_params(axis='both', colors='white', labelsize=tick_fontsize)

        self.main.figure.tight_layout()
        self.main.canvas.draw()