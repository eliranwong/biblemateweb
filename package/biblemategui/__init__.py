from pathlib import Path
from agentmake import readTextFile, writeTextFile
from biblemategui import config
import os, glob

BIBLEMATEGUI_APP_DIR = os.path.dirname(os.path.realpath(__file__))
BIBLEMATEGUI_USER_DIR = os.path.join(os.path.expanduser("~"), "biblemate")
BIBLEMATEGUI_DATA = os.path.join(os.path.expanduser("~"), "biblemate", "data")
if not os.path.isdir(BIBLEMATEGUI_USER_DIR):
    Path(BIBLEMATEGUI_USER_DIR).mkdir(parents=True, exist_ok=True)
BIBLEMATEGUI_DATA_CUSTOM = os.path.join(os.path.expanduser("~"), "biblemate", "data_custom")
if not os.path.isdir(BIBLEMATEGUI_DATA_CUSTOM):
    Path(BIBLEMATEGUI_DATA_CUSTOM).mkdir(parents=True, exist_ok=True)
for i in ("audio", "bibles"):
    if not os.path.isdir(os.path.join(BIBLEMATEGUI_DATA, i)):
        Path(os.path.join(BIBLEMATEGUI_DATA, i)).mkdir(parents=True, exist_ok=True)
CONFIG_FILE_BACKUP = os.path.join(BIBLEMATEGUI_USER_DIR, "biblemategui.config")

# NOTE: When add a config item, update both `write_user_config` and `default_config`

def write_user_config():
    """Writes the current configuration to the user's config file."""
    configurations = f"""config.avatar="{config.avatar}"
config.storage_secret="{config.storage_secret}"
config.port={config.port}"""
    writeTextFile(CONFIG_FILE_BACKUP, configurations)

# restore config backup after upgrade
default_config = '''config.avatar=""
config.storage_secret="REPLACE_ME_WITH_A_REAL_SECRET"
config.port=33355'''

def load_config():
    """Loads the user's configuration from the config file."""
    if not os.path.isfile(CONFIG_FILE_BACKUP):
        exec(default_config, globals())
        write_user_config()
    else:
        exec(readTextFile(CONFIG_FILE_BACKUP), globals())
    # check if new config items are added
    changed = False
    for config_item in default_config[7:].split("\nconfig."):
        key, _ = config_item.split("=", 1)
        if not hasattr(config, key):
            exec(f"config.{config_item}", globals())
            changed = True
    if changed:
        write_user_config()

# load user config at startup
load_config()

from biblemategui import config
from biblemategui.pages.bibles.original_reader import original_reader
from biblemategui.pages.bibles.original_interlinear import original_interlinear
from biblemategui.pages.bibles.original_parallel import original_parallel
from biblemategui.pages.bibles.original_discourse import original_discourse
from biblemategui.pages.bibles.original_linguistic import original_linguistic
from biblemategui.pages.bibles.bible_translation import bible_translation
config.original_reader = original_reader
config.original_interlinear = original_interlinear
config.original_parallel = original_parallel
config.original_discourse = original_discourse
config.original_linguistic = original_linguistic
config.bible_translation = bible_translation

# general settings; stored on sever side
config.bibles = {os.path.basename(i)[:-6]: i for i in glob.glob(os.path.join(BIBLEMATEGUI_DATA, "bibles", "*.bible"))}
config.bibles_custom = {os.path.basename(i)[:-6]: i for i in glob.glob(os.path.join(BIBLEMATEGUI_DATA_CUSTOM, "bibles", "*.bible"))}