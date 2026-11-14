# **Books Guide**

The Books tool is a reader for reference books (`.book` files) inside BibleMate AI Web, shown in the tool pane next to the Bible.

## **Opening the Tool**

- Desktop: open the tools menu and choose **Books**.
- Mobile / narrow screens: open the left drawer and choose **Books**.

The tool is not tied to the current Bible chapter, so changing the Bible passage does not change the book you are reading.

## **Reading a Book**

1. Pick a book from the **book** menu.
2. Pick a chapter from the **chapter** menu, or use the previous / next buttons.
3. The chapter content appears in the reader below. The view scrolls back to the top when you change chapters.

Dark mode and the font size preference are applied to book content. Books that have no chapter list hide the chapter menu and navigation buttons.

### **Interactive Links**

Links inside book content work like those elsewhere in the app. Bible references open in the Bible area, and links to other resources, such as lexicons, dictionaries, promises and parallels, open in the app. Website links open in a new browser tab. Scripts and unsafe inline handlers in book content are removed.

## **Adding Your Own Books**

Books are discovered by scanning folders each time the tool is opened. You can add or remove books **without restarting the server**.

| Folder | Visible to |
| :---- | :---- |
| `~/biblemate/data/books` | All users |
| `~/biblemate/data_custom/books` | Only users with a valid [custom token](../custom_token.md) |

- Only files ending in `.book` are listed. Hidden files (starting with `.`) are ignored.
- The book name shown in the menu is the file name without `.book`.
- If a custom book has the same name as a standard book, the custom one replaces it for users with access.
- The folders are created automatically if they do not exist.
- Each file is a SQLite database with a `Reference` table. `Chapter` holds the chapter title and `Content` holds the HTML of each chapter, in row order. This is the format used by [UniqueBible](https://github.com/eliranwong/UniqueBible) reference books.

If no books are found, the tool shows "No books found."

## **API**

Book names are also returned in the `referenceBookList` entry of the API resource listing.

## **Interface Languages**

The tool is translated into Traditional and Simplified Chinese ("參考書籍" / "参考书籍").
