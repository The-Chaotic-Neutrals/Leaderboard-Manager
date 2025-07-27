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

        primary_col = self.main.data_model.plot_primary
        secondary_col = self.main.data_model.plot_secondary
        if primary_col or secondary_col:
            # Sort df by primary if present, else secondary
            sort_col = primary_col if primary_col else secondary_col if secondary_col else self.main.data_model.model_col_name
            sorted_df = self.main.data_model.df.sort_values(by=sort_col, ascending=False)

            labels = sorted_df["Model"]
            x = range(len(sorted_df))
            y = list(range(len(sorted_df)))[::-1]  # for horizontal

            primary_name = primary_col or ""
            secondary_name = secondary_col or ""
            primary_values = sorted_df[primary_col] if primary_col else pd.Series()
            secondary_values = sorted_df[secondary_col] if secondary_col else pd.Series()
            primary_colors = [self.main.data_model.get_column_color(primary_col, v).name() for v in primary_values] if primary_col and len(primary_values) > 0 else []
            secondary_colors = [self.main.data_model.get_column_color(secondary_col, v).name() for v in secondary_values] if secondary_col and len(secondary_values) > 0 else []

            if type in ["Pie", "Boxplot", "Histogram"] and primary_col and secondary_col:
                self.main.ax = self.main.figure.subplots(1, 2)
                ax1, ax2 = self.main.ax
            else:
                self.main.ax = self.main.figure.subplots()
                ax = self.main.ax

            primary_default_color = 'blue'
            secondary_default_color = 'green'

            primary_has_colors = primary_col and primary_col in self.main.data_model.column_tiers
            secondary_has_colors = secondary_col and secondary_col in self.main.data_model.column_tiers

            if type == "Bar":
                bar_width = 0.4
                if primary_col:
                    colors = primary_colors if primary_has_colors else primary_default_color
                    ax.bar([i - bar_width/2 for i in x], primary_values, width=bar_width, color=colors, label=primary_name)
                if secondary_col:
                    colors = secondary_colors if secondary_has_colors else secondary_default_color
                    ax.bar([i + bar_width/2 for i in x], secondary_values, width=bar_width, color=colors, label=secondary_name)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=35, ha="right")

            elif type == "Horizontal Bar":
                bar_height = 0.4
                if primary_col:
                    colors = primary_colors if primary_has_colors else primary_default_color
                    ax.barh([i - bar_height/2 for i in y], primary_values, height=bar_height, color=colors, label=primary_name)
                if secondary_col:
                    colors = secondary_colors if secondary_has_colors else secondary_default_color
                    ax.barh([i + bar_height/2 for i in y], secondary_values, height=bar_height, color=colors, label=secondary_name)
                ax.set_yticks(y)
                ax.set_yticklabels(labels)

            elif type == "Line":
                if primary_col:
                    ax.plot(x, primary_values, marker='o', label=primary_name, color=primary_default_color)
                if secondary_col:
                    ax.plot(x, secondary_values, marker='s', label=secondary_name, color=secondary_default_color)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=35, ha="right")

            elif type == "Scatter":
                if primary_col:
                    ax.scatter(x, primary_values, label=primary_name, color=primary_default_color)
                if secondary_col:
                    ax.scatter(x, secondary_values, label=secondary_name, color=secondary_default_color)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=35, ha="right")

            elif type == "Pie":
                if primary_col and secondary_col:
                    ax1.pie(primary_values, labels=labels, autopct='%1.1f%%', colors=primary_colors if primary_has_colors else None)
                    ax1.set_title(primary_name)
                    ax2.pie(secondary_values, labels=labels, autopct='%1.1f%%', colors=secondary_colors if secondary_has_colors else None)
                    ax2.set_title(secondary_name)
                elif primary_col:
                    ax.pie(primary_values, labels=labels, autopct='%1.1f%%', colors=primary_colors if primary_has_colors else None)
                    ax.set_title(primary_name)
                elif secondary_col:
                    ax.pie(secondary_values, labels=labels, autopct='%1.1f%%', colors=secondary_colors if secondary_has_colors else None)
                    ax.set_title(secondary_name)

            elif type == "Histogram":
                if primary_col and secondary_col:
                    ax1.hist(primary_values, bins=10, color=primary_default_color, alpha=0.7)
                    ax1.set_title(primary_name)
                    ax2.hist(secondary_values, bins=10, color=secondary_default_color, alpha=0.7)
                    ax2.set_title(secondary_name)
                elif primary_col:
                    ax.hist(primary_values, bins=10, color=primary_default_color, alpha=0.7)
                    ax.set_title(primary_name)
                elif secondary_col:
                    ax.hist(secondary_values, bins=10, color=secondary_default_color, alpha=0.7)
                    ax.set_title(secondary_name)

            elif type == "Boxplot":
                if primary_col and secondary_col:
                    ax1.boxplot(primary_values)
                    ax1.set_title(primary_name)
                    ax2.boxplot(secondary_values)
                    ax2.set_title(secondary_name)
                elif primary_col:
                    ax.boxplot(primary_values)
                    ax.set_title(primary_name)
                elif secondary_col:
                    ax.boxplot(secondary_values)
                    ax.set_title(secondary_name)

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
                if primary_col and primary_col in self.main.data_model.column_tiers:
                    is_ach, tiers = self.main.data_model.column_tiers[primary_col]
                    if is_ach:
                        handles += [Patch(color=color, label=label) for minv, label, color in tiers]
                    else:
                        handles += [Patch(color=color, label=label) for minv, maxv, label, color in tiers]
                if secondary_col and secondary_col in self.main.data_model.column_tiers:
                    is_ach, tiers = self.main.data_model.column_tiers[secondary_col]
                    if is_ach:
                        handles += [Patch(color=color, label=label) for minv, label, color in tiers]
                    else:
                        handles += [Patch(color=color, label=label) for minv, maxv, label, color in tiers]
                if handles:
                    legend_ax = self.main.figure.add_axes([0.9, 0.1, 0.1, 0.8])
                    legend_ax.axis('off')
                    legend_ax.legend(handles=handles, loc='center left', facecolor="#000", edgecolor="#FFFFFF", labelcolor="#FFFFFF", fontsize=legend_fontsize, ncol=1)

        self.main.figure.tight_layout(rect=[0, 0, 0.9, 1])
        self.main.canvas.draw()