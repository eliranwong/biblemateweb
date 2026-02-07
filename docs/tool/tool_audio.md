# **Bible Audio Player Guide**

This tool provides verse-by-verse audio playback of the Bible, allowing you to listen to Scripture with synchronized text display.

## **What is the Audio Player?**

The Audio Player lets you listen to Bible chapters with professional narration while following along with the text. Each verse is individually controllable, making it perfect for meditation, memorization, or accessibility needs.

## **How to Use the Audio Player**

### **Basic Playback**

1. **Select a Passage**: Use the Bible selector at the top to choose your desired book, chapter, and starting verse.
2. **Click "Go"**: Load the audio for that chapter.
3. **Play a Verse**: Click the audio icon (🔊) next to any verse to start playback.
4. **Auto-Continue**: The player automatically advances to the next verse when the current one finishes.

### **Navigation**

- **Book Dropdown**: Select from all 66 books of the Bible.
- **Chapter Dropdown**: Choose any chapter within the selected book.
- **Verse Dropdown**: Pick a specific starting verse.
- **Go Button**: Apply your selection and load the audio.

## **Player Controls**

| Control | Function |
| :---- | :---- |
| **Volume Icon** | Click any verse's icon to start/stop playback for that verse |
| **Audio Player** | Standard HTML5 audio controls (play, pause, seek, volume) |
| **Loop Toggle** | Enable to automatically restart the chapter after completion |

## **Features**

### **Verse-by-Verse Control**

- Click any verse to jump directly to that point in the chapter.
- The currently playing verse is highlighted with a speaker icon (🔊).
- Inactive verses show a muted icon (🔇).

### **Auto-Advance**

The player automatically moves to the next verse when the current verse finishes, creating a seamless listening experience through the entire chapter.

### **Loop Mode**

Enable the "Loop" switch to:
- Automatically restart playback from verse 1 when the chapter ends.
- Perfect for memorization or meditation on a specific chapter.

### **Next Chapter Auto-Load**

When loop mode is disabled and the chapter ends, the player can automatically load the next chapter (feature depends on settings).

### **Multi-Version Support**

The audio player supports multiple Bible versions and original language texts:
- **English Translations**: NET, KJV, and other available audio Bibles.
- **Original Languages**: Hebrew (BHS5) for Old Testament, Greek (OGNT) for New Testament.
- **Custom Audio**: If you've added custom audio files, they'll appear in the version selector.

## **Original Language Features**

When playing Hebrew or Greek audio:
- **Hebrew Text**: Displayed right-to-left with proper formatting.
- **Tooltips**: Hover over Hebrew or Greek words to see lexical information.
- **Transliteration**: See how words are pronounced.

## **Tips for Effective Use**

1. **Memorization**: Use loop mode and follow along with the text to memorize passages.
2. **Meditation**: Play a single verse repeatedly to meditate deeply on its meaning.
3. **Accessibility**: Enable audio for visually impaired users or those who prefer auditory learning.
4. **Multitasking**: Listen while doing other activities—the auto-advance keeps the reading flowing.
5. **Language Learning**: Use original language audio to improve your Hebrew or Greek pronunciation.
6. **Start Mid-Chapter**: If you only need verses 15-20, set the starting verse to 15 before loading.

## **Keyboard Shortcuts**

The standard HTML5 audio player supports common keyboard controls:
- **Spacebar**: Play/Pause (when audio player is focused)
- **Arrow Keys**: Seek forward/backward
- **Volume Keys**: Adjust volume

## **Technical Notes**

- Audio files must be available in your data directory (`~/biblemate/data/audio/bibles/`).
- Supported audio formats: MP3.
- Each verse has its own audio file for precise control.
- Internet connection is not required—all audio is played locally.
