import asyncio
from nicegui import ui

async def load_verses(progress_bar, status_label):
    # 1. Show elements and reset progress
    status_label.set_visibility(True)
    progress_bar.set_visibility(True)
    progress_bar.set_value(0)
    
    total_verses = 200
    
    for i in range(1, total_verses + 1):
        await asyncio.sleep(0.01)  # Simulating fast data fetch
        
        # Update UI
        current_progress = i / total_verses
        progress_bar.set_value(current_progress)
        status_label.set_text(f"Fetching verse {i} of {total_verses}...")

    # 2. Briefly show completion state
    status_label.set_text("Success! Verses loaded.")
    await asyncio.sleep(1.5) 
    
    # 3. Hide everything again
    status_label.set_visibility(False)
    progress_bar.set_visibility(False)

@ui.page('/')
def main_page():
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('BibleMate AI').classes('text-h4 mb-4')
        
        # Action button
        ui.button('Load Verses', on_click=lambda: load_verses(progress_bar, status_label))
        
        # Feedback area (Hidden by default)
        status_label = ui.label('').classes('mt-4 text-grey-7')
        status_label.set_visibility(False)
        
        progress_bar = ui.linear_progress(value=0).classes('w-64 mt-2')
        progress_bar.set_visibility(False)

ui.run(port=9999)