# 安裝 Ubuntu 容器

要在 Android 上透過 Termux 運行 Ubuntu 環境且無需 Root 權限（使用 proot）：

參考資料：https://github.com/jorexdeveloper/termux-ubuntu

```
# install ubuntu
cd
pkg update && pkg upgrade && pkg install -y git wget proot curl
curl -fsSLO https://raw.githubusercontent.com/jorexdeveloper/termux-ubuntu/main/install-ubuntu.sh
bash install-ubuntu.sh -y
# tweak audio
echo 'pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1' >> ~/.bashrc
source ~/.bashrc
```

## 啟動 Ubuntu

```
ubuntu
```

## 安裝程式庫

```
# basic
cd
apt update && apt full-upgrade
apt install -y bash-completion
apt install -y python3
apt install -y python3-setuptools python3-pip python3-dev python3-venv portaudio19-dev ffmpeg wget curl git wget nano micro sqlite3 libsqlite3-dev net-tools
apt install libxcb-cursor0 pulseaudio-utils alsa-base alsa-utils mpg123 espeak

# add missing group names
groupadd -g 3003 groupname3003
groupadd -g 9997 groupname9997
groupadd -g 20298 groupname20385
groupadd -g 50298 groupname50385

# Document conversion
sudo apt install pandoc

# text editor
echo 'alias micro="micro -softwrap true -wordwrap true"' >> ~/.bashrc

# support container sound output
echo 'export PULSE_SERVER=127.0.0.1' >> ~/.bashrc

# install golang
add-apt-repository ppa:longsleep/golang-backports
apt update
apt install golang-go

# add a local path
echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc

# add a standard user; enter a password for 'me'
## a standard user is required to run Claude Code with `--dangerously-skip-permissions` flag
su - me
usermod -aG sudo me
echo "me ALL=(ALL:ALL) ALL" > /etc/sudoers.d/me
chmod 0440 /etc/sudoers.d/me
echo 'su - me' >> ~/.bashrc

# reload variables
source ~/.bashrc
```

## 設定 `biblemate` 目錄

```
cd ~
ln -s /data/data/com.termux/files/home/biblemate biblemate
```

## 退出 Ubuntu

若要退出一般使用者工作階段並返回 root 工作階段，請執行：

```
exit
```

若要結束 Ubuntu 並返回 Termux，請執行：

```
exit
```

## 常用的內建指令

輕鬆管理 Ubuntu 安裝的內建命令列參數：

在 Termux 中執行（不是在 Ubuntu 內部），例如：

```
ubuntu --backup <archive-name>

ubuntu --restore <archive-name>

ubuntu --rename <new-directory>

ubuntu --uninstall
```

## 故障排除 - 更新 man-db 時記憶體不足...

```
sudo dpkg --configure -a
sudo apt --fix-broken install
sudo apt remove man-db
```
