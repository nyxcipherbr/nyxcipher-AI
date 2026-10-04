"""
Módulo para mixagem final de vídeo, áudio dublado e legendas.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Callable
from core.ffmpeg_setup import run_ffmpeg, configure_environment

configure_environment()


def get_video_duration(video_path: str) -> float:
    """Obtém a duração total do vídeo em segundos usando ffprobe ou ffmpeg."""
    from pydub.utils import mediainfo
    try:
        info = mediainfo(video_path)
        if "duration" in info and float(info["duration"]) > 0:
            return float(info["duration"])
    except Exception:
        pass

    # Fallback via comando FFmpeg
    try:
        res = run_ffmpeg(["-i", video_path], check=False)
        for line in res.stderr.splitlines():
            if "Duration:" in line:
                # Exemplo: Duration: 00:01:23.45, start: ...
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        pass

    return 60.0  # fallback seguro


def mix_video_and_audio(
    video_path: str,
    dubbed_audio_path: Optional[str],
    output_video_path: str,
    original_audio_volume: float = 0.0,
    srt_subtitles_path: Optional[str] = None,
    burn_in_subtitles: bool = True,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> str:
    """
    Combina o vídeo com a nova faixa de áudio e/ou legendas.
    - original_audio_volume: 0.0 (mudo para o áudio original em inglês) ou > 0.0 (ex: 0.15 para voz de fundo).
    - srt_subtitles_path: se informado, inclui as legendas.
    - burn_in_subtitles: se True, queima as legendas na imagem; se False, embute no MP4.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo de entrada não encontrado: {video_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)

    if progress_callback:
        progress_callback("Iniciando renderização do vídeo final...", 0.1)

    args = ["-y", "-i", video_path]

    # Se há áudio dublado
    has_dubbed_audio = dubbed_audio_path and os.path.exists(dubbed_audio_path)
    if has_dubbed_audio:
        args.extend(["-i", dubbed_audio_path])

    # Configuração de vídeo e filtros
    video_filters = []
    if srt_subtitles_path and os.path.exists(srt_subtitles_path) and burn_in_subtitles:
        escaped_srt = os.path.abspath(srt_subtitles_path).replace(":", "\\:").replace("'", "\\'")
        video_filters.append(
            f"subtitles='{escaped_srt}':force_style='FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,MarginV=25'"
        )

    # Decidir codecs e filtros
    if video_filters:
        # Se queimar legenda, precisa recodificar o vídeo com libx264
        args.extend(["-vf", ",".join(video_filters), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22"])
    else:
        # Sem queimar legenda, pode copiar o fluxo de vídeo diretamente (ultra rápido e sem perda)
        args.extend(["-c:v", "copy"])

    # Configuração de áudio
    if has_dubbed_audio:
        if original_audio_volume > 0.0:
            # Mixagem do áudio original atenuado + áudio dublado
            filter_complex = (
                f"[0:a]volume={original_audio_volume:.2f}[a0];"
                f"[1:a]volume=1.0[a1];"
                f"[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            args.extend([
                "-filter_complex", filter_complex,
                "-map", "0:v:0",
                "-map", "[aout]",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest"
            ])
        else:
            # Substituição total: somente o áudio dublado
            args.extend([
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest"
            ])
    else:
        # Mantém o áudio original
        args.extend(["-c:a", "copy"])

    # Se legendas forem adicionadas como softsub (sem burn-in)
    if srt_subtitles_path and os.path.exists(srt_subtitles_path) and not burn_in_subtitles:
        args.extend([
            "-i", srt_subtitles_path,
            "-c:s", "mov_text",
            "-metadata:s:s:0", "language=por"
        ])

    args.append(output_video_path)

    if progress_callback:
        progress_callback("Processando e exportando o vídeo com FFmpeg...", 0.5)

    res = run_ffmpeg(args, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Erro na renderização final com FFmpeg:\n{res.stderr}")

    if progress_callback:
        progress_callback("Vídeo final gerado com sucesso!", 1.0)

    return output_video_path
