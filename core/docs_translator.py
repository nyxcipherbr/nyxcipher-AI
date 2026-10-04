"""
Módulo Nyx Docs: Leitura, tradução e sumarização de Trabalhos, Artigos e Tarefas (PDF, DOCX, TXT).
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from core.translator import MultiProviderTranslator


def extract_text_from_file(file_path: str) -> str:
    """Extrai o texto bruto de arquivos PDF, DOCX ou TXT."""
    ext = Path(file_path).suffix.lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        return "\n\n".join(pages_text)

    elif ext in (".docx", ".doc"):
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    else:
        raise ValueError(f"Formato não suportado: {ext}. Envie PDF, DOCX ou TXT.")


def split_into_paragraphs(text: str, max_chars: int = 1500) -> List[str]:
    """Divide o texto em blocos coerentes para tradução sem estourar limites."""
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_length = 0

    for p in raw_paragraphs:
        if current_length + len(p) > max_chars and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [p]
            current_length = len(p)
        else:
            current_chunk.append(p)
            current_length += len(p) + 1

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def translate_document(
    file_path: str,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    """
    Processa e traduz um documento escolar/acadêmico:
    - Extrai texto
    - Traduz parágrafo por parágrafo
    - Retorna texto original, texto traduzido e resumo dos pontos-chave
    """
    if progress_callback:
        progress_callback("Extraindo texto do documento...", 0.1)

    raw_text = extract_text_from_file(file_path)
    if not raw_text.strip():
        raise ValueError("O documento enviado está vazio ou não contém texto legível.")

    chunks = split_into_paragraphs(raw_text)
    total_chunks = len(chunks)

    translator = MultiProviderTranslator(source="en", target="pt")
    translated_chunks = []

    if progress_callback:
        progress_callback("Traduzindo conteúdo para o português...", 0.2)

    for i, chunk in enumerate(chunks):
        trans = translator.translate_one(chunk)
        translated_chunks.append(trans)
        if progress_callback:
            progress = 0.2 + (0.7 * ((i + 1) / total_chunks))
            progress_callback(f"Traduzindo seção {i + 1} de {total_chunks}...", progress)

    full_translated = "\n\n".join(translated_chunks)

    if progress_callback:
        progress_callback("Finalizando documento...", 0.95)

    # Gerar resumo simples dos pontos principais (primeiros blocos essenciais)
    summary_preview = translated_chunks[0] if translated_chunks else ""
    if len(summary_preview) > 500:
        summary_preview = summary_preview[:500] + "..."

    if progress_callback:
        progress_callback("Tradução do documento concluída com sucesso!", 1.0)

    return {
        "original_text": raw_text,
        "translated_text": full_translated,
        "paragraphs_count": len(chunks),
        "char_count": len(full_translated),
        "summary_preview": summary_preview
    }
