import asyncio
from nicegui import ui, run

async def load_verses(progress_bar, status_label):
    # 1. Reset and show progress
    progress_bar.set_value(0)
    progress_bar.set_visibility(True)
    status_label.set_text("Starting to load verses...")
    
    total_verses = 200
    
    # 2. Simulate the loading process
    for i in range(1, total_verses + 1):
        # We use run.io_bound to simulate a database/API call without blocking the UI
        await asyncio.sleep(0.02) # Simulating network latency
        
        # Update progress (value is between 0.0 and 1.0)
        percentage = i / total_verses
        progress_bar.set_value(percentage)
        
        if i % 10 == 0:
            status_label.set_text(f"Loaded {i}/{total_verses} verses...")

    # 3. Finalize
    status_label.set_text("")
    status_label.set_visibility(False)
    #await asyncio.sleep(2)
    progress_bar.set_visibility(False)

@ui.page('/')
def main_page():
    ui.label('BibleMate AI Loader').classes('text-h4')
    
    # Define the UI components
    status_label = ui.label("")
    status_label.set_visibility(False)
    progress_bar = ui.linear_progress(value=0, show_value=False).props('instant-feedback')
    progress_bar.set_visibility(False) # Hide until needed

    # Trigger button
    ui.button('Load Bible Verses', on_click=lambda: load_verses(progress_bar, status_label))

ui.run(port=9999)