# BibleMate AI GUI

BibleMate AI Web Application - Web GUI

BibleMate AI Web Version is designed to combine the most valuable features from the following two projects into a single, unified web interface:

https://github.com/eliranwong/biblemate

and

https://github.com/eliranwong/UniqueBible

# Supported Platforms

1. Web Mode to run on popular web browsers

2. Desktop Mode on Windows/macOS/Linux

# Development in Progress ...

Install for testing:

> pip install --upgrade biblemategui

Run:

> biblemategui

Open:

http://localhost:33355

## Coutomization

Server Side:

Save changes of `avatar`, `port` and `storage_secret` key in ~/biblemate/biblemategui.config, then restart `biblemategui`.

User Preferences:

http://localhost:33355/settings

## Storage Secret Key

A Storage Secret Key is necessary for deployment.

You generate a random key by running `openssl rand -hex 32` or `openssl rand -base64 32`

## Recent Updates

[Cross-Highlighting & Synchronized Scrolling](https://youtu.be/TDyT1ioesmY)

[![Watch the video](https://img.youtube.com/vi/TDyT1ioesmY/maxresdefault.jpg)](https://youtu.be/TDyT1ioesmY)

[UI Overview](https://youtu.be/UL8b1O97560)

[![Watch the video](https://img.youtube.com/vi/UL8b1O97560/maxresdefault.jpg)](https://youtu.be/UL8b1O97560)

## Use Existing UniqueBible App Data

Run the following command first before the first launch of `biblemategui`

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

## Server Setup

Please read https://nicegui.io/documentation/section_configuration_deployment#server_hosting