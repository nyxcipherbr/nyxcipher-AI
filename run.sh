#!/usr/bin/env bash
# ==============================================================================
# VideoTranslator-PT: Script de Inicialização
# Tradução e Dublagem de Vídeos (Inglês -> Português)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "          🎬 Iniciando VideoTranslator-PT (Streamlit)            "
echo "=================================================================="

VENV_DIR="$SCRIPT_DIR/venv"

# 1. Verificar / Criar ambiente virtual se necessário
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/3] Criando ambiente virtual Python..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Ativar venv e checar dependências
echo "[2/3] Verificando dependências..."
source "$VENV_DIR/bin/activate"

# Garantir FFmpeg e FFprobe
python3 -c "
import static_ffmpeg
static_ffmpeg.add_paths()
" || true

# 3. Iniciar a interface Web Streamlit
PORT=${1:-8510}
echo "[3/3] Iniciando servidor web Streamlit na porta $PORT..."
echo ""
echo "👉 Acesse no seu navegador: http://localhost:$PORT"
echo ""

exec streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
