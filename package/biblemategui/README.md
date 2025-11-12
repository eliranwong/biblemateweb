# BibleMate AI GUI

BibleMate AI Web Application - Web GUI

BibleMate AI Web Version is designed to combine the most valuable features from the following two projects into a single, unified web interface:

https://github.com/eliranwong/biblemate

and

https://github.com/eliranwong/UniqueBible

# Development in Progress ...

Install for testing:

> pip install --upgrade biblemategui

Run:

> biblemategui

## Recent Updates

[Cross-Highlighting & Synchronized Scrolling](https://youtu.be/TDyT1ioesmY)

[![Watch the video](https://img.youtube.com/vi/TDyT1ioesmY/maxresdefault.jpg)](https://youtu.be/TDyT1ioesmY)

[UI Overview](https://youtu.be/UL8b1O97560)

[![Watch the video](https://img.youtube.com/vi/UL8b1O97560/maxresdefault.jpg)](https://youtu.be/UL8b1O97560)

## Use Existing UniqueBible App Data

```
cd
mkdir biblemate
cd biblemate
ln -s ../UniqueBible/marvelData data
cd data
ln -s ../../UniqueBible/audio/ audio
mkdir original
cd original
ln -s ~/UniqueBible/marvelData/bibles/MOB.bible ORB.bible
ln -s ~/UniqueBible/marvelData/bibles/MIB.bible OIB.bible
ln -s ~/UniqueBible/marvelData/bibles/MPB.bible OPB.bible
ln -s ~/UniqueBible/marvelData/bibles/MTB.bible ODB.bible
ln -s ~/UniqueBible/marvelData/bibles/MAB.bible OLB.bible
```