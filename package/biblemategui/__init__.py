from pathlib import Path
from agentmake import readTextFile, writeTextFile
from biblemategui import config
import os, glob, apsw, re

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
    configurations = f"""config.hot_reload={config.hot_reload}
config.reload_after_sync={config.reload_after_sync}
config.avatar="{config.avatar}"
config.custom_token="{config.custom_token}"
config.storage_secret="{config.storage_secret}"
config.port={config.port}"""
    writeTextFile(CONFIG_FILE_BACKUP, configurations)

# restore config backup after upgrade
default_config = '''config.hot_reload=False
config.reload_after_sync=False
config.avatar=""
config.custom_token=""
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

# bibles resources

def getBibleInfo(db):
    abb = os.path.basename(db)[:-6]
    try:
        with apsw.Connection(db) as connn:
            query = "SELECT Title FROM Details limit 1"
            cursor = connn.cursor()
            cursor.execute(query)
            info = cursor.fetchone()
    except:
        try:
            with apsw.Connection(db) as connn:
                query = "SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse=? limit 1"
                cursor = connn.cursor()
                cursor.execute(query, (0, 0, 0))
                info = cursor.fetchone()
        except:
            return abb
    return info[0] if info else abb

bibles_dir = os.path.join(BIBLEMATEGUI_DATA, "bibles")
if os.path.isdir(bibles_dir):
    config.bibles = dict(sorted({os.path.basename(i)[:-6]: (getBibleInfo(i), i) for i in glob.glob(os.path.join(bibles_dir, "*.bible")) if not re.search("(MOB|MIB|MAB|MTB|MPB).bible$", i)}.items()))
else:
    Path(bibles_dir).mkdir(parents=True, exist_ok=True)
    config.bibles = {}
bibles_dir_custom = os.path.join(BIBLEMATEGUI_DATA_CUSTOM, "bibles")
if os.path.isdir(bibles_dir_custom):
    config.bibles_custom = dict(sorted({os.path.basename(i)[:-6]: (getBibleInfo(i), i) for i in glob.glob(os.path.join(bibles_dir_custom, "*.bible")) if not re.search("(MOB|MIB|MAB|MTB|MPB).bible$", i)}.items()))
else:
    Path(bibles_dir_custom).mkdir(parents=True, exist_ok=True)
    config.bibles_custom = {}
# audio resources
audio_dir = os.path.join(BIBLEMATEGUI_DATA, "audio", "bibles")
if os.path.isdir(audio_dir):
    config.audio = {i: os.path.join(audio_dir, i, "default") for i in os.listdir(audio_dir) if os.path.isdir(os.path.join(audio_dir, i)) and not i in ("BHS5", "OGNT")}
else:
    Path(audio_dir).mkdir(parents=True, exist_ok=True)
    config.audio = {}
audio_dir_custom = os.path.join(BIBLEMATEGUI_DATA_CUSTOM, "audio", "bibles")
if os.path.isdir(audio_dir_custom):
    config.audio_custom = {i: os.path.join(audio_dir_custom, i, "default") for i in os.listdir(audio_dir_custom) if os.path.isdir(os.path.join(audio_dir_custom, i)) and not i in ("BHS5", "OGNT")}
else:
    Path(audio_dir_custom).mkdir(parents=True, exist_ok=True)
    config.audio_custom = {}

config.available_tools = ["audio", "chronology"]

# User Default Settings

USER_DEFAULT_SETTINGS = {
    'font_size': 100,
    'primary_color': '#12a189',
    'secondary_color': '#12a189',
    'avatar': '',
    'custom_token': '',
    'default_bible': 'NET',
    'default_commentary': 'CBSC',
    'default_encyclopedia': 'ISBE',
    'default_lexicon': 'Morphology',
    'ai_backend': 'googleai',
    'api_endpoint': '',
    'api_key': '',
    'language': 'English',
    'dark_mode': True,
    'left_drawer_open': False,
}