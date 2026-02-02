# **Bible Commentary Guide**

This tool provides access to comprehensive Bible commentaries that explain and interpret Scripture verse by verse.

## **What is the Commentary Tool?**

The Commentary tool gives you instant access to scholarly and devotional commentaries on any Bible passage. Commentaries provide historical context, theological insights, linguistic explanations, and practical applications for understanding Scripture more deeply.

## **How to Use the Commentary Tool**

### **Basic Usage**

1. **Select a Commentary**: Choose from the dropdown menu of available commentaries.
2. **Enter a Reference**: Type a Bible verse or passage reference (e.g., "John 3:16" or "Romans 8:1-17").
3. **Press Enter**: The commentary for that passage will load instantly.
4. **Browse**: Scroll through the commentary content and click any embedded references.

### **Input Options**

The input field supports:
- **Single Verses**: `John 3:16`
- **Verse Ranges**: `Romans 8:1-17`
- **Multiple References**: `John 3:16; Romans 8:1; Psalm 23:1-6`
- **Autocomplete**: Start typing a book name for suggestions

### **Navigation Controls**

| Control | Function |
| :---- | :---- |
| **Commentary Dropdown** | Select which commentary to view |
| **Input Field** | Enter Bible references (with autocomplete) |
| **History Icon** (⏱️) | Restore your last search by clicking or pressing Up Arrow |
| **Up Arrow Key** | Restore the previous reference you searched |

## **Available Commentaries**

The tool provides access to multiple commentary types:

### **AI-Generated Commentaries**

- **AIC** (AI Commentary - English)
- **AICTC** (AI Commentary - Traditional Chinese)
- **AICSC** (AI Commentary - Simplified Chinese)

These provide verse-by-verse AI-generated insights in markdown format, converted to HTML for easy reading.

### **Classical Commentaries**

- **CBSC** (Cambridge Bible for Schools and Colleges)
- Many other traditional commentaries available in your library

### **Commentary Features**

Different commentaries may include:
- Verse-by-verse exposition
- Historical and cultural background
- Greek and Hebrew word studies
- Cross-references to related passages
- Theological explanations
- Practical applications

## **Features**

### **Multi-Reference Support**

Enter multiple references separated by semicolons to view commentary on several passages at once:
```
Genesis 1:1; John 1:1; Revelation 21:1
```

### **Verse Range Handling**

The tool intelligently handles verse ranges:
- For AI commentaries: Loads commentary for each individual verse
- For classical commentaries: Extracts relevant portions from chapter commentaries

### **Clickable Cross-References**

Commentary content includes clickable links:
- **Bible References**: Click to open that passage in the Bible area
- **Lexicon Links**: Click to open word studies (if available)
- **Website Links**: External references open in new tabs

### **Dark Mode Support**

Commentary colors automatically adjust for dark mode:
- Text colors are optimized for readability
- Table backgrounds adapt to your theme
- Font colors change appropriately

### **Instant Search History**

- Press **Up Arrow** or click the **History Icon** to restore your last search
- Quickly return to previous passages without retyping
- Perfect for comparing different commentaries on the same passage

### **Commentary Switching**

Change commentaries on the fly:
1. Select a different commentary from the dropdown
2. The tool automatically reloads with the new commentary
3. Your current reference is preserved

## **Input Methods**

### **Direct URL Parameters**

Load specific commentary and passage via URL:
```
?tool=commentary&q=CBSC:::John+3:16
```
Format: `commentary_code:::reference`

### **Standard Input**

Simply type or paste references in the input field:
- Auto-focus for immediate typing
- Autocomplete for book names
- Clear button to reset input

## **Tips for Effective Use**

1. **Compare Commentaries**: Load the same passage in different commentaries to get multiple perspectives.
2. **Context Reading**: Use verse ranges (not just single verses) to understand the broader context.
3. **Cross-Reference Following**: Click embedded references to explore related passages.
4. **Historical Background**: Pay attention to cultural and historical notes for better understanding.
5. **Original Languages**: Look for Greek and Hebrew word explanations in commentaries.
6. **Quick Navigation**: Use the Up Arrow key to quickly restore your last search.
7. **Multiple Passages**: Study related verses together by entering multiple references.

## **Example Workflows**

### **Deep Word Study**

1. Enter: `Ephesians 2:8-9`
2. Read commentary explanation
3. Click any lexicon links for word studies
4. Switch to a different commentary for another perspective

### **Comparative Study**

1. Enter: `Matthew 5:3-12; Luke 6:20-23` (parallel passages)
2. Read commentary on both accounts
3. Note similarities and differences
4. Click cross-references for additional context

### **Topical Study**

1. Search for key verses on a topic: `Romans 3:23; Romans 6:23; John 3:16; Ephesians 2:8-9`
2. Read commentary on each verse
3. Build a comprehensive understanding of the topic

## **Keyboard Shortcuts**

- **Enter**: Submit your search
- **Up Arrow**: Restore last search
- **Escape**: Clear the input field (if using clear button)

## **Technical Notes**

- Commentaries are stored locally in `~/biblemate/data/commentaries/`
- AI commentaries are generated in markdown and converted to HTML
- Classical commentaries may be chapter-based or verse-based
- Commentary content supports HTML formatting including tables, lists, and styling
- All lexicon and reference links are interactive
