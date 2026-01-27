#!/bin/bash
# Clarus Backend systemd service installer
# Usage: ./systemd-install.sh [backend_path] [venv_path]

set -e

# Configuration
BACKEND_PATH="${1:-$(pwd)}"
VENV_PATH="${2:-$(dirname $BACKEND_PATH)/venv}"
ENV_FILE="$BACKEND_PATH/.env"
SERVICE_NAME="clarus-backend"

echo "=== Clarus Backend Service Installer ==="
echo "Backend path: $BACKEND_PATH"
echo "Venv path: $VENV_PATH"
echo ""

# Step 1: Verify paths exist
if [ ! -d "$BACKEND_PATH" ]; then
    echo "ERROR: Backend path does not exist: $BACKEND_PATH"
    exit 1
fi
if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Venv path does not exist: $VENV_PATH"
    exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
    echo "WARNING: .env file not found at $ENV_FILE"
    echo "Service may fail to start without environment variables."
fi

# Step 2: Generate service file
echo "Generating service file..."
cat > /tmp/${SERVICE_NAME}.service << SERVICEEOF
[Unit]
Description=Clarus Backend API
After=network.target docker.service

[Service]
Type=simple
User=$(whoami)
EnvironmentFile=$ENV_FILE
WorkingDirectory=$BACKEND_PATH
ExecStart=$VENV_PATH/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 30
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Step 3: Validate service file syntax
echo "Validating service file..."
if command -v systemd-analyze &> /dev/null; then
    if ! systemd-analyze verify /tmp/${SERVICE_NAME}.service 2>/dev/null; then
        echo "WARNING: Service file validation failed (non-critical)"
    fi
fi

# Step 4: Install (requires sudo)
echo ""
echo "Installing service (requires sudo password)..."
sudo cp /tmp/${SERVICE_NAME}.service /etc/systemd/system/
sudo systemctl daemon-reload

# Step 5: Success message
echo ""
echo "=== Installation Complete ==="
echo ""
echo "To start the service:"
echo "  sudo systemctl start ${SERVICE_NAME}"
echo ""
echo "To enable on boot:"
echo "  sudo systemctl enable ${SERVICE_NAME}"
echo ""
echo "To start and enable in one command:"
echo "  sudo systemctl enable --now ${SERVICE_NAME}"
echo ""
echo "To check status:"
echo "  systemctl status ${SERVICE_NAME}"
echo ""
echo "To view logs:"
echo "  journalctl -u ${SERVICE_NAME} -f"
