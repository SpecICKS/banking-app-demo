from pathlib import Path

WIDTH = 360
HEIGHT = 460
APP_TITLE = "Banking App"
DEBUG = False
PROJECT_ROOT = Path(__file__).resolve().parents[2]
KEY_PATH = PROJECT_ROOT / "java_backend" / "key.txt"
JAVA_CLASS_PATH = PROJECT_ROOT / "java_backend" / "bin"

BG_COLOR = "#1E1E2E"          # BG BLUE-GREY
TEXT_COLOR = "#FFFFFF"        # WHITE
SUBTEXT_COLOR = "#A6ADC8"     # Grey
INPUT_BG = "#313244"          # Text-box

BTN_LOGIN_COLOR = "#3B82F6"   # LIGHT BLUE for Login
BTN_REG_COLOR = "#10B981"     # Green for Register
BTN_BACK_COLOR = "#45475A"    # Grey for back
BORDER_COLOR = "#585B70"

TITLE_FONT = ("Segoe UI", 22, "bold")
SUBTITLE_FONT = ("Segoe UI", 11)
LABEL_FONT = ("Segoe UI", 9, "bold")
INPUT_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 11, "bold")
SMALL_FONT = ("Segoe UI", 9)


def darken(color):
    """Return a darker hover color for a six-digit hex color."""
    red = max(0, int(color[1:3], 16) - 30)
    green = max(0, int(color[3:5], 16) - 30)
    blue = max(0, int(color[5:7], 16) - 30)
    return f"#{red:02X}{green:02X}{blue:02X}"