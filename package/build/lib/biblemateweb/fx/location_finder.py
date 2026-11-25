import apsw, os, re
from biblemateweb import BIBLEMATEWEB_DATA
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

class LocationIndexes:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(BIBLEMATEWEB_DATA, "indexes2.sqlite")

    def fetchLocations(self, query, keys):
        fetch = []
        with apsw.Connection(self.database) as connn:
            cursor = connn.cursor()
            cursor.execute(query, keys)
            fetchall = cursor.fetchall()
        if fetchall:
            p = re.compile("'(BL[0-9]+?)'")
            for i in fetchall:
                fetch += p.findall(i[0])
        return fetch

    def getBookLocations(self, b):
        query = "SELECT Information FROM exlbl WHERE Book = ?"
        keys = (b,)
        return self.fetchLocations(query, keys)

    def getChapterLocations(self, b, c, startV=None, endV=None):
        if startV is not None and endV is not None:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse >= ? AND Verse <= ?"
            keys = (b, c, startV, endV)
        elif startV is not None:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse >= ?"
            keys = (b, c, startV)
        elif endV is not None:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse <= ?"
            keys = (b, c, endV)
        else:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ?"
            keys = (b, c)
        return self.fetchLocations(query, keys)

    def getVerseLocations(self, b, c, v):
        query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse = ?"
        keys = (b, c, v)
        return self.fetchLocations(query, keys)

class LocationFinder:
    def __init__(self):
        self.indexes = LocationIndexes()

    def getLocations(self, references):
        parser = BibleVerseParser(False)
        verseList = parser.extractAllReferences(references, tagged=False)
        if not verseList:
            return []
        else:
            combinedLocations = []
            for reference in verseList:
                combinedLocations += self.getLocationsFromReference(reference)
            return sorted(list(set(combinedLocations)))

    def getLocationsFromReference(self, reference):
        if reference:
            combinedLocations = []
            if len(reference) == 5:
                b, c, v, ce, ve = reference
                if c == ce:
                    if v == ve:
                        combinedLocations += self.indexes.getVerseLocations(b, c, v)
                    elif ve > v:
                        combinedLocations += self.indexes.getChapterLocations(b, c, startV=v, endV=ve)
                elif ce > c:
                    combinedLocations += self.indexes.getChapterLocations(b, c, startV=v)
                    combinedLocations += self.indexes.getChapterLocations(b, ce, endV=ve)
                    if (ce - c) > 1:
                        for i in range(c+1, ce):
                            combinedLocations += self.indexes.getChapterLocations(b, i)
            else:
                b, c, v, *_ = reference
                combinedLocations += self.indexes.getVerseLocations(b, c, v)
            return combinedLocations
        else:
            return []

if __name__ == "__main__":
    finder = LocationFinder()
    locations = finder.getLocations("Rev 1:11, Josh 10:1-43, Act 15:36-18:22")
    print(locations)