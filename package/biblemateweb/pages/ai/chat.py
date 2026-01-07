from nicegui import ui, app, run
import asyncio, datetime, re, os
from biblemateweb.pages.ai.stream import stream_response
from biblemateweb import BIBLEMATEWEB_APP_DIR, get_translation
from biblemateweb.mcp_tools.elements import TOOL_ELEMENTS
from biblemateweb.api.api import get_api_content
from biblemate.core.systems import get_system_tool_instruction
#from biblemate.bible_study_mcp import chapter2verses
from agentmake import readTextFile

def chapter2verses(request:str) -> str:
    return re.sub("[Cc][Hh][Aa][Pp][Tt][Ee][Rr] ([0-9]+?)([^0-9])", r"\1:1-180\2", request)

def ai_chat(gui=None, q="", **_):

    SEND_BUTTON = None
    REQUEST_INPUT = None
    MESSAGES = None
    MESSAGE_CONTAINER = None
    SCROLL_AREA = None
    CANCEL_EVENT = None
    CANCEL_NOTIFICATION = None
    DELETE_DIALOG = None

    SYSTEM_TOOL_SELECTION = readTextFile(os.path.join(BIBLEMATEWEB_APP_DIR, "mcp_tools", "system_tool_selection_lite.md"))
    TOOLS = eval(readTextFile(os.path.join(BIBLEMATEWEB_APP_DIR, "mcp_tools", "tools.py")))
    TOOLS_SCHEMA = eval(readTextFile(os.path.join(BIBLEMATEWEB_APP_DIR, "mcp_tools", "tools_schema.py")))

    TOOL_INSTRUCTION_PROMPT = """Please transform the following suggestions into clear, precise, and actionable instructions."""
    TOOL_INSTRUCTION_SUFFIX = """

# Remember

* Provide me with the instructions directly.
* Do not start your response, like, 'Here are the insturctions ...'
* Do not ask me if I want to execute the instruction."""

    def reset_ui():
        nonlocal SEND_BUTTON, REQUEST_INPUT, CANCEL_EVENT, CANCEL_NOTIFICATION
        if not CANCEL_EVENT.is_set():
            CANCEL_EVENT.set()
        if CANCEL_EVENT is not None:
            CANCEL_EVENT = None
        SEND_BUTTON.set_text(get_translation("Send"))
        SEND_BUTTON.props('color=primary')
        REQUEST_INPUT.enable()
        REQUEST_INPUT.set_value("")
        REQUEST_INPUT.run_method('focus')
        if CANCEL_NOTIFICATION is not None:
            CANCEL_NOTIFICATION.dismiss()
            CANCEL_NOTIFICATION = None

    async def stop_confirmed():
        nonlocal DELETE_DIALOG, CANCEL_NOTIFICATION, CANCEL_EVENT
        DELETE_DIALOG.close()
        CANCEL_NOTIFICATION = ui.notification(get_translation("Stopping..."), timeout=None, spinner=True)
        if CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
            CANCEL_EVENT.set()
        await asyncio.sleep(0)

    async def handle_send_click():

        """Handles the logic when the Send button is pressed."""
        nonlocal REQUEST_INPUT, SCROLL_AREA, MESSAGE_CONTAINER, SEND_BUTTON, MESSAGES, CANCEL_EVENT
        if CANCEL_EVENT is None or CANCEL_EVENT.is_set():
            CANCEL_EVENT = asyncio.Event() # do not use threading.Event() in this case
        else:
            DELETE_DIALOG.open()
            return None

        if not MESSAGES:
            MESSAGES = [{"role": "system", "content": "You are BibleMate AI, an autonomous agent designed to assist users with their Bible study."}]
        prompt_markdown = None
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
                    with ui.expansion(get_translation("Prompt Engineering"), icon='tune', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as prompt_expansion:
                        prompt_markdown = ui.markdown().style('font-size: 1.1rem')
                    user_request = await stream_response(MESSAGES, user_request, prompt_markdown, CANCEL_EVENT, system="improve_prompt_2", scroll_area=SCROLL_AREA)
                    if not user_request or user_request.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # refine response
                        if "```" in user_request:
                            user_request = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                            prompt_markdown.content = user_request
                            await asyncio.sleep(0)
                        # close prompt expansion
                        prompt_expansion.close()
                
                # tool selection
                selected_tool = "get_direct_text_response" # default
                if app.storage.user["auto_tool_selection"]:
                    with ui.expansion(get_translation("Tool Selection"), icon='handyman', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as tools_expansion:
                        tools_markdown = ui.markdown().style('font-size: 1.1rem')
                    suggested_tools = await stream_response(MESSAGES, user_request, tools_markdown, CANCEL_EVENT, system=SYSTEM_TOOL_SELECTION, scroll_area=SCROLL_AREA)
                    if not suggested_tools or suggested_tools.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # refine response
                        suggested_tools = re.sub(r"^.*?(\[.*?\]).*?$", r"\1", suggested_tools, flags=re.DOTALL)
                        try:
                            suggested_tools = eval(suggested_tools.replace("`", "'")) if suggested_tools.startswith("[") and suggested_tools.endswith("]") else ["get_direct_text_response"] # fallback to direct response
                        except:
                            suggested_tools = ["get_direct_text_response"]
                        # close prompt expansion
                        tools_expansion.close()

                    selected_tool = suggested_tools[0]
                    if not selected_tool in TOOLS_SCHEMA:
                        selected_tool = "get_direct_text_response"
                    tools_markdown.content = f"## Suggested Tools\n\n`{suggested_tools[1:-1]}`\n\n## Selected Tool:\n\n`{selected_tool}`"
                    await asyncio.sleep(0)
                    selected_tool_description = TOOLS.get(selected_tool, "No description available.")
                    tool_instruction_draft = TOOL_INSTRUCTION_PROMPT + "\n\n# Suggestions\n\n"+user_request+f"\n\n# Tool Description of `{selected_tool}`\n\n"+selected_tool_description+TOOL_INSTRUCTION_SUFFIX
                    system_tool_instruction = get_system_tool_instruction(selected_tool, selected_tool_description)
                    with ui.expansion(get_translation("Tool Instruction"), icon='handyman', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as tool_instruction_expansion:
                        tool_instruction_markdown = ui.markdown().style('font-size: 1.1rem')
                    user_request = await stream_response(MESSAGES, tool_instruction_draft, tool_instruction_markdown, CANCEL_EVENT, system=system_tool_instruction, scroll_area=SCROLL_AREA)
                    if not user_request or user_request.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # close prompt expansion
                        tool_instruction_expansion.close()

                # generate response
                n = None
                answers = None
                try:
                    if selected_tool == "get_direct_text_response":
                        with ui.expansion(get_translation("Agent"), icon='support_agent', value=True) \
                                .classes('w-full border rounded-lg shadow-sm') \
                                .props('header-class="font-bold text-lg text-secondary"') as agent_expansion:
                            agent_markdown = ui.markdown().style('font-size: 1.1rem')
                        output_markdown = ui.markdown().style('font-size: 1.1rem')
                        answers = await stream_response(MESSAGES, user_request, output_markdown, CANCEL_EVENT, system="auto" if app.storage.user["use_agent"] else None, scroll_area=SCROLL_AREA, agent_expansion=agent_expansion, agent_markdown=agent_markdown)
                        # update
                        if not answers or answers.strip() == "[NO_CONTENT]":
                            reset_ui()
                            return None
                    else:
                        element = TOOL_ELEMENTS.get(selected_tool)
                        # API access
                        if isinstance(element, str):
                            output_markdown = ui.markdown().style('font-size: 1.1rem')
                            n = ui.notification(get_translation("Loading..."), timeout=None, spinner=True)
                            await asyncio.sleep(0)
                            if not selected_tool == "search_the_whole_bible":
                                user_request = chapter2verses(user_request)
                            api_query = f"{element}{user_request}"
                            answers = await run.io_bound(get_api_content, api_query, app.storage.user["ui_language"], app.storage.client["custom"])
                            output_markdown.content = answers if answers else "[NO_CONTENT]"
                            await asyncio.sleep(0)
                        # AI generation
                        elif isinstance(element, dict):
                            system = element.pop("system") if "system" in element else None
                            if system == "auto":
                                with ui.expansion(get_translation("Agent"), icon='support_agent', value=True) \
                                        .classes('w-full border rounded-lg shadow-sm') \
                                        .props('header-class="font-bold text-lg text-secondary"') as agent_expansion:
                                    agent_markdown = ui.markdown().style('font-size: 1.1rem')
                            else:
                                agent_markdown = None
                                agent_expansion = None
                            output_markdown = ui.markdown().style('font-size: 1.1rem')
                            answers = await stream_response(MESSAGES, user_request, output_markdown, CANCEL_EVENT, system=system, scroll_area=SCROLL_AREA, agent_expansion=agent_expansion, agent_markdown=agent_markdown, **element)
                            # update
                            if not answers or answers.strip() == "[NO_CONTENT]":
                                reset_ui()
                                return None
                except Exception as e:
                    output_markdown.content = f"[{get_translation('Error')}: {str(e)}]"
                    await asyncio.sleep(0)
                    #import traceback
                    #traceback.print_exc()
                finally:
                    if n is not None:
                        n.spinner = False
                        n.dismiss()
                        n = None
                    if answers and not answers.strip() == "[NO_CONTENT]":
                        MESSAGES += [
                            {"role": "user", "content": user_request},
                            {"role": "assistant", "content": answers},
                        ]

                #reset
                reset_ui()

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
                ui.checkbox(get_translation("Auto-scroll")).classes('w-full').bind_value(app.storage.user, 'auto_scroll').props('dense')
                SEND_BUTTON = ui.button('Send', on_click=handle_send_click).classes('w-full')
        
        with ui.row().classes('w-full flex-nowrap items-end mb-30'):
            ui.checkbox(get_translation("Improve Prompt")).classes('w-full').bind_value(app.storage.user, 'prompt_engineering').props('dense')
            ui.checkbox(get_translation("Agent")).classes('w-full').bind_value(app.storage.user, 'use_agent').props('dense')
            ui.checkbox(get_translation("Tools")).classes('w-full').bind_value(app.storage.user, 'auto_tool_selection').props('dense')

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
