from agentmake import agentmake, DEFAULT_AI_BACKEND, unpack_instruction_content, unpack_system_content
from agentmake.utils.text_wrapper import get_stream_event_text
from agentmake.utils.read_assistant_response import is_openai_style
from nicegui import ui, app, run
import asyncio
import importlib
from biblemateweb import config, get_translation, DEFAULT_MESSAGES

# Signed-in CLI backends. When more than one use_*_for_default flag is on,
# the first entry here wins: grok, then claude, then antigravity.
_SUBSCRIPTION_BACKENDS = (
    # id, show flag, default flag, package, model prefixes
    ("grok", "show_grok_build", "use_grok_build_for_default", "grokbuildstreaming", ("grok-",)),
    ("claude", "show_claude_code", "use_claude_code_for_default", "claudecodestreaming", ("claude", "sonnet", "opus", "haiku")),
    ("antigravity", "show_antigravity", "use_antigravity_for_default", "antigravitystreaming", ("gemini",)),
)


def _subscription_flags():
    flags = {}
    for _backend, show_flag, use_flag, _package, _prefixes in _SUBSCRIPTION_BACKENDS:
        flags[show_flag] = bool(getattr(config, show_flag, False))
        flags[use_flag] = bool(getattr(config, use_flag, False))
    return flags


def choose_subscription_backend(user_backend, user_key, server_backend, flags):
    """Return the signed-in CLI backend for this turn, or None to use agentmake.

    An explicit user choice counts only when that backend's show flag is on.
    A blank or ``default`` choice uses the first use_*_for_default flag that is on.
    A saved API key on any other backend stays with agentmake. ``config.ai_backend``
    set to grok, claude, or antigravity is the fallback.
    """
    user_backend = (user_backend or "").strip()
    user_key = (user_key or "").strip()
    server_backend = (server_backend or "").strip()
    for backend, show_flag, _use_flag, _package, _prefixes in _SUBSCRIPTION_BACKENDS:
        if flags.get(show_flag) and user_backend == backend:
            return backend
    if user_backend in ("", "default"):
        for backend, _show_flag, use_flag, _package, _prefixes in _SUBSCRIPTION_BACKENDS:
            if flags.get(use_flag):
                return backend
    if user_key and user_backend and user_backend != "default":
        return None
    for backend, _show_flag, _use_flag, _package, _prefixes in _SUBSCRIPTION_BACKENDS:
        if server_backend == backend:
            return backend
    return None


def subscription_model(backend, model):
    """Return ``model`` when it belongs to ``backend``, else None so the library default is used."""
    text = (model or "").strip()
    if not text or not backend:
        return None
    lowered = text.lower()
    for name, _show_flag, _use_flag, _package, prefixes in _SUBSCRIPTION_BACKENDS:
        if name == backend:
            if any(lowered.startswith(prefix) for prefix in prefixes):
                return text
            return None
    return None


def _subscription_backend():
    """Backend id when this turn should stream from a signed-in CLI, else None."""
    return choose_subscription_backend(
        app.storage.user.get("ai_backend"),
        app.storage.user.get("api_key"),
        getattr(config, "ai_backend", ""),
        _subscription_flags(),
    )


def _package_for(backend):
    for name, _show_flag, _use_flag, package, _prefixes in _SUBSCRIPTION_BACKENDS:
        if name == backend:
            return package
    return None


async def _stream_with_subscription(backend, messages, user_request, response_markdown, cancel_event, system=None, scroll_area=None):
    """Stream one signed-in CLI turn into the markdown widget.

    Prompt names are already unpacked by the caller. This path does not call agentmake.
    ``backend`` is grok (grokbuildstreaming), claude (claudecodestreaming), or
    antigravity (antigravitystreaming).
    """
    package = _package_for(backend)
    try:
        stream_text = importlib.import_module(package).stream_text
    except ImportError:
        response_markdown.content = f"[{get_translation('Error')}: {package} is not installed]"
        await asyncio.sleep(0)
        if cancel_event is not None:
            cancel_event.set()
        return None

    n = ui.notification(get_translation("Loading..."), timeout=None, spinner=True)
    if app.storage.user["auto_scroll"] and scroll_area is not None:
        await ui.run_javascript(f'getElement({scroll_area.id}).setScrollPosition("vertical", 99999, 300)')
    await asyncio.sleep(0)
    text_chunks = ""
    try:
        model = subscription_model(backend, app.storage.user.get("ai_model"))
        n.message = get_translation("Running...")
        await asyncio.sleep(0)
        async for text_chunk in stream_text(
            messages,
            follow_up=user_request,
            system=system if isinstance(system, str) and system.strip() else None,
            model=model,
            cancel_event=cancel_event,
        ):
            if not ui.context.client.connected:
                break
            if cancel_event is not None and cancel_event.is_set():
                break
            if not text_chunk:
                continue
            text_chunks += text_chunk
            response_markdown.content = text_chunks
            await asyncio.sleep(0)
        if cancel_event is not None and cancel_event.is_set():
            n.message = get_translation("Cancelled!")
            response_markdown.content = f"[{get_translation('Cancelled!')}]"
            await asyncio.sleep(0)
        else:
            n.message = get_translation("Done!")
            if app.storage.user["auto_scroll"] and scroll_area is not None:
                await asyncio.sleep(0.1)
                await ui.run_javascript(f'getElement({scroll_area.id}).setScrollPosition("vertical", 99999, 300)')
    except Exception as e:
        response_markdown.content = f"[{get_translation('Error')}: {str(e)}]"
        await asyncio.sleep(0)
        if cancel_event is not None:
            cancel_event.set()

    n.spinner = False
    n.dismiss()
    if cancel_event is not None and cancel_event.is_set():
        return None
    return text_chunks.replace(" ", " ").replace("‑", "-")


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

    subscription = _subscription_backend()

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
        if subscription:
            # These CLIs take the unpacked role as the system prompt.
            # Embedding it above the user request makes the model answer the request instead.
            system = system_content
        else:
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

    if subscription:
        return await _stream_with_subscription(subscription, messages, user_request, response_markdown, cancel_event, system=system, scroll_area=scroll_area)

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
    try:
        if config.disable_local_api_endpoint and (app.storage.user["api_endpoint"].strip().lower().startswith("http://localhost") or app.storage.user["api_endpoint"].strip().lower().startswith("http://127.0.0.1")):
            app.storage.user["api_endpoint"] = ""
        completion = await run.io_bound(
            agentmake, 
            messages, 
            system=system,
            backend=app.storage.user["ai_backend"].strip() if app.storage.user["api_key"].strip() and not app.storage.user["ai_backend"].strip() == "default" else config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND, 
            model=app.storage.user["ai_model"].strip() if app.storage.user["api_key"].strip() and app.storage.user["ai_model"].strip() and not app.storage.user["ai_backend"].strip() == "default" else None, 
            api_key=app.storage.user["api_key"].strip() if app.storage.user["api_key"].strip() and not app.storage.user["ai_backend"].strip() == "default" else None,
            api_endpoint=app.storage.user["api_endpoint"].strip() if app.storage.user["api_key"].strip() and app.storage.user["api_endpoint"].strip() and not app.storage.user["ai_backend"].strip() == "default" else None,
            max_tokens=int(app.storage.user["max_tokens"]) if app.storage.user["api_key"].strip() and app.storage.user["max_tokens"] and not app.storage.user["ai_backend"].strip() == "default" else None,
            temperature=float(app.storage.user["temperature"]) if app.storage.user["api_key"].strip() and app.storage.user["temperature"] and not app.storage.user["ai_backend"].strip() == "default" else None,
            follow_up_prompt=user_request, 
            stream=True, 
            print_on_terminal=False, 
            stream_events_only=True, 
            #streaming_event=cancel_event, # this works only for unpacking completion text; not useful in this case
            **kwargs,
        )
        n.message = get_translation("Running...")
        await asyncio.sleep(0)

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
            if text_chunk := get_stream_event_text(event, openai_style=is_openai_style(app.storage.user["ai_backend"].strip() if app.storage.user["api_key"].strip() and not app.storage.user["ai_backend"].strip() == "default" else config.ai_backend if config.ai_backend else DEFAULT_AI_BACKEND)):
                text_chunks += text_chunk
                response_markdown.content = text_chunks
                await asyncio.sleep(0)
        # when cancelled
        if cancel_event is not None and cancel_event.is_set():
            n.message = get_translation("Cancelled!")
            response_markdown.content = f"[{get_translation('Cancelled!')}]"
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
