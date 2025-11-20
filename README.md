# BibleMate AI GUI

BibleMate AI Web Application - Web GUI

BibleMate AI Web Version is designed to combine the most valuable features from the following two projects into a single, unified web interface:

https://github.com/eliranwong/biblemate

and

https://github.com/eliranwong/UniqueBible

## Recent Updates

[Hebrew & Greek Tooltips](https://youtu.be/qCMku8-UZ3I)

[![Watch the video](https://img.youtube.com/vi/qCMku8-UZ3I/maxresdefault.jpg)](https://youtu.be/qCMku8-UZ3I)

[User Customization](https://youtu.be/QMJ2oo1qkjY)

[![Watch the video](https://img.youtube.com/vi/QMJ2oo1qkjY/maxresdefault.jpg)](https://youtu.be/QMJ2oo1qkjY)

[Bible Audio](https://youtu.be/GL98FaJlYUQ)

[![Watch the video](https://img.youtube.com/vi/GL98FaJlYUQ/maxresdefault.jpg)](https://youtu.be/GL98FaJlYUQ)

[Cross-Highlighting & Synchronized Scrolling](https://youtu.be/TDyT1ioesmY)

[![Watch the video](https://img.youtube.com/vi/TDyT1ioesmY/maxresdefault.jpg)](https://youtu.be/TDyT1ioesmY)

[UI Overview](https://youtu.be/UL8b1O97560)

[![Watch the video](https://img.youtube.com/vi/UL8b1O97560/maxresdefault.jpg)](https://youtu.be/UL8b1O97560)

# Supported Platforms

1. Web Mode to run on popular web browsers

2. Desktop Mode on Windows/macOS/Linux

# Development in Progress ...

## Public Testing

https://biblemate.gospelchurch.uk

## Local Testing:

> pip install --upgrade biblemategui

Run:

> biblemategui

Open:

http://localhost:33355

## Customization

Server Side:

Save changes of `avatar`, `port` and `storage_secret` key in ~/biblemate/biblemategui.config, then restart `biblemategui`.

User Preferences:

http://localhost:33355/settings

## Storage Secret Key

A Storage Secret Key is necessary for deployment.

You may generate a random key by running `openssl rand -hex 32` or `openssl rand -base64 32`

Save it as the value of `config.storage_secret` in ~/biblemate/biblemategui.config, then restart `biblemategui`.

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

## Supported Parameters with URL


* t: str | None = None, # Token for using custom data: allow users to pass a custom token, which won't be stored, via a parameter when using public devices. For personal devices, enable persistent settings using `custom_token`.
* k: bool | None = True, # keep valid specified parameters in history
* m: bool | None = True, # display menu
* l: int | None = None, # layout; either: 1 (bible area only) or 2 (bible & tool areas) or 3 (tool area only)
* bbt: str | None = None, # bible bible text
* bb: int | None = None, # bible book
* bc: int | None = None, # bible chapter
* bv: int | None = None, # bible verse
* tbt: str | None = None, # tool bible text
* tb: int | None = None, # tool book
* tc: int | None = None, # tool chapter
* tv: int | None = None, # tool verse
* tool: str | None = None, # supported options: bible, ...