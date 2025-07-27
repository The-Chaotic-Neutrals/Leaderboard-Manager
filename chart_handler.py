# chart_handler.py
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.colors as mcolors
import pandas as pd

class ChartHandler:
    def __init__(self, main):
        self.main = main
        self.main.view_selector.currentTextChanged.connect(self.change_view)

    def change_view(self, view):
        self.main.change_view(view)

    def update_chart(self):
        chart_type = self.main.chart_type_selector.currentText()
        title_fontsize = self.main.chart_base_font_size + 2
        tick_fontsize = self.main.chart_base_font_size - 1
        legend_fontsize = self.main.chart_base_font_size - 2

        # Ensure canvas widget background is transparent
        self.main.canvas.setStyleSheet("background-color: transparent;")

        # Clear figure and set semi-transparent black background
        self.main.figure.clear()
        self.main.figure.set_facecolor((0, 0, 0, 0.5))  # RGBA: semi-transparent black

        plot_cols = self.main.data_model.plot_columns
        if not plot_cols:
            self.main.canvas.draw()
            return

        sort_col = plot_cols[0] if plot_cols else self.main.data_model.model_col_name
        sorted_df = self.main.data_model.df.sort_values(by=sort_col, ascending=False)

        labels = sorted_df["Model"]
        x = range(len(sorted_df))
        y = list(range(len(sorted_df)))[::-1]  # for horizontal bars

        values_dict = {col: sorted_df[col] for col in plot_cols}
        colors_dict = {
            col: [self.main.data_model.get_column_color(col, v).name() for v in values_dict[col]]
            for col in plot_cols
        }
        has_colors_dict = {col: col in self.main.data_model.column_tiers for col in plot_cols}

        num_series = len(plot_cols)
        default_colors = list(mcolors.TABLEAU_COLORS.values())
        # Removed Pie, Histogram, Boxplot entirely, so no subplots_types needed
        # We'll just create single axes since multiple subplots not supported anymore
        self.main.ax = self.main.figure.subplots()
        axes = [self.main.ax] * num_series

        for i, col in enumerate(plot_cols):
            ax = axes[0]  # Always same ax since no multi subplot for these types
            values = values_dict[col]
            series_color = default_colors[i % len(default_colors)]
            colors = colors_dict[col] if has_colors_dict[col] else series_color

            if chart_type == "Bar":
                bar_width = 0.8 / num_series if num_series > 1 else 0.4
                offset = (i - (num_series - 1) / 2) * bar_width
                ax.bar([j + offset for j in x], values, width=bar_width, color=colors, label=col)

            elif chart_type == "Horizontal Bar":
                bar_height = 0.8 / num_series if num_series > 1 else 0.4
                offset = (i - (num_series - 1) / 2) * bar_height
                ax.barh([j + offset for j in y], values, height=bar_height, color=colors, label=col)

            elif chart_type == "Line":
                ax.plot(x, values, marker='o', label=col, color=series_color)

            elif chart_type == "Scatter":
                ax.scatter(x, values, label=col, color=series_color)

        ax = axes[0]
        if chart_type in ["Bar", "Line", "Scatter"]:
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=35, ha="right")
        if chart_type == "Horizontal Bar":
            ax.set_yticks(y)
            ax.set_yticklabels(labels)
        if chart_type in ["Bar", "Horizontal Bar", "Line", "Scatter"]:
            ax.legend()

        # Style all axes to be transparent
        for a in self.main.figure.get_axes():
            a.set_facecolor("none")  # fully transparent axes
            for spine in a.spines.values():
                spine.set_color("white")
            a.tick_params(axis="both", colors="white", labelsize=tick_fontsize)
            a.grid(True, linestyle="--", alpha=0.3, color="gray")

        if self.main.show_legends:
            handles = []
            for col in plot_cols:
                if col in self.main.data_model.column_tiers:
                    is_min_threshold, tiers = self.main.data_model.column_tiers[col]
                    if is_min_threshold:
                        handles += [Patch(color=color, label=label) for _, label, color in tiers]
                    else:
                        handles += [Patch(color=color, label=label) for _, _, label, color in tiers]
            if handles:
                legend_ax = self.main.figure.add_axes([0.9, 0.1, 0.1, 0.8])
                legend_ax.set_facecolor("none")
                legend_ax.axis("off")
                legend_ax.legend(
                    handles=handles,
                    loc="center left",
                    facecolor="none",
                    edgecolor="white",
                    labelcolor="#FFFFFF",
                    fontsize=legend_fontsize,
                    ncol=1
                )

        self.main.figure.tight_layout(rect=[0, 0, 0.9, 1])
        self.main.canvas.draw()
