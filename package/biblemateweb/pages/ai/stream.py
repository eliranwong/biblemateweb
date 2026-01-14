from agentmake import agentmake, DEFAULT_AI_BACKEND, unpack_instruction_content, unpack_system_content
from agentmake.utils.text_wrapper import get_stream_event_text
from agentmake.utils.read_assistant_response import is_openai_style
from nicegui import ui, app, run
import asyncio
from biblemateweb import config, get_translation, DEFAULT_MESSAGES


async def stream_response(messages, user_request, response_markdown, cancel_event, system=None, scroll_area=None, agent_expansion=None, agent_markdown=None, **kwargs):
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

    if "instruction" in kwargs:
        instruction_content = kwargs.pop("instruction")
        instruction_content = unpack_instruction_content(instruction_content)
        # refine user request
        user_request = instruction_content + "\n" + user_request

    if system == "auto":
        system = await stream_response(DEFAULT_MESSAGES, user_request, agent_markdown, cancel_event, system="bible/create_agent", scroll_area=scroll_area)
        if not system or system.strip() == "[NO_CONTENT]":
            return None
        else:
            # refine response
            system = system.replace("should:", "should:\n")
            system = system.replace("examples:", "examples:\n")
            if system.startswith("```agent\n"):
                system = system[9:]
            if system.endswith("```"):
                system = system[:-3].strip()
            agent_markdown.content = system
            await asyncio.sleep(0)
            # close prompt expansion
            if agent_expansion is not None:
                agent_expansion.close()
    elif system is not None:
        system_content = unpack_system_content(system)
        system = None
        # refine user request
        # Note: when a conversation goes long, system message placed in the beginning of the messages chain does not work properly.
        # Embed the system message into the user request to enhance the response
        user_request = f"""---

START OF YOUR NEW ROLE

---

{system_content}

---

START OF MY REQUEST

---

{user_request}"""

    # get streaming object
    n = ui.notification(get_translation("Loading..."), timeout=None, spinner=True)
    if app.storage.user["auto_scroll"] and scroll_area is not None:
        # Give the client a moment to render the new content
        #await asyncio.sleep(0.1)
        # scroll to the bottom
        await ui.run_javascript(f'getElement({scroll_area.id}).setScrollPosition("vertical", 99999, 300)')
    await asyncio.sleep(0)
    # run completion
    text_chunks = ""
    completion = await run.io_bound(
        agentmake, 
        messages, 
        system=system,
        backend=app.storage.user["ai_backend"].strip() if app.storage.user["api_key"].strip() and app.storage.user["ai_backend"].strip() else config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND, 
        model=app.storage.user["ai_model"].strip() if app.storage.user["api_key"].strip() and app.storage.user["ai_model"].strip() else None, 
        api_key=app.storage.user["api_key"].strip() if app.storage.user["api_key"].strip() else None,
        api_endpoint=app.storage.user["api_endpoint"].strip() if app.storage.user["api_key"].strip() and app.storage.user["api_endpoint"].strip() else None,
        max_tokens=int(app.storage.user["max_tokens"]) if app.storage.user["max_tokens"] and app.storage.user["api_endpoint"].strip() else None,
        temperature=float(app.storage.user["temperature"]) if app.storage.user["temperature"] and app.storage.user["api_endpoint"].strip() else None,
        follow_up_prompt=user_request, 
        stream=True, 
        print_on_terminal=False, 
        stream_events_only=True, 
        #streaming_event=cancel_event, # this works only for unpacking completion text; not useful in this case
        **kwargs,
    )
    n.message = get_translation("Running...")
    await asyncio.sleep(0)
    try:
        while cancel_event is not None and not cancel_event.is_set():
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
            if text_chunk := get_stream_event_text(event, openai_style=is_openai_style(app.storage.user["ai_backend"].strip() if app.storage.user["api_key"].strip() and app.storage.user["ai_backend"].strip() else config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND)):
                text_chunks += text_chunk
                response_markdown.content = text_chunks
                await asyncio.sleep(0)
        # when cancelled
        if cancel_event is not None and cancel_event.is_set():
            n.message = get_translation("Cancelled!")
            response_markdown.content = f"[{get_translation("Cancelled!")}]"
            await asyncio.sleep(0)
        # when done
        else:
            n.message = get_translation("Done!")
            if app.storage.user["auto_scroll"] and scroll_area is not None:
                # Give the client a moment to render the new content
                await asyncio.sleep(0.1)
                # scroll to the bottom
                await ui.run_javascript(f'getElement({scroll_area.id}).setScrollPosition("vertical", 99999, 300)')
    except Exception as e:
        response_markdown.content = f"[{get_translation('Error')}: {str(e)}]"
        await asyncio.sleep(0)
        # check traceback
        #import traceback
        #traceback.print_exc()
        cancel_event.set()

    # stop this spinner
    n.spinner = False
    n.dismiss()
    n = None
    if cancel_event.is_set():
        cancel_event = None
        return None
    
    return text_chunks.replace(" ", " ").replace("‑", "-") # replace non-standard characters in some LLM output, e.g. gpt-oss
