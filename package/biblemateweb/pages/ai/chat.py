from agentmake import agentmake
from nicegui import ui, app
#from pathlib import Path
import asyncio, datetime, threading
from biblemateweb import get_translation

def ai_chat(gui=None, q="", **_):

    RUNNING = False
    SEND_BUTTON = None
    REQUEST_INPUT = None
    MESSAGES = None
    MESSAGE_CONTAINER = None 
    SCROLL_AREA = None
    AUTO_SCROLL_CHECKBOX = None
    STREAMING_EVENT = None


    async def handle_send_click():
        """Handles the logic when the Send button is pressed."""
        nonlocal RUNNING, REQUEST_INPUT, SCROLL_AREA, MESSAGE_CONTAINER, SEND_BUTTON, AUTO_SCROLL_CHECKBOX, MESSAGES, STREAMING_EVENT
        if RUNNING:
            STREAMING_EVENT.set()
            RUNNING = False
            return None

        if not MESSAGES:
            MESSAGES = [{"role": "system", "content": "You are BibleMate AI, an autonomous agent designed to assist users with their Bible study."}]
        RUNNING = True
        output_markdown = None
        if user_request := REQUEST_INPUT.value:
            SEND_BUTTON.set_text('Cancel')
            SEND_BUTTON.props('color=negative')

            with MESSAGE_CONTAINER:
                ui.chat_message(user_request,
                    #name='Eliran Wong',
                    stamp=datetime.datetime.now().strftime("%H:%M"),
                    avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                )
                output_markdown = ui.markdown()

            n = ui.notification(timeout=None)

            STREAMING_EVENT = threading.Event()
            awaitable = asyncio.to_thread(agentmake, MESSAGES, follow_up_prompt=user_request, stream=True, print_on_terminal=False, streaming_event=STREAMING_EVENT)
            task = asyncio.create_task(awaitable)
            while RUNNING and not task.done():
                n.message = get_translation('Loading...')
                n.spinner = True
                await asyncio.sleep(0.2)
            if not RUNNING:
                task.cancel()
                n.message = 'Cancelled!'
            else:
                n.message = 'Done!'
                MESSAGES = task.result()
                output_markdown.content = MESSAGES[-1]['content']
                output_markdown.update()
                # clean input
                REQUEST_INPUT.set_value('')
                
                if AUTO_SCROLL_CHECKBOX.value:
                    # Give the client a moment to render the new content
                    await asyncio.sleep(0.1)
                    # scroll to the bottom
                    await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')

                RUNNING = False
                
            # restore send button
            SEND_BUTTON.set_text('Send')
            SEND_BUTTON.props('color=primary')
            # stop spinner
            n.spinner = False
            await asyncio.sleep(1)
            n.dismiss()

    with ui.column().classes('w-full h-screen no-wrap gap-0') as chat_container:

        def check_screen(ev):
            nonlocal gui, chat_container
            if gui.is_portrait and app.storage.user["layout"] == 2:
                chat_container.classes(remove='h-screen', add='h-[50vh]')
            else:
                chat_container.classes(remove='h-[50vh]', add='h-screen')
            chat_container.update()

        # check screen when loaded
        check_screen(None)
        # bind
        ui.on('resize', check_screen)

        # Capture the ui.scroll_area instance in the global variable
        # w-full flex-grow p-4 border border-gray-300 rounded-lg mb-2
        with ui.column().classes('w-full flex-grow overflow-hidden'):
            with ui.scroll_area().classes('w-full p-4 border rounded-lg h-full') as SCROLL_AREA:
                MESSAGE_CONTAINER = ui.column().classes('w-full items-start gap-2')

        with ui.row().classes('w-full flex-nowrap items-end mb-30'):
            REQUEST_INPUT = ui.textarea(placeholder='Enter your message...').props('rows=4').classes('flex-grow h-full resize-none').on('keydown.shift.enter.prevent', handle_send_click)
            with ui.column().classes('h-full justify-between gap-2'):
                AUTO_SCROLL_CHECKBOX = ui.checkbox('Auto-scroll', value=True).classes('w-full')
                SEND_BUTTON = ui.button('Send', on_click=handle_send_click).classes('w-full')
                

        ui.label('BibleMate AI | © 2025 | Eliran Wong')

        if q:
            if not q.strip().endswith("# Query"):
                q = f'# Selected text\n\n{q}\n\n# Query\n\n'
            elif q.endswith("# Query"):
                q += "\n\n"
            REQUEST_INPUT.set_value(q)
        REQUEST_INPUT.run_method('focus')
        ui.run_javascript(f'''
            const el = document.getElementById({REQUEST_INPUT.id}).querySelector('textarea');
            el.setSelectionRange(el.value.length, el.value.length);
        ''')
