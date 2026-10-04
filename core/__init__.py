"""
VideoTranslator-PT Core Package
"""
from core.ffmpeg_setup import get_ffmpeg_path, configure_environment

# Configurações globais ao importar o core
configure_environment()

__all__ = ["get_ffmpeg_path", "configure_environment"]
