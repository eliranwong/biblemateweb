#!/usr/bin/env python3
from nicegui import ui
import random

area1_tabs = None
area2_tabs = None
area1_tab_panels = {}  # Dictionary to store tab panels by name
area2_tab_panels = {}

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

@ui.page('/')
def main_page():
    ui.label('BibleMate AI - Synced Scroll Demo').classes('text-2xl font-bold p-4 text-center')

    # Generate the two different chapter HTML blobs
    chapter_html_1 = """<verse><u><b>Introduction and Thanksgiving</b></u><br><br><vid id="v63.1.1" onclick="luV(1)">1</vid> From the elder, to an elect lady and her children, whom I love in truth (and not I alone, but also all those who know the truth),</verse> <verse><vid id="v63.1.2" onclick="luV(2)">2</vid> because of the truth that resides in us and will be with us forever.</verse> <verse><vid id="v63.1.3" onclick="luV(3)">3</vid> Grace, mercy, and peace will be with us from God the Father and from Jesus Christ the Son of the Father, in truth and love.</verse> <verse><br><br><vid id="v63.1.4" onclick="luV(4)">4</vid> I rejoiced greatly because I have found some of your children living according to the truth, just as the Father commanded us.</verse> <verse><br><br><u><b>Warning Against False Teachers</b></u><br><br><vid id="v63.1.5" onclick="luV(5)">5</vid> But now I ask you, lady (not as if I were writing a new commandment to you, but the one we have had from the beginning), that we love one another.</verse> <verse><vid id="v63.1.6" onclick="luV(6)">6</vid> (Now this is love: that we walk according to his commandments.) This is the commandment, just as you have heard from the beginning; thus you should walk in it.</verse> <verse><vid id="v63.1.7" onclick="luV(7)">7</vid> For many deceivers have gone out into the world, people who do not confess Jesus as Christ coming in the flesh. This person is the deceiver and the antichrist!</verse> <verse><vid id="v63.1.8" onclick="luV(8)">8</vid> Watch out, so that you do not lose the things we have worked for, but receive a full reward.</verse> <verse><br><br><vid id="v63.1.9" onclick="luV(9)">9</vid> Everyone who goes on ahead and does not remain in the teaching of Christ does not have God. The one who remains in this teaching has both the Father and the Son.</verse> <verse><vid id="v63.1.10" onclick="luV(10)">10</vid> If anyone comes to you and does not bring this teaching, do not receive him into your house and do not give him any greeting,</verse> <verse><vid id="v63.1.11" onclick="luV(11)">11</vid> because the person who gives him a greeting shares in his evil deeds.</verse> <verse><br><br><u><b>Conclusion</b></u><br><br><vid id="v63.1.12" onclick="luV(12)">12</vid> Though I have many other things to write to you, I do not want to do so with paper and ink, but I hope to come visit you and speak face to face, so that our joy may be complete.</verse> <verse><br><br><vid id="v63.1.13" onclick="luV(13)">13</vid> The children of your elect sister greet you.</verse>"""
    chapter_html_2 = """<verse><u><b>約翰二書</b></u><br><u><b>問候</b></u><br><br><vid id="v63.1.1" onclick="luV(1)">1</vid> <zh>作長老的寫信給蒙揀選的太太〔註：或譯：教會；下同〕和她的兒女，就是我誠心所愛的；不但我愛，也是一切知道真理之人所愛的。</zh></verse> <verse><vid id="v63.1.2" onclick="luV(2)">2</vid> <zh>愛你們是為真理的緣故，這真理存在我們裏面，也必永遠與我們同在。</zh></verse> <verse><vid id="v63.1.3" onclick="luV(3)">3</vid> <zh>恩惠、憐憫、平安從父上帝和他兒子耶穌基督在真理和愛心上必常與我們同在！</zh></verse> <verse><br><br><u><b>真理和愛</b></u><br><br><vid id="v63.1.4" onclick="luV(4)">4</vid> <zh>我見你的兒女，有照我們從父所受之命令遵行真理的，就甚歡喜。</zh></verse> <verse><vid id="v63.1.5" onclick="luV(5)">5</vid> <zh>太太啊，我現在勸你，我們大家要彼此相愛。這並不是我寫一條新命令給你，乃是我們從起初所受的命令。</zh></verse> <verse><vid id="v63.1.6" onclick="luV(6)">6</vid> <zh>我們若照他的命令行，這就是愛。你們從起初所聽見當行的，就是這命令。</zh></verse> <verse><vid id="v63.1.7" onclick="luV(7)">7</vid> <zh>因為世上有許多迷惑人的出來，他們不認耶穌基督是成了肉身來的；這就是那迷惑人、敵基督的。</zh></verse> <verse><vid id="v63.1.8" onclick="luV(8)">8</vid> <zh>你們要小心，不要失去你們〔註：有古卷：我們〕所做的工，乃要得着滿足的賞賜。</zh></verse> <verse><vid id="v63.1.9" onclick="luV(9)">9</vid> <zh>凡越過基督的教訓不常守着的，就沒有上帝；常守這教訓的，就有父又有子。</zh></verse> <verse><vid id="v63.1.10" onclick="luV(10)">10</vid> <zh>若有人到你們那裏，不是傳這教訓，不要接他到家裏，也不要問他的安；</zh></verse> <verse><vid id="v63.1.11" onclick="luV(11)">11</vid> <zh>因為問他安的，就在他的惡行上有分。</zh></verse> <verse><br><br><u><b>問安</b></u><br><br><vid id="v63.1.12" onclick="luV(12)">12</vid> <zh>我還有許多事要寫給你們，卻不願意用紙墨〔寫出來〕，但盼望到你們那裏，與你們當面談論，使你們的喜樂滿足。</zh></verse> <verse><vid id="v63.1.13" onclick="luV(13)">13</vid> <zh>你那蒙揀選之姊妹的兒女都問你安。</zh></verse>"""

    # Create the splitter
    with ui.splitter(value=50).classes('w-full h-[80vh]') as splitter:
        
        # Left pane (e.g., KJV)
        with splitter.before:
            area1_wrapper = ui.column().classes('w-full h-full')
            with area1_wrapper:
                area1_tabs = ui.tabs().classes('w-full')
                with area1_tabs:
                    ui.tab('tab1_1', label='Bible 1')
                    ui.tab('tab1_2', label='Bible 2')
                
                area1_tab_panels_container = ui.tab_panels(area1_tabs, value='tab1_1').classes('w-full h-full')
                
                with area1_tab_panels_container:
                    with ui.tab_panel('tab1_1'):
                        area1_tab_panels['tab1_1'] = ui.scroll_area().classes('w-full h-full p-4 scroll-area-1')
                        with area1_tab_panels['tab1_1']:
                            ui.html(chapter_html_1, sanitize=False).classes('w-full chapter-1')
                    
                    with ui.tab_panel('tab1_2'):
                        area1_tab_panels['tab1_2'] = ui.scroll_area().classes('w-full h-full p-4 scroll-area-1')
                        with area1_tab_panels['tab1_2']:
                            ui.html(chapter_html_2, sanitize=False).classes('w-full chapter-1')

        # Right pane (e.g., NIV)
        with splitter.after:
            area2_wrapper = ui.column().classes('w-full h-full')
            with area2_wrapper:
                area2_tabs = ui.tabs().classes('w-full')
                with area2_tabs:
                    ui.tab('tab2_1', label='Tool 1')
                    ui.tab('tab2_2', label='Tool 2')
                
                area2_tab_panels_container = ui.tab_panels(area2_tabs, value='tab2_1').classes('w-full h-full')
                
                with area2_tab_panels_container:
                    with ui.tab_panel('tab2_1'):
                        area2_tab_panels['tab2_1'] = ui.scroll_area().classes('w-full h-full p-4 scroll-area-2')
                        with area2_tab_panels['tab2_1']:
                            ui.html(chapter_html_2, sanitize=False).classes('w-full chapter-2')
                    
                    with ui.tab_panel('tab2_2'):
                        area2_tab_panels['tab2_2'] = ui.scroll_area().classes('w-full h-full p-4 scroll-area-2')
                        with area2_tab_panels['tab2_2']:
                            ui.html(chapter_html_1, sanitize=False).classes('w-full chapter-2')

    # After the page is built and ready, run our JavaScript
    ui.run_javascript(f"""
        {JAVASCRIPT_SYNC_LOGIC}
        
        // We wait 500ms for all elements to be rendered and positioned
        // before we set up the listeners.
        setTimeout(() => {{
            // Note the new verse selectors!
            setupSyncScroll('.scroll-area-1', '.scroll-area-2', '.chapter-1 vid', '.chapter-2 vid');
        }}, 500);
    """)

# Run the app
ui.run(port=9999)