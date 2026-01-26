from nicegui import ui, app, run
import asyncio, datetime, re, os
from biblemateweb.pages.ai.stream import stream_response
from biblemateweb import BIBLEMATEWEB_APP_DIR, get_translation, markdown2html, get_watermark, chapter2verses, download_txt, download_docx, DEFAULT_MESSAGES
from biblemateweb.mcp_tools.elements import TOOL_ELEMENTS
from biblemateweb.mcp_tools.tools import TOOLS
from biblemateweb.api.api import get_api_content
from biblemateweb.dialogs.review_dialog import ReviewDialog
from biblemateweb.dialogs.selection_dialog import SelectionDialog
from biblemateweb.dialogs.filename_dialog import FilenameDialog
from biblemate.core.systems import get_system_tool_instruction
from copy import deepcopy
from agentmake import readTextFile
import traceback, tempfile, pypandoc


def ai_chat(gui=None, q="", **_):
    
    START = True

    DOWNLOAD_CONTAINER = None
    SEND_BUTTON = None
    REQUEST_INPUT = None
    MESSAGES = None
    MESSAGE_CONTAINER = None
    SCROLL_AREA = None
    CANCEL_EVENT = None
    CANCEL_NOTIFICATION = None
    DELETE_DIALOG = None

    SYSTEM_TOOL_SELECTION = readTextFile(os.path.join(BIBLEMATEWEB_APP_DIR, "mcp_tools", "system_tool_selection_lite.md"))

    TOOL_INSTRUCTION_PROMPT = """Please transform the following suggestions into clear, precise, and actionable instructions."""
    TOOL_INSTRUCTION_SUFFIX = """

# Remember

* Provide me with the instructions directly.
* Do not start your response, like, 'Here are the insturctions ...'
* Do not ask me if I want to execute the instruction."""

    AVAILABLE_TOOLS = sorted(list(TOOL_ELEMENTS.keys()))
    AVAILABLE_TOOLS.insert(0, "get_direct_text_response")
    AVAILABLE_TOOLS_PATTERN = "|".join(AVAILABLE_TOOLS)

    async def eidt_response(index, output_markdown):
        nonlocal MESSAGES
        response = MESSAGES[index]["content"]
        if edited_item := await ReviewDialog().open_with_text(response, label=get_translation("Edit")):
            MESSAGES[index]["content"] = edited_item
            output_markdown.content = edited_item
            await asyncio.sleep(0)

    def reset_ui():
        nonlocal SEND_BUTTON, REQUEST_INPUT, CANCEL_EVENT, CANCEL_NOTIFICATION, MESSAGES, DOWNLOAD_CONTAINER
        if not CANCEL_EVENT.is_set():
            CANCEL_EVENT.set()
        if CANCEL_EVENT is not None:
            CANCEL_EVENT = None
        SEND_BUTTON.enable()
        SEND_BUTTON.set_text(get_translation("Send"))
        SEND_BUTTON.props('color=primary')
        REQUEST_INPUT.enable()
        REQUEST_INPUT.set_value("")
        REQUEST_INPUT.run_method('focus')
        if CANCEL_NOTIFICATION is not None:
            CANCEL_NOTIFICATION.dismiss()
            CANCEL_NOTIFICATION = None
        with MESSAGE_CONTAINER:
            with ui.row().classes('w-full justify-center') as DOWNLOAD_CONTAINER:
                ui.button(get_translation("Download the whole Conversation"), on_click=lambda: download_all_content(MESSAGES))

    async def stop_confirmed():
        nonlocal DELETE_DIALOG, CANCEL_NOTIFICATION, CANCEL_EVENT, SEND_BUTTON
        SEND_BUTTON.disable()
        DELETE_DIALOG.close()
        CANCEL_NOTIFICATION = ui.notification(get_translation("Stopping..."), timeout=None, spinner=True)
        if CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
            CANCEL_EVENT.set()
        await asyncio.sleep(0)

    async def download_all_content(messages):
        filename = await FilenameDialog().open_with_filename("BibleMate_AI_Conversation")
        if filename is None or not filename.strip():
            return
        elif not filename.strip().endswith('.txt'):
            filename = filename.strip() + '.txt'
        messages_copy = deepcopy(messages)
        content = """---

I'm BibleMate AI, an autonomous agent designed to assist you with your Bible study.

---

"""
        content += "\n\n---\n\n".join([("[REQUEST] "+i.get("content", "")) if index%2 == 0 else ("[RESPONSE] "+i.get("content", "")) for index, i in enumerate(messages_copy[1:])])
        content += get_watermark()
        ui.download(content.encode('utf-8'), filename=filename)
        ui.notify(get_translation("Downloaded!"), type='positive')

    async def handle_send_click():

        """Handles the logic when the Send button is pressed."""
        nonlocal REQUEST_INPUT, SCROLL_AREA, MESSAGE_CONTAINER, SEND_BUTTON, MESSAGES, CANCEL_EVENT, START, DOWNLOAD_CONTAINER, DELETE_DIALOG

        if DOWNLOAD_CONTAINER is not None:
            DOWNLOAD_CONTAINER.clear()

        if START:
            START = False
            MESSAGE_CONTAINER.clear()

        if CANCEL_EVENT is None or CANCEL_EVENT.is_set():
            CANCEL_EVENT = asyncio.Event() # do not use threading.Event() in this case
        else:
            DELETE_DIALOG.open()
            return None

        if not MESSAGES:
            MESSAGES = deepcopy(DEFAULT_MESSAGES)
        prompt_markdown = None
        output_markdown = None
        specified_tool = None
        if user_request := REQUEST_INPUT.value:
            if re.search(f"""^@({AVAILABLE_TOOLS_PATTERN}) """, user_request):
                specified_tool = re.search(f"""^@({AVAILABLE_TOOLS_PATTERN}) """, user_request).group(1)
                user_request = user_request[len(specified_tool)+2:]
            gui.update_active_area2_tab_records(q=user_request)

            REQUEST_INPUT.disable()
            SEND_BUTTON.set_text(get_translation("Stop"))
            SEND_BUTTON.props('color=negative')

            with MESSAGE_CONTAINER:
                ui.chat_message(user_request,
                    #name='Eliran Wong',
                    stamp=datetime.datetime.now().strftime("%H:%M"),
                    avatar=app.storage.user['avatar'] if app.storage.user['avatar'].strip() else 'https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                )

                # when prompt-engineering is enabled
                if app.storage.user["prompt_engineering"]:
                    with ui.expansion(get_translation("Prompt Engineering"), icon='tune', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as prompt_expansion:
                        prompt_markdown = ui.markdown().style('font-size: 1.1rem')
                    user_request = await stream_response(MESSAGES, user_request, prompt_markdown, CANCEL_EVENT, system="improve_prompt_2", scroll_area=SCROLL_AREA)
                    if app.storage.user["chat_mode_review"] and user_request is not None:
                        user_request = await ReviewDialog().open_with_text(user_request)
                        if user_request is None:
                            prompt_markdown.content = f"[{get_translation("Cancelled!")}]"
                    if not user_request or user_request.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # refine response
                        if "```" in user_request:
                            user_request = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                        # apply the last fix from stream output
                        prompt_markdown.content = user_request
                        await asyncio.sleep(0)
                        # close prompt expansion
                        prompt_expansion.close()
                
                # tool selection
                selected_tool = specified_tool if specified_tool else "get_direct_text_response" # default
                if app.storage.user["auto_tool_selection"] or specified_tool:
                    with ui.expansion(get_translation("Tool Selection"), icon='handyman', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as tools_expansion:
                        tools_markdown = ui.markdown().style('font-size: 1.1rem')
                    if specified_tool:
                        suggested_tools = [specified_tool]
                    else:
                        suggested_tools = await stream_response(MESSAGES, user_request, tools_markdown, CANCEL_EVENT, system=SYSTEM_TOOL_SELECTION, scroll_area=SCROLL_AREA)
                        if not suggested_tools or suggested_tools.strip() == "[NO_CONTENT]":
                            suggested_tools = ["get_direct_text_response"]
                        else:
                            # refine response
                            suggested_tools = re.sub(r"^.*?(\[.*?\]).*?$", r"\1", suggested_tools, flags=re.DOTALL)
                            try:
                                suggested_tools = eval(suggested_tools.replace("`", "'")) if suggested_tools.startswith("[") and suggested_tools.endswith("]") else ["get_direct_text_response"] # fallback to direct response
                            except:
                                suggested_tools = ["get_direct_text_response"]
                            # close prompt expansion
                            tools_expansion.close()

                        if app.storage.user["chat_mode_review"]:
                            # tool selection dialog
                            suggested_tools.append(get_translation("More..."))
                            selected_tool = await SelectionDialog().open_with_options(suggested_tools)
                            if selected_tool is not None and selected_tool.strip() == get_translation("More..."):
                                selected_tool = await SelectionDialog(big=True).open_with_options(AVAILABLE_TOOLS)
                            if selected_tool is None:
                                tools_markdown.content = f"[{get_translation("Cancelled!")}]"
                                await reset_ui()
                                return None
                        else:
                            selected_tool = suggested_tools[0]

                    if not selected_tool in TOOLS:
                        selected_tool = "get_direct_text_response"
                    if specified_tool:
                        tools_markdown.content = f"## Selected Tool:\n\n`{selected_tool}`"
                    else:
                        suggested_tools = "\n".join([f"{order+1}. `{i}`" for order, i in enumerate(suggested_tools)])
                        tools_markdown.content = f"## Suggested Tools\n\n{suggested_tools}\n\n## Selected Tool:\n\n`{selected_tool}`"
                    await asyncio.sleep(0)
                    selected_tool_description = TOOLS.get(selected_tool, "No description available.")
                    tool_instruction_draft = TOOL_INSTRUCTION_PROMPT + "\n\n# Suggestions\n\n"+user_request+f"\n\n# Tool Description of `{selected_tool}`\n\n"+selected_tool_description+TOOL_INSTRUCTION_SUFFIX
                    system_tool_instruction = get_system_tool_instruction(selected_tool, selected_tool_description)
                    with ui.expansion(get_translation("Tool Instruction"), icon='handyman', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as tool_instruction_expansion:
                        tool_instruction_markdown = ui.markdown().style('font-size: 1.1rem')
                    user_request = await stream_response(MESSAGES, tool_instruction_draft, tool_instruction_markdown, CANCEL_EVENT, system=system_tool_instruction, scroll_area=SCROLL_AREA)
                    if user_request is not None and app.storage.user["chat_mode_review"]:
                        user_request = await ReviewDialog().open_with_text(user_request)
                        if user_request is None:
                            tool_instruction_markdown.content = f"[{get_translation("Cancelled!")}]"
                    if not user_request or user_request.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # apply the last fix from stream output
                        tool_instruction_markdown.content = user_request
                        await asyncio.sleep(0)
                        # close prompt expansion
                        tool_instruction_expansion.close()

                # generate response
                n = None
                answers = None
                try:
                    if selected_tool == "get_direct_text_response":
                        if app.storage.user["use_agent"]:
                            with ui.expansion(get_translation("Agent"), icon='support_agent', value=True) \
                                    .classes('w-full border rounded-lg shadow-sm') \
                                    .props('header-class="font-bold text-lg text-secondary"') as agent_expansion:
                                agent_markdown = ui.markdown().style('font-size: 1.1rem')
                            output_markdown = ui.markdown().style('font-size: 1.1rem')
                            answers = await stream_response(MESSAGES, user_request, output_markdown, CANCEL_EVENT, system="auto", scroll_area=SCROLL_AREA, agent_expansion=agent_expansion, agent_markdown=agent_markdown)
                        else:
                            output_markdown = ui.markdown().style('font-size: 1.1rem')
                            answers = await stream_response(MESSAGES, user_request, output_markdown, CANCEL_EVENT, system=None, scroll_area=SCROLL_AREA)
                        # update
                        if not answers or answers.strip() == "[NO_CONTENT]":
                            reset_ui()
                            return None
                        else:
                            # apply the last fix from stream output
                            output_markdown.content = answers
                            await asyncio.sleep(0)
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
                            else:
                                # apply the last fix from stream output
                                output_markdown.content = answers
                                await asyncio.sleep(0)
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
                        with ui.row().classes('w-full justify-center'):
                            index = len(MESSAGES)-1
                            ui.button("📋 "+get_translation("Copy"), on_click=lambda: gui.copy_text(output_markdown.content))
                            ui.button("📥 TXT", on_click=lambda: download_txt(output_markdown.content))
                            ui.button("📥 DOCX", on_click=lambda: download_docx(output_markdown.content))
                            ui.button("✒️ "+get_translation("Edit"), on_click=lambda: eidt_response(index, output_markdown))

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
                with ui.column().classes('w-full items-start gap-2') as MESSAGE_CONTAINER:
                    welcome_message = """**Hello! I’m BibleMate AI.** You’ve enabled my Chat Mode capabilities.

I’m here to chat with you about anything in the Bible. Whether you have questions about a verse, need historical context, or just want to explore a topic, let’s talk!

What would you like to discuss today? Enter your message below to get started.

---

💡 Tips — Enhance your experience:

* Enhance: Check this to automatically improve and clarify your prompt.
* Agent: Check this to engage my advanced reasoning for more detailed responses.
* Tools: Check this to let me access my dedicated suite of Bible study tools for better accuracy.
* Review: Check this to review and adjust my responses after each round.

---"""
                    ui.chat_message(markdown2html(get_translation(welcome_message if app.storage.user["ui_language"] == "eng" else get_translation("welcome_chat_mode"))),
                        name='BibleMate AI',
                        stamp=datetime.datetime.now().strftime("%H:%M"),
                        avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                        text_html=True,
                        sanitize=False,
                    )
                    ui.markdown(f"---\n\n## {get_translation('Other AI Modes')}\n\n")
                    ui.button(get_translation("Partner Mode"), on_click=lambda: gui.load_area_2_content(title="partner"))
                    ui.button(get_translation("Agent Mode"), on_click=lambda: gui.load_area_2_content(title="agent"))
                    ui.markdown("---")

        with ui.row().classes('w-full flex-nowrap items-end mb-0'):
            REQUEST_INPUT = ui.textarea(placeholder=get_translation("Enter your request here...")).props('rows=4').classes('flex-grow h-full resize-none').on('keydown.shift.enter.prevent', handle_send_click)
            with ui.column().classes('h-full justify-between gap-2'):
                ui.checkbox(get_translation("Auto-scroll")).classes('w-full').bind_value(app.storage.user, 'auto_scroll').props('dense').tooltip(get_translation("Scroll to the end automatically"))
                SEND_BUTTON = ui.button(get_translation("Send"), on_click=handle_send_click).classes('w-full')
        
        with ui.row().classes('w-full flex-nowrap items-end mb-27'):
            ui.checkbox(get_translation("Enhance")).classes('w-full').bind_value(app.storage.user, 'prompt_engineering').props('dense').tooltip(get_translation("Improve Prompt"))
            ui.checkbox(get_translation("Agent")).classes('w-full').bind_value(app.storage.user, 'use_agent').props('dense').tooltip(get_translation("Create agents to improve responses"))
            ui.checkbox(get_translation("Tools")).classes('w-full').bind_value(app.storage.user, 'auto_tool_selection').props('dense').tooltip(get_translation("Use tools to improve responses"))
            ui.checkbox(get_translation("Review")).classes('w-full').bind_value(app.storage.user, 'chat_mode_review').props('dense').tooltip(get_translation("Review"))

        ui.label('BibleMate AI | © 2025-2026 | Eliran Wong')

        # Dialog to confirm the reset
        with ui.dialog() as DELETE_DIALOG, ui.card():
            ui.label(f'{get_translation("Stop running task?")}?')
            with ui.row().classes('justify-end w-full'):
                ui.button(get_translation("Cancel"), on_click=DELETE_DIALOG.close).props('flat text-color=secondary')
                ui.button(get_translation("Stop"), color='negative', on_click=stop_confirmed)

        if q:
            REQUEST_INPUT.set_value(q)
        REQUEST_INPUT.run_method('focus')
        ui.run_javascript(f'''
            const el = document.getElementById({REQUEST_INPUT.id}).querySelector('textarea');
            el.setSelectionRange(el.value.length, el.value.length);
        ''')
