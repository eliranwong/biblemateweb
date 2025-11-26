import re, sqlite3

def update_scripture_strings(db_file, regex, replacement):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 1. Fetch all records (need Scripture text, and primary key fields for update)
    # The primary key for the update is the combination of Book, Chapter, and Verse
    cursor.execute('SELECT Book, Chapter, Verse, Scripture FROM Verses WHERE Book > 39')
    rows = cursor.fetchall()

    updates = []
    
    # 2. Iterate through rows and perform search/replace
    for book, chapter, verse, scripture in rows:
        # Perform the regex search and replace
        new_scripture = regex.sub(replacement, scripture)

        # Check if the text was actually modified before scheduling the update
        updates.append((new_scripture, book, chapter, verse))

    # 3. Execute batch UPDATE
    if updates:
        # SQL UPDATE statement uses placeholders (?) for parameterized execution
        # We update the Scripture column WHERE the primary key columns match
        update_sql = '''
        UPDATE Verses 
        SET Scripture = ? 
        WHERE Book = ? AND Chapter = ? AND Verse = ?
        '''
        # Use executemany for a fast, single-transaction update of multiple rows
        cursor.executemany(update_sql, updates)
        
        # 4. Commit the changes to the original SQLite file
        conn.commit()
        print("Update committed successfully.")
    else:
        print("No changes found to commit.")

    conn.close()

# Execute the function
compiled_regex = re.compile(r'onclick="w\([0-9]+?,([0-9]+?)\)" onmouseover="iw\([0-9]+?,[0-9]+?\)"')
replacement_string = r'id="w\1"'
update_scripture_strings("/home/eliran/UniqueBible/marvelData/bibles/OHGB.bible", compiled_regex, replacement_string)