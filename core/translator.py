"""
Módulo de tradução Inglês -> Português com suporte a múltiplos provedores
e fallback automático para máxima confiabilidade.
"""

from typing import List, Dict, Any, Callable, Optional
import time


class MultiProviderTranslator:
    def __init__(self, source: str = "en", target: str = "pt"):
        self.source = source
        self.target = target
        self._cache = {}

    def translate_one(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        if text in self._cache:
            return self._cache[text]

        # 1. Tentar MyMemoryTranslator (muito estável e gratuito)
        try:
            from deep_translator import MyMemoryTranslator
            # MyMemory usa formato com região ex: en-US, pt-BR
            src = "en-US" if self.source.startswith("en") else self.source
            tgt = "pt-BR" if self.target.startswith("pt") else self.target
            res = MyMemoryTranslator(source=src, target=tgt).translate(text)
            if res and not res.startswith("MYMEMORY WARNING"):
                self._cache[text] = res
                return res
        except Exception:
            pass

        # 2. Tentar GoogleTranslator como fallback
        try:
            from deep_translator import GoogleTranslator
            res = GoogleTranslator(source=self.source, target=self.target).translate(text)
            if res:
                self._cache[text] = res
                return res
        except Exception:
            pass

        # 3. Fallback: retornar texto original se não conseguir traduzir
        return text


def translate_segments(
    segments: List[Dict[str, Any]],
    source_lang: str = "en",
    target_lang: str = "pt",
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> List[Dict[str, Any]]:
    """
    Traduz a lista de segmentos transcritos para a língua de destino (Português).
    """
    if not segments:
        return []

    translator = MultiProviderTranslator(source=source_lang, target=target_lang)
    translated_segments = []
    total = len(segments)

    if progress_callback:
        progress_callback("Iniciando tradução para o português...", 0.0)

    for i, seg in enumerate(segments):
        original_text = seg["text"].strip()
        translated_text = translator.translate_one(original_text)

        seg_copy = dict(seg)
        seg_copy["translated_text"] = (translated_text or original_text).strip()
        translated_segments.append(seg_copy)

        if progress_callback:
            progress = (i + 1) / total
            progress_callback(f"Traduzindo frase {i + 1} de {total}...", progress)
        
        # Pequena pausa para evitar flood
        time.sleep(0.1)

    if progress_callback:
        progress_callback("Tradução finalizada com sucesso!", 1.0)

    return translated_segments


def translate_text(text: str, source_lang: str = "en", target_lang: str = "pt") -> str:
    """Traduz uma única string de texto."""
    translator = MultiProviderTranslator(source=source_lang, target=target_lang)
    return translator.translate_one(text)


if __name__ == "__main__":
    test_str = "Artificial Intelligence is transforming video production and translation."
    print("Original:", test_str)
    print("Traduzido:", translate_text(test_str))
