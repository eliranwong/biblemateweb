# Install Ollama

To enable semantic search for BibleMateWeb, we need to install Ollama server and download the embedding model `paraphrase-multilingual`.

Launch Ubuntu first:

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