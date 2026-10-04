"""
Orquestrador do Pipeline de Tradução e Dublagem de Vídeos.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Callable, Optional

from core.ffmpeg_setup import configure_environment
from core.transcriber import extract_audio, transcribe_audio
from core.translator import translate_segments
from core.subtitle_generator import save_srt_file, embed_subtitles
from core.dubber import generate_dubbed_audio
from core.video_mixer import get_video_duration, mix_video_and_audio

configure_environment()


def translate_video_pipeline(
    video_path: str,
    mode: str = "both",  # "subtitles", "dubbing", "both"
    whisper_model: str = "base",
    voice: str = "pt-BR-FranciscaNeural",
    original_volume: float = 0.0,
    burn_in_subtitles: bool = True,
    output_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    Executa o fluxo completo de tradução do vídeo:
    1. Extração de áudio
    2. Transcrição com timestamps (Whisper)
    3. Tradução para Português
    4. Geração de Legendas (.srt)
    5. Síntese de Voz (Edge-TTS) se modo envolver dublagem
    6. Renderização do vídeo final
    """
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo de entrada não encontrado: {video_path}")

    base_name = Path(video_path).stem
    out_dir = output_dir or os.path.join(os.path.dirname(video_path), "output")
    os.makedirs(out_dir, exist_ok=True)

    temp_dir = tempfile.mkdtemp(prefix="vt_pipeline_")

    try:
        def update_progress(msg: str, step_progress: float, step_idx: int, total_steps: int):
            if progress_callback:
                overall = (step_idx - 1) / total_steps + (step_progress / total_steps)
                progress_callback(msg, min(1.0, max(0.0, overall)))

        total_steps = 4 if mode == "subtitles" else 5

        # -------------------------------------------------------------
        # Etapa 1: Extrair Áudio
        # -------------------------------------------------------------
        update_progress("Extraindo áudio do vídeo original...", 0.2, 1, total_steps)
        audio_wav = os.path.join(temp_dir, "original_audio.wav")
        extract_audio(video_path, audio_wav)
        total_duration = get_video_duration(video_path)
        update_progress("Áudio extraído com sucesso!", 1.0, 1, total_steps)

        # -------------------------------------------------------------
        # Etapa 2: Transcrever Áudio em Inglês (Whisper)
        # -------------------------------------------------------------
        def trans_cb(m, p):
            update_progress(m, p, 2, total_steps)

        segments = transcribe_audio(
            audio_path=audio_wav,
            model_size=whisper_model,
            language="en",
            progress_callback=trans_cb
        )

        if not segments:
            raise RuntimeError("Nenhuma fala em inglês foi detectada no vídeo.")

        # -------------------------------------------------------------
        # Etapa 3: Traduzir para Português
        # -------------------------------------------------------------
        def transl_cb(m, p):
            update_progress(m, p, 3, total_steps)

        translated_segments = translate_segments(
            segments=segments,
            source_lang="en",
            target_lang="pt",
            progress_callback=transl_cb
        )

        # Salvar arquivo SRT
        srt_file = os.path.join(out_dir, f"{base_name}_pt.srt")
        save_srt_file(translated_segments, srt_file, use_translated=True)

        dubbed_audio_file = None
        final_video_file = os.path.join(out_dir, f"{base_name}_traduzido.mp4")

        # -------------------------------------------------------------
        # Etapa 4: Síntese de Voz (Dublagem) se aplicável
        # -------------------------------------------------------------
        if mode in ("dubbing", "both"):
            def dub_cb(m, p):
                update_progress(m, p, 4, total_steps)

            dubbed_audio_file = os.path.join(temp_dir, "dubbed_pt.wav")
            generate_dubbed_audio(
                segments=translated_segments,
                total_duration_sec=total_duration,
                output_audio_path=dubbed_audio_file,
                voice=voice,
                temp_dir=temp_dir,
                progress_callback=dub_cb
            )

        # -------------------------------------------------------------
        # Etapa 5: Mixagem e Renderização Final
        # -------------------------------------------------------------
        current_step = total_steps
        update_progress("Renderizando vídeo com FFmpeg...", 0.2, current_step, total_steps)

        if mode == "subtitles":
            # Apenas legendas no vídeo
            embed_subtitles(
                video_path=video_path,
                srt_path=srt_file,
                output_video_path=final_video_file,
                burn_in=burn_in_subtitles
            )
        else:
            # Dublagem ou Dublagem + Legendas
            mix_video_and_audio(
                video_path=video_path,
                dubbed_audio_path=dubbed_audio_file,
                output_video_path=final_video_file,
                original_audio_volume=original_volume,
                srt_subtitles_path=srt_file if mode == "both" else None,
                burn_in_subtitles=burn_in_subtitles,
                progress_callback=lambda m, p: update_progress(m, p, current_step, total_steps)
            )

        update_progress("Processamento concluído com sucesso!", 1.0, total_steps, total_steps)

        return {
            "output_video_path": final_video_file,
            "srt_path": srt_file,
            "segments": translated_segments,
            "dubbed_audio_path": dubbed_audio_file,
            "total_duration": total_duration
        }

    finally:
        # Limpeza segura dos arquivos temporários
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
