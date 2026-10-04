"""
Módulo de dublagem: síntese de voz neural (Edge-TTS) e sincronização temporal.
"""

import os
import asyncio
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from pydub import AudioSegment
from core.ffmpeg_setup import run_ffmpeg, configure_environment

configure_environment()

AVAILABLE_VOICES = {
    "Francisca (Feminina - Natural)": "pt-BR-FranciscaNeural",
    "Antônio (Masculino - Natural)": "pt-BR-AntonioNeural",
    "Thalita (Feminina - Multilíngue)": "pt-BR-ThalitaMultilingualNeural"
}


async def _generate_single_tts(text: str, voice: str, output_path: str, rate: str = "+0%"):
    """Gera áudio para um trecho específico usando Edge-TTS."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def change_audio_speed(audio_path: str, target_duration_sec: float, output_path: str) -> str:
    """
    Ajusta a velocidade do áudio para caber na duração desejada se necessário,
    usando o filtro 'atempo' do FFmpeg para preservar o tom natural da voz.
    """
    audio = AudioSegment.from_file(audio_path)
    current_sec = len(audio) / 1000.0

    if current_sec <= 0.1 or target_duration_sec <= 0.1:
        return audio_path

    # Se o áudio couber no tempo original (com folga de 5%), não precisa acelerar
    if current_sec <= target_duration_sec * 1.05:
        return audio_path

    # Calcular fator de aceleração necessário
    speed_factor = current_sec / target_duration_sec
    # Limitar para no máximo 1.45x para não soar robótico/incompreensível
    speed_factor = min(1.45, speed_factor)

    args = [
        "-y",
        "-i", audio_path,
        "-filter:a", f"atempo={speed_factor:.2f}",
        "-vn",
        output_path
    ]
    res = run_ffmpeg(args, check=False)
    if res.returncode == 0 and os.path.exists(output_path):
        return output_path

    return audio_path


def generate_dubbed_audio(
    segments: List[Dict[str, Any]],
    total_duration_sec: float,
    output_audio_path: str,
    voice: str = "pt-BR-FranciscaNeural",
    temp_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> str:
    """
    Gera a faixa de áudio dublada completa:
    1. Sintetiza a fala para cada segmento traduzido.
    2. Ajusta o tempo da fala para caber no intervalo original.
    3. Posiciona cada trecho no timestamp exato (start time).
    4. Exporta a faixa final em formato WAV/MP3.
    """
    if not segments:
        raise ValueError("Nenhum segmento fornecido para dublagem.")

    os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)
    temp_folder = temp_dir or tempfile.mkdtemp(prefix="dub_")
    os.makedirs(temp_folder, exist_ok=True)

    # Cria uma faixa de silêncio do tamanho total do vídeo
    total_ms = int(max(total_duration_sec, segments[-1]["end"] + 1.0) * 1000)
    final_audio = AudioSegment.silent(duration=total_ms, frame_rate=24000)

    total_segments = len(segments)

    if progress_callback:
        progress_callback("Iniciando geração das vozes neurais...", 0.0)

    for i, seg in enumerate(segments):
        text = seg.get("translated_text", seg.get("text", "")).strip()
        start_ms = int(seg["start"] * 1000)
        target_dur_sec = max(0.5, seg["end"] - seg["start"])

        if not text:
            continue

        raw_tts_file = os.path.join(temp_folder, f"tts_{i}.mp3")
        adjusted_file = os.path.join(temp_folder, f"adjusted_{i}.wav")

        try:
            # Síntese com Edge-TTS
            asyncio.run(_generate_single_tts(text, voice, raw_tts_file))

            # Ajuste de velocidade se necessário
            final_segment_file = change_audio_speed(raw_tts_file, target_dur_sec, adjusted_file)

            # Carrega o áudio sintetizado e sobrepõe na linha do tempo
            seg_audio = AudioSegment.from_file(final_segment_file)
            final_audio = final_audio.overlay(seg_audio, position=start_ms)

        except Exception as e:
            print(f"Aviso: falha ao sintetizar trecho {i} ('{text}'): {e}")

        if progress_callback:
            progress = (i + 1) / total_segments
            progress_callback(f"Gerando voz para frase {i + 1} de {total_segments}...", progress)

    # Exporta a faixa de áudio dublado
    final_audio.export(output_audio_path, format="wav")

    if progress_callback:
        progress_callback("Áudio dublado gerado com sucesso!", 1.0)

    return output_audio_path
