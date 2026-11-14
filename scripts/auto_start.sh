## auto-start web server
start_bmweb() {
  echo "Starting BibleMate AI WEB server ..."
  nohup biblemateweb &
  echo "BibleMate AI WEB server started."
}
### Check if BibleMate WEB server is already running
if ! pgrep -f "/bin/biblemateweb" > /dev/null; then
  start_bmweb
else
  echo "BibleMate AI WEB server is already running."
fi