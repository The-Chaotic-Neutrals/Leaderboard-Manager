# colors.py
from PyQt5.QtGui import QColor

OVERALL_COLOR_DEFS = [
    ("Leviathan: Elite Models (Overall >= 90)", "#EE82EE"),
    ("Gold Standard: Premium (Overall >= 75)", "#FFD700"),
    ("Silver: Solid (Overall >= 50)", "#C0C0C0"),
    ("Bronze: Basic (Overall >= 25)", "#CD7F32"),
    ("Subpar: Weak (Rest)", "#8B4513")
]

ABNORMAL_COLOR_DEFS = [
    ("N/A (Abnormal Behavior = 0)", "#D3D3D3"),
    ("Minimal (1 <= Abnormal Behavior <= 5)", "#40A040"),
    ("Low (6 <= Abnormal Behavior <= 10)", "#0028FF"),
    ("Moderate (11 <= Abnormal Behavior <= 15)", "#808080"),
    ("High (16 <= Abnormal Behavior <= 20)", "#3280CD"),
    ("Severe (Abnormal Behavior > 20)", "#74BAEC")
]

def get_color_for_score(score):
    try:
        score = float(score)
        if score >= 90:
            return QColor("#EE82EE")  # Leviathan - Violet
        elif score >= 75:
            return QColor("#FFD700")  # Gold Standard
        elif score >= 50:
            return QColor("#C0C0C0")  # Silver
        elif score >= 25:
            return QColor("#CD7F32")  # Bronze
        else:
            return QColor("#8B4513")  # Subpar - Brown
    except ValueError:
        return QColor("#8B4513")

def get_color_for_abnormal(score):
    try:
        score = float(score)
        if score == 0:
            return QColor("#D3D3D3")  # N/A - Light Gray
        elif score <= 5:
            return QColor("#40A040")  # Minimal - Green
        elif score <= 10:
            return QColor("#0028FF")  # Low - Blue
        elif score <= 15:
            return QColor("#808080")  # Moderate - Gray
        elif score <= 20:
            return QColor("#3280CD")  # High - Dark Blue
        else:
            return QColor("#74BAEC")  # Severe - Light Blue
    except ValueError:
        return QColor("#8B4513")

def is_light_color(color):
    r, g, b = color.red(), color.green(), color.blue()
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance > 0.5