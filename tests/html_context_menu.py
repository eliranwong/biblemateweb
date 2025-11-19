from nicegui import ui

# 1. INJECT JAVASCRIPT LISTENER
# This script runs once on page load. It listens for any "Right Click" (contextmenu)
# and immediately saves the highlighted text to a global variable 'window.bibleMateSelection'.
ui.add_head_html('''
<script>
    window.bibleMateSelection = "";
    document.addEventListener('contextmenu', function() {
        window.bibleMateSelection = window.getSelection().toString();
    });
</script>
''')

def handle_selection(text, action):
    if not text.strip():
        ui.notify('No text selected!', type='warning')
        return
    
    # Display the result (simulating your AI processing)
    ui.notify(f"{action}: {text}")
    print(f"Sending '{text}' to AI for {action}...")

async def get_selection_and_process(action):
    # 2. RETRIEVE THE SNAPSHOT
    # Instead of asking for the *current* selection (which might be gone),
    # we ask for the variable we saved when the user right-clicked.
    selected_text = await ui.run_javascript('window.bibleMateSelection')
    
    handle_selection(selected_text, action)

# --- UI Layout ---
ui.markdown('## BibleMate AI - Smart Selection')

with ui.card().classes('w-full max-w-2xl bg-gray-50'):
    
    # We assign a specific ID or class if we want to scope the listener, 
    # but the global listener above works fine for this.
    content = """
    <h3 class="text-xl font-bold mb-2">John 1:1</h3>
    <p class="mb-2">In the beginning was the Word, and the Word was with God, and the Word was God.</p>
    <p>The same was in the beginning with God.</p>
    """
    ui.html(content, sanitize=False).classes('text-lg font-serif text-gray-800')

    # The Context Menu
    with ui.context_menu():
        ui.menu_item('🔍 Analyze Greek', 
                     on_click=lambda: get_selection_and_process('Greek Analysis'))
        ui.menu_item('📝 Summarize', 
                     on_click=lambda: get_selection_and_process('Summarize'))
        ui.separator()
        ui.menu_item('💾 Save Verse', 
                     on_click=lambda: get_selection_and_process('Save'))

ui.run(port=9999)