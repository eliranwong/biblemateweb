from biblemategui import getBibleVersionList
from biblemategui.fx.bible import getBiblePath, getBibleChapterVerses
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from agentmake.utils.handle_text import htmlToMarkdown
import re

def get_verses_content(query: str, language: str = 'eng', custom: bool = False):
    return ""

API_TOOLS = {
    #"chat": ai_chat,
    #"morphology": word_morphology,
    #"indexes": resource_indexes,
    #"podcast": bibles_podcast,
    #"audio": bibles_audio,
    "verses": get_verses_content, # API with additional options
    #"treasury": treasury,
    #"commentary": bible_commentary, # API with additional options
    #"chronology": bible_chronology,
    #"timelines": bible_timelines,
    #"xrefs": xrefs,
    #"promises": search_bible_promises,
    #"promises_": bible_promises_menu,
    #"parallels": search_bible_parallels,
    #"parallels_": bible_parallels_menu,
    #"topics": search_bible_topics,
    #"characters": search_bible_characters,
    #"locations": search_bible_locations,
    #"names": search_bible_names,
    #"dictionaries": search_bible_dictionaries,
    #"encyclopedias": search_bible_encyclopedias, # API with additional options
    #"lexicons": search_bible_lexicons, # API with additional options
    #"maps": search_bible_maps,
    #"relationships": search_bible_relationships,
}

def get_tool_content(tool: str, query: str, custom: bool = False):
    return f"{tool} {query}"

def get_api_content(query: str, language: str = 'eng', custom: bool = False):
    bibles = getBibleVersionList(custom)
    parser = BibleVerseParser(False, language=language)
    refs = parser.extractAllReferences(query)
    if query.lower().startswith("bible:::") and refs:
        query = query[8:]
        b,c,*_ = refs[0]
        if ":::" in query and query.split(":::", 1)[0].strip() in bibles:
            version, query = query.split(":::", 1)
            version = version.strip()
        else:
            version = "NET"
        db = getBiblePath(version)
        verses = getBibleChapterVerses(db, b, c)
        chapter = f"# {parser.bcvToVerseReference(b,c,1)[:-2]}\n\n"
        if verses:
            verses = [f"[{v}] {re.sub("<[^<>]*?>", "", verse_text).strip()}" for *_, v, verse_text in verses]
            chapter += "* "+"\n* ".join(verses)
        return chapter
    elif ":::" in query and query.split(":::", 1)[0].strip().lower() in ["audio", "verses", "commentary"]:
        tool, query = query.split(":::", 1)
        tool = tool.strip()
        return get_tool_content(tool, query, custom)
    return ""