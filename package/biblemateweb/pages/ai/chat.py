from agentmake import agentmake, DEFAULT_AI_BACKEND
from agentmake.utils.text_wrapper import get_stream_event_text
from agentmake.utils.read_assistant_response import is_openai_style
from nicegui import ui, app, run
import asyncio, datetime, re
from biblemateweb import config, get_translation

def ai_chat(gui=None, q="", **_):

    SEND_BUTTON = None
    REQUEST_INPUT = None
    MESSAGES = None
    MESSAGE_CONTAINER = None
    SCROLL_AREA = None
    CANCEL_EVENT = None
    DELETE_DIALOG = None
    n = None

    def resume_input():
        nonlocal SEND_BUTTON, REQUEST_INPUT
        SEND_BUTTON.set_text(get_translation("Send"))
        SEND_BUTTON.props('color=primary')
        REQUEST_INPUT.enable()
        REQUEST_INPUT.set_value("")
        REQUEST_INPUT.run_method('focus')

    async def stop_confirmed():
        DELETE_DIALOG.close()
        if n is not None:
            n.message = get_translation("Stopping...")
        if CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
            CANCEL_EVENT.set()
        await asyncio.sleep(0)

    async def handle_send_click():

        def get_next_chunk(iterator):
            """
            Runs in a separate thread. 
            Returns the next item, or None if the iterator is exhausted.
            """
            try:
                return next(iterator)
            except StopIteration:
                return None
            except Exception as e:
                return e  # Return the error to be handled in the main loop

        """Handles the logic when the Send button is pressed."""
        nonlocal REQUEST_INPUT, SCROLL_AREA, MESSAGE_CONTAINER, SEND_BUTTON, MESSAGES, CANCEL_EVENT, n
        if CANCEL_EVENT is None or CANCEL_EVENT.is_set():
            CANCEL_EVENT = asyncio.Event() # do not use threading.Event() in this case
        else:
            DELETE_DIALOG.open()
            return None

        if not MESSAGES:
            MESSAGES = [{"role": "system", "content": "You are BibleMate AI, an autonomous agent designed to assist users with their Bible study."}]
        prompt_markdown = None
        agent_markdown = None
        output_markdown = None
        if user_request := REQUEST_INPUT.value:
            REQUEST_INPUT.disable()
            SEND_BUTTON.set_text(get_translation("Stop"))
            SEND_BUTTON.props('color=negative')

            with MESSAGE_CONTAINER:
                ui.chat_message(user_request,
                    #name='Eliran Wong',
                    stamp=datetime.datetime.now().strftime("%H:%M"),
                    avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                )

                # when prompt-engineering is enabled
                if app.storage.user["prompt_engineering"]:
                    # holder for prompt text
                    with ui.expansion(get_translation("Prompt Engineering"), icon='tune', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as prompt_expansion:
                        prompt_markdown = ui.markdown()
                    # get streaming object
                    n = ui.notification(get_translation("Creating agent..."), timeout=None, spinner=True)
                    if app.storage.user["auto_scroll"]:
                        # Give the client a moment to render the new content
                        #await asyncio.sleep(0.1)
                        # scroll to the bottom
                        await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')
                    await asyncio.sleep(0)
                    # run completion
                    answers = ""
                    completion = await run.io_bound(
                        agentmake, 
                        MESSAGES, 
                        system="improve_prompt_2",
                        backend=config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND, 
                        follow_up_prompt=user_request, 
                        stream=True, 
                        print_on_terminal=False, 
                        stream_events_only=True, 
                        #streaming_event=CANCEL_EVENT, # this works only for unpacking completion text; not useful in this case
                    )
                    n.message = get_translation("Loading...")
                    await asyncio.sleep(0)
                    try:
                        while CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
                            # 0. SAFETY CHECK: Stop if user closed the tab
                            if not ui.context.client.connected:
                                #print("Client disconnected. Stopping stream.")
                                break
                            # 1. Fetch next chunk using the helper
                            # This moves the blocking 'next()' call AND the StopIteration catch 
                            # into the thread. We just wait for the result.
                            event = await run.io_bound(get_next_chunk, completion)

                            # 2. Explicit check: Is the iterator exhausted?
                            if event is None:
                                #print("Stream finished successfully.") # Debug log
                                break
                            # 3. Check for errors returned by the helper
                            elif isinstance(event, Exception):
                                ui.notify(f"Stream interrupted: {str(event)}", type='warning')
                                break

                            # --- Process the valid event below ---
                            if answer := get_stream_event_text(event, openai_style=is_openai_style(config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND)):
                                answers += answer
                                prompt_markdown.content = answers
                                await asyncio.sleep(0)
                        # when cancelled
                        if CANCEL_EVENT is not None and CANCEL_EVENT.is_set():
                            print(2)
                            n.message = get_translation("Cancelled!")
                            prompt_markdown.content = f"[{get_translation("Cancelled!")}]"
                            await asyncio.sleep(0)
                        # when done
                        else:
                            n.message = get_translation("Done!")
                            if "```" in answers:
                                answers = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", answers, flags=re.DOTALL).strip()
                                prompt_markdown.content = answers
                                await asyncio.sleep(0)
                            user_request = answers
                            # close agent expansion
                            prompt_expansion.close()
                            if app.storage.user["auto_scroll"]:
                                # Give the client a moment to render the new content
                                await asyncio.sleep(0.1)
                                # scroll to the bottom
                                await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')
                    except Exception as e:
                        # check errors here
                        #print(f"Error: {str(e)}")
                        #import traceback
                        #traceback.print_exc()
                        pass

                    # stop this spinner
                    n.spinner = False
                    n.dismiss()
                    n = None
                    if CANCEL_EVENT.is_set():
                        CANCEL_EVENT = None
                        resume_input()
                        return None
                
                # when agent is enabled
                if app.storage.user["use_agent"]:
                    # holder for agent text
                    system_message = None # default
                    with ui.expansion(get_translation("Agent"), icon='support_agent', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as agent_expansion:
                        agent_markdown = ui.markdown()
                    # get streaming object
                    n = ui.notification(get_translation("Creating agent..."), timeout=None, spinner=True)
                    if app.storage.user["auto_scroll"]:
                        # Give the client a moment to render the new content
                        #await asyncio.sleep(0.1)
                        # scroll to the bottom
                        await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')
                    await asyncio.sleep(0)
                    # run completion
                    answers = ""
                    completion = await run.io_bound(
                        agentmake, 
                        MESSAGES, 
                        system="create_agent",
                        backend=config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND, 
                        follow_up_prompt=user_request, 
                        stream=True, 
                        print_on_terminal=False, 
                        stream_events_only=True, 
                        #streaming_event=CANCEL_EVENT, # this works only for unpacking completion text; not useful in this case
                    )
                    n.message = get_translation("Loading...")
                    await asyncio.sleep(0)
                    try:
                        while CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
                            # 0. SAFETY CHECK: Stop if user closed the tab
                            if not ui.context.client.connected:
                                #print("Client disconnected. Stopping stream.")
                                break
                            # 1. Fetch next chunk using the helper
                            # This moves the blocking 'next()' call AND the StopIteration catch 
                            # into the thread. We just wait for the result.
                            event = await run.io_bound(get_next_chunk, completion)

                            # 2. Explicit check: Is the iterator exhausted?
                            if event is None:
                                #print("Stream finished successfully.") # Debug log
                                break
                            # 3. Check for errors returned by the helper
                            elif isinstance(event, Exception):
                                ui.notify(f"Stream interrupted: {str(event)}", type='warning')
                                break

                            # --- Process the valid event below ---
                            if answer := get_stream_event_text(event, openai_style=is_openai_style(config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND)):
                                answers += answer
                                if answers.startswith("```agent\n"):
                                    answers = answers[9:]
                                agent_markdown.content = answers
                                await asyncio.sleep(0)
                        # when cancelled
                        if CANCEL_EVENT is not None and CANCEL_EVENT.is_set():
                            n.message = get_translation("Cancelled!")
                            agent_markdown.content = f"[{get_translation("Cancelled!")}]"
                            await asyncio.sleep(0)
                        # when done
                        else:
                            n.message = get_translation("Created!")
                            if answers.endswith("```"):
                                answers = answers[:-3].strip()
                                agent_markdown.content = answers
                                await asyncio.sleep(0)
                            system_message = answers
                            # close agent expansion
                            agent_expansion.close()
                            if app.storage.user["auto_scroll"]:
                                # Give the client a moment to render the new content
                                await asyncio.sleep(0.1)
                                # scroll to the bottom
                                await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')
                    except Exception as e:
                        # check errors here
                        #print(f"Error: {str(e)}")
                        #import traceback
                        #traceback.print_exc()
                        pass

                    # stop this spinner
                    n.spinner = False
                    n.dismiss()
                    n = None
                    if CANCEL_EVENT.is_set():
                        CANCEL_EVENT = None
                        resume_input()
                        return None

                # holder for output text
                output_markdown = ui.markdown() 
                # get streaming object
                n = ui.notification(get_translation("Connecting..."), timeout=None, spinner=True)
                if app.storage.user["auto_scroll"]:
                    # Give the client a moment to render the new content
                    #await asyncio.sleep(0.1)
                    # scroll to the bottom
                    await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')
                await asyncio.sleep(0)
                # run completion
                answers = ""
                completion = await run.io_bound(
                    agentmake, 
                    MESSAGES, 
                    system=system_message,
                    backend=config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND, 
                    follow_up_prompt=user_request, 
                    stream=True, 
                    print_on_terminal=False, 
                    stream_events_only=True, 
                    #streaming_event=CANCEL_EVENT, # this works only for unpacking completion text; not useful in this case
                )
                n.message = get_translation("Running...")
                await asyncio.sleep(0)
                try:
                    while CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
                        # 0. SAFETY CHECK: Stop if user closed the tab
                        if not ui.context.client.connected:
                            #print("Client disconnected. Stopping stream.")
                            break
                        # 1. Fetch next chunk using the helper
                        # This moves the blocking 'next()' call AND the StopIteration catch 
                        # into the thread. We just wait for the result.
                        event = await run.io_bound(get_next_chunk, completion)

                        # 2. Explicit check: Is the iterator exhausted?
                        if event is None:
                            #print("Stream finished successfully.") # Debug log
                            break
                        # 3. Check for errors returned by the helper
                        elif isinstance(event, Exception):
                            ui.notify(f"Stream interrupted: {str(event)}", type='warning')
                            break

                        # --- Process the valid event below ---
                        if answer := get_stream_event_text(event, openai_style=is_openai_style(config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND)):
                            answers += answer
                            output_markdown.content = answers
                            await asyncio.sleep(0)
                    # when cancelled
                    if CANCEL_EVENT is not None and CANCEL_EVENT.is_set():
                        n.message = get_translation("Cancelled!")
                        output_markdown.content = f"[{get_translation("Cancelled!")}]"
                        await asyncio.sleep(0)
                    # when done
                    else:
                        CANCEL_EVENT.set()
                        n.message = get_translation("Done!")
                        MESSAGES += [
                            {"role": "user", "content": user_request},
                            {"role": "assistant", "content": answers},
                        ]
                        if app.storage.user["auto_scroll"]:
                            # Give the client a moment to render the new content
                            await asyncio.sleep(0.1)
                            # scroll to the bottom
                            await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')
                except Exception as e:
                    # check errors here
                    #print(f"Error: {str(e)}")
                    #import traceback
                    #traceback.print_exc()
                    pass

                # restore send button
                CANCEL_EVENT = None
                resume_input()
                # stop spinner
                await asyncio.sleep(1)
                n.spinner = False
                n.dismiss()
                n = None

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

        with ui.row().classes('w-full flex-nowrap items-end mb-0'):
            REQUEST_INPUT = ui.textarea(placeholder=get_translation("Enter your message...")).props('rows=4').classes('flex-grow h-full resize-none').on('keydown.shift.enter.prevent', handle_send_click)
            with ui.column().classes('h-full justify-between gap-2'):
                ui.checkbox(get_translation("Auto-scroll"), value=True).classes('w-full').bind_value(app.storage.user, 'auto_scroll').props('dense')
                SEND_BUTTON = ui.button('Send', on_click=handle_send_click).classes('w-full')
        
        with ui.row().classes('w-full flex-nowrap items-end mb-30'):
            ui.checkbox(get_translation("Improve Prompt"), value=True).classes('w-full').bind_value(app.storage.user, 'prompt_engineering').props('dense')
            ui.checkbox(get_translation("Agent"), value=True).classes('w-full').bind_value(app.storage.user, 'use_agent').props('dense')
                

        ui.label('BibleMate AI | © 2025 | Eliran Wong')

        # Dialog to confirm the reset
        with ui.dialog() as DELETE_DIALOG, ui.card():
            ui.label(f'{get_translation("Stop running task?")}?')
            with ui.row().classes('justify-end w-full'):
                ui.button(get_translation("Cancel"), on_click=DELETE_DIALOG.close).props('flat text-color=secondary')
                ui.button(get_translation("Stop"), color='negative', on_click=stop_confirmed)

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
