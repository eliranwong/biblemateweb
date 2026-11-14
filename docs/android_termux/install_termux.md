# Install Termux on Android

# Do NOT use Play Store to Install Termux

The following instructions install the offical `termux` package downloaded from github repository.

# FIRST, Give Permission to Chrome App

We will describe how to install the Termux apk file via Chrome app, but first you need to enable your Chrome app to install unknown app.

1. Go to `Settings` > `Apps` > `Special app access` > `Install unknown apps`

2. Select Chrome

3. Enable "Allow from this source"

<b>Remarks:</b> You may disable this feature after you install Termux app.

# Install Termux App

1. Launch Chrome on your Android device.

2. Go to official Termux GitHub release page: https://github.com/termux/termux-app/releases

3. Download the "universal" version from the list under "Assets"

4. After the file is downloaded, select it from Chrome download list

5. Select "Install"

Extra step for Android 14+ users, read https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md#commands-for-android-14-and-higher

# Install Repositories

Launch Termux and run,

> pkg install root-repo

> pkg install x11-repo

# Update and Upgrade

> pkg upgrade

# Termux:API & termux-api

Termux:API app and termux-api package are two different elements that needed to be installed separately.

1. Download and install a `*.apk` file from https://github.com/termux/termux-api/releases

2. Run in termux:

> pkg install termux-api

Read more at https://wiki.termux.com/wiki/Termux:API

# Storage Setup

Go to `Settings` > `Apps` > `Termux` > `Permissions` > `Files` > `Allow`

> termux-setup-storage

Locate the shared storage in `$HOME/storage`

Read more at https://wiki.termux.com/wiki/Sharing_Data

# Set up `biblemate` directory

1. With your Android phone `Files` app, create a folder `bilbemate` in `Documents`.

2. Launch the `Termux` app and run:

```
cd ~
ln -s storage/shared/Documents/biblemate biblemate
```
