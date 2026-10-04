"""
Utilitário para detecção e configuração do executável FFmpeg.
Garante que o FFmpeg funcione mesmo sem instalação prévia no sistema,
utilizando o binário fornecido por imageio-ffmpeg se necessário.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_ffmpeg_path() -> str:
    """
    Retorna o caminho absoluto para o executável do FFmpeg.
    Verifica PATH, venv/bin, imageio-ffmpeg e diretórios locais.
    """
    # 1. Verificar no venv/bin
    venv_bin = Path(sys.prefix) / "bin" / "ffmpeg"
    if venv_bin.exists() and os.access(venv_bin, os.X_OK):
        return str(venv_bin)

    # 2. Verificar no PATH do sistema
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    # 3. Verificar via imageio-ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_bin and os.path.exists(ffmpeg_bin):
            return ffmpeg_bin
    except ImportError:
        pass

    # 4. Fallback local na pasta do projeto
    local_bin = Path(__file__).resolve().parent.parent / "bin" / "ffmpeg"
    if local_bin.exists() and os.access(local_bin, os.X_OK):
        return str(local_bin)

    raise RuntimeError(
        "FFmpeg não foi encontrado no sistema nem através do imageio-ffmpeg. "
        "Instale o FFmpeg ou execute 'pip install imageio-ffmpeg'."
    )


def configure_environment():
    """Garante que o binário do FFmpeg esteja no PATH do processo e configura pydub."""
    try:
        ffmpeg_exe = get_ffmpeg_path()
        ffmpeg_dir = str(Path(ffmpeg_exe).parent)
        current_path = os.environ.get("PATH", "")
        if ffmpeg_dir not in current_path.split(os.pathsep):
            os.environ["PATH"] = f"{ffmpeg_dir}{os.pathsep}{current_path}"

        from pydub import AudioSegment
        AudioSegment.converter = ffmpeg_exe
    except Exception:
        pass


def run_ffmpeg(args: list, check: bool = True) -> subprocess.CompletedProcess:
    """Executa um comando FFmpeg com o executável detectado."""
    ffmpeg_exe = get_ffmpeg_path()
    cmd = [ffmpeg_exe] + args
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)


# Configuração automática na inicialização
configure_environment()


if __name__ == "__main__":
    try:
        path = get_ffmpeg_path()
        print(f"FFmpeg detectado com sucesso: {path}")
        res = run_ffmpeg(["-version"], check=True)
        print("Versão:", res.stdout.splitlines()[0])
    except Exception as e:
        print("Erro ao verificar FFmpeg:", e)
