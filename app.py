"""
==============================================================================
⚡ NYXCIPHER AI: Next-Gen English to Portuguese Translation Suite
Created & Engineered by nyxcipher
==============================================================================
"""

import os
import shutil
import tempfile
import pandas as pd
import streamlit as st

from core.dubber import AVAILABLE_VOICES
from core.pipeline import translate_video_pipeline
from core.docs_translator import translate_document
from core.music_translator import generate_bilingual_lyrics
from core.translator import translate_text

# Configuração da página Streamlit
st.set_page_config(
    page_title="NyxCipher AI | Suite de Tradução",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Visual Cyberpunk / Dark Tech Premium com a marca nyxcipher
st.markdown("""
<style>
    /* Estilo Global Dark */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Cabeçalho Hero */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.2);
    }
    .brand-title {
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        margin-bottom: 0.3rem;
    }
    .brand-badge {
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        vertical-align: middle;
        margin-left: 0.8rem;
    }
    .brand-sub {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }

    /* Cards e Caixas */
    .nyx-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        transition: border-color 0.2s ease;
    }
    .nyx-card:hover {
        border-color: #6366f1;
    }
    
    /* Botões Principais */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: 700;
        letter-spacing: 0.02em;
        padding: 0.75rem 2.2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(168, 85, 247, 0.5);
    }
    
    /* Rodapé Oficial */
    .footer-nyx {
        margin-top: 4rem;
        padding: 1.8rem 0;
        border-top: 1px solid #1e293b;
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
    }
    .footer-nyx b {
        color: #818cf8;
    }

    /* Abas estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #111827;
        border-radius: 8px 8px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e1b4b !important;
        color: #c084fc !important;
        border-bottom: 2px solid #818cf8 !important;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="hero-container">
        <div>
            <span class="brand-title">NYXCIPHER AI</span>
            <span class="brand-badge">PRO SUITE</span>
        </div>
        <div class="brand-sub">
            Plataforma All-in-One de Tradução Inteligente de <b>Inglês para Português</b> • Desenvolvido por <b>nyxcipher</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="footer-nyx">
        ⚡ <b>NYXCIPHER AI</b> &copy; 2026 • Criado e desenvolvido com tecnologia de ponta por <b>nyxcipher</b>.<br>
        <span style="font-size: 0.8rem; color: #475569;">Tradução Neural, Transcrição Whisper e Síntese de Voz por IA.</span>
    </div>
    """, unsafe_allow_html=True)


def tab_video():
    st.markdown("### 🎬 Nyx Video: Tradução & Dublagem de Vídeos")
    st.markdown("Traduza qualquer vídeo em inglês gerando **Legendas Sincronizadas** e **Dublagem com Voz Neural em Português**.")

    col_conf, col_upload = st.columns([1, 1.4])

    with col_conf:
        st.markdown("#### ⚙️ Configurações de Vídeo")
        mode_option = st.radio(
            "Modo de Tradução:",
            [
                "🎙️ Dublagem + 📝 Legendas (Completo)",
                "🎙️ Apenas Dublagem",
                "📝 Apenas Legendas"
            ],
            key="vid_mode"
        )
        mode_map = {
            "🎙️ Dublagem + 📝 Legendas (Completo)": "both",
            "🎙️ Apenas Dublagem": "dubbing",
            "📝 Apenas Legendas": "subtitles"
        }
        selected_mode = mode_map[mode_option]

        if selected_mode in ("both", "dubbing"):
            voice_choice = st.selectbox(
                "Voz em Português (pt-BR):",
                list(AVAILABLE_VOICES.keys()),
                key="vid_voice"
            )
            selected_voice = AVAILABLE_VOICES[voice_choice]

            volume_slider = st.slider(
                "Volume do Áudio Original em Inglês:",
                min_value=0,
                max_value=40,
                value=0,
                step=5,
                help="0% substitui totalmente o áudio. 15% cria voz sobreposta estilo documentário."
            )
            original_volume = volume_slider / 100.0
        else:
            selected_voice = "pt-BR-FranciscaNeural"
            original_volume = 0.0

        burn_in = st.checkbox(
            "Gravar legendas na imagem (Hardsub)",
            value=True,
            help="As legendas ficam visíveis em qualquer celular, TV ou reprodutor.",
            key="vid_burnin"
        )

        whisper_model = st.selectbox(
            "Modelo Whisper (Precisão):",
            ["base (Equilibrado)", "tiny (Rápido)", "small (Alta Precisão)"],
            key="vid_whisper"
        ).split()[0]

    with col_upload:
        st.markdown("#### 📤 Enviar Vídeo")
        uploaded_video = st.file_uploader(
            "Selecione um vídeo (MP4, MKV, MOV, AVI, WEBM)",
            type=["mp4", "mkv", "mov", "avi", "webm"],
            key="uploader_video"
        )

        if uploaded_video:
            st.video(uploaded_video)
            btn_process_video = st.button("🚀 Iniciar Tradução do Vídeo", key="btn_run_video")

            if btn_process_video:
                p_bar = st.progress(0.0)
                status_msg = st.empty()

                temp_dir = tempfile.mkdtemp(prefix="nyx_vid_")
                in_path = os.path.join(temp_dir, uploaded_video.name)
                out_dir = os.path.join(temp_dir, "output")
                os.makedirs(out_dir, exist_ok=True)

                with open(in_path, "wb") as f:
                    f.write(uploaded_video.getbuffer())

                try:
                    def p_callback(msg, pct):
                        p_bar.progress(pct)
                        status_msg.markdown(f"**Processando:** {msg}")

                    res = translate_video_pipeline(
                        video_path=in_path,
                        mode=selected_mode,
                        whisper_model=whisper_model,
                        voice=selected_voice,
                        original_volume=original_volume,
                        burn_in_subtitles=burn_in,
                        output_dir=out_dir,
                        progress_callback=p_callback
                    )

                    st.success("🎉 Vídeo traduzido com sucesso!")

                    st.markdown("---")
                    res_col1, res_col2 = st.columns([1.2, 0.8])

                    with res_col1:
                        st.markdown("#### 📺 Vídeo Traduzido")
                        final_vid = res["output_video_path"]
                        if os.path.exists(final_vid):
                            with open(final_vid, "rb") as vf:
                                v_bytes = vf.read()
                                st.video(v_bytes)
                                st.download_button(
                                    label="📥 Baixar Vídeo Traduzido (MP4)",
                                    data=v_bytes,
                                    file_name=f"nyxcipher_{uploaded_video.name}",
                                    mime="video/mp4"
                                )

                    with res_col2:
                        st.markdown("#### 📄 Arquivos e Legendas")
                        srt_p = res.get("srt_path")
                        if srt_p and os.path.exists(srt_p):
                            with open(srt_p, "r", encoding="utf-8") as sf:
                                s_bytes = sf.read()
                                st.download_button(
                                    label="📥 Baixar Legenda (.srt)",
                                    data=s_bytes,
                                    file_name=f"nyxcipher_legenda_{os.path.splitext(uploaded_video.name)[0]}.srt",
                                    mime="text/plain"
                                )

                    st.markdown("#### 📑 Falas Detectadas e Traduzidas")
                    df = pd.DataFrame([{
                        "Início": f"{s['start']:.1f}s",
                        "Fim": f"{s['end']:.1f}s",
                        "Original (Inglês)": s.get("text", ""),
                        "Traduzido (Português)": s.get("translated_text", "")
                    } for s in res.get("segments", [])])
                    st.dataframe(df, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"Erro no processamento do vídeo: {e}")


def tab_music():
    st.markdown("### 🎵 Nyx Music & Podcasts: Músicas e Áudios com Letra Sincronizada")
    st.markdown("Envie músicas, podcasts ou áudios em inglês para obter a **letra sincronizada verso a verso em português** (estilo karaokê bilíngue).")

    col_up, col_res = st.columns([1, 1.2])

    with col_up:
        uploaded_audio = st.file_uploader(
            "Envie uma música ou arquivo de áudio (MP3, WAV, M4A, OGG, AAC, FLAC)",
            type=["mp3", "wav", "m4a", "ogg", "aac", "flac"],
            key="uploader_audio"
        )
        if uploaded_audio:
            st.audio(uploaded_audio)
            btn_process_music = st.button("🎵 Transcrever e Traduzir Letra", key="btn_run_music")

    if uploaded_audio and 'btn_process_music' in locals() and btn_process_music:
        with col_res:
            p_bar_m = st.progress(0.0)
            status_m = st.empty()

            temp_dir = tempfile.mkdtemp(prefix="nyx_music_")
            audio_path = os.path.join(temp_dir, uploaded_audio.name)
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())

            try:
                def m_callback(msg, pct):
                    p_bar_m.progress(pct)
                    status_m.markdown(f"**Processando áudio:** {msg}")

                music_res = generate_bilingual_lyrics(
                    audio_path=audio_path,
                    whisper_model="base",
                    progress_callback=m_callback
                )

                st.success("🎉 Letra sincronizada gerada com sucesso!")

                # Botões de download
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button(
                        label="📥 Baixar Letra (.txt)",
                        data=music_res["bilingual_lyrics"],
                        file_name=f"letra_bilingue_{os.path.splitext(uploaded_audio.name)[0]}.txt",
                        mime="text/plain"
                    )
                with dl_col2:
                    st.download_button(
                        label="📥 Baixar Formato Sincronizado (.lrc)",
                        data=music_res["lrc_content"],
                        file_name=f"{os.path.splitext(uploaded_audio.name)[0]}.lrc",
                        mime="text/plain"
                    )

                st.markdown("#### 🎤 Letra Bilíngue Sincronizada")
                for seg in music_res["segments"]:
                    st.markdown(f"""
                    <div style="background:#1e1b4b; padding:10px 15px; border-radius:8px; margin-bottom:8px; border-left:4px solid #818cf8;">
                        <span style="font-size:0.8rem; color:#94a3b8; font-weight:bold;">⏱️ {seg['start']:.1f}s</span><br>
                        <span style="color:#e2e8f0; font-size:1.05rem;">{seg['text']}</span><br>
                        <span style="color:#c084fc; font-weight:600;">{seg['translated_text']}</span>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erro ao processar música: {e}")


def tab_docs():
    st.markdown("### 📄 Nyx Docs & Papers: Trabalhos Escolares, Artigos & Tarefas")
    st.markdown("Envie documentos em PDF, Word (.docx) ou Texto (.txt) em inglês. O NyxCipher traduz o conteúdo mantendo a estrutura e gera um resumo executivo.")

    uploaded_doc = st.file_uploader(
        "Envie o arquivo do trabalho ou artigo (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        key="uploader_doc"
    )

    if uploaded_doc:
        btn_process_doc = st.button("📄 Traduzir Trabalho Agora", key="btn_run_doc")

        if btn_process_doc:
            p_bar_d = st.progress(0.0)
            status_d = st.empty()

            temp_dir = tempfile.mkdtemp(prefix="nyx_doc_")
            doc_path = os.path.join(temp_dir, uploaded_doc.name)
            with open(doc_path, "wb") as f:
                f.write(uploaded_doc.getbuffer())

            try:
                def d_callback(msg, pct):
                    p_bar_d.progress(pct)
                    status_d.markdown(f"**Processando documento:** {msg}")

                doc_res = translate_document(doc_path, progress_callback=d_callback)
                st.success("🎉 Documento traduzido com sucesso!")

                # Exibir Resumo dos Pontos Principais
                st.markdown("#### 💡 Resumo dos Pontos Principais (Takeaways)")
                st.info(doc_res["summary_preview"])

                # Botão de download
                st.download_button(
                    label="📥 Baixar Trabalho Traduzido (.txt)",
                    data=doc_res["translated_text"],
                    file_name=f"traduzido_nyxcipher_{os.path.splitext(uploaded_doc.name)[0]}.txt",
                    mime="text/plain"
                )

                # Comparador Lado a Lado
                st.markdown("#### 📑 Comparador de Conteúdo")
                c_orig, c_trans = st.columns(2)
                with c_orig:
                    st.markdown("**Original em Inglês:**")
                    st.text_area("", value=doc_res["original_text"][:3000] + ("..." if len(doc_res["original_text"]) > 3000 else ""), height=400, disabled=True)
                with c_trans:
                    st.markdown("**Traduzido em Português:**")
                    st.text_area("", value=doc_res["translated_text"][:3000] + ("..." if len(doc_res["translated_text"]) > 3000 else ""), height=400, disabled=True)

            except Exception as e:
                st.error(f"Erro ao processar documento: {e}")


def tab_express():
    st.markdown("### ⚡ Nyx Express: Tradução Rápida & Gírias em Inglês")
    st.markdown("Cole frases rápidas, e-mails, conversas de redes sociais ou termos do dia a dia.")

    user_text = st.text_area("Cole seu texto ou frase em inglês aqui:", height=150, placeholder="Ex: That project was a piece of cake! I think we should call it a day.")

    if st.button("⚡ Traduzir com NyxCipher", key="btn_run_express"):
        if user_text.strip():
            with st.spinner("Traduzindo..."):
                translated = translate_text(user_text, source_lang="en", target_lang="pt")

                st.markdown("#### 🇧🇷 Tradução em Português:")
                st.success(translated)

                # Identificação inteligente de gírias e expressões populares
                idioms_db = {
                    "piece of cake": "Algo muito fácil ('mamão com açúcar' ou 'moleza').",
                    "call it a day": "Encerrar o trabalho do dia / dar o dia por terminado.",
                    "break a leg": "Boa sorte! (expressão usada no teatro/apresentações).",
                    "hit the sack": "Ir dormir / ir para a cama.",
                    "spill the beans": "Revelar um segredo antes da hora.",
                    "under the weather": "Sentindo-se mal ou meio doente.",
                    "once in a blue moon": "Algo muito raro de acontecer ('uma vez na vida, outra na morte').",
                    "bite the bullet": "Enfrentar uma situação difícil com coragem."
                }

                found_idioms = []
                lower_text = user_text.lower()
                for idiom, meaning in idioms_db.items():
                    if idiom in lower_text:
                        found_idioms.append((idiom, meaning))

                if found_idioms:
                    st.markdown("#### 🧠 Dicionário Nyx de Expressões Detectadas:")
                    for idiom, meaning in found_idioms:
                        st.markdown(f"- **'{idiom}'**: {meaning}")
        else:
            st.warning("Por favor, digite ou cole um texto em inglês.")


def main():
    render_header()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎬 Nyx Video (Vídeos & Dublagem)",
        "🎵 Nyx Music (Músicas & Áudios)",
        "📄 Nyx Docs (Trabalhos & PDFs)",
        "⚡ Nyx Express (Tradução Rápida)"
    ])

    with tab1:
        tab_video()

    with tab2:
        tab_music()

    with tab3:
        tab_docs()

    with tab4:
        tab_express()

    render_footer()


if __name__ == "__main__":
    main()
