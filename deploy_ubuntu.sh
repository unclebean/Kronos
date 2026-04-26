#!/bin/bash

# ==============================================================================
# Kronos Deployment Script for Ubuntu
# Description: Installs dependencies, sets up a virtual environment, and starts the Web UI
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting Kronos Deployment Pipeline..."

# 1. Update system logs and install system dependencies
echo "📦 Installing system dependencies (Python3, pip, venv)..."
sudo apt-get update -y || true
sudo apt-get install -y python3 python3-pip python3-venv git tmux

# 2. Setup working directory
# We assume the user has already cloned/copied the repo and is running the script from inside it.
PROJECT_DIR=$(pwd)
echo "📂 Working directory: $PROJECT_DIR"

# 3. Setup Python Virtual Environment
VENV_DIR="$PROJECT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists."
fi

# 4. Activate Virtual Environment
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 5. Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# 6. Install Python Dependencies
echo "📥 Installing dependencies from requirements.txt..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt"
else
    echo "⚠️ requirements.txt not found! Skipping..."
fi

# 7. Install WebUI specific packages (if they aren't fully covered in requirements.txt)
echo "📥 Installing WebUI dependencies (Flask, CORS, Plotly)..."
pip install flask flask-cors plotly

# 8. Start the Application
echo "🌐 Starting Kronos Web UI..."

# The frontend defaults to port 7070 in webui/app.py.
# We will use tmux to run it in the background so it doesn't die when you close SSH.
SESSION_NAME="kronos-webui"

# Check if session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "🛑 Stopping existing application session..."
    tmux kill-session -t $SESSION_NAME
fi

echo "▶️ Launching application in a background tmux session..."
tmux new-session -d -s $SESSION_NAME "source '$VENV_DIR/bin/activate' && python3 '$PROJECT_DIR/webui/app.py'"

echo ""
echo "================================================================"
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "================================================================"
echo "The Kronos Web UI is now running in the background."
echo "You can access it at: http://<your-server-ip>:7070"
echo ""
echo "To view the live application logs, run the following command:"
echo "    tmux attach-session -t $SESSION_NAME"
echo ""
echo "To detach from the logs (leave it running), press: Ctrl+B, then D"
echo "================================================================"
