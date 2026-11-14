# 安裝 Ollama

若要為 BibleMateWeb 啟用語義搜索，我們需要安裝 Ollama 伺服器並下載嵌入模型 `paraphrase-multilingual`。

首先啟動 Ubuntu：

```
ubuntu
```

```
# install ollama
curl -fsSL https://ollama.com/install.sh | sh
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.bashrc

## auto start ollama server
tee -a ~/.bashrc > /dev/null << 'EOF'

## ollama server
start_ollama() {
  echo "Starting Ollama server ..."
  nohup ollama serve &
}
## Check if Ollama server is already running
if ! pgrep -f "ollama serve" > /dev/null; then
  start_ollama
else
  echo "Ollama server is already running."
fi
EOF

# set up ollama
nohup ollama serve &
ollama pull paraphrase-multilingual
```
