# 在 Android 上安裝 Termux

# 請勿使用 Play Store 安裝 Termux

以下說明將安裝從 GitHub 存放庫下載的官方 `termux` 安裝套件。

# 首先，授予 Chrome 應用程式權限

我們將說明如何透過 Chrome 應用程式安裝 Termux APK 檔案，但首先您需要允許 Chrome 應用程式安裝未知應用程式。

1. 前往「`設定`」>「`應用程式`」>「`特殊應用程式存取權`」>「`安裝未知應用程式`」

2. 選擇 Chrome

3. 開啟「允許來自此來源」

<b>備註：</b>安裝 Termux 應用程式後，您可以停用此功能。

# 安裝 Termux 應用程式

1. 在您的 Android 裝置上啟動 Chrome。

2. 前往官方 Termux GitHub 發佈頁面：https://github.com/termux/termux-app/releases

3. 從「Assets」下方的列表中下載「universal」版本

4. 檔案下載完成後，從 Chrome 下載列表中選取該檔案

5. 選擇「安裝」

Android 14+ 使用者的額外步驟，請參閱 https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md#commands-for-android-14-and-higher

# 安裝套件庫

啟動 Termux 並執行：

> pkg install root-repo

> pkg install x11-repo

# 更新與升級

> pkg upgrade

# Termux:API 與 termux-api

Termux:API 應用程式與 termux-api 套件是兩個不同的組件，需要分別安裝。

1. 從 https://github.com/termux/termux-api/releases 下載並安裝 `*.apk` 檔案

2. 在 Termux 中執行：

> pkg install termux-api

欲了解更多資訊，請參閱 https://wiki.termux.com/wiki/Termux:API

# 儲存空間設定

前往「`設定`」>「`應用程式`」>「`Termux`」>「`權限`」>「`檔案`」>「`允許`」

> termux-setup-storage

共享儲存空間位於 `$HOME/storage`

欲了解更多資訊，請參閱 https://wiki.termux.com/wiki/Sharing_Data

# 設定 `biblemate` 目錄

1. 使用 Android 手機的 `Files`（檔案）應用程式，在 `Documents` 中建立 `biblemate` 資料夾。

2. 啟動 `Termux` 應用程式並執行：

```
cd ~
ln -s storage/shared/Documents/biblemate biblemate
```
