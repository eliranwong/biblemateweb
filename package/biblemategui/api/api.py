from biblemategui import config, BIBLEMATEGUI_DATA, getBibleVersionName, getBibleVersionList, getLexiconList, getCommentaryVersionName, getCommentaryVersionList, getAudioVersionList, get_default_bible, resolve_verses_additional_options, update_verses_sql_query
from biblemategui.fx.bible import getBiblePath, getBibleChapterVerses, get_bible_content

from biblemategui.pages.tools.commentary import fetch_commentary_content
from biblemategui.pages.tools.morphology import fetch_morphology
from biblemategui.pages.tools.xrefs import fetch_xrefs
from biblemategui.pages.tools.treasury import fetch_tske
from biblemategui.pages.search.lexicons import fetch_bible_lexicons_entry
from biblemategui.pages.search.bible_promises import fetch_promises_topic
from biblemategui.pages.search.bible_parallels import fetch_parallels_topic
from biblemategui.pages.search.bible_locations import fetch_bible_locations_entry
from biblemategui.pages.search.bible_characters import fetch_bible_characters_entry
from biblemategui.pages.search.bible_topics import fetch_bible_topics_entry
from biblemategui.pages.search.dictionaries import fetch_bible_dictionaries_entry
from biblemategui.pages.search.encyclopedias import fetch_bible_encyclopedias_entry

from biblemategui.data.bible_events import bible_events

from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from agentmake.utils.handle_text import htmlToMarkdown
import re, json, apsw, os

# TODO: DICTIONARY, ENCYCLOPEDIA, EXLB, _promise, _harmony

def get_resources(custom):
    client_bibles = getBibleVersionList(custom)
    client_commentaries = getCommentaryVersionList(custom)
    client_lexicons = getLexiconList(custom)
    client_audios = getAudioVersionList(custom)

    resources = {}
    resources["bibleListAbb"] = client_bibles
    resources["strongBibleListAbb"] = [i for i in client_bibles if i.endswith("x")]
    resources["bibleList"] = [getBibleVersionName(i) for i in client_bibles]
    resources["commentaryListAbb"] = client_commentaries
    resources["commentaryList"] = [getCommentaryVersionName(i) for i in client_commentaries]
    resources["referenceBookList"] = [] # backward compatibility to UBA
    resources["topicListAbb"] = list(config.topics.keys())
    resources["topicList"] = list(config.topics.values())
    resources["lexiconList"] = client_lexicons
    resources["dictionaryListAbb"] = list(config.dictionaries.keys())
    resources["dictionaryList"] = list(config.dictionaries.values())
    resources["encyclopediaListAbb"] = list(config.encyclopedias.keys())
    resources["encyclopediaList"] = list(config.encyclopedias.values())
    resources["thirdPartyDictionaryList"] = [] # backward compatibility to UBA
    resources["pdfList"] = [] # backward compatibility to UBA
    resources["epubList"] = [] # backward compatibility to UBA
    resources["docxList"] = [] # backward compatibility to UBA
    resources["bibleAudioModules"] = client_audios
    resources["dataList"] = [] # backward compatibility to UBA
    resources["searchToolList"] = [] # backward compatibility to UBA
    return resources

def refine_bible_module_and_query(query, language, custom):
    client_bibles = getBibleVersionList(custom)
    if ":::" in query and query.split(":::", 1)[0].strip() in client_bibles:
        module, query = query.split(":::", 1)
    elif language == 'tc':
        module = "CUV"
    elif language == 'sc':
        module = "CUVs"
    else:
        module = "NET"
    return module, query

def get_compare_chapters_content(query, language, custom): # accept multiple chapter reference
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    chapters = []
    for b in selected_bibles:
        q = f"{b}:::{query}"
        chapters.append(get_chapter_content(q, language, custom))
    return "\n\n".join(chapters)

def get_chapter_content(query, language, custom): # accept multiple chapter reference
    module, query = refine_bible_module_and_query(query, language, custom)
    parser = BibleVerseParser(False, language=language)
    refs = [(b, c) for b, c, *_ in parser.extractAllReferences(query)]
    chapters = []
    for b, c in sorted(list(set(refs))):
        db = getBiblePath(module)
        verses = getBibleChapterVerses(db, b, c)
        if not verses: continue
        chapter = f"## {parser.bcvToVerseReference(b,c,1, isChapter=True)} [{module}]\n\n"
        if verses:
            verses = [f"[{v}] {re.sub("<[^<>]*?>", "", verse_text).strip()}" for *_, v, verse_text in verses]
            chapter += "* "+"\n* ".join(verses)
        chapters.append(chapter)
    return "\n\n".join(chapters)

def get_verses_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    #module, query = refine_bible_module_and_query(query, language, custom)
    parser = BibleVerseParser(False, language=language)
    verses = get_bible_content(user_input=query, bible=selected_bibles, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_literal_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    parser = BibleVerseParser(False, language=language)
    sql_query = update_verses_sql_query(selected_books)
    verses = get_bible_content(user_input=query, bible=selected_bibles, sql_query=sql_query, search_mode=1, api=True, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_regex_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    parser = BibleVerseParser(False, language=language)
    sql_query = update_verses_sql_query(selected_books)
    verses = get_bible_content(user_input=query, bible=selected_bibles, sql_query=sql_query, search_mode=2, api=True, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_semantic_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    parser = BibleVerseParser(False, language=language)
    sql_query = update_verses_sql_query(selected_books)
    verses = get_bible_content(user_input=query, bible=selected_bibles, sql_query=sql_query, search_mode=3, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_treasury_content(query, language, custom): # accept multiple references
    markdown_contents = []
    parser = BibleVerseParser(False, language=language)
    for b, c, v in parser.extractExhaustiveReferences(query):
        html = fetch_tske(b, c, v)
        if not html: continue
        markdown_contents.append(htmlToMarkdown(html))
    return "\n\n".join(markdown_contents)

def get_xrefs_content(query, language, custom): # accept multiple references
    module, query = refine_bible_module_and_query(query, language, custom)
    markdown_contents = []
    parser = BibleVerseParser(False, language=language)
    for b, c, v in parser.extractExhaustiveReferences(query):
        query = fetch_xrefs(b, c, v)
        if not query: continue
        markdown_content = f"## Cross References - {parser.bcvToVerseReference(b,c,v)}\n\n"
        query = parser.bcvToVerseReference(b, c, v) + "; " + query
        verses = get_bible_content(query, bible=module, parser=parser)
        verses = [f"[{i['ref']}] {i['content']}" for i in verses]
        markdown_content += "* "+"\n* ".join(verses)
        markdown_contents.append(markdown_content)
    return "\n\n".join(markdown_contents)

def get_promises_content(query, language, custom): # accept single reference
    module, query = refine_bible_module_and_query(query, language, custom)
    topic, query = fetch_promises_topic(query)
    parser = BibleVerseParser(False, language=language)
    verses = get_bible_content(query, bible=module, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    markdown_content = f"## Promises - {topic}\n\n"
    markdown_content += "* "+"\n* ".join(verses)
    return markdown_content

def get_parallels_content(query, language, custom): # accept single reference
    module, query = refine_bible_module_and_query(query, language, custom)
    topic, query = fetch_parallels_topic(query)
    parser = BibleVerseParser(False, language=language)
    verses = get_bible_content(query, bible=module, parser=parser)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    markdown_content = f"## Promises - {topic}\n\n"
    markdown_content += "* "+"\n* ".join(verses)
    return markdown_content

def get_morphology_content(query, language, custom): # accept multiple references
    markdown_contents = []
    parser = BibleVerseParser(False, language=language)
    for b, c, v in parser.extractExhaustiveReferences(query):
        if results := fetch_morphology(b,c,v):
            markdown_content = f"## Morphology - {parser.bcvToVerseReference(b,c,v)}\n\n"
            for wordID, clauseID, book, chapter, verse, word, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronunciation, interlinear, translation, gloss in results:
                markdown_content += f"- **{word}** ({lexicalEntry.split(',')[-2]}): {morphology} — {gloss}\n"
            markdown_contents.append(markdown_content)
    return "\n\n".join(markdown_contents)

def get_commentary_content(query, language, custom): # accept multiple references
    def get_default_commentary_module(language):
        if language == 'tc':
            module = "AICTC"
        elif language == 'sc':
            module = "AICSC"
        else:
            module = "AIC"
        return module
    if ":::" in query:
        module, query = query.split(":::", 1)
        if not module in getCommentaryVersionList(custom):
            module = get_default_commentary_module(language)
    else:
        module = get_default_commentary_module(language)
    html = fetch_commentary_content(query, module, language)
    return htmlToMarkdown(html)

def get_lexicon_content(query, language, custom): # accept single references
    if ":::" in query:
        lexicon, topic = query.split(":::", 1)
    else:
        lexicon, topic = "SECE", query
    client_lexicons = getLexiconList(custom)
    html = fetch_bible_lexicons_entry(client_lexicons, lexicon, topic)
    return htmlToMarkdown(html)

def get_chronology_content():
    markdown_contents = "## Bible Chronnology\n\n"
    for i in bible_events:
        markdown_contents += f"- {i.get("year", "")} | {i.get("event", "")} | {i.get("reference", "")}"
    return markdown_contents

def get_locations_content(query, language, custom):
    html, *_ = fetch_bible_locations_entry(query)
    return htmlToMarkdown(html)

def get_characters_content(query, language, custom):
    html = fetch_bible_characters_entry(query)
    return htmlToMarkdown(html)

def get_topics_content(query, language, custom):
    html = fetch_bible_topics_entry(query)
    return htmlToMarkdown(html)

def get_names_content(query, language, custom):
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "exlb.db")
    sql_table = "exlbn"
    with apsw.Connection(db_file) as connn:
        cursor = connn.cursor()
        cursor.execute(f"SELECT entry FROM {sql_table} WHERE path = ?;", (query,))
        fetch = cursor.fetchone()
    return fetch[0] if fetch else ""

def get_dictionaries_content(query, language, custom):
    html = fetch_bible_dictionaries_entry(query)
    return htmlToMarkdown(html)

def get_encyclopedias_content(query, language, custom):
    if ":::" in query:
        sql_table, query = query.split(":::", 1)
    else:
        sql_table = "ISB"
    html = fetch_bible_encyclopedias_entry(query, sql_table)
    return htmlToMarkdown(html)

API_TOOLS = {
    #"chat": ai_chat,
    "morphology": get_morphology_content, # API with additional options
    #"indexes": get_indexes_content,
    #"podcast": bibles_podcast,
    #"audio": bibles_audio,
    "chapter": get_chapter_content, # API with additional options
    "comparechapter": get_compare_chapters_content, # API with additional options
    "bible": get_verses_content, # backward compatibility to UBA
    "verses": get_verses_content, # API with additional options
    "literal": get_literal_content, # API with additional options
    "regex": get_regex_content, # API with additional options
    "semantic": get_semantic_content, # API with additional options
    "treasury": get_treasury_content, # API with additional options
    "tske": get_treasury_content, # backward compatibility to UBA
    "commentary": get_commentary_content, # API with additional options
    "chronology": get_chronology_content,
    #"timelines": bible_timelines,
    "xrefs": get_xrefs_content, # API with additional options
    "crossreference": get_xrefs_content, # backward compatibility to UBA
    "promises": get_promises_content,
    #"promises_": bible_promises_menu,
    "parallels": get_parallels_content,
    #"parallels_": bible_parallels_menu,
    "topics": get_topics_content,
    "characters": get_characters_content,
    "locations": get_locations_content,
    "names": get_names_content,
    "dictionaries": get_dictionaries_content,
    "encyclopedias": get_encyclopedias_content, # API with additional options
    "lexicons": get_lexicon_content, # API with additional options
    "lexicon": get_lexicon_content, # backward compatibility to UBA
    #"maps": search_bible_maps,
    #"relationships": search_bible_relationships,
}

def get_tool_content(tool: str, query: str, language: str = 'eng', custom: bool = False):
    content = API_TOOLS[tool](query, language, custom)
    # refine markdown text
    search_replace = (
        (r"\n([0-9]+?) \(([^\(\)]+?)\)", r"\n- `\1` (`\2`)"),
        (r"^([0-9]+?) \(([^\(\)]+?)\)", r"- `\1` (`\2`)"),
        (r"\n\(([^\(\)]+?)\)", r"\n- (`\1`)"),
        (r"^\(([^\(\)]+?)\)", r"- (`\1`)"),
    )
    for search, replace in search_replace:
        content = re.sub(search, replace, content)
    return content

def get_api_content(query: str, language: str = 'eng', custom: bool = False):
    if query.lower() == ".resources":
        return json.dumps(get_resources(custom))
    elif ":::" in query and query.split(":::", 1)[0].strip().lower() in API_TOOLS:
        tool, query = query.split(":::", 1)
        tool = tool.strip()
        return get_tool_content(tool, query, language, custom)
    elif query.strip():
        return get_tool_content("verses", query, language, custom)
    return ""