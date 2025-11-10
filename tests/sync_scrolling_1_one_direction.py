#!/usr/bin/env python3
from nicegui import ui
from faker import Faker  # Used for generating dummy text
import random

# Initialize a text generator for dummy content
fake = Faker()

# This is the core JavaScript logic to handle the synchronization
# It will be injected into the page later
JAVASCRIPT_SYNC_LOGIC = """
function setupSyncScroll(area1Selector, area2Selector, verse1Selector, verse2Selector) {
    const area1 = document.querySelector(area1Selector);
    const area2 = document.querySelector(area2Selector);

    // NiceGUI's ui.scroll_area is a Quasar q-scrollarea.
    // We need to find the actual scrollable DOM element,
    // which is the parent of the .q-scrollarea__content div.
    if (!area1 || !area2) {
        console.error('Scroll areas not found');
        return;
    }
    const scrollRoot1 = area1.querySelector('.q-scrollarea__content')?.parentElement;
    const scrollRoot2 = area2.querySelector('.q-scrollarea__content')?.parentElement;
    
    if (!scrollRoot1 || !scrollRoot2) {
        console.error('Scrollable content roots not found');
        return;
    }

    // Get all verse elements and map them by their 'data-vid' for quick lookup
    const verses1 = Array.from(area1.querySelectorAll(verse1Selector));
    const verses2 = Array.from(area2.querySelectorAll(verse2Selector));
    const verses1Map = new Map(verses1.map(v => [v.dataset.vid, v]));
    const verses2Map = new Map(verses2.map(v => [v.dataset.vid, v]));

    let timer1, timer2;
    let scrollingFromSync = false; // Flag to prevent infinite loops

    // Finds the topmost visible verse in a scrolling container
    function getTopVerse(scrollRoot, verses) {
        const scrollTop = scrollRoot.scrollTop;
        // We add a 5px buffer to be less sensitive
        const scrollThreshold = scrollTop + 5; 
        
        // Find the first verse whose top offset is at or just below the scroll top
        let topVerse = verses[0];
        for (let i = 0; i < verses.length; i++) {
            if (verses[i].offsetTop >= scrollThreshold) {
                // We've gone past it, so the previous one was the top one
                topVerse = verses[i-1] || verses[0];
                break;
            }
            topVerse = verses[i]; // Keep updating in case it's the last one
        }
        return topVerse;
    }

    // Scroll handler for Area 1
    scrollRoot1.addEventListener('scroll', () => {
        if (scrollingFromSync) return; // Don't sync if this scroll was triggered by the other pane
        clearTimeout(timer1);
        timer1 = setTimeout(() => { // Debounce to avoid lag
            const topVerse = getTopVerse(scrollRoot1, verses1);
            if (topVerse) {
                const vid = topVerse.dataset.vid;
                const targetElement = verses2Map.get(vid);
                if (targetElement) {
                    scrollingFromSync = true;
                    // Set the scroll position of the other pane
                    scrollRoot2.scrollTop = targetElement.offsetTop;
                    // Release the sync lock after a short delay
                    setTimeout(() => { scrollingFromSync = false; }, 200); 
                }
            }
        }, 50); // 50ms debounce
    });

    // Scroll handler for Area 2
    scrollRoot2.addEventListener('scroll', () => {
        if (scrollingFromSync) return; // Don't sync if this scroll was triggered by the other pane
        clearTimeout(timer2);
        timer2 = setTimeout(() => { // Debounce
            const topVerse = getTopVerse(scrollRoot2, verses2);
            if (topVerse) {
                const vid = topVerse.dataset.vid;
                const targetElement = verses1Map.get(vid);
                if (targetElement) {
                    scrollingFromSync = true;
                    // Set the scroll position of the other pane
                    scrollRoot1.scrollTop = targetElement.offsetTop;
                    // Release the sync lock after a short delay
                    setTimeout(() => { scrollingFromSync = false; }, 200);
                }
            }
        }, 50);
    });
}
"""



@ui.page('/')
def main_page():

    # Add some basic styling for the verse elements
    # We use ui.add_head_html to inject a <style> tag
    ui.add_head_html("""
    <style>
        /* Style for the <vid> tag you mentioned */
        vid {
            display: block; /* Make each verse its own block */
            padding: 8px;
            border-bottom: 1px dashed #ddd;
        }
        /* Style for the verse number (e.g., v63.1.7) */
        vid > b {
            color: #b91c1c; /* red-700 */
            margin-right: 10px;
            font-family: monospace;
        }
    </style>
    """)

    ui.label('BibleMate AI - Synced Scroll Demo').classes('text-2xl font-bold p-4 text-center')

    # Create the splitter
    with ui.splitter(value=50).classes('w-full h-[80vh]') as splitter:
        
        # Left pane (e.g., KJV)
        with splitter.before:
            with ui.scroll_area().classes('w-full h-full scroll-area-1'):
                for i in range(1, 51):
                    vid = f"v63.1.{i}"
                    # Generate short text
                    text = fake.sentence(nb_words=random.randint(15, 25))
                    # Use ui.html to render your <vid> tag
                    # We add 'verse-item-1' class and 'data-vid' prop for JS
                    ui.html(f'<vid><b>{vid}</b> {text}</vid>', sanitize=False) \
                        .classes('verse-item-1') \
                        .props(f'data-vid="{vid}"')

        # Right pane (e.g., NIV)
        with splitter.after:
            with ui.scroll_area().classes('w-full h-full scroll-area-2'):
                for i in range(1, 51):
                    vid = f"v63.1.{i}"
                    # Generate longer text to ensure heights are different
                    text = fake.sentence(nb_words=random.randint(25, 45))
                    # We add 'verse-item-2' class and 'data-vid' prop for JS
                    ui.html(f'<vid><b>{vid}</b> {text}</vid>', sanitize=False) \
                        .classes('verse-item-2') \
                        .props(f'data-vid="{vid}"')

    # After the page is built and ready, run our JavaScript
    # We remove the ui.on_page_ready wrapper, as ui.run_javascript
    # called here is already executed when the page is ready.
    ui.run_javascript(f"""
        {JAVASCRIPT_SYNC_LOGIC}
        
        // We wait 500ms for all elements to be rendered and positioned
        // before we set up the listeners.
        setTimeout(() => {{
            setupSyncScroll('.scroll-area-1', '.scroll-area-2', '.verse-item-1', '.verse-item-2');
        }}, 500);
    """)

# Run the app
ui.run(port=9999)