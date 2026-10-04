"""
Módulo para extração de áudio e transcrição com Faster-Whisper.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from core.ffmpeg_setup import run_ffmpeg


def extract_audio(video_path: str, output_wav_path: str) -> str:
    """
    Extrai o áudio do arquivo de vídeo e converte em WAV mono 16kHz.
    Formato ideal para transcrição no Whisper.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)

    # -vn: sem vídeo
    # -acodec pcm_s16le: PCM 16-bit
    # -ar 16000: taxa de amostragem 16000 Hz
    # -ac 1: 1 canal (mono)
    # -y: sobrescrever se existir
    args = [
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_wav_path
    ]

    res = run_ffmpeg(args, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Erro ao extrair áudio com FFmpeg:\n{res.stderr}")

    return output_wav_path


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: str = "en",
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> List[Dict[str, Any]]:
    """
    Transcreve um arquivo de áudio utilizando Faster-Whisper.
    Retorna uma lista de segmentos com start, end e text.
    """
    from faster_whisper import WhisperModel

    if progress_callback:
        progress_callback("Carregando modelo de transcrição Whisper...", 0.1)

    # Configuração para CPU com quantização int8 para alta velocidade
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    if progress_callback:
        progress_callback("Transcrevendo falas em inglês...", 0.3)

    segments_generator, info = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
        beam_size=5,
        word_timestamps=False,
        vad_filter=True  # Filtra silêncios para evitar alucinações
    )

    total_duration = info.duration if info and info.duration > 0 else 1.0
    segments = []

    for seg in segments_generator:
        text = seg.text.strip()
        if not text:
            continue

        segments.append({
            "id": len(segments) + 1,
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": text
        })

        if progress_callback:
            progress = min(0.9, 0.3 + (seg.end / total_duration) * 0.6)
            progress_callback(f"Transcrevendo: {seg.end:.1f}s / {total_duration:.1f}s", progress)

    if progress_callback:
        progress_callback("Transcrição concluída com sucesso!", 1.0)

    return segments
