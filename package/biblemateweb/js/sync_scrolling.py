# This is the core JavaScript logic to handle the synchronization
# It will be injected into the page later
SYNC_JS = """
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

    // Get all verse elements (the <vid> tags) and map them by their ID
    const verses1 = Array.from(area1.querySelectorAll(verse1Selector));
    const verses2 = Array.from(area2.querySelectorAll(verse2Selector));
    
    // We change from 'dataset.vid' to 'id' to match your HTML
    const verses1Map = new Map(verses1.map(v => [v.id, v]));
    const verses2Map = new Map(verses2.map(v => [v.id, v]));

    let timer1, timer2;
    let lastScroller = null; // Replaces 'scrollingFromSync'

    // Finds the topmost visible verse in a scrolling container
    function getTopVerse(scrollRoot, verses) {
        const scrollTop = scrollRoot.scrollTop;
        // We add a 5px buffer to be less sensitive
        const scrollThreshold = scrollTop + 5; 
        
        // Find the first verse whose top offset is at or just below the scroll top
        let topVerse = verses[0];
        for (let i = 0; i < verses.length; i++) {
            // We use the <vid> tag's parentElement (<verse>) for offsetTop
            // to get the top of the whole verse block.
            const verseBlock = verses[i].parentElement;
            if (verseBlock.offsetTop >= scrollThreshold) {
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
        if (lastScroller === 'area2') return; // Ignore scrolls caused by area2
        clearTimeout(timer1);
        timer1 = setTimeout(() => { // Debounce to avoid lag
            lastScroller = 'area1'; // Mark area1 as the one scrolling
            const topVerse = getTopVerse(scrollRoot1, verses1);
            if (topVerse) {
                const vid = topVerse.id; // Use .id
                const targetElement = verses2Map.get(vid);
                if (targetElement) {
                    // Scroll to the top of the target's parent <verse> tag
                    const targetBlock = targetElement.parentElement;
                    scrollRoot2.scrollTop = targetBlock.offsetTop;
                    // Release the lock after a short delay
                    setTimeout(() => { lastScroller = null; }, 150); 
                } else {
                    lastScroller = null; // Release lock if no target
                }
            } else {
                 lastScroller = null; // Release lock if no verse
            }
        }, 50); // 50ms debounce
    });

    // Scroll handler for Area 2
    scrollRoot2.addEventListener('scroll', () => {
        if (lastScroller === 'area1') return; // Ignore scrolls caused by area1
        clearTimeout(timer2);
        timer2 = setTimeout(() => { // Debounce
            lastScroller = 'area2'; // Mark area2 as the one scrolling
            const topVerse = getTopVerse(scrollRoot2, verses2);
            if (topVerse) {
                const vid = topVerse.id; // Use .id
                const targetElement = verses1Map.get(vid);
                if (targetElement) {
                    // Scroll to the top of the target's parent <verse> tag
                    const targetBlock = targetElement.parentElement;
                    scrollRoot1.scrollTop = targetBlock.offsetTop;
                    // Release the lock after a short delay
                    setTimeout(() => { lastScroller = null; }, 150);
                } else {
                    lastScroller = null; // Release lock if no target
                }
            } else {
                 lastScroller = null; // Release lock if no verse
            }
        }, 50);
    });
}
"""

def get_sync_fx(tab1, tab2):
    return f"""        
        // We wait 500ms for all elements to be rendered and positioned
        // before we set up the listeners.
        setTimeout(() => {{
            // Note the new verse selectors!
            setupSyncScroll('.{tab1}', '.{tab2}', '.{tab1+"_chapter"} vid', '.{tab2+"_chapter"} vid');
        }}, 500);
    """