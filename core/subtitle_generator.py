"""
Módulo para geração e gravação de legendas (SRT / VTT).
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from core.ffmpeg_setup import run_ffmpeg


def format_timestamp_srt(seconds: float) -> str:
    """Converte segundos em formato de timestamp SRT: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Converte segundos em formato WebVTT: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def create_srt_content(segments: List[Dict[str, Any]], use_translated: bool = True) -> str:
    """Gera o texto no padrão SRT a partir dos segmentos."""
    entries = []
    text_key = "translated_text" if use_translated else "text"

    for i, seg in enumerate(segments, start=1):
        start_str = format_timestamp_srt(seg["start"])
        end_str = format_timestamp_srt(seg["end"])
        text = seg.get(text_key, seg.get("text", "")).strip()

        entries.append(f"{i}\n{start_str} --> {end_str}\n{text}\n")

    return "\n".join(entries)


def save_srt_file(segments: List[Dict[str, Any]], output_path: str, use_translated: bool = True) -> str:
    """Salva a lista de segmentos em um arquivo .srt UTF-8."""
    content = create_srt_content(segments, use_translated=use_translated)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


def embed_subtitles(
    video_path: str,
    srt_path: str,
    output_video_path: str,
    burn_in: bool = True
) -> str:
    """
    Grava a legenda no vídeo.
    Se burn_in=True: grava a legenda diretamente na imagem (hardsub), compatível com qualquer reprodutor.
    Se burn_in=False: embute a faixa de legenda no contêiner MP4 (softsub).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo de entrada não encontrado: {video_path}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Arquivo SRT não encontrado: {srt_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)

    if burn_in:
        # Para queimar legenda no Linux, usamos o filtro subtitles
        # O caminho precisa ter caracteres especiais escapados
        escaped_srt = os.path.abspath(srt_path).replace(":", "\\:").replace("'", "\\'")
        args = [
            "-y",
            "-i", video_path,
            "-vf", f"subtitles='{escaped_srt}':force_style='FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,MarginV=25'",
            "-c:a", "copy",
            output_video_path
        ]
    else:
        # Softsub: adiciona como stream de legenda
        args = [
            "-y",
            "-i", video_path,
            "-i", srt_path,
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-metadata:s:s:0", "language=por",
            output_video_path
        ]

    res = run_ffmpeg(args, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Erro ao embutir legendas com FFmpeg:\n{res.stderr}")

    return output_video_path
