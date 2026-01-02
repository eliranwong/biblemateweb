from biblemateweb import config, BIBLEMATEWEB_DATA, getBibleVersionName, getBibleVersionList, getLexiconList, getCommentaryVersionName, getCommentaryVersionList, getAudioVersionList, get_default_bible, resolve_verses_additional_options, update_verses_sql_query
from biblemateweb.fx.bible import getBiblePath, getBibleChapterVerses, get_bible_content

from biblemateweb.pages.tools.commentary import fetch_commentary_content
from biblemateweb.pages.tools.morphology import fetch_morphology
from biblemateweb.pages.tools.xrefs import fetch_xrefs
from biblemateweb.pages.tools.treasury import fetch_tske
from biblemateweb.pages.search.lexicons import fetch_bible_lexicons_entry
from biblemateweb.pages.search.bible_promises import fetch_promises_topic
from biblemateweb.pages.search.bible_parallels import fetch_parallels_topic
from biblemateweb.pages.search.bible_locations import fetch_bible_locations_entry
from biblemateweb.pages.search.bible_characters import fetch_bible_characters_entry
from biblemateweb.pages.search.bible_topics import fetch_bible_topics_entry
from biblemateweb.pages.search.dictionaries import fetch_bible_dictionaries_entry
from biblemateweb.pages.search.encyclopedias import fetch_bible_encyclopedias_entry

from biblemateweb.data.bible_events import bible_events

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
    verses = get_bible_content(user_input=query, bible=selected_bibles, parser=parser, html=False)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_literal_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    parser = BibleVerseParser(False, language=language)
    sql_query = update_verses_sql_query(selected_books)
    verses = get_bible_content(user_input=query, bible=selected_bibles, sql_query=sql_query, search_mode=1, api=True, parser=parser, html=False)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_regex_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    parser = BibleVerseParser(False, language=language)
    sql_query = update_verses_sql_query(selected_books)
    verses = get_bible_content(user_input=query, bible=selected_bibles, sql_query=sql_query, search_mode=2, api=True, parser=parser, html=False)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    return "* "+"\n* ".join(verses)

def get_semantic_content(query, language, custom):
    client_bibles, selected_bibles, selected_books, query = resolve_verses_additional_options(query, get_default_bible(language), custom)
    parser = BibleVerseParser(False, language=language)
    sql_query = update_verses_sql_query(selected_books)
    verses = get_bible_content(user_input=query, bible=selected_bibles, sql_query=sql_query, search_mode=3, parser=parser, html=False)
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
        query = parser.bcvToVerseReference(b, c, v) + "; " + query[0]
        verses = get_bible_content(query, bible=module, parser=parser, html=False)
        verses = [f"[{i['ref']}] {i['content']}" for i in verses]
        markdown_content += "* "+"\n* ".join(verses)
        markdown_contents.append(markdown_content)
    return "\n\n".join(markdown_contents)

def get_promises_content(query, language, custom): # accept single reference
    module, query = refine_bible_module_and_query(query, language, custom)
    topic, query = fetch_promises_topic(query)
    parser = BibleVerseParser(False, language=language)
    verses = get_bible_content(query, bible=module, parser=parser, html=False)
    verses = [f"[{i['ref']}] {i['content']}" for i in verses]
    markdown_content = f"## Promises - {topic}\n\n"
    markdown_content += "* "+"\n* ".join(verses)
    return markdown_content

def get_parallels_content(query, language, custom): # accept single reference
    module, query = refine_bible_module_and_query(query, language, custom)
    topic, query = fetch_parallels_topic(query)
    parser = BibleVerseParser(False, language=language)
    verses = get_bible_content(query, bible=module, parser=parser, html=False)
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

def get_chronology_content(query, language, custom):
    markdown_contents = "## Bible Chronnology\n\n"
    for i in bible_events:
        year = i.get("year", "")
        event = i.get("event", "")
        reference = i.get("reference", "")
        if not query:
            markdown_contents += f"- {year} | {event} | {reference}"
        elif re.search(query, year) or re.search(query, event) or re.search(query, reference):
            markdown_contents += f"- {year} | {event} | {reference}"
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
    db_file = os.path.join(BIBLEMATEWEB_DATA, "vectors", "exlb.db")
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
    "morphology": ("retrieve word morphology in bible verse(s)", "e.g. morphology:::John 3:16", get_morphology_content),
    "chapter": ("retrieve bible chapter(s)", "e.g. chapter:::John 3, chapter:::KJV:::John 3", get_chapter_content),
    "comparechapter": ("compare bible chapter(s)", "e.g. comparechapter:::KJV,CUV:::John 3", get_compare_chapters_content),
    "bible": ("", "backward compatibility to UBA", get_verses_content),
    "verses": ("retrieve bible verse(s)", "e.g. verses:::John 3:16; Rm 5:8, verses:::KJV:::John 3:16; Rm 5:8", get_verses_content),
    "literal": ("literal string search for bible verse(s)", "e.g. literal:::Jesus love, literal:::KJV:::Jesus love, literal:::Matt,KJV:::love", get_literal_content),
    "regex": ("regular expression search for bible verse(s)", "e.g. regex:::Jesus.*?love, regex:::KJV:::Jesus.*?love, regex:::Matt,KJV:::Jesus.*?love", get_regex_content),
    "semantic": ("semantic search for bible verse(s)", "e.g. semantic:::Jesus love, semantic:::KJV:::Jesus love , semantic:::Matt,KJV:::Jesus love", get_semantic_content),
    "treasury": ("treasury of scripture knowledge of bible verse(s)", "e.g. treasury:::John 3:16", get_treasury_content),
    "tske": ("", "backward compatibility to UBA", get_treasury_content),
    "commentary": ("", "e.g. commentary:::John 3:16, commentary:::AICTC:::John 3:16", get_commentary_content),
    "chronology": ("retrieve or search for bible chronology", "e.g. chronology:::, chronology:::70 AD, chronology:::Jesus, chronology:::Acts 15", get_chronology_content),
    "xrefs": ("retrieve bible verse cross-references", "; e.g. xrefs:::John 3:16, xrefs:::KJV:::John 3:16", get_xrefs_content),
    "crossreference": ("", "backward compatibility to UBA", get_xrefs_content),
    "promises": ("retrieve bible promises", "e.g. promises:::1.1, promises:::KJV:::1.1", get_promises_content),
    "parallels": ("retrieve bible parallel passages", "e.g. parallels:::1.1, parallels:::KJV:::1.1", get_parallels_content),
    "topics": ("", "e.g. topic:::NAV100", get_topics_content),
    "characters": ("retrieve bible character studies", "e.g. characters:::BP100", get_characters_content),
    "locations": ("retrieve bible location studies", "e.g. locations:::BP100", get_locations_content),
    "names": ("search for bible names and their meanings", "e.g. names:::Joshua", get_names_content),
    "dictionaries": ("retrieve bible dictionary entries", "e.g. dictionaries:::EAS100", get_dictionaries_content),
    "encyclopedias": ("retrieve bible encyclopedia entries", "e.g. encyclopedias:::ISB:::ISBE100", get_encyclopedias_content),
    "lexicons": ("retrieve bible lexicon entries", "e.g. lexicons:::H100, lexicons:::Morphology:::G100", get_lexicon_content),
    "lexicon": ("", "backward compatibility to UBA", get_lexicon_content),
}

def get_tool_content(tool: str, query: str, language: str = 'eng', custom: bool = False):
    content = API_TOOLS[tool][-1](query, language, custom)
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

def get_help_content():
    intro = """# API Usage

Each API query combines a keyword and its options, separated by `:::`

"""
    help_content = []
    for i in API_TOOLS:
        help_content.append(f"""## Keyword - {i}
{i[0].capitalize()}
{i[1]}""")
    return intro + "\n\n".join(help_content)

def get_api_content(query: str, language: str = 'eng', custom: bool = False):
    if query.lower() == ".help":
        return get_help_content()
    elif query.lower() == ".resources":
        return json.dumps(get_resources(custom))
    elif ":::" in query and query.split(":::", 1)[0].strip().lower() in API_TOOLS:
        tool, query = query.split(":::", 1)
        tool = tool.strip()
        return get_tool_content(tool, query, language, custom)
    elif query.strip():
        return get_tool_content("verses", query, language, custom)
    return ""