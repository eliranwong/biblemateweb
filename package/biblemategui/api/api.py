from biblemategui import getBibleVersionList
from biblemategui.fx.bible import getBiblePath, getBibleChapterVerses, get_bible_content
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from agentmake.utils.handle_text import htmlToMarkdown
import re

def get_verses_content(query, custom, parser):
    verses = get_bible_content(user_input=query, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_literal_content(query, custom, parser):
    sql_query = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture LIKE ?) ORDER BY Book, Chapter, Verse"
    verses = get_bible_content(user_input=query, sql_query=sql_query, search_mode=1, api=True, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_regex_content(query, custom, parser):
    sql_query = "PRAGMA case_sensitive_like = false; SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE (Scripture REGEXP ?) ORDER BY Book, Chapter, Verse"
    verses = get_bible_content(user_input=query, sql_query=sql_query, search_mode=2, api=True, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_semantic_content(query, custom, parser):
    verses = get_bible_content(user_input=query, search_mode=3, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

API_TOOLS = {
    #"chat": ai_chat,
    #"morphology": word_morphology,
    #"indexes": resource_indexes,
    #"podcast": bibles_podcast,
    #"audio": bibles_audio,
    "verses": get_verses_content, # API with additional options
    "literal": get_literal_content, # API with additional options
    "regex": get_regex_content, # API with additional options
    "semantic": get_semantic_content, # API with additional options
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

def get_tool_content(tool, query, custom, parser):
    return API_TOOLS[tool](query, custom=custom, parser=parser)

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
    elif ":::" in query and query.split(":::", 1)[0].strip().lower() in API_TOOLS:
        tool, query = query.split(":::", 1)
        tool = tool.strip()
        return get_tool_content(tool, query, custom, parser)
    return ""