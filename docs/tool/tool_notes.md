# **Cloud Notes Guide**

This tool provides verse-specific note-taking with automatic cloud sync to your Google Drive, allowing you to maintain organized Bible study notes across all your devices.

## **What are Cloud Notes?**

Cloud Notes is a powerful note-taking system that lets you create and sync notes for specific Bible verses, chapters, or entire books. All notes are automatically saved to your Google Drive account, ensuring your study notes are backed up and accessible from any device.

## **Getting Started**

### **Login Requirement**

To use Cloud Notes, you must:
1. Click "Login with Google"
2. Authorize BibleMate AI to access your Google Drive
3. Grant permission to store files in the App Data folder

**Privacy Note**: BibleMate AI stores notes exclusively in your own Google Drive. The application does not collect, store, or share your personal notes on its servers.

### **First-Time Setup**

1. Open the Notes tool
2. Click "Login with Google"
3. Complete Google OAuth authorization
4. Wait for the tool to initialize your note index
5. Start taking notes!

## **How to Use Cloud Notes**

### **Creating and Editing Notes**

1. **Select a Verse**: Use the Bible selector to choose a book, chapter, and verse.
2. **Type Your Note**: Write in the text area using Markdown formatting.
3. **Save**: Click the menu (⋮) and select "Save" to sync to the cloud.
4. **Switch Verses**: Select different verses to create multiple notes.

### **Special Note Types**

- **Verse Notes**: Select a specific verse (e.g., John 3:16)
- **Chapter Notes**: Set verse to "0" to create a note for the entire chapter
- **Book Notes**: Set chapter to "0" to create a note for the entire book

### **Bible Selector Options**

The Bible selector includes special zero options:
- **Chapter 0**: Creates a book-level note
- **Verse 0**: Creates a chapter-level note (when chapter > 0)

## **Toolbar Menu**

Click the menu button (⋮) to access all note management features:

### **View and Edit**

| Option | Icon | Function |
| :---- | :---- | :---- |
| **Read / Edit** | 👁️ / ✏️ | Toggle between reading formatted Markdown and editing raw text |

### **Note Management**

| Option | Icon | Function |
| :---- | :---- | :---- |
| **Save** | 💾 | Save current note to Google Drive (syncs across devices) |
| **Delete** | ❌ | Delete the current note (with confirmation) |
| **Download** | 📥 | Download current note as a `.json` file |
| **Download All** | 📥 | Download all notes as a `.zip` file for backup |

### **Import and Sync**

| Option | Icon | Function |
| :---- | :---- | :---- |
| **Import** | 📤 | Import notes from `.json` or `.zip` files |
| **Rebuild Index** | 🛠️ | Rebuild the search index (for maintenance or after bulk imports) |
| **Download Index** | 📥 | Download the note index as a backup file |

### **Account**

| Option | Icon | Function |
| :---- | :---- | :---- |
| **Logout** | 🔒 | Log out of Google account (recommended on shared devices) |

## **Features**

### **Automatic Cloud Sync**

- Notes are saved to your Google Drive App Data folder
- Syncs across all devices where you're logged in
- Automatic backup—never lose your notes
- Secure storage in your own Google account

### **Markdown Formatting**

Write notes in Markdown and see them beautifully formatted in Read Mode:

```markdown
# Study Notes for John 3:16

## Key Observations
- God's **love** is universal
- Belief leads to eternal life

## Cross-References
- Romans 5:8
- 1 John 4:9-10

## Application
Trust in God's love today.
```

### **Clickable Bible References**

Type Bible references in your notes, and they become clickable in Read Mode:
- `John 3:16` → Opens in Bible area when clicked
- `Genesis 1:1-3` → Automatically parsed and linked
- Multiple references work too!

### **Verse-Organized Storage**

Each note is identified by its verse ID:
- **Format**: `BookNumber_ChapterNumber_VerseNumber`
- **Example**: `43_3_16` = John 3:16
- **Chapter Note**: `43_3_0` = John chapter 3
- **Book Note**: `43_0_0` = Book of John

### **Search Index**

The tool maintains a search index of all your notes:
- Tracks which verses have notes
- Enables quick lookup
- Can be downloaded as backup
- Rebuilt automatically when needed

### **Import and Export**

**Export Options**:
- **Single Note**: Download current note as `.json`
- **All Notes**: Download everything as `.zip` with index

**Import Options**:
- **Single Note**: Upload a `.json` file
- **Bulk Import**: Upload a `.zip` with multiple notes

**Use Cases**:
- Backup before major changes
- Transfer notes between accounts
- Share study notes with others
- Migrate from other systems

### **Edit/Read Modes**

**Edit Mode**:
- Full-height text area for comfortable typing
- Markdown syntax for formatting
- Auto-saves to browser temporarily
- Real-time editing

**Read Mode**:
- Formatted HTML display
- Clickable Bible references
- Tables, lists, and headers rendered properly
- Scrollable preview area

## **Tips for Effective Use**

1. **Save Regularly**: Click Save after making important changes.
2. **Use Markdown**: Format notes with headers, lists, and emphasis for better organization.
3. **Chapter Overviews**: Create chapter-level notes (verse 0) for summaries.
4. **Book Introductions**: Create book-level notes (chapter 0) for background information.
5. **Cross-Reference**: Include related verses in your notes for easy navigation.
6. **Regular Backups**: Download all notes periodically as insurance.
7. **Rebuild Index**: If notes seem missing, rebuild the index to rescan your Drive.
8. **Logout on Shared Devices**: Always logout when using public computers.

## **Example Workflows**

### **Verse-by-Verse Study**

1. Select John 3:1
2. Write observations about Nicodemus
3. Click Save
4. Select John 3:2
5. Continue verse by verse through the chapter

### **Chapter Summary**

1. Read through John 3
2. Select John chapter 3, verse 0
3. Write chapter overview:
   ```markdown
   # John 3 - New Birth
   ## Theme: Regeneration
   - Nicodemus encounter (vv. 1-21)
   - John the Baptist's testimony (vv. 22-36)
   ```
4. Save the chapter note

### **Topical Study Across Verses**

1. Study "Love" theme
2. Create notes on:
   - John 3:16 (God's love)
   - Romans 5:8 (Love demonstrated)
   - 1 John 4:8 (God is love)
3. Cross-reference in each note
4. Download all as backup

### **Sermon Preparation**

1. Select sermon passage
2. Create detailed notes:
   ```markdown
   # Sermon: The Good Shepherd
   ## Text: John 10:11-18

   ### Outline
   1. The Good Shepherd lays down his life (v. 11)
   2. The hired hand flees (vv. 12-13)
   3. Jesus knows his sheep (vv. 14-15)

   ### Illustrations
   - Story about shepherd protecting flock

   ### Application
   - Trust Jesus as protector
   ```
3. Save and access from any device

## **Data Management**

### **Rebuild Index**

The index tracks all your notes. Rebuild it if:
- Notes seem missing after import
- The count seems incorrect
- You've manually added files to Drive

**How to Rebuild**:
1. Click menu (⋮)
2. Select "Rebuild Index"
3. Wait for completion (may take time for many notes)
4. Check the success notification

### **Backup Strategy**

**Recommended backup plan**:
1. Google Drive automatically backs up all notes
2. Periodically click "Download All" for local backup
3. Store backup `.zip` file safely
4. Download Index file as additional safety

### **Import After Backup**

To restore from backup:
1. Click menu (⋮)
2. Select "Import"
3. Choose your `.zip` file
4. Wait for upload and processing
5. Rebuild index if needed

## **Privacy and Security**

### **Where Notes are Stored**

- **Google Drive**: App Data folder (hidden from regular Drive view)
- **Not Visible**: Won't appear in your main Google Drive file list
- **Secure**: Protected by your Google account security
- **Private**: Only accessible through BibleMate AI or with special Drive API access

### **What BibleMate AI Can Access**

- **Can**: Read and write files in App Data folder only
- **Cannot**: Access your other Google Drive files
- **Cannot**: Share your notes with others
- **Cannot**: See your notes on BibleMate servers

### **Data Policy**

BibleMate AI:
- Does NOT collect your notes
- Does NOT store your notes on its servers
- Does NOT share your notes with third parties
- ONLY facilitates sync to YOUR Google Drive

## **Troubleshooting**

**Notes not saving:**
- Check internet connection
- Verify you're logged in
- Try logout and login again
- Check Google Drive permissions

**Notes missing after login:**
- Click "Rebuild Index"
- Check if you're logged into the correct Google account
- Verify notes weren't accidentally deleted

**Import failing:**
- Ensure file is valid `.json` or `.zip`
- Check file isn't corrupted
- Try smaller batches for large imports
- Verify internet connection is stable

**Can't see notes in Google Drive:**
- Notes are in App Data folder (hidden by default)
- This is normal and expected
- Use "Download All" to get visible backup

## **Comparison: Notes vs. Notepad**

| Cloud Notes | Notepad |
| :---- | :---- |
| Verse-specific organization | Single notepad |
| Google Drive sync | Local storage only |
| Access across all devices | One device only |
| Requires login | No login needed |
| Automatic backup | Manual download for backup |
| Best for: organized Bible study | Best for: quick temporary notes |
