import apsw, os, re
from biblemateweb import BIBLEMATEWEB_DATA
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser


def create_indexes():

    parser = BibleVerseParser(False)

    # --- CONFIGURATION ---
    DB_FILE = os.path.join(BIBLEMATEWEB_DATA, "collections3.sqlite")
    with apsw.Connection(DB_FILE) as connn:
        cursor = connn.cursor()
        cursor.execute("SELECT * FROM PROMISES")
        fetches = cursor.fetchall()
    
        for tool, number, topic, passages in fetches:
            print(topic)
            refs = parser.extractExhaustiveReferences(re.sub("<[^<>]+?>", "", passages))
            refs = str(refs) if refs else ""
            insert_sql = """
            INSERT INTO PROMISES_INDEXES (Tool, Number, Topic, Passages)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(insert_sql, (tool, number, topic, refs))

create_indexes()