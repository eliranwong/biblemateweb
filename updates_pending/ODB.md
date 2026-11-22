Also, along similiar line, dynamically load translation in ODB.

In O.T., delete between `</vid> ` and `<div class='bhsa'>` and replace with placeholder, e.g.:

from

</vid> <u><b>The Creation of the World</b></u><br><br>In the beginning God created the heavens and the earth.<div class='bhsa'>

to

</vid> <trans></trans><div class='bhsa'>

In N.T., delete between `</vid> ` and `<div class='e'>` and replace with placeholder:

from

<verse><vid id="v40.1.1" onclick="luV(1)">1</vid> <u><b>The Genealogy of Jesus Christ</b></u><br><br>This is the record of the genealogy of Jesus Christ, the son of David, the son of Abraham.<div class='e'>

to

</vid> <trans></trans><div class='e'>

In Settings / Preferences, add dropdown options from available bible versions.

ODB OT Translation: default - KJV
ODB NT Translation: default - KJV


Also, work out the bidirectional highlighting and translation word tooltip.