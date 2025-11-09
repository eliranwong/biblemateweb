from nicegui import ui

def luV(event):
    b, c, v = event.args
    ui.notify(f"b: {b}, c: {c}, v: {v}")
    
    # Create a context menu at the click position
    with ui.context_menu() as menu:
        ui.menu_item('Bible Commentaries', on_click=lambda: ui.navigate.to('/tool/commentary'))
        ui.menu_item('Cross-references', on_click=lambda: ui.navigate.to('/tool/xref'))
        ui.menu_item('Treasury of Scripture Knowledge', on_click=lambda: ui.navigate.to('/tool/tske'))
        ui.menu_item('Discourse Analysis', on_click=lambda: ui.navigate.to('/tool/discourse'))
        ui.menu_item('Morphological Data', on_click=lambda: ui.navigate.to('/tool/morphology'))
        ui.menu_item('Translation Spectrum', on_click=lambda: ui.navigate.to('/tool/translations'))
    menu.open()
def luW(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")
def lex(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")
def bdbid(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")
def etcbcmorph(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")
def rmac(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")
def searchWord(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")
def searchLexicalEntry(event):
    # whatever we sent from the browser is available as event.args
    payload = event.args
    print(type(payload))
    print('Server received payload:', payload)
    ui.notify(f"Server got: {payload}")