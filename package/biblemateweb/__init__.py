from pathlib import Path
import os

BIBLEMATEWEB_APP_DIR = os.path.dirname(os.path.realpath(__file__))
BIBLEMATEWEB_USER_DIR = os.path.join(os.path.expanduser("~"), "biblemate")
BIBLEMATEWEB_DATA = os.path.join(os.path.expanduser("~"), "biblemate", "data")
if not os.path.isdir(BIBLEMATEWEB_USER_DIR):
    Path(BIBLEMATEWEB_USER_DIR).mkdir(parents=True, exist_ok=True)
BIBLEMATEWEB_PRIVATE_DATA = os.path.join(os.path.expanduser("~"), "biblemate", "data_private")
if not os.path.isdir(BIBLEMATEWEB_PRIVATE_DATA):
    Path(BIBLEMATEWEB_PRIVATE_DATA).mkdir(parents=True, exist_ok=True)
for i in ("audio", "bibles"):
    if not os.path.isdir(os.path.join(BIBLEMATEWEB_DATA, i)):
        Path(os.path.join(BIBLEMATEWEB_DATA, i)).mkdir(parents=True, exist_ok=True)