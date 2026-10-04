"""
Script de teste ponta a ponta para validação do VideoTranslator-PT.
Cria um vídeo sintético com áudio em inglês e testa o pipeline completo.
"""

import os
import asyncio
import edge_tts
from core.ffmpeg_setup import run_ffmpeg, configure_environment
from core.pipeline import translate_video_pipeline

configure_environment()

TEMP_DIR = "/home/alexa/.gemini/antigravity/scratch/video_translator/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def create_sample_video():
    """Gera áudio em inglês e monta um vídeo MP4 curto para teste."""
    sample_text = "Welcome to this test video. We are testing automatic video translation and dubbing from English to Portuguese."
    sample_audio = os.path.join(TEMP_DIR, "sample_english.mp3")
    sample_video = os.path.join(TEMP_DIR, "sample_english.mp4")

    print("[1/3] Sintetizando voz de teste em inglês...")
    tts = edge_tts.Communicate(sample_text, "en-US-AriaNeural")
    await tts.save(sample_audio)

    print("[2/3] Gerando vídeo MP4 de teste com FFmpeg...")
    # Cria vídeo com fundo azul escuro e o áudio em inglês
    args = [
        "-y",
        "-f", "lavfi", "-i", "color=c=#1e293b:s=640x360:d=7",
        "-i", sample_audio,
        "-vf", "drawtext=text='Video de Teste (Ingles)':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        sample_video
    ]
    res = run_ffmpeg(args, check=False)
    if res.returncode != 0:
        # Se drawtext falhar por falta de libfreetype, gera sem texto na tela
        args = [
            "-y",
            "-f", "lavfi", "-i", "color=c=#1e293b:s=640x360:d=7",
            "-i", sample_audio,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            sample_video
        ]
        run_ffmpeg(args, check=True)

    print(f"Vídeo de teste gerado em: {sample_video}")
    return sample_video


def main():
    sample_video = asyncio.run(create_sample_video())
    print("\n[3/3] Executando pipeline completo de tradução (Legendas + Dublagem)...")

    def progress(msg, pct):
        print(f"[{int(pct*100):3d}%] {msg}")

    result = translate_video_pipeline(
        video_path=sample_video,
        mode="both",
        whisper_model="tiny",  # tiny para teste rápido
        voice="pt-BR-FranciscaNeural",
        original_volume=0.15,
        burn_in_subtitles=True,
        progress_callback=progress
    )

    print("\n=== RESULTADOS DO TESTE ===")
    print("Vídeo Traduzido:", result["output_video_path"])
    print("Arquivo SRT:", result["srt_path"])
    print("Segmentos traduzidos:")
    for seg in result["segments"]:
        print(f"  [{seg['start']}s -> {seg['end']}s]")
        print(f"    Inglês:     {seg['text']}")
        print(f"    Português:  {seg.get('translated_text')}")

    if os.path.exists(result["output_video_path"]) and os.path.getsize(result["output_video_path"]) > 1000:
        print("\nTESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\nERRO: Arquivo final não foi gerado ou está vazio.")


if __name__ == "__main__":
    main()
