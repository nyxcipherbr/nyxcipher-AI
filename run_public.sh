#!/usr/bin/env bash
# ==============================================================================
# VideoTranslator-PT: Iniciar Aplicativo com Link Público (Cloudflare Tunnel)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT=8510
BIN_DIR="$SCRIPT_DIR/bin"
CLOUDFLARED="$BIN_DIR/cloudflared"

# 1. Iniciar o Streamlit em segundo plano se ainda não estiver rodando
if ! ss -tulpn | grep -q ":$PORT "; then
    echo "Iniciando servidor Streamlit..."
    source "$SCRIPT_DIR/venv/bin/activate"
    nohup streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false > /tmp/streamlit_vt.log 2>&1 &
    sleep 3
fi

# 2. Iniciar o Cloudflare Tunnel
echo "Criando link público seguro..."
exec "$CLOUDFLARED" tunnel --url "http://127.0.0.1:$PORT"
