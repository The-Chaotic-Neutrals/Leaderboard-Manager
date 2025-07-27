# chart_handler.py
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

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

        if self.main.data_model.score_col or self.main.data_model.penalty_col:
            # Sort df by score_col for consistent ordering
            sort_col = self.main.data_model.score_col if self.main.data_model.score_col else self.main.data_model.penalty_col if self.main.data_model.penalty_col else self.main.data_model.model_col_name
            sorted_df = self.main.data_model.df.sort_values(by=sort_col, ascending=False)

            labels = sorted_df["Model"]
            x = range(len(sorted_df))
            y = list(range(len(sorted_df)))[::-1]  # for horizontal

            score_name = self.main.data_model.score_col or ""
            penalty_name = self.main.data_model.penalty_col or ""
            score_values = sorted_df[self.main.data_model.score_col] if self.main.data_model.score_col else pd.Series()
            penalty_values = sorted_df[self.main.data_model.penalty_col] if self.main.data_model.penalty_col else pd.Series()
            score_colors = [self.main.data_model.get_score_color(v).name() for v in score_values] if len(score_values) > 0 else []
            penalty_colors = [self.main.data_model.get_penalty_color(v).name() for v in penalty_values] if len(penalty_values) > 0 else []

            if type in ["Pie", "Boxplot", "Histogram"] and (len(score_values) > 0 and len(penalty_values) > 0):
                self.main.ax = self.main.figure.subplots(1, 2)
                ax1, ax2 = self.main.ax
            else:
                self.main.ax = self.main.figure.subplots()
                ax = self.main.ax

            if type == "Bar":
                bar_width = 0.4
                if len(score_values) > 0:
                    ax.bar([i - bar_width/2 for i in x], score_values, width=bar_width, color=score_colors, label=score_name)
                if len(penalty_values) > 0:
                    ax.bar([i + bar_width/2 for i in x], penalty_values, width=bar_width, color=penalty_colors, label=penalty_name)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=35, ha="right")

            elif type == "Horizontal Bar":
                bar_height = 0.4
                if len(score_values) > 0:
                    ax.barh([i - bar_height/2 for i in y], score_values, height=bar_height, color=score_colors, label=score_name)
                if len(penalty_values) > 0:
                    ax.barh([i + bar_height/2 for i in y], penalty_values, height=bar_height, color=penalty_colors, label=penalty_name)
                ax.set_yticks(y)
                ax.set_yticklabels(labels)

            elif type == "Line":
                if len(score_values) > 0:
                    ax.plot(x, score_values, marker='o', label=score_name, color='blue')
                if len(penalty_values) > 0:
                    ax.plot(x, penalty_values, marker='s', label=penalty_name, color='green')
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=35, ha="right")

            elif type == "Scatter":
                if len(score_values) > 0:
                    ax.scatter(x, score_values, label=score_name, color='blue')
                if len(penalty_values) > 0:
                    ax.scatter(x, penalty_values, label=penalty_name, color='green')
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=35, ha="right")

            elif type == "Pie":
                if len(score_values) > 0 and len(penalty_values) > 0:
                    ax1.pie(score_values, labels=labels, autopct='%1.1f%%', colors=score_colors)
                    ax1.set_title(score_name)
                    ax2.pie(penalty_values, labels=labels, autopct='%1.1f%%', colors=penalty_colors)
                    ax2.set_title(penalty_name)
                elif len(score_values) > 0:
                    ax.pie(score_values, labels=labels, autopct='%1.1f%%', colors=score_colors)
                    ax.set_title(score_name)
                elif len(penalty_values) > 0:
                    ax.pie(penalty_values, labels=labels, autopct='%1.1f%%', colors=penalty_colors)
                    ax.set_title(penalty_name)

            elif type == "Histogram":
                if len(score_values) > 0 and len(penalty_values) > 0:
                    ax1.hist(score_values, bins=10, color='blue', alpha=0.7)
                    ax1.set_title(score_name)
                    ax2.hist(penalty_values, bins=10, color='green', alpha=0.7)
                    ax2.set_title(penalty_name)
                elif len(score_values) > 0:
                    ax.hist(score_values, bins=10, color='blue', alpha=0.7)
                    ax.set_title(score_name)
                elif len(penalty_values) > 0:
                    ax.hist(penalty_values, bins=10, color='green', alpha=0.7)
                    ax.set_title(penalty_name)

            elif type == "Boxplot":
                if len(score_values) > 0 and len(penalty_values) > 0:
                    ax1.boxplot(score_values)
                    ax1.set_title(score_name)
                    ax2.boxplot(penalty_values)
                    ax2.set_title(penalty_name)
                elif len(score_values) > 0:
                    ax.boxplot(score_values)
                    ax.set_title(score_name)
                elif len(penalty_values) > 0:
                    ax.boxplot(penalty_values)
                    ax.set_title(penalty_name)

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
                handles = [Patch(color=color, label=label) for _, label, color in self.main.data_model.score_tiers]
                handles += [Patch(color=color, label=label) for _, _, label, color in self.main.data_model.penalty_tiers]
                legend_ax = self.main.figure.add_axes([0.9, 0.1, 0.1, 0.8])
                legend_ax.axis('off')
                legend_ax.legend(handles=handles, loc='center left', facecolor="#000", edgecolor="#FFFFFF", labelcolor="#FFFFFF", fontsize=legend_fontsize, ncol=1)

        self.main.figure.tight_layout(rect=[0, 0, 0.9, 1])
        self.main.canvas.draw()