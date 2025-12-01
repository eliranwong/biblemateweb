from pathlib import Path
from agentmake import readTextFile, writeTextFile
from biblemategui import config
from nicegui import app
from typing import List
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
config.embedding_model="{config.embedding_model}"
config.custom_token="{config.custom_token}"
config.storage_secret="{config.storage_secret}"
config.port={config.port}"""
    writeTextFile(CONFIG_FILE_BACKUP, configurations)

# restore config backup after upgrade
default_config = '''config.hot_reload=False
config.reload_after_sync=False
config.avatar=""
config.embedding_model="paraphrase-multilingual"
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

def getBibleVersionList() -> List[str]:
    """Returns a list of available Bible versions"""
    bibleVersionList = ["ORB", "OIB", "OPB", "ODB", "OLB"]+list(config.bibles.keys())
    if app.storage.client["custom"]:
        bibleVersionList += list(config.bibles_custom.keys())
        bibleVersionList = list(set(bibleVersionList))
    return sorted(bibleVersionList)

# lexicons resources
lexicons_dir = os.path.join(BIBLEMATEGUI_DATA, "lexicons")
if os.path.isdir(lexicons_dir):
    config.lexicons = dict(sorted({os.path.basename(i)[:-8]: i for i in glob.glob(os.path.join(lexicons_dir, "*.lexicon"))}.items()))
else:
    Path(lexicons_dir).mkdir(parents=True, exist_ok=True)
    config.lexicons = {}
lexicons_dir_custom = os.path.join(BIBLEMATEGUI_DATA_CUSTOM, "lexicons")
if os.path.isdir(lexicons_dir_custom):
    config.lexicons_custom = dict(sorted({os.path.basename(i)[:-8]: i for i in glob.glob(os.path.join(lexicons_dir_custom, "*.lexicon"))}.items()))
else:
    Path(lexicons_dir_custom).mkdir(parents=True, exist_ok=True)
    config.lexicons_custom = {}

def getLexiconList() -> List[str]:
    """Returns a list of available Lexicons"""
    client_lexicons = list(config.lexicons.keys())
    if app.storage.client["custom"]:
        client_lexicons += list(config.lexicons_custom.keys())
    return sorted(list(set(client_lexicons)))

# audio resources
app.add_media_files('/bhs5_audio', os.path.join(BIBLEMATEGUI_DATA, "audio", "bibles", "BHS5", "default"))
app.add_media_files('/ognt_audio', os.path.join(BIBLEMATEGUI_DATA, "audio", "bibles", "OGNT", "default"))
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

config.topics = {
    "HIT": "Hitchcock's New and Complete Analysis of the Bible",
    "NAV": "Nave's Topical Bible",
    "TCR": "Thompson Chain References",
    "TNT": "Torrey's New Topical Textbook",
    "TOP": "Topical Bible",
}
config.dictionaries = {
    "AMT": "American Tract Society Dictionary",
    "BBD": "Bridgeway Bible Dictionary",
    "BMC": "Freeman's Handbook of Bible Manners and Customs",
    "BUC": "Buck's A Theological Dictionary",
    "CBA": "Companion Bible Appendices",
    "DRE": "Dictionary Of Religion And Ethics",
    "EAS": "Easton's Illustrated Bible Dictionary",
    "FAU": "Fausset's Bible Dictionary",
    "FOS": "Bullinger's Figures of Speech",
    "HBN": "Hitchcock's Bible Names Dictionary",
    "MOR": "Morrish's Concise Bible Dictionary",
    "PMD": "Poor Man's Dictionary",
    "SBD": "Smith's Bible Dictionary",
    "USS": "Annals of the World",
    "VNT": "Vine's Expository Dictionary of New Testament Words",
}
config.encyclopedias = {
    "DAC": "Hasting's Dictionary of the Apostolic Church",
    "DCG": "Hasting's Dictionary Of Christ And The Gospels",
    "HAS": "Hasting's Dictionary of the Bible",
    "ISB": "International Standard Bible Encyclopedia",
    "KIT": "Kitto's Cyclopedia of Biblical Literature",
    "MSC": "McClintock & Strong's Cyclopedia of Biblical Literature",
}

# User Default Settings

USER_DEFAULT_SETTINGS = {
    'font_size': 100,
    'primary_color': '#12a189',
    'secondary_color': '#12a189',
    'negative_color': '#ff384f',
    'avatar': '',
    'custom_token': '',
    'primary_bible': 'NET',
    'secondary_bible': 'KJV',
    'favorite_commentary': 'CBSC',
    'favorite_encyclopedia': 'ISB',
    'favorite_lexicon': 'Morphology',
    'hebrew_lexicon': 'TBESH',
    'greek_lexicon': 'TBESG',
    'ai_backend': 'googleai',
    'api_endpoint': '',
    'api_key': '',
    'ui_language': 'eng',
    'dark_mode': True,
    'left_drawer_open': False,
    'search_case_sensitivity': False,
    'search_mode': 1,
    'top_similar_entries': 5,
    'top_similar_verses': 20,
    'default_number_of_tabs1': 3,
    'default_number_of_tabs2': 3,
    'layout_swap_button': True,
}