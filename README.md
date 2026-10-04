# ⚡ NYXCIPHER AI

> **Next-Gen English to Portuguese Translation Suite**  
> *Created & Engineered by nyxcipher*

---

## 🌟 Visão Geral

O **NyxCipher AI** é uma plataforma tudo-em-um desenvolvida para eliminar qualquer barreira entre o inglês e o português, reunindo ferramentas de Inteligência Artificial para **Vídeos**, **Músicas**, **Trabalhos Escolares/Acadêmicos** e **Textos Rápidos**.

Projetado com uma interface moderna em estilo *Dark Cyber*, o NyxCipher destaca a assinatura exclusiva da marca para que qualquer usuário saiba quem desenvolveu a plataforma.

---

## 🚀 Os 4 Módulos Principais

### 1. 🎬 Nyx Video (Vídeos & Dublagem com IA)
- **Legendas Sincronizadas**: Geração de `.srt` e opção de gravar a legenda direto no vídeo (*Hardsub*).
- **Dublagem com Voz Neural**: Substituição ou voz sobreposta com vozes realistas brasileiras (`pt-BR-FranciscaNeural` ou `pt-BR-AntonioNeural`).
- **Sincronia Temporal**: Encaixe dinâmico da velocidade da fala no intervalo original do vídeo.

### 2. 🎵 Nyx Music (Músicas, Podcasts & Áudios)
- **Letras Sincronizadas Bilíngues**: Transcreve a música em inglês e gera a tradução verso a verso (estilo karaokê).
- **Exportação Dupla**: Download da letra bilíngue em `.txt` para estudos e no formato `.lrc` para players de música.

### 3. 📄 Nyx Docs (Trabalhos, Artigos & PDFs)
- **Leitura Universal**: Suporte a arquivos `.pdf`, `.docx` (Word) e `.txt`.
- **Tradução Acadêmica**: Preserva a organização de parágrafos e termos técnicos.
- **Resumo Executivo (Takeaways)**: Gera os pontos principais do trabalho em português para leitura rápida.

### 4. ⚡ Nyx Express (Tradução Rápida & Gírias)
- **Instantâneo**: Traduza frases, e-mails ou mensagens coladas no campo de texto.
- **Dicionário Nyx**: Detecta e explica o significado real de expressões idiomáticas e gírias em inglês (*slangs*).

---

## 💻 Como Iniciar Localmente

```bash
cd /home/alexa/.gemini/antigravity/scratch/video_translator
./run.sh
```
Acesse no navegador: **http://localhost:8510**

---

## 🌐 Como Compartilhar com Outras Pessoas (24/7)

Para que amigos, estudantes e outras pessoas usem a plataforma:

### Opção 1: Iniciar com Link Público Imediato
```bash
./run_public.sh
```
Gera um link seguro com HTTPS que funciona em qualquer celular ou computador no mundo.

### Opção 2: Deploy Grátis no Streamlit Community Cloud (Permanente)
1. Suba esta pasta para um repositório no seu GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io).
3. Conecte seu repositório e selecione o arquivo `app.py`.
4. Você terá um link fixo e permanente (ex: `https://nyxcipher.streamlit.app`) online 24h por dia!

---

## 📂 Estrutura do Código

```text
video_translator/
├── app.py                      # Interface Web Cyberpunk NyxCipher (Streamlit)
├── run.sh                      # Script de execução local
├── run_public.sh               # Script de execução com túnel público
├── requirements.txt            # Dependências da suíte
└── core/
    ├── __init__.py
    ├── ffmpeg_setup.py         # Configuração FFmpeg/FFprobe
    ├── transcriber.py          # Transcrição Whisper com timestamps
    ├── translator.py           # Motor de tradução multi-provedor
    ├── subtitle_generator.py   # Gerador de legendas SRT/VTT
    ├── dubber.py               # Síntese vocal pt-BR com Edge-TTS
    ├── video_mixer.py          # Mixagem de áudio e vídeo
    ├── docs_translator.py      # Tradução de PDFs, DOCX e TXT com resumos
    ├── music_translator.py     # Transcrição lírica e letras sincronizadas
    └── pipeline.py             # Orquestrador do módulo de vídeo
```

---

*⚡ NyxCipher AI • Engineered by nyxcipher • All Rights Reserved*
