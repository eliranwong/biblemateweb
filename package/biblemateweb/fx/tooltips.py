import os, apsw, re
from biblemateweb import BIBLEMATEWEB_DATA, config
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from nicegui import app

def convert_uba_bible_cmd(match):
    refs = BibleVerseParser(False).extractAllReferences(match.group(1))
    if refs:
        return f'''<ref onclick="bcv{refs[0]}">'''
    return match.group(0)

def get_tooltip_data(word):
    """Fetch tooltip data from database"""
    if word.startswith("bn,"):
        # bible notes
        return get_bn_data(word)
    elif re.search("^(wh|w)[0-9]+?$", word):
        # Hebrew or Greek ID
        return get_morphology_data(word)
    elif re.search("^(H|G)[0-9]", word):
        # Hebrew or Greek Strong's numbers
        return get_lexical_data(word)

def get_lexical_data(word):
    """Fetch lexical data from database"""
    lexicon = app.storage.user["hebrew_lexicon"] if word.startswith("H") else app.storage.user["greek_lexicon"]
    db = config.lexicons_custom[lexicon] if lexicon in config.lexicons_custom else config.lexicons[lexicon] if lexicon in config.lexicons else ""
    if not db:
        return None
    app.storage.user['favorite_lexicon'] = lexicon
    with apsw.Connection(db) as connn:
        cursor = connn.cursor()
        sql_query = f"SELECT Definition FROM Lexicon WHERE Topic=? limit 1"
        cursor.execute(sql_query, (word,))
        fetch = cursor.fetchone()
    if fetch:
        content = fetch[0]
        content = f'''<ref onclick='lex("{word}")'>[{lexicon}] {word}</ref><hr>{content}'''
        content = re.sub(r'''(onclick|ondblclick)="(lex|cr|bcv)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
        content = re.sub(r"""(onclick|ondblclick)='(lex|cr|bcv)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
        return {'description': content, 'links': ""}
    return None

def get_morphology_data(word):
    result = None
    db = os.path.join(BIBLEMATEWEB_DATA, "morphology.sqlite")
    with apsw.Connection(db) as connn:
        query = "SELECT * FROM morphology WHERE WordID=? and Book < 40" if word.startswith("wh") else "SELECT * FROM morphology WHERE WordID=? and Book > 39"
        cursor = connn.cursor()
        cursor.execute(query, (int(word[2:] if word.startswith("wh") else word[1:]),))
        result = cursor.fetchone()    
    if result:
        wordID, clauseID, book, chapter, verse, word, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronunciation, interlinear, translation, gloss = result
        audio_path = '/bhs5_audio' if book < 40 else '/ognt_audio'
        audio_module = 'BHS5' if book < 40 else 'OGNT'
        audio_file = f'{audio_path}/{book}_{chapter}/{audio_module}_{book}_{chapter}_{verse}_{wordID}.mp3'
        audio_file_lex = f'{audio_path}/{book}_{chapter}/lex_{audio_module}_{book}_{chapter}_{verse}_{wordID}.mp3'
        lexicon_entry_1, lexicon_entry_2, *_ = lexicalEntry.split(',')
        if not lexicon_entry_2:
            lexicon_entry_2 = lexicon_entry_1
        description = f'''<{'heb' if book < 40 else 'grk'} onclick="emitEvent('wd', ['{lexicon_entry_1}']); return false;">{word}</{'heb' if book < 40 else 'grk'}> | <wphono>{transliteration}</wphono> | <wphono>{pronunciation}</wphono><br>
<audio controls style="margin-top: 4px;">
  <source src="{audio_file}" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>
<{'heb' if book < 40 else 'grk'} onclick="emitEvent('wd', ['{lexicon_entry_2}']); return false;">{lexeme}</{'heb' if book < 40 else 'grk'}><br>
<audio controls style="margin-top: 4px;">
  <source src="{audio_file_lex}" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>
<clid>{morphology[:-1].replace(",", ", ")}</clid><br>
<wgloss>{interlinear}</wgloss><br>
<wtrans>{translation}</wtrans>'''
        return {'description': description, 'links': ""}
    return None

def get_bn_data(word):
    _, bible, b, c, v, id = word.split(",", 5)
    db = config.bibles_custom[bible][-1] if bible in config.bibles_custom else config.bibles[bible][-1] if bible in config.bibles else ""
    if not db:
        return None
    with apsw.Connection(db) as connn:
        query = "SELECT Note FROM Notes WHERE Book=? AND Chapter=? AND Verse=? AND ID=?"
        args = (int(b), int(c), int(v), id)
        cursor = connn.cursor()
        cursor.execute(query, args)
        fetch = cursor.fetchone()
    if fetch:
        content = fetch[0]
        if not "<" in content and not ">" in content: # when the note is non-tagged
            content = BibleVerseParser(False).parseText(content)
        # handle UBA cmd
        if '''<ref onclick='document.title="BIBLE:::''' in content:
            content = re.sub('''<ref onclick='document.title="BIBLE:::([^<>]+?)"'>''', convert_uba_bible_cmd, content)
        content = re.sub(r'''(onclick|ondblclick)="(cr|bcv)\((.*?)\)"''', r'''\1="emitEvent('\2', [\3]); return false;"''', content)
        content = re.sub(r"""(onclick|ondblclick)='(cr|bcv)\((.*?)\)'""", r"""\1='emitEvent("\2", [\3]); return false;'""", content)
        return {'description': content, 'links': ""}
    return None