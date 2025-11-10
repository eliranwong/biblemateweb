Re the BibleMate AI I am development, I have two NiceGUI scroll areas, arranged side by side, separated by a splitter, show the same bible chapter of two different bible versions. There height are different as text length are different, but they have one thing in common, each verse number is tagged with, e.g. <vid id="v63.1.7" ...>...</vid>.



I want to sync the scrolling on both side:

* when I move the left scroll area, e.g. when the verse at the visible top is id="v63.1.5", the right scoll area scoll the item with id="v63.1.5" to the top

I checked the NiceGUI official documentation, they offers an example that may be relevant:



```

from nicegui importui



with ui.row():

    with ui.card().classes('w-32 h-48'):

        with ui.scroll_area(on_scroll=lambda e: area2.scroll_to(percent=e.vertical_percentage)) as area1:

            ui.label('I scroll. ' * 20)



    with ui.card().classes('w-32 h-48'):

        with ui.scroll_area() as area2:

            ui.label('I scroll. ' * 20)



ui.run()

```



In this example, however, they scroll not detecting the changes in element id that I need.



Help me to work out a full code I need according to my specification, thanks.