# **Advanced Bible Search Guide**

This guide explains the powerful search modes and settings available in the application.

## **1. Search Modes**

The app supports three distinct modes for searching content, plus a dedicated mode for finding verse references.

### **A. Search Verse References (Navigation)**

To quickly navigate to a specific passage, simply enter the Bible reference.

**Example:**

John 3:16; Gen 1:1-5; Ps 23:1-6

### **B. Literal Search (Plain Text)**

This is the default mode for finding exact matches of a word or phrase. The search engine looks for the specific sequence of characters you enter.

**Example:**

In the beginning  
The Lord is my shepherd

### **C. Regular Expression (Regex) Search**

**Regular Expressions (Regex)** are sequences of characters that define a search pattern. This advanced mode allows you to find complex patterns, word variations, or combinations of words within a single verse.

*For detailed guidance on Regex syntax, we recommend external resources like [regexone.com](https://regexone.com) or [regular-expressions.info](https://regular-expressions.info).*

Use this advanced mode to find complex patterns, word variations, or combinations of words within a single verse.

| Pattern | Description | Example |
| :---- | :---- | :---- |
| **OR Search** | Finds verses containing any of the listed words. | `love|hope|faith` |
| **AND Search** | Finds verses containing all of the specified words, regardless of order. | `^(?=.\blove\b)(?=.\bhope\b)(?=.\bfaith\b).` |
| **Proximity Search** | Finds words appearing in a specific order, potentially with words in between. | Naomi.\*?Ruth |

### **D. Semantic Search (Meaning)**

Use this mode to search for the *similar words* or *meaning* or *concept* behind a phrase, rather than the exact words. This is useful for finding verses that convey a similar idea.

**Example:**

* David fled
* wisdom
* new creation

**Note on Similarity:** The maximum number of similar verses displayed is controlled by the **Similar Verses** number setting, which can be adjusted in your application's preferences.

## **2. Search Scope and Settings**

These options allow you to refine where and how your search is executed.

### **Search Scope**

| Setting | Description | Default Behavior |
| :---- | :---- | :---- |
| **Books Filter** | Select specific books from the dropdown list to limit the search to only those books (e.g., only the Gospels). | All books are included. |
| **Multiple Bibles** | Select one or more Bibles from the Bible dropdown list to perform searches across multiple translations simultaneously. | If no Bible is explicitly selected, the search runs only against the Bible currently open in the active area tab. |

### **Case-Sensitivity Toggle**

This feature allows you to control whether the search distinguishes between uppercase and lowercase letters.

* **Applies to:** Literal Search and Regular Expression (Regex) Search modes only.  
* **Location:** Use the dedicated checkbox to toggle support for case-sensitive matches.

## **3. Post-Search Actions**

### **Filter Search Results**

After a search is completed, you can refine the resulting list by typing additional words into the input field. This acts as a real-time filter on the already found verses.

### **Open a Full Chapter**

To view the complete context of a verse, click the verse reference button (e.g., Jn 3:16) in the search result list. This will open the full chapter either in the main Bible area or in the Tool area, based on your selection.