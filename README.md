# BibleMate AI GUI

BibleMate AI Web Application - Web GUI & Http Server & API Server

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

> pip install --upgrade biblemateweb

One-off Data Setup:

> biblematedata

Run:

> biblemateweb

Open:

http://localhost:33355

## Setup Bible Notes Sync with Google Accounts

This feature has already been implemented at https://biblemate.gospelchurch.uk

Setup notes will be added here soon ...

## Customization

Server Side:

Save changes of `avatar`, `port` and `storage_secret` key in ~/biblemate/biblemateweb.config, then restart `biblemateweb`.

User Preferences:

http://localhost:33355/settings

## Storage Secret Key

A Storage Secret Key is necessary for deployment.

You may generate a random key by running `openssl rand -hex 32` or `openssl rand -base64 32`

Save it as the value of `config.storage_secret` in ~/biblemate/biblemateweb.config, then restart `biblemateweb`.

## Public Deployment

Please read additional notes at https://nicegui.io/documentation/section_configuration_deployment#server_hosting

