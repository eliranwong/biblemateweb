import datetime
from functools import partial
from nicegui import ui, app
from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
from biblemateweb import get_translation
from biblemateweb.data.readings import allDays


def parse_day_passages(day: int, ui_language: str = "eng") -> list[dict]:
    """Parse day readings from English into localized passage dicts."""
    raw_list = allDays.get(day)
    if not raw_list:
        return []
    eng_parser = BibleVerseParser(False, language="eng")
    ui_parser = BibleVerseParser(False, language=ui_language)
    passages = []
    for segment in raw_list[0].split(","):
        seg = segment.strip()
        if not seg:
            continue
        refs = eng_parser.extractAllReferences(seg)
        if not refs:
            passages.append({"ref": seg, "b": 1, "c": 1, "v": 1})
            continue
        first_ref = refs[0]
        b, c = first_ref[0], first_ref[1]
        v = first_ref[2] if len(first_ref) >= 3 else 1
        # Check if original segment specifies only a chapter (no ':' in segment)
        is_chapter_only = ":" not in seg
        loc_ref = ui_parser.bcvToVerseReference(b, c, v, isChapter=is_chapter_only)
        if not is_chapter_only and len(first_ref) >= 4 and first_ref[3] and first_ref[3] != v:
            loc_ref = f"{loc_ref}-{first_ref[3]}"
        elif len(first_ref) >= 5 and first_ref[3] and first_ref[4]:
            end_ref = ui_parser.bcvToVerseReference(b, first_ref[3], first_ref[4])
            loc_ref = f"{loc_ref}–{end_ref}"
        passages.append({"ref": loc_ref, "b": b, "c": c, "v": v})
    return passages


def _compute_streak(completed_set: set[int], current_day: int) -> int:
    """Count consecutive completed days ending at current_day (or current_day - 1)."""
    if not completed_set:
        return 0
    anchor = current_day if current_day in completed_set else current_day - 1
    streak = 0
    while anchor >= 1 and anchor in completed_set:
        streak += 1
        anchor -= 1
    return streak


def reading_plan(gui=None, q='', **_):
    today_num = min(365, max(1, datetime.date.today().timetuple().tm_yday))
    initial_day = int(q) if (q and str(q).strip().isdigit() and 1 <= int(str(q).strip()) <= 365) else today_num
    state = {"day": initial_day}

    def get_completed() -> set[int]:
        return {int(d) for d in (app.storage.user.get("reading_plan_completed") or []) if 1 <= int(d) <= 365}

    def save_completed(completed: set[int]):
        app.storage.user["reading_plan_completed"] = sorted(completed)

    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-4'):
        ui.label(f"📅 {get_translation('Bible Reading Plan')}").classes('text-2xl font-serif text-secondary font-bold')

        # Progress Summary Card
        progress_card = ui.column().classes('w-full p-3 rounded-lg border border-gray-200 gap-2')
        # Navigation Row
        nav_row = ui.row().classes('w-full items-center justify-between gap-2 flex-wrap')
        # Day Content
        day_container = ui.column().classes('w-full gap-3')
        # 365-Day Overview
        overview_container = ui.column().classes('w-full gap-2')

        def render_progress():
            progress_card.clear()
            completed = get_completed()
            done_count = len(completed)
            pct = round(done_count / 365 * 100, 1)
            streak = _compute_streak(completed, today_num)
            with progress_card:
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(f"{done_count} / 365 {get_translation('days')} ({pct}%)").classes('font-semibold text-sm')
                    ui.badge(f"🔥 {get_translation('Streak')}: {streak} {get_translation('days')}", color='orange' if streak > 0 else 'grey')
                ui.linear_progress(value=done_count / 365, show_value=False).props('rounded size=10px color=primary')

        def set_day(new_day: int):
            state["day"] = min(365, max(1, int(new_day)))
            if day_select.value != state["day"]:
                day_select.value = state["day"]
            render_day()

        def jump_next_unread():
            completed = get_completed()
            for d in range(1, 366):
                if d not in completed:
                    set_day(d)
                    return
            ui.notify(get_translation('All 365 days completed!'), type='positive')

        with nav_row:
            with ui.row().classes('items-center gap-1'):
                ui.button(icon='chevron_left', on_click=lambda: set_day(state["day"] - 1)).props('outline dense').tooltip(get_translation('Previous Day'))
                day_select = ui.select(
                    options={d: f"{get_translation('Day')} {d}" for d in range(1, 366)},
                    value=state["day"],
                    on_change=lambda e: set_day(e.value) if e.value != state["day"] else None,
                ).props('dense outlined').classes('w-32')
                ui.button(icon='chevron_right', on_click=lambda: set_day(state["day"] + 1)).props('outline dense').tooltip(get_translation('Next Day'))
            with ui.row().classes('items-center gap-2'):
                ui.button(get_translation('Today'), icon='today', on_click=lambda: set_day(today_num)).props('outline size=sm')
                ui.button(get_translation('Next Unread'), icon='fast_forward', on_click=jump_next_unread).props('outline size=sm color=secondary')

        def render_day():
            day_container.clear()
            day = state["day"]
            ui_lang = app.storage.user.get("ui_language", "eng")
            passages = parse_day_passages(day, ui_lang)
            completed = get_completed()
            is_done = day in completed

            def toggle_day_complete(e):
                cur = get_completed()
                if e.value:
                    cur.add(day)
                else:
                    cur.discard(day)
                save_completed(cur)
                render_progress()
                if overview_expansion.value:
                    render_overview()

            def open_passage(b, c, v):
                if gui:
                    gui.change_area_1_bible_chapter(None, b, c, v)

            def open_all_in_verses():
                if not gui or not passages:
                    return
                app.storage.user["tool_query"] = "; ".join(p["ref"] for p in passages)
                gui.select_next_area2_tab()
                gui.load_area_2_content(title='Verses')

            with day_container:
                with ui.row().classes('w-full items-center justify-between flex-wrap gap-2'):
                    ui.label(f"{get_translation('Day')} {day}").classes('text-xl font-bold')
                    ui.checkbox(
                        get_translation('Mark Day Complete'),
                        value=is_done,
                        on_change=toggle_day_complete,
                    ).classes('font-semibold')

                with ui.column().classes('w-full gap-2'):
                    for p in passages:
                        with ui.row().classes('w-full items-center justify-between p-3 rounded-lg border border-gray-200 shadow-sm'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('menu_book', color='primary')
                                ui.label(p["ref"]).classes('text-base font-medium')
                            ui.button(
                                get_translation('Read'),
                                icon='open_in_new',
                                on_click=partial(open_passage, p["b"], p["c"], p["v"]),
                            ).props('outline size=sm color=primary')

                with ui.row().classes('w-full justify-end mt-1'):
                    ui.button(
                        get_translation('Read All in Verses'),
                        icon='auto_stories',
                        on_click=open_all_in_verses,
                    ).props('outline color=secondary')

        def render_overview():
            overview_container.clear()
            completed = get_completed()
            with overview_container:
                with ui.row().classes('w-full gap-1 flex-wrap'):
                    for d in range(1, 366):
                        if d == state["day"]:
                            btn_props = 'dense size=xs color=primary'
                        elif d in completed:
                            btn_props = 'dense size=xs color=positive'
                        else:
                            btn_props = 'outline dense size=xs color=grey'
                        ui.button(str(d), on_click=partial(set_day, d)).props(btn_props).classes('w-9')
                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button(
                        get_translation('Reset Progress'),
                        icon='restart_alt',
                        on_click=lambda: (
                            save_completed(set()),
                            render_progress(),
                            render_day(),
                            render_overview(),
                            ui.notify(get_translation('Progress reset'), type='info'),
                        ),
                    ).props('flat size=sm color=negative')

        with ui.expansion(
            get_translation('365-Day Overview'),
            icon='grid_view',
            value=False,
            on_value_change=lambda e: render_overview() if e.value else None,
        ).classes('w-full rounded-lg border border-gray-200') as overview_expansion:
            overview_container = ui.column().classes('w-full p-2 gap-2')

        render_progress()
        render_day()
