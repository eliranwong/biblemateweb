# BibleMate AI WEB

This repository focuses only on the Web UI, HTTP and API servers of a larger project, [BibleMate AI](https://github.com/eliranwong/biblemate).

For CLI Version / MCP Server / Agent Mode / Partner Mode / Bible Data, read https://github.com/eliranwong/biblemate

---

BibleMate AI Web Application - Web GUI & Http Server & API Server

BibleMate AI Web Version is designed to combine the most valuable features from the following two projects into a single, unified web interface:

https://github.com/eliranwong/biblemate

and

https://github.com/eliranwong/UniqueBible

## Latest New - Agent Mode on the BibleMate Web Version

We are pleased to announce that Agent Mode is now fully integrated across both the BibleMate Web and CLI platforms, providing a unified experience for all users.

### Additional Options for Agent Mode Setup

Agent Mode consumes more tokens than standard mode. Consider restricting public access to manage costs.

Configuration options `disable_agent_mode` and `limit_agent_mode_once_daily` are designed to limit access to Agent Mode.

To disable public access to agent mode, set:

> config.disable_agent_mode=True

To daily limit access to agent mode, set:

> config.limit_agent_mode_once_daily=True

Users can still use the Agent Mode by entering a custom token or their own API keys in `Preferences`, even either of the two options above are set to `True`.

Note: Setting a daily limit requires [Google Account authentication](https://github.com/eliranwong/biblemateweb/blob/main/docs/google_drive_notes_setup.md), as users' access settings are stored directly in users' own Google Drive. BibleMate AI is designed for privacy; our servers do not store any user data.

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

* Web UI runs with all popular web browsers
* Http & API Servers runs on any standard platforms
* API Data Access independent of running platforms

# Public Demo

https://biblemate.gospelchurch.uk

# Local Setup

> pip install --upgrade biblemateweb

One-off Data Setup:

> biblematedata

Run HTTP & API Servers:

> biblemateweb

Open Web UI:

> open http://localhost:33355

## API Usage

Run API Client:

> biblemateapi -h

Read more at:

https://github.com/eliranwong/biblemateweb/blob/main/tests/api_client.py

https://github.com/eliranwong/biblemateweb/blob/main/docs/api_query.md

## Setup Bible Notes Sync with Google Accounts

The BibleMate web UI allows users to create and store personal study notes for any book, chapter, or verse directly in Google Drive. This integration ensures that all notes stay synced across devices, making them easily accessible whenever and wherever you need them.

For demo, check out https://biblemate.gospelchurch.uk

Read setup notes at https://github.com/eliranwong/biblemateweb/blob/main/docs/google_drive_notes_setup.md

## Support Exported Agent Mode Report in Word Document Format

`pandoc` is required to export content to DOCX format.

To install, for example, on Debian/Ubuntu:

> sudo apt install pandoc

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

