#!/usr/bin/env python3
"""
NiceGUI app with custom context menu for selected text in HTML content.
Right-click on selected text to show a context menu with various actions.
"""

from nicegui import ui, app
import json

# Sample HTML content
HTML_CONTENT = """
<div id="content-container">
    <h2>Sample Text Content</h2>
    <p>This is a sample paragraph with some text that you can select. 
    Try selecting any portion of this text and right-clicking to see the context menu.</p>
    
    <p>You can perform various actions on the selected text such as:
    copying it, searching for it, translating it, or processing it in any custom way.</p>
    
    <blockquote>
        "The only way to do great work is to love what you do." - Steve Jobs
    </blockquote>
    
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
</div>
"""

# CSS for the context menu
CONTEXT_MENU_CSS = """
<style>
/* Context menu styles */
.context-menu {
    position: fixed;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    padding: 8px 0;
    min-width: 180px;
    display: none;
    z-index: 10000;
}

.context-menu.show {
    display: block;
}

.context-menu-item {
    padding: 8px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: background-color 0.2s;
}

.context-menu-item:hover {
    background-color: #f0f0f0;
}

.context-menu-item i {
    width: 20px;
    text-align: center;
    color: #666;
}

.context-menu-separator {
    height: 1px;
    background-color: #e0e0e0;
    margin: 4px 0;
}

/* Disable default browser context menu on our content */
#content-container {
    user-select: text;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
    margin: 20px 0;
}

/* Selection highlight */
::selection {
    background-color: #b3d4fc;
    color: #000;
}

/* Toast notification styles */
.toast-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #333;
    color: white;
    padding: 12px 20px;
    border-radius: 4px;
    animation: slideIn 0.3s ease-out;
    z-index: 10001;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
</style>
"""

# JavaScript for context menu functionality
CONTEXT_MENU_JS = """
<script>
let selectedText = '';
let contextMenu = null;

// Initialize context menu
function initContextMenu() {
    // Create context menu element
    const menuHTML = `
        <div id="customContextMenu" class="context-menu">
            <div class="context-menu-item" data-action="copy">
                <i class="fas fa-copy"></i>
                <span>Copy</span>
            </div>
            <div class="context-menu-item" data-action="search">
                <i class="fas fa-search"></i>
                <span>Search Google</span>
            </div>
            <div class="context-menu-item" data-action="uppercase">
                <i class="fas fa-font"></i>
                <span>Convert to Uppercase</span>
            </div>
            <div class="context-menu-item" data-action="lowercase">
                <i class="fas fa-text-height"></i>
                <span>Convert to Lowercase</span>
            </div>
            <div class="context-menu-separator"></div>
            <div class="context-menu-item" data-action="count">
                <i class="fas fa-calculator"></i>
                <span>Word Count</span>
            </div>
            <div class="context-menu-item" data-action="analyze">
                <i class="fas fa-chart-bar"></i>
                <span>Analyze Text</span>
            </div>
            <div class="context-menu-separator"></div>
            <div class="context-menu-item" data-action="highlight">
                <i class="fas fa-highlighter"></i>
                <span>Highlight</span>
            </div>
            <div class="context-menu-item" data-action="note">
                <i class="fas fa-sticky-note"></i>
                <span>Add Note</span>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', menuHTML);
    contextMenu = document.getElementById('customContextMenu');
    
    // Add click handlers for menu items
    contextMenu.querySelectorAll('.context-menu-item').forEach(item => {
        item.addEventListener('click', function() {
            const action = this.dataset.action;
            handleContextMenuAction(action, selectedText);
            hideContextMenu();
        });
    });
}

// Handle context menu actions
async function handleContextMenuAction(action, text) {
    switch(action) {
        case 'copy':
            await navigator.clipboard.writeText(text);
            showToast('Text copied to clipboard!');
            break;
            
        case 'search':
            window.open(`https://www.google.com/search?q=${encodeURIComponent(text)}`, '_blank');
            break;
            
        case 'uppercase':
            // Send to Python backend
            pywebview.api.process_text(text, 'uppercase');
            break;
            
        case 'lowercase':
            // Send to Python backend
            pywebview.api.process_text(text, 'lowercase');
            break;
            
        case 'count':
            const wordCount = text.trim().split(/\\s+/).length;
            const charCount = text.length;
            showToast(`Words: ${wordCount}, Characters: ${charCount}`);
            break;
            
        case 'analyze':
            // Send to Python backend for analysis
            pywebview.api.process_text(text, 'analyze');
            break;
            
        case 'highlight':
            highlightSelection();
            break;
            
        case 'note':
            const note = prompt('Add a note for this selection:');
            if (note) {
                pywebview.api.process_text(text, 'note', note);
            }
            break;
    }
}

// Show context menu
function showContextMenu(x, y) {
    contextMenu.style.left = x + 'px';
    contextMenu.style.top = y + 'px';
    contextMenu.classList.add('show');
}

// Hide context menu
function hideContextMenu() {
    if (contextMenu) {
        contextMenu.classList.remove('show');
    }
}

// Show toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Highlight selected text
function highlightSelection() {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const span = document.createElement('span');
        span.style.backgroundColor = 'yellow';
        span.style.padding = '2px';
        try {
            range.surroundContents(span);
        } catch (e) {
            // Fallback for complex selections
            const contents = range.extractContents();
            span.appendChild(contents);
            range.insertNode(span);
        }
        selection.removeAllRanges();
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initContextMenu();
    
    // Prevent default context menu on our content area
    const contentContainer = document.getElementById('content-container');
    if (contentContainer) {
        contentContainer.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            
            // Get selected text
            const selection = window.getSelection();
            selectedText = selection.toString().trim();
            
            // Only show menu if text is selected
            if (selectedText) {
                showContextMenu(e.pageX, e.pageY);
            }
        });
    }
    
    // Hide context menu when clicking elsewhere
    document.addEventListener('click', function(e) {
        if (!contextMenu.contains(e.target)) {
            hideContextMenu();
        }
    });
    
    // Hide context menu on scroll
    window.addEventListener('scroll', hideContextMenu);
});

// Python-JavaScript bridge (for NiceGUI)
window.pywebview = {
    api: {
        process_text: async function(text, action, extra) {
            // Send to Python backend
            const response = await fetch('/api/process-text', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    text: text,
                    action: action,
                    extra: extra
                })
            });
            const result = await response.json();
            
            if (result.message) {
                showToast(result.message);
            }
            
            if (result.processed_text) {
                // You can do something with the processed text
                console.log('Processed:', result.processed_text);
            }
        }
    }
};
</script>
"""

# Store for notes and processed text
text_store = {
    'notes': [],
    'processed': []
}

@ui.page('/')
def main_page():
    """Main page with HTML content and context menu."""
    
    # Add Font Awesome for icons
    ui.add_head_html('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">')
    
    # Add custom CSS
    ui.add_head_html(CONTEXT_MENU_CSS)
    
    # Page title
    ui.label('NiceGUI Context Menu Demo').classes('text-3xl font-bold mb-4')
    
    with ui.row().classes('w-full gap-4'):
        # Main content area
        with ui.column().classes('flex-grow'):
            ui.label('Right-click on selected text to see the context menu:').classes('text-lg mb-2')
            
            # HTML content with context menu
            ui.html(HTML_CONTENT, sanitize=False)
            
            # Add JavaScript for context menu
            ui.add_body_html(CONTEXT_MENU_JS)
        
        # Sidebar for displaying results
        with ui.column().classes('w-80 p-4 bg-gray-100 rounded'):
            ui.label('Processing Results').classes('text-xl font-bold mb-4')
            
            # Results container
            results_container = ui.column().classes('gap-2')
            
            @ui.refreshable
            def show_results():
                results_container.clear()
                with results_container:
                    if text_store['notes']:
                        ui.label('Notes:').classes('font-bold mt-2')
                        for note in text_store['notes'][-5:]:  # Show last 5 notes
                            with ui.card().classes('p-2 w-full'):
                                ui.label(f"Text: {note['text'][:50]}...")
                                ui.label(f"Note: {note['note']}").classes('text-sm text-gray-600')
                    
                    if text_store['processed']:
                        ui.label('Processed Text:').classes('font-bold mt-2')
                        for item in text_store['processed'][-5:]:  # Show last 5 items
                            with ui.card().classes('p-2 w-full'):
                                ui.label(f"Action: {item['action']}")
                                ui.label(f"Result: {item['result'][:100]}...").classes('text-sm')
            
            show_results()
            
            # Clear button
            ui.button('Clear Results', on_click=lambda: (
                text_store.update({'notes': [], 'processed': []}),
                show_results.refresh()
            )).classes('mt-4')
    
    # Instructions
    with ui.expansion('Instructions', value=True).classes('mt-8'):
        ui.markdown("""
        ### How to use:
        1. **Select any text** in the content area above
        2. **Right-click** on the selected text
        3. Choose an action from the context menu:
           - **Copy**: Copy text to clipboard
           - **Search Google**: Search for selected text
           - **Convert Case**: Change to uppercase/lowercase
           - **Word Count**: Count words and characters
           - **Analyze Text**: Get text analysis
           - **Highlight**: Highlight selected text in yellow
           - **Add Note**: Add a note to selected text
        
        Results will appear in the sidebar on the right.
        """)

# API endpoint for processing text
@app.post('/api/process-text')
async def process_text(request: dict):
    """Process text based on the selected action."""
    text = request.get('text', '')
    action = request.get('action', '')
    extra = request.get('extra', '')
    
    result = {'success': True}
    
    if action == 'uppercase':
        processed = text.upper()
        text_store['processed'].append({'action': 'Uppercase', 'result': processed})
        result['processed_text'] = processed
        result['message'] = 'Converted to uppercase'
        
    elif action == 'lowercase':
        processed = text.lower()
        text_store['processed'].append({'action': 'Lowercase', 'result': processed})
        result['processed_text'] = processed
        result['message'] = 'Converted to lowercase'
        
    elif action == 'analyze':
        word_count = len(text.split())
        char_count = len(text)
        sentences = text.count('.') + text.count('!') + text.count('?')
        analysis = f"Words: {word_count}, Chars: {char_count}, Sentences: {sentences}"
        text_store['processed'].append({'action': 'Analysis', 'result': analysis})
        result['message'] = analysis
        
    elif action == 'note':
        text_store['notes'].append({'text': text, 'note': extra})
        result['message'] = 'Note added successfully'
    
    return result

ui.run(
    title='NiceGUI Context Menu Demo',
    port=9999,
    reload=False
)