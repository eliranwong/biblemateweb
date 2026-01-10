from nicegui import ui, app, run
import asyncio, datetime, re, os, pypandoc, tempfile, traceback, json
from biblemateweb.pages.ai.stream import stream_response
from biblemateweb import BIBLEMATEWEB_APP_DIR, get_translation, markdown2html, config, DEFAULT_MESSAGES
from biblemateweb.mcp_tools.elements import TOOL_ELEMENTS
from biblemateweb.mcp_tools.tools import TOOLS
from biblemateweb.mcp_tools.tool_descriptions import TOOL_DESCRIPTIONS
from biblemateweb.api.api import get_api_content
from biblemate.core.systems import get_system_tool_instruction, get_system_master_plan, get_system_make_suggestion, get_system_progress
from agentmake import readTextFile
from copy import deepcopy
from biblemateweb.fx.cloud_index_manager import get_drive_service


class ReviewDialog(ui.dialog):
    def __init__(self):
        super().__init__()
        with self, ui.card().classes('w-full'): # w-96 sets a fixed width, adjust as needed
            ui.label(get_translation("Partner Mode Review")).classes('text-h6 font-bold')
            
            # The editable text area
            self.editor = ui.textarea(label='Edit Content') \
                .classes('w-full') \
                .props('outlined rows=10') # Make it look like a distinct box
            
            with ui.row().classes('w-full justify-end'):
                # Button 1: Cancel
                # Sending None indicates "Canceled"
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                
                # Button 2: Confirm
                # Sending the text value indicates "Confirmed"
                ui.button(get_translation("Confirm"), on_click=lambda: self.submit(self.editor.value))

    def open_with_text(self, text_to_review: str):
        """
        Updates the text area and opens the dialog.
        Returns an awaitable object.
        """
        self.editor.value = text_to_review
        return self # This allows us to write: await dialog

class SelectionDialog(ui.dialog):
    def __init__(self):
        super().__init__()
        with self, ui.card().classes('w-full max-w-md'):
            ui.label(get_translation("Tool Selection")).classes('text-xl font-bold text-secondary mb-4')
            
            # This container will hold the radio selection dynamically
            self.selection_container = ui.column().classes('w-full')
            
            with ui.row().classes('w-full justify-end'):
                # Button 1: Cancel
                # Sending None indicates "Canceled"
                ui.button(get_translation("Cancel"), on_click=lambda: self.submit(None)) \
                    .props('flat color=grey')
                
                # Button 2: Confirm
                # Sending the text value indicates "Confirmed"
                ui.button(get_translation("Confirm"), on_click=lambda: self.submit(self.radio.value))

    def open_with_options(self, options: list):
        """
        Updates the options and opens the dialog.
        Returns an awaitable object.
        """
        self.selection_container.clear()
        with self.selection_container:
            # We use a radio button for selection
            self.radio = ui.radio(options).classes('w-full').props('color=primary')
        return self # This allows us to write: await dialog

def chapter2verses(request:str) -> str:
    return re.sub("[Cc][Hh][Aa][Pp][Tt][Ee][Rr] ([0-9]+?)([^0-9])", r"\1:1-180\2", request)

def ai_partner(gui=None, q="", **_):

    REVIEW_DIALOG = ReviewDialog()
    SELECTION_DIALOG = SelectionDialog()

    MASTER_USER_REQUEST = None
    PROGRESS_STATUS = "START"
    MESSAGES = None
    FINAL_INSTRUCTION = """# Instruction
Please provide a comprehensive response that resolves my original request, ensuring all previously completed milestones and data points are fully integrated.

# Original Request
"""

    SEND_BUTTON = None
    REQUEST_INPUT = None
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

    MASTER_PLAN_PROMPT_TEMPLATE = """Provide me with the `Preliminary Action Plan` and the `Measurable Outcome` for resolving `My Request`.
    
# Available Tools

Available tools are: {available_tools}.

{tool_descriptions}

# My Request

{user_request}"""

    def download_all_content(messages):
        content = """---

I'm BibleMate AI [developed by Eliran Wong], an autonomous agent designed to assist you with your Bible study.

---

"""
        content += "\n\n---\n\n".join([i.get("content", "") for i in messages[1:]])
        ui.download(content.encode('utf-8'), 'BibleMate_AI_Conversation.txt')
        ui.notify(get_translation("Downloaded!"), type='positive')

    def download_report(markdown_content):
        try:
            # 1. Create a temporary file that acts as the bridge
            # 'delete=False' is sometimes needed on Windows to close/re-open, 
            # but in a simple flow, we can just read it back.
            with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
                
                # 2. Convert Markdown -> DOCX file
                pypandoc.convert_text(
                    markdown_content, 
                    'docx', 
                    format='md', 
                    outputfile=tmp.name
                )
                
                # 3. Read bytes back into memory
                tmp.seek(0)
                docx_bytes = tmp.read()

            # 4. Trigger download in NiceGUI (no file left on server)
            ui.download(docx_bytes, filename='BibleMate_AI_Report.docx')
            ui.notify(get_translation("Downloaded!"), type='positive')
        except:
            traceback.print_exc()

    def reset_page():
        nonlocal MASTER_USER_REQUEST, MESSAGES, PROGRESS_STATUS, MESSAGE_CONTAINER
        MASTER_USER_REQUEST = None
        MESSAGES = None
        PROGRESS_STATUS = "START"
        MESSAGE_CONTAINER.clear()

    def reset_ui():
        nonlocal SEND_BUTTON, REQUEST_INPUT, CANCEL_EVENT, CANCEL_NOTIFICATION, PROGRESS_STATUS
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
        PROGRESS_STATUS = "STOP"

    async def stop_confirmed():
        nonlocal DELETE_DIALOG, CANCEL_NOTIFICATION, CANCEL_EVENT
        DELETE_DIALOG.close()
        CANCEL_NOTIFICATION = ui.notification(get_translation("Stopping..."), timeout=None, spinner=True)
        if CANCEL_EVENT is not None and not CANCEL_EVENT.is_set():
            CANCEL_EVENT.set()
        await asyncio.sleep(0)

    def load_access_note(service):
        try:
            filename = "access_note_partner_mode.json"
            results = service.files().list(
                q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
                spaces='appDataFolder',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])
            
            if files:
                request = service.files().get_media(fileId=files[0]['id'])
                data = json.loads(request.execute())
                return data.get("content", "")
            return ""
        except Exception as e:
            #ui.notify(f"Error loading: {e}", type='negative')
            return ""

    def save_access_note(service, content):
        """
        Performs the slow network calls to Google Drive.
        Running this on the main thread would freeze the app.
        """
        import json, io
        from googleapiclient.http import MediaIoBaseUpload
        
        # access file
        filename = "access_note_partner_mode.json"
        # Prepare the file data
        file_data = {"content": content}
        media = MediaIoBaseUpload(
            io.BytesIO(json.dumps(file_data).encode('utf-8')), 
            mimetype='application/json'
        )
        
        # 1. Search for existing file
        results = service.files().list(
            q=f"name='{filename}' and 'appDataFolder' in parents and trashed=false",
            spaces='appDataFolder',
            fields='files(id)'
        ).execute()
        files = results.get('files', [])

        # 2. Update or Create
        if files:
            service.files().update(fileId=files[0]['id'], media_body=media).execute()
            return "updated"
        else:
            meta = {'name': filename, 'parents': ['appDataFolder']}
            service.files().create(body=meta, media_body=media).execute()
            return "created"

    async def handle_send_click():
        """Handles the logic when the Send button is pressed."""

        nonlocal REQUEST_INPUT, SCROLL_AREA, MESSAGE_CONTAINER, SEND_BUTTON, MESSAGES, CANCEL_EVENT, PROGRESS_STATUS, MASTER_USER_REQUEST, DELETE_DIALOG, FINAL_INSTRUCTION, REVIEW_DIALOG, SELECTION_DIALOG

        # daily limit check
        if config.limit_partner_mode_once_daily and not app.storage.client["custom"] and not app.storage.user["api_key"].strip():
            n = ui.notification(get_translation("Checking daily limit..."), timeout=None, spinner=True)
            await asyncio.sleep(0)
            # 1. Auth Check        
            token = app.storage.user.get('google_token', "")
            if not token:
                with ui.card().classes('absolute-center'):
                    ui.html('Sign in with Google to securely save and sync your personal notes across all your devices.<br><i><b>Data Policy Note:</b> BibleMate AI does not collect or store your personal notes. Your notes are saved directly within your own Google Account.</i>', sanitize=False)
                    with ui.row().classes('w-full justify-center'):
                        ui.button('Login with Google', on_click=lambda: ui.navigate.to('/login'))
                    with ui.expansion(get_translation("BibleMate AI Data Policy & Privacy Commitment"), icon='privacy_tip').props('header-class="text-secondary"'):
                        ui.html(
                            """<b>We respect your privacy.</b>
To keep your data private, BibleMate AI doesn't collect, store or share your personal information on its servers. 
Instead, daily logs or bible notes are saved exclusively on <b>your own Google Drive/Account.</b>, ensuring that you retain full control and ownership of your private data at all times.""", 
                            sanitize=False,
                        )
                n.spinner = False
                n.dismiss() 
                return
            # verify last access when user doesn't use custom token nor their own API keys
            service = get_drive_service(token)
            last_access_date = await run.io_bound(load_access_note, service)
            # check current date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            if last_access_date == current_date:
                MESSAGE_CONTAINER.clear()
                with MESSAGE_CONTAINER:
                    ui.html("<h2>Daily Limit Reached</h2>", sanitize=False)
                    preferences = get_translation("Preferences")
                    markdown_info = f"""You've reached your daily limit for using the BibleMate AI Partner Mode. Please try again tomorrow!

To remove the daily limit, please update your `{preferences}` with one of the following:

* A valid custom token (provided by your server administrator).
* Your own AI backend API key and connection details."""
                    ui.chat_message(markdown2html(markdown_info),
                        name='BibleMate AI',
                        stamp=datetime.datetime.now().strftime("%H:%M"),
                        avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                        text_html=True,
                        sanitize=False,
                    )
                    ui.button(f'Go to {preferences}', on_click=lambda: ui.navigate.to('/settings'))
                    ui.link('How to set up a custom token?', 'https://github.com/eliranwong/biblemateweb/blob/main/docs/custom_token.md')
                    ui.link('How to set up an API key?', 'https://github.com/eliranwong/biblemateweb/blob/main/docs/api_key_setup.md')
                return None
            # save access note
            n.message = get_translation("Saving access note...")
            await run.io_bound(save_access_note, service, current_date)
            # close spinner
            n.spinner = False
            await asyncio.sleep(0)
            n.dismiss()
        
        if CANCEL_EVENT is None or CANCEL_EVENT.is_set():
            CANCEL_EVENT = asyncio.Event() # do not use threading.Event() in this case
        else:
            DELETE_DIALOG.open()
            return None

        if MASTER_USER_REQUEST is not None and PROGRESS_STATUS == "STOP":
            reset_page()

        if not MESSAGES:
            MESSAGES = deepcopy(DEFAULT_MESSAGES)
        prompt_markdown = None
        output_markdown = None
        if user_request := REQUEST_INPUT.value:
            gui.update_active_area2_tab_records(q=user_request)
            
            MASTER_USER_REQUEST = user_request
            REQUEST_INPUT.disable()
            SEND_BUTTON.set_text(get_translation("Stop"))
            SEND_BUTTON.props('color=negative')

            MESSAGE_CONTAINER.clear()
            with MESSAGE_CONTAINER:
                user_request = re.sub(r"^[#]+ (.*?)\n", r"**\1**\n", user_request, flags=re.MULTILINE)
                ui.chat_message(markdown2html(user_request),
                    name='You',
                    stamp=datetime.datetime.now().strftime("%H:%M"),
                    avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                    text_html=True,
                    sanitize=False,
                )

                # when prompt-engineering is enabled
                if app.storage.user["prompt_engineering"]:
                    with ui.expansion(get_translation("Prompt Engineering"), icon='tune', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as prompt_expansion:
                        prompt_markdown = ui.markdown().style('font-size: 1.1rem')
                    user_request = await stream_response(MESSAGES, user_request, prompt_markdown, CANCEL_EVENT, system="improve_prompt_2", scroll_area=SCROLL_AREA)
                    if user_request is not None:
                        user_request = await REVIEW_DIALOG.open_with_text(user_request)
                        if user_request is None:
                            prompt_markdown.content = f"[{get_translation("Cancelled!")}]"
                    if not user_request or user_request.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        MASTER_USER_REQUEST = user_request
                        # refine response
                        if "```" in user_request:
                            MASTER_USER_REQUEST = user_request = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
                        # apply the last fix from stream output
                        prompt_markdown.content = user_request
                        await asyncio.sleep(0)
                        # close prompt expansion
                        prompt_expansion.close()

                # master plan
                with ui.expansion(get_translation("Master Plan"), icon='architecture', value=True) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"') as plan_expansion:
                    plan_markdown = ui.markdown().style('font-size: 1.1rem')
                master_plan_prompt = MASTER_PLAN_PROMPT_TEMPLATE.format(available_tools=list(TOOLS.keys()), tool_descriptions=TOOL_DESCRIPTIONS, user_request=user_request)
                master_plan = await stream_response(MESSAGES, master_plan_prompt, plan_markdown, CANCEL_EVENT, system=get_system_master_plan(), scroll_area=SCROLL_AREA)
                if master_plan is not None:
                    master_plan = await REVIEW_DIALOG.open_with_text(master_plan)
                    if master_plan is None:
                        plan_markdown.content = f"[{get_translation("Cancelled!")}]"
                if not master_plan or master_plan.strip() == "[NO_CONTENT]":
                    reset_ui()
                    return None
                else:
                    # refine response
                    # apply the last fix from stream output
                    plan_markdown.content = master_plan
                    await asyncio.sleep(0)
                    # close prompt expansion
                    plan_expansion.close()
                
                ROUND =  1
                MESSAGES += [
                    {"role": "user", "content": MASTER_USER_REQUEST},
                    {"role": "assistant", "content": "Let's begin!"},
                ]
                while not ("STOP" in PROGRESS_STATUS or re.sub("^[^A-Za-z]*?([A-Za-z]+?)[^A-Za-z]*?$", r"\1", PROGRESS_STATUS).upper() == "STOP"):
                    # display round
                    ui.markdown(f"### {get_translation('Round')} {ROUND}").style('font-size: 1.1rem')
                    # suggestion
                    system_make_suggestion = get_system_make_suggestion(master_plan=master_plan)
                    follow_up_prompt = "Please provide me with the next step suggestion, based on the action plan."
                    with ui.expansion(get_translation("Suggestion"), icon='lightbulb', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as suggestion_expansion:
                        suggestion_markdown = ui.markdown().style('font-size: 1.1rem')
                    suggestion = await stream_response(MESSAGES, follow_up_prompt, suggestion_markdown, CANCEL_EVENT, system=system_make_suggestion, scroll_area=SCROLL_AREA)
                    if not suggestion or suggestion.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # refine response
                        # apply the last fix from stream output
                        suggestion_markdown.content = suggestion
                        await asyncio.sleep(0)
                        # close prompt expansion
                        suggestion_expansion.close()

                    # tool selection
                    selected_tool = "get_direct_text_response" # default
                    with ui.expansion(get_translation("Tool Selection"), icon='handyman', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as tools_expansion:
                        tools_markdown = ui.markdown().style('font-size: 1.1rem')
                    suggested_tools = await stream_response(DEFAULT_MESSAGES, suggestion, tools_markdown, CANCEL_EVENT, system=SYSTEM_TOOL_SELECTION, scroll_area=SCROLL_AREA)
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
                    
                    # tool selection dialog
                    selected_tool = await SELECTION_DIALOG.open_with_options(suggested_tools)
                    if selected_tool is None:
                        tools_markdown.content = f"[{get_translation("Cancelled!")}]"
                        reset_ui()
                        return None

                    if not selected_tool in TOOLS:
                        selected_tool = "get_direct_text_response"
                    suggested_tools = "\n".join([f"{order+1}. `{i}`" for order, i in enumerate(suggested_tools)])
                    tools_markdown.content = f"## Suggested Tools\n\n{suggested_tools}\n\n## Selected Tool:\n\n`{selected_tool}`"
                    await asyncio.sleep(0)
                    selected_tool_description = TOOLS.get(selected_tool, "No description available.")
                    tool_instruction_draft = TOOL_INSTRUCTION_PROMPT + "\n\n# Suggestions\n\n"+suggestion+f"\n\n# Tool Description of `{selected_tool}`\n\n"+selected_tool_description+TOOL_INSTRUCTION_SUFFIX
                    system_tool_instruction = get_system_tool_instruction(selected_tool, selected_tool_description)
                    container = ui.column()
                    with container:
                        with ui.expansion(get_translation("Tool Instruction"), icon='handyman', value=True) \
                                .classes('w-full border rounded-lg shadow-sm') \
                                .props('header-class="font-bold text-lg text-secondary"') as tool_instruction_expansion:
                            tool_instruction_markdown = ui.markdown().style('font-size: 1.1rem')
                    user_request = await stream_response(MESSAGES, tool_instruction_draft, tool_instruction_markdown, CANCEL_EVENT, system=system_tool_instruction, scroll_area=SCROLL_AREA)
                    if user_request is not None:
                        user_request = await REVIEW_DIALOG.open_with_text(user_request)
                        if user_request is None:
                            tool_instruction_markdown.content = f"[{get_translation("Cancelled!")}]"
                    if not user_request or user_request.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        container.clear()
                        with container:
                            user_request = re.sub(r"^[#]+ (.*?)\n", r"**\1**\n", user_request, flags=re.MULTILINE)
                            ui.chat_message(markdown2html(user_request),
                                name='BibleMate AI',
                                stamp=datetime.datetime.now().strftime("%H:%M"),
                                avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                                text_html=True,
                                sanitize=False,
                            )

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
                            answers = await stream_response(MESSAGES, user_request, output_markdown, CANCEL_EVENT, system="auto", scroll_area=SCROLL_AREA, agent_expansion=agent_expansion, agent_markdown=agent_markdown)
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
                                {"role": "user", "content": f"[ROUND {ROUND}]\n\n{user_request}"},
                                {"role": "assistant", "content": f"[TOOL] {selected_tool}\n\n[RESPONSE]\n\n{answers}"},
                            ]

                    # check progress
                    system_progress = get_system_progress(master_plan=master_plan)
                    follow_up_prompt="Please decide either to `CONTINUE` or `STOP` the process."
                    with ui.expansion(get_translation("Progress"), icon='trending_up', value=True) \
                            .classes('w-full border rounded-lg shadow-sm') \
                            .props('header-class="font-bold text-lg text-secondary"') as progress_expansion:
                        progress_markdown = ui.markdown().style('font-size: 1.1rem')
                    PROGRESS_STATUS = await stream_response(MESSAGES, follow_up_prompt, progress_markdown, CANCEL_EVENT, system=system_progress, scroll_area=SCROLL_AREA)
                    if not PROGRESS_STATUS or PROGRESS_STATUS.strip() == "[NO_CONTENT]":
                        reset_ui()
                        return None
                    else:
                        # refine response
                        # n/a
                        # close prompt expansion
                        progress_expansion.close()

                    # update round
                    ROUND += 1

                # final report
                ui.markdown("---")
                ui.chat_message(markdown2html(get_translation("Wrapping up...")),
                    name='BibleMate AI',
                    stamp=datetime.datetime.now().strftime("%H:%M"),
                    avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                    text_html=True,
                    sanitize=False,
                )
                system_report = "write_final_answer"
                follow_up_prompt=f"""{FINAL_INSTRUCTION}{MASTER_USER_REQUEST}"""
                with ui.expansion(get_translation("Final Report"), icon='summarize', value=True) \
                        .classes('w-full border rounded-lg shadow-sm') \
                        .props('header-class="font-bold text-lg text-secondary"') as report_expansion:
                    report_markdown = ui.markdown().style('font-size: 1.1rem')
                report = await stream_response(MESSAGES, follow_up_prompt, report_markdown, CANCEL_EVENT, system=system_report, scroll_area=SCROLL_AREA)
                if not report or report.strip() == "[NO_CONTENT]":
                    reset_ui()
                    return None
                else:
                    # refine response
                    # apply the last fix from stream output
                    report_markdown.content = report
                    await asyncio.sleep(0)
                    # update
                    MESSAGES += [
                        {"role": "user", "content": "[FINAL] Please provide a comprehensive response that resolves my original request, ensuring all previously completed milestones and data points are fully integrated."},
                        {"role": "assistant", "content": f"[REPORT]\n\n{report}"},
                    ]
                    # close prompt expansion
                    report_expansion.close()

                    # offer downloads
                    with ui.column().classes('w-full items-center'):
                        ui.button(get_translation("Download the whole Conversation"), on_click=lambda: download_all_content(MESSAGES))
                        ui.button(get_translation("Download the Final Report Only"), on_click=lambda: download_report(report))

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
                    welcome_message = """**Hello! I’m BibleMate AI.** You’ve enabled my Partner Mode capabilities.

In this mode, we work together as a team. Like Agent Mode, I will handle complex, multi-step Bible study tasks, but you remain in the driver’s seat. You can review and refine the master plan, approve tool selections, and edit the instructions for every step I take.

What shall we study together today? Enter your request below to begin our collaboration.

---

💡 Tip: Check the Enhance box to automatically improve and clarify your prompt for better results.

---"""
                    ui.chat_message(markdown2html(get_translation(welcome_message if app.storage.user["ui_language"] == "eng" else get_translation("welcome_partner_mode"))),
                        name='BibleMate AI',
                        stamp=datetime.datetime.now().strftime("%H:%M"),
                        avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
                        text_html=True,
                        sanitize=False,
                    )
                    ui.markdown(f"---\n\n## {get_translation('Other AI Modes')}\n\n")
                    ui.button(get_translation("Chat Mode"), on_click=lambda: gui.load_area_2_content(title="chat"))
                    ui.button(get_translation("Agent Mode"), on_click=lambda: gui.load_area_2_content(title="agent"))
                    ui.markdown("---")

        with ui.row().classes('w-full flex-nowrap items-end mb-27'):
            REQUEST_INPUT = ui.textarea(placeholder=get_translation("Enter your request here...")).props('rows=4').classes('flex-grow h-full resize-none').on('keydown.shift.enter.prevent', handle_send_click)
            with ui.column().classes('h-full justify-between gap-2'):
                ui.checkbox(get_translation("Auto-scroll")).classes('w-full').bind_value(app.storage.user, 'auto_scroll').props('dense').tooltip(get_translation("Scroll to the end automatically"))
                ui.checkbox(get_translation("Enhance")).classes('w-full').bind_value(app.storage.user, 'prompt_engineering').props('dense').tooltip(get_translation("Improve Prompt"))
                SEND_BUTTON = ui.button('Send', on_click=handle_send_click).classes('w-full')

        ui.label('BibleMate AI | © 2025-2026 | Eliran Wong')

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
