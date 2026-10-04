"""
Módulo Nyx Music: Transcrição e Tradução de Músicas, Podcasts e Áudios com Letras Sincronizadas.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from core.ffmpeg_setup import run_ffmpeg, configure_environment
from core.transcriber import transcribe_audio
from core.translator import translate_segments

configure_environment()


def convert_audio_to_wav(input_audio_path: str, output_wav_path: str) -> str:
    """Converte qualquer formato de áudio (MP3, M4A, OGG, etc.) para WAV 16kHz."""
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    args = [
        "-y",
        "-i", input_audio_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_wav_path
    ]
    res = run_ffmpeg(args, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Erro ao converter áudio com FFmpeg:\n{res.stderr}")
    return output_wav_path


def format_lrc_timestamp(seconds: float) -> str:
    """Converte segundos para o formato padrão de letra sincronizada LRC: [mm:ss.xx]"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    hundredths = int((seconds - int(seconds)) * 100)
    return f"[{mins:02d}:{secs:02d}.{hundredths:02d}]"


def generate_bilingual_lyrics(
    audio_path: str,
    whisper_model: str = "base",
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    Transcreve a música ou áudio em inglês e gera a letra traduzida sincronizada.
    """
    temp_wav = os.path.splitext(audio_path)[0] + "_processed.wav"

    try:
        if progress_callback:
            progress_callback("Convertendo áudio da música...", 0.1)

        convert_audio_to_wav(audio_path, temp_wav)

        def trans_cb(m, p):
            if progress_callback:
                progress_callback(m, 0.1 + (0.5 * p))

        # Transcrição lírica com Whisper
        segments = transcribe_audio(
            audio_path=temp_wav,
            model_size=whisper_model,
            language="en",
            progress_callback=trans_cb
        )

        def transl_cb(m, p):
            if progress_callback:
                progress_callback(m, 0.6 + (0.35 * p))

        # Tradução verso a verso
        translated = translate_segments(
            segments=segments,
            source_lang="en",
            target_lang="pt",
            progress_callback=transl_cb
        )

        # Montagem do arquivo de letra bilíngue (.lrc e .txt)
        lrc_lines = []
        bilingual_text_lines = []

        for seg in translated:
            time_tag = format_lrc_timestamp(seg["start"])
            en_verse = seg.get("text", "")
            pt_verse = seg.get("translated_text", "")

            # Formato LRC bilíngue
            lrc_lines.append(f"{time_tag} {en_verse} | {pt_verse}")

            # Formato de estudo bilíngue
            bilingual_text_lines.append(f"{time_tag}\nEN: {en_verse}\nPT: {pt_verse}\n")

        if progress_callback:
            progress_callback("Letra sincronizada concluída com sucesso!", 1.0)

        return {
            "segments": translated,
            "lrc_content": "\n".join(lrc_lines),
            "bilingual_lyrics": "\n".join(bilingual_text_lines),
            "total_verses": len(translated)
        }

    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass
