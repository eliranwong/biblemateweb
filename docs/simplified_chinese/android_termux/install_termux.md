# 在 Android 上安装 Termux

# 请勿使用 Play Store 安装 Termux

以下说明将安装从 GitHub 仓库下载的官方 `termux` 安装包。

# 首先，授予 Chrome 应用程序权限

我们将说明如何通过 Chrome 应用程序安装 Termux APK 文件，但首先您需要允许 Chrome 应用程序安装未知应用。

1. 前往“`设定`”>“`应用`”>“`特殊应用权限`”>“`安装未知应用`”

2. 选择 Chrome

3. 开启“允许来自此来源”

<b>备注：</b>安装 Termux 应用程序后，您可以禁用此功能。

# 安装 Termux 应用程序

1. 在您的 Android 设备上启动 Chrome。

2. 前往官方 Termux GitHub 发布页面：https://github.com/termux/termux-app/releases

3. 从“Assets”下方的列表中下载“universal”版本

4. 文件下载完成后，从 Chrome 下载列表中选择该文件

5. 选择“安装”

Android 14+ 用户的额外步骤，请参阅 https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md#commands-for-android-14-and-higher

# 安装软件源

启动 Termux 并运行：

> pkg install root-repo

> pkg install x11-repo

# 更新与升级

> pkg upgrade

# Termux:API 与 termux-api

Termux:API 应用程序与 termux-api 软件包是两个不同的组件，需要分别安装。

1. 从 https://github.com/termux/termux-api/releases 下载并安装 `*.apk` 文件

2. 在 Termux 中运行：

> pkg install termux-api

欲了解更多信息，请参阅 https://wiki.termux.com/wiki/Termux:API

# 存储空间设定

前往“`设定`”>“`应用`”>“`Termux`”>“`权限`”>“`文件`”>“`允许`”

> termux-setup-storage

共享存储空间位于 `$HOME/storage`

欲了解更多信息，请参阅 https://wiki.termux.com/wiki/Sharing_Data

# 设定 `biblemate` 目录

1. 使用 Android 手机的 `Files`（文件）应用程序，在 `Documents` 中创建 `biblemate` 文件夹。

2. 启动 `Termux` 应用程序并运行：

```
cd ~
ln -s storage/shared/Documents/biblemate biblemate
```
