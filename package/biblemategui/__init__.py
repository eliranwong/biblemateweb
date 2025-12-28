from pathlib import Path
from agentmake import readTextFile, writeTextFile
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks
from biblemategui import config
from biblemategui.translations.eng import translation_eng
from biblemategui.translations.tc import translation_tc
from biblemategui.translations.sc import translation_sc
from nicegui import app, ui
from typing import List
import os, glob, apsw, re, asyncio
import numpy as np
import json


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
config.avatar="{config.avatar}"
config.embedding_model="{config.embedding_model}"
config.custom_token="{config.custom_token}"
config.google_client_id="{config.google_client_id}"
config.google_client_secret="{config.google_client_secret}"
config.auth_uri="{config.auth_uri}"
config.storage_secret="{config.storage_secret}"
config.port={config.port}
config.verses_limit={config.verses_limit}"""
    writeTextFile(CONFIG_FILE_BACKUP, configurations)

# restore config backup after upgrade
default_config = '''config.hot_reload=False
config.avatar=""
config.embedding_model="paraphrase-multilingual"
config.custom_token=""
config.google_client_id=""
config.google_client_secret=""
config.auth_uri=""
config.storage_secret="REPLACE_ME_WITH_A_REAL_SECRET"
config.port=33355
config.verses_limit=2000'''

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

# frequently used functions

class VerseEventObj:
    def __init__(self, args):
        *_, b, c, v = args
        self.args = (b, c, v)

def get_translation(text: str):
    if app.storage.user["ui_language"] == "tc":
        return translation_tc.get(text, text)
    elif app.storage.user["ui_language"] == "sc":
        return translation_sc.get(text, text)
    return translation_eng.get(text, text)

async def loading(func, *args, **kwargs):
    n = ui.notification(timeout=None)
    try:
        awaitable = asyncio.to_thread(func, *args, **kwargs)
        task = asyncio.create_task(awaitable)
        while not task.done():
            n.message = get_translation('Loading...')
            n.spinner = True
            await asyncio.sleep(0.2)
        #n.message = 'Done!'
        n.spinner = False
        await asyncio.sleep(1)
        #n.dismiss()
        return task.result()
    except Exception as e:
        n.message = f'Error: {str(e)}'
        n.type = 'negative'    
    finally:
        # 3. Always dismiss the notification, even if errors occur
        n.dismiss()

def load_topic_vectors_from_db(db_file, sql_table):
    entries = []
    entry_vectors = []
    
    with apsw.Connection(db_file) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT entry, entry_vector FROM {sql_table}")
        
        # Heavy CPU work: Parsing JSON
        for entry, vector_json in cursor.fetchall():
            if entry and vector_json:
                entries.append(entry)
                entry_vectors.append(np.array(json.loads(vector_json)))

    if not entries:
        return [], None

    # Heavy CPU work: Stacking arrays
    document_matrix = np.vstack(entry_vectors)
    return entries, document_matrix

def load_vectors_from_db(db_file, sql_table):
    entries = []
    entry_vectors = []
    
    # Open a NEW connection inside the worker (essential for thread safety)
    with apsw.Connection(db_file) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT path, entry, entry_vector FROM {sql_table}")
        
        # Heavy CPU work: Fetching and parsing JSON
        for path, entry, vector_json in cursor.fetchall():
            if path and entry and vector_json:
                entries.append(f"[{path}] {entry}")
                entry_vectors.append(np.array(json.loads(vector_json)))

    if not entries:
        return [], None

    # Heavy CPU work: Stacking arrays
    document_matrix = np.vstack(entry_vectors)
    return entries, document_matrix

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

def getBibleVersionList(custom: bool = False) -> List[str]:
    """Returns a list of available Bible versions"""
    bibleVersionList = ["ORB", "OIB", "OPB", "ODB", "OLB"]+list(config.bibles.keys())
    if custom: # app.storage.client["custom"]
        bibleVersionList += list(config.bibles_custom.keys())
        bibleVersionList = list(set(bibleVersionList))
    return sorted(bibleVersionList)

def getBibleVersionName(abb):
    if abb in config.bibles_custom:
        return config.bibles_custom[abb][0]
    elif abb in config.bibles:
        return config.bibles[abb][0]
    return abb

def get_default_bible(language):
    if language == 'tc':
        module = "CUV"
    elif language == 'sc':
        module = "CUVs"
    else:
        module = "NET"
    return module

def resolve_verses_additional_options(q: str = None, default_bible: str = "NET", custom: bool = False):
    BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]
    OT_BOOKS = BIBLE_BOOKS[:39]
    NT_BOOKS = BIBLE_BOOKS[39:]
    client_bibles = getBibleVersionList(custom)
    selected_bibles = default_bible
    selected_books = ['All', 'OT', 'NT'] + BIBLE_BOOKS
    if q and ":::" in q:
        additional_options, q = q.split(":::", 1)
        valid_books = []
        valid_bibles = []
        for i in additional_options.split(","):
            if i.strip() in selected_books+["None"]:
                valid_books.append(i.strip())
            elif i.strip() in client_bibles:
                valid_bibles.append(i.strip())
        # refine valid books and bibles
        if "None" in valid_books:
            valid_books = ["None"]
        elif "All" in valid_books or ("OT" in valid_books and "NT" in valid_books):
            valid_books = selected_books
        else:
            if "OT" in valid_books:
                valid_books += OT_BOOKS
                valid_books = list(set(valid_books))
            if "NT" in valid_books:
                valid_books += NT_BOOKS
                valid_books = list(set(valid_books))
        if valid_books:
            selected_books = valid_books
        if valid_bibles:
            selected_bibles = valid_bibles
    return client_bibles, selected_bibles, selected_books, q

def update_verses_sql_query(selected_values):
    """Generates the SQLite query based on selection."""
    BIBLE_BOOKS = [BibleBooks.abbrev["eng"][str(i)][0] for i in range(1,67)]
    BOOK_MAP = {book: i + 1 for i, book in enumerate(BIBLE_BOOKS)}
    OT_BOOKS = BIBLE_BOOKS[:39]
    NT_BOOKS = BIBLE_BOOKS[39:]
    if "OT" in selected_values:
        selected_values.remove("OT")
        selected_values += OT_BOOKS
    if "NT" in selected_values:
        selected_values.remove("NT")
        selected_values += NT_BOOKS
    selected_values = list(set(selected_values))
    
    # Filter to keep ONLY the actual book strings (ignore All/None/OT/NT)
    real_books = [b for b in selected_values if b in BIBLE_BOOKS]
    book_ids = [str(BOOK_MAP[b]) for b in real_books]
    
    base_query = "PRAGMA case_sensitive_like = false; SELECT * FROM Verses"
    where_clauses = []

    # Handle Book Logic
    if 'All' in selected_values:
        pass 
    elif not real_books:
        where_clauses.append("1=0")
    elif len(real_books) == 1:
        where_clauses.append(f"Book={book_ids[0]}")
    else:
        # Optimization: check if it's exactly OT or NT for cleaner SQL?
        # (Optional, but strictly sticking to IDs is safer for the engine)
        where_clauses.append(f"Book IN ({', '.join(book_ids)})")

    where_clauses.append(f"(Scripture REGEXP ?) ORDER BY Book, Chapter, Verse")

    # Assemble
    full_query = base_query
    if where_clauses:
        full_query += " WHERE " + " AND ".join(where_clauses)
    
    return full_query

# commentaries resources

config.commentaries_names = {
    "Barnes": "Notes on the Old and New Testaments (Barnes) [26 vol.]",
    "Benson": "Commentary on the Old and New Testaments (Benson) [5 vol.]",
    "BI": "Biblical Illustrator (Exell) [58 vol.]",
    "Brooks": "Complete Summary of the Bible (Brooks) [2 vol.]",
    "Calvin": "John Calvin's Commentaries (Calvin) [22 vol.]",
    "Clarke": "Commentary on the Bible (Clarke) [6 vol.]",
    "CBSC": "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]",
    "CECNT": "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]",
    "CGrk": "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]",
    "CHP": "Church Pulpit Commentary (Nisbet) [12 vol.]",
    "CPBST": "College Press Bible Study Textbook Series (College) [59 vol.]",
    "EBC": "Expositor's Bible Commentary (Nicoll) [49 vol.]",
    "ECER": "Commentary for English Readers (Ellicott) [8 vol.]",
    "EGNT": "Expositor's Greek New Testament (Nicoll) [5 vol.]",
    "GCT": "Greek Testament Commentary (Alford) [4 vol.]",
    "Gill": "Exposition of the Entire Bible (Gill) [9 vol.]",
    "Henry": "Exposition of the Old and New Testaments (Henry) [6 vol.]",
    "HH": "Horæ Homileticæ (Simeon) [21 vol.]",
    "ICCNT": "International Critical Commentary, NT (1896-1929) [16 vol.]",
    "JFB": "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]",
    "KD": "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]",
    "Lange": "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]",
    "MacL": "Expositions of Holy Scripture (MacLaren) [32 vol.]",
    "PHC": "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]",
    "Pulpit": "Pulpit Commentary (Spence) [23 vol.]",
    "Rob": "Word Pictures in the New Testament (Robertson) [6 vol.]",
    "Spur": "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]",
    "Vincent": "Word Studies in the New Testament (Vincent) [4 vol.]",
    "Wesley": "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]",
    "Whedon": "Commentary on the Old and New Testaments (Whedon) [14 vol.]",
}

def getCommentaryInfo(db):
    abb = os.path.basename(db)[1:-11]
    if abb in config.commentaries_names:
        return config.commentaries_names[abb]
    try:
        with apsw.Connection(db) as connn:
            query = "SELECT Title FROM Details limit 1"
            cursor = connn.cursor()
            cursor.execute(query)
            info = cursor.fetchone()
    except:
        return abb
    return info[0] if info else abb

commentaries_dir = os.path.join(BIBLEMATEGUI_DATA, "commentaries")
if os.path.isdir(commentaries_dir):
    config.commentaries = dict(sorted({os.path.basename(i)[1:-11]: (getCommentaryInfo(i), i) for i in glob.glob(os.path.join(commentaries_dir, "*.commentary"))}.items()))
else:
    Path(commentaries_dir).mkdir(parents=True, exist_ok=True)
    config.commentaries = {}
commentaries_dir_custom = os.path.join(BIBLEMATEGUI_DATA_CUSTOM, "commentaries")
if os.path.isdir(commentaries_dir_custom):
    config.commentaries_custom = dict(sorted({os.path.basename(i)[1:-11]: (getCommentaryInfo(i), i) for i in glob.glob(os.path.join(commentaries_dir_custom, "*.commentary"))}.items()))
else:
    Path(commentaries_dir_custom).mkdir(parents=True, exist_ok=True)
    config.commentaries_custom = {}

def getCommentaryVersionList(custom: bool = False) -> List[str]:
    """Returns a list of available Commentary versions"""
    commentaryVersionList = list(config.commentaries.keys())
    if custom: # app.storage.client["custom"]
        commentaryVersionList += list(config.commentaries_custom.keys())
        commentaryVersionList = list(set(commentaryVersionList))
    return sorted(commentaryVersionList)

def getCommentaryVersionName(abb):
    if abb in config.commentaries_custom:
        return config.commentaries_custom[abb][0]
    elif abb in config.commentaries:
        return config.commentaries[abb][0]
    return abb

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

def getLexiconList(custom: bool = False) -> List[str]:
    """Returns a list of available Lexicons"""
    client_lexicons = list(config.lexicons.keys())
    if custom: # app.storage.client["custom"]
        client_lexicons += list(config.lexicons_custom.keys())
    return sorted(list(set(client_lexicons)))

# fonts
app.add_static_files('/fonts', os.path.join(BIBLEMATEGUI_APP_DIR, "fonts"))

# images
app.add_static_files('/timelines', os.path.join(BIBLEMATEGUI_DATA, "books", "Timelines"))

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

def getAudioVersionList(custom: bool = False) -> List[str]:
    """Returns a list of available Audio versions"""
    version_options = list(config.audio.keys())
    if custom:
        version_options += list(config.audio_custom.keys())
        version_options = list(set(version_options))
    return version_options

config.topics = {
    "HIT": "Hitchcock's New and Complete Analysis of the Bible",
    "NAV": "Nave's Topical Bible",
    "TCR": "Thompson Chain References",
    "TOR": "Torrey's New Topical Textbook",
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
    'primary_color': '#827e67', # #827e67
    'secondary_color': '#c7c279', # #c7c279
    'negative_color': '#ff384f',
    'avatar': '',
    'custom_token': '',
    'primary_bible': 'NET',
    'secondary_bible': 'KJV',
    'favorite_commentary': 'AIC',
    'favorite_encyclopedia': 'ISB',
    'favorite_lexicon': 'Morphology',
    'hebrew_lexicon': 'TBESH',
    'greek_lexicon': 'TBESG',
    'ai_backend': 'googleai',
    'api_endpoint': '',
    'api_key': '',
    'ui_language': 'eng',
    'dark_mode': True,
    'notes': True,
    'left_drawer_open': False,
    'search_case_sensitivity': False,
    'search_mode': 1,
    'top_similar_entries': 5,
    'top_similar_verses': 20,
    'default_number_of_tabs1': 3,
    'default_number_of_tabs2': 3,
    'layout_swap_button': True,
    'bible_select_button': True,
    'loop_audio': True,
    'loop_podcast': True,
}