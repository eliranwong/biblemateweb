from nicegui import ui
import asyncio

# --- 1. Mock Database Service ---
# in your actual app, this would query your SQLite/PostgreSQL db
async def mock_fetch_verse_text(reference: str):
    # Simulating a database delay
    await asyncio.sleep(0.1) 
    
    # Mock responses based on input for demonstration
    ref_clean = reference.strip().lower()
    if "deut" in ref_clean:
        return "Hear, O Israel: The LORD our God, the LORD is one."
    elif "john" in ref_clean:
        return "For God so loved the world that he gave his one and only Son..."
    elif "rom" in ref_clean:
        return "But God demonstrates his own love for us in this: While we were still sinners, Christ died for us."
    else:
        return "Text not found in mock database."

# --- 2. Navigation Handler ---
def open_chapter_view(reference: str):
    # logic to navigate to the chapter page
    # e.g., ui.navigate.to(f'/bible/{book}/{chapter}')
    ui.notify(f"Opening full chapter view for: {reference}", type='info')

# --- 3. Main UI Logic ---
@ui.page('/')
def main_page():
    
    # Container to hold the search results
    results_container = ui.column().classes('w-full max-w-3xl gap-4')

    async def perform_search():
        query = search_input.value
        if not query:
            return

        results_container.clear()
        
        # Split input by semicolon and remove empty strings
        references = [ref.strip() for ref in query.split(';') if ref.strip()]

        for ref in references:
            # Fetch text (mocked)
            text_content = await mock_fetch_verse_text(ref)
            
            with results_container:
                # Card or Row style for each verse
                with ui.row().classes('w-full items-start no-wrap border-b border-gray-200 pb-4'):
                    
                    # The Chip Button
                    # NOTE: We use default=ref inside lambda to capture the current variable value
                    ui.chip(
                        ref, 
                        on_click=lambda e, r=ref: open_chapter_view(r), 
                        icon='book'
                    ).classes('bg-primary text-white cursor-pointer')
                    
                    # The Verse Content
                    ui.label(text_content).classes('text-lg pt-1 leading-relaxed text-gray-800')

    # --- Page Layout ---
    with ui.column().classes('w-full items-center p-10 gap-8'):
        
        ui.label('BibleMate AI Multi-Search').classes('text-3xl font-bold text-primary')

        # Input Area
        with ui.row().classes('w-full max-w-3xl items-center gap-2'):
            search_input = ui.input(
                placeholder='Ex: Deut 6:4; John 3:16; Rom 5:8'
            ).classes('w-full text-lg').on('keydown.enter', perform_search)
            
            # Enter Button
            ui.button(icon='subdirectory_arrow_left', on_click=perform_search)\
                .props('flat round color=primary')

        # This is where the verses will appear
        results_container

ui.run(title="BibleMate AI", port=9999, reload=False)