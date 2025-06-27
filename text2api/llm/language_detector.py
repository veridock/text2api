"""
Detektor języka dla analizy tekstu
"""

import re
from typing import Dict, List, Optional
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException


class LanguageDetector:
    """Wykrywa język tekstu i dostosowuje prompty"""

    def __init__(self):
        # Zapewnia deterministyczne wyniki
        DetectorFactory.seed = 0

        # Wzorce językowe dla dodatkowej walidacji
        self.language_patterns = {
            "pl": [
                r"\b(się|że|dla|które|można|będzie|systemu|użytkowników|zarządzania)\b",
                r"\b(API|REST|HTTP|JSON|baza|danych|aplikacja|serwis)\b",
                r"(ów|ach|ami|em|ie|ę|ą|ę)$",  # końcówki polskie
            ],
            "en": [
                r"\b(the|and|for|with|that|will|can|system|users|management)\b",
                r"\b(API|REST|HTTP|JSON|database|application|service)\b",
                r"(ing|tion|ed|er|ly)$",  # końcówki angielskie
            ],
            "de": [
                r"\b(der|die|das|und|für|mit|dass|wird|kann|System|Benutzer)\b",
                r"\b(API|REST|HTTP|JSON|Datenbank|Anwendung|Service)\b",
                r"(ung|tion|ert|end|lich)$",  # końcówki niemieckie
            ],
            "fr": [
                r"\b(le|la|les|et|pour|avec|que|sera|peut|système|utilisateurs)\b",
                r"\b(API|REST|HTTP|JSON|base|données|application|service)\b",
                r"(tion|ment|eur|ant|ique)$",  # końcówki francuskie
            ],
            "es": [
                r"\b(el|la|los|y|para|con|que|será|puede|sistema|usuarios)\b",
                r"\b(API|REST|HTTP|JSON|base|datos|aplicación|servicio)\b",
                r"(ción|miento|dor|ante|ico)$",  # końcówki hiszpańskie
            ],
        }

        # Mapowanie nazw języków
        self.language_names = {
            "pl": "Polski",
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "it": "Italiano",
            "pt": "Português",
            "ru": "Русский",
            "cs": "Čeština",
            "sk": "Slovenčina",
        }

    def detect_language(self, text: str) -> str:
        """
        Wykrywa język tekstu

        Args:
            text: Tekst do analizy

        Returns:
            Kod języka (np. 'pl', 'en')
        """

        # Oczyszczenie tekstu
        cleaned_text = self._clean_text(text)

        if len(cleaned_text) < 10:
            return "en"  # domyślnie angielski dla krótkich tekstów

        try:
            # Główna detekcja używając langdetect
            detected = detect(cleaned_text)

            # Walidacja używając wzorców
            pattern_score = self._validate_with_patterns(cleaned_text, detected)

            # Jeśli wzorce nie potwierdzają, sprawdź alternatywy
            if pattern_score < 0.3:
                alternative = self._detect_with_patterns(cleaned_text)
                if alternative and alternative != detected:
                    detected = alternative

            return detected

        except LangDetectException:
            # Fallback do wykrywania wzorcami
            return self._detect_with_patterns(cleaned_text) or "en"

    def _clean_text(self, text: str) -> str:
        """Oczyszcza tekst przed detekcją"""

        # Usuń zbędne whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Usuń URLs
        text = re.sub(r"http[s]?://\S+", "", text)

        # Usuń email
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", text)

        # Usuń nadmiar znaków specjalnych (ale zostaw polskie znaki)
        text = re.sub(r"[^\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ.,!?;:()\-]", "", text)

        return text

    def _validate_with_patterns(self, text: str, detected_lang: str) -> float:
        """Waliduje wykryty język używając wzorców"""

        if detected_lang not in self.language_patterns:
            return 0.5  # neutralny wynik dla nieznanych języków

        patterns = self.language_patterns[detected_lang]
        matches = 0
        total_checks = 0

        text_lower = text.lower()

        for pattern in patterns:
            total_checks += 1
            if re.search(pattern, text_lower, re.IGNORECASE):
                matches += 1

        return matches / total_checks if total_checks > 0 else 0

    def _detect_with_patterns(self, text: str) -> Optional[str]:
        """Wykrywa język używając tylko wzorców"""

        scores = {}
        text_lower = text.lower()

        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches

            # Normalizuj względem długości tekstu
            normalized_score = score / len(text.split()) if text.split() else 0
            scores[lang] = normalized_score

        if not scores:
            return None

        # Zwróć język z najwyższym wynikiem
        best_lang = max(scores, key=scores.get)

        # Tylko jeśli wynik jest wystarczająco wysoki
        return best_lang if scores[best_lang] > 0.01 else None

    def get_confidence(self, text: str, detected_lang: str) -> float:
        """Zwraca poziom pewności detekcji (0-1)"""

        pattern_score = self._validate_with_patterns(text, detected_lang)

        # Dodatkowe czynniki
        text_length_factor = min(
            len(text) / 100, 1.0
        )  # dłuższe teksty = większa pewność

        # Sprawdź czy tekst zawiera mieszankę języków
        mixed_language_penalty = self._check_mixed_languages(text)

        confidence = pattern_score * text_length_factor * (1 - mixed_language_penalty)

        return max(0.0, min(1.0, confidence))

    def _check_mixed_languages(self, text: str) -> float:
        """Sprawdza czy tekst zawiera mieszankę języków"""

        # Podziel tekst na fragmenty
        sentences = re.split(r"[.!?]+", text)

        if len(sentences) < 2:
            return 0.0

        detected_langs = []

        for sentence in sentences:
            if len(sentence.strip()) > 10:
                try:
                    lang = detect(sentence.strip())
                    detected_langs.append(lang)
                except:
                    continue

        if len(detected_langs) < 2:
            return 0.0

        # Oblicz różnorodność języków
        unique_langs = set(detected_langs)
        diversity = len(unique_langs) / len(detected_langs)

        return diversity

    def get_language_info(self, text: str) -> Dict[str, any]:
        """Zwraca pełne informacje o wykrytym języku"""

        detected_lang = self.detect_language(text)
        confidence = self.get_confidence(text, detected_lang)

        return {
            "language": detected_lang,
            "language_name": self.language_names.get(
                detected_lang, detected_lang.upper()
            ),
            "confidence": confidence,
            "text_length": len(text),
            "word_count": len(text.split()),
            "is_mixed": self._check_mixed_languages(text) > 0.3,
        }

    def suggest_improvements(self, text: str) -> List[str]:
        """Sugeruje poprawki dla lepszej detekcji języka"""

        suggestions = []

        if len(text) < 50:
            suggestions.append(
                "Tekst jest bardzo krótki. Dodaj więcej szczegółów dla lepszej analizy."
            )

        if self._check_mixed_languages(text) > 0.5:
            suggestions.append(
                "Tekst zawiera mieszankę języków. Użyj jednego języka dla lepszych wyników."
            )

        # Sprawdź czy tekst zawiera dużo kodu/technicznych terminów
        tech_ratio = len(re.findall(r"\b[A-Z_]{2,}\b|\{|\}|\[|\]", text)) / len(
            text.split()
        )
        if tech_ratio > 0.3:
            suggestions.append(
                "Tekst zawiera dużo kodu/terminów technicznych. Dodaj więcej opisowego tekstu."
            )

        return suggestions

    def get_supported_languages(self) -> Dict[str, str]:
        """Zwraca listę obsługiwanych języków"""
        return self.language_names.copy()

    def is_supported_language(self, lang_code: str) -> bool:
        """Sprawdza czy język jest obsługiwany"""
        return lang_code in self.language_patterns
