"""
metrics.py

Prosty moduł do obliczania WER, SER oraz CER między tekstem referencyjnym (oryginalnym)
 a tekstem rozpoznanym (transkrypcją).

- WER (Word Error Rate): odległość Levenshteina na poziomie słów / liczba słów w referencji.
- CER (Character Error Rate): odległość Levenshteina na poziomie znaków / liczba znaków w referencji.
- SER (Sentence Error Rate): odsetek zdań różniących się od odpowiadających im zdań w hipotezie.

Uwagi:
- Normalizacja (np. zamiana na małe litery, uproszczenie białych znaków, usuwanie znaków interpunkcyjnych)
  może istotnie wpływać na wynik — można ją włączyć/wyłączyć parametrami.
- CER domyślnie liczone bez spacji (typowa praktyka); można to zmienić parametrem.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple
import re


def normalize_text(
    text: str,
    lowercase: bool = True,
    strip_punct: bool = False,
    normalize_whitespace: bool = True,
) -> str:
    """
    Prosta normalizacja tekstu.
    - lowercase: zamiana na małe litery
    - strip_punct: usunięcie znaków interpunkcyjnych
    - normalize_whitespace: zamiana wielu białych znaków na pojedynczą spację i trim
    """
    if lowercase:
        text = text.lower()
    if strip_punct:
        # Usuwamy większość znaków interpunkcyjnych (pozostawiamy litery/cyfry i spacje)
        text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    if normalize_whitespace:
        text = re.sub(r"\s+", " ", text, flags=re.UNICODE).strip()
    return text


def tokenize_words(text: str) -> List[str]:
    """Tokenizacja po białych znakach (prosto i szybko)."""
    if not text:
        return []
    return text.split()


def split_sentences(text: str, method: str = "simple") -> List[str]:
    """
    Dzieli tekst na zdania.
    - method="newline": dzieli tylko po znakach nowej linii
    - method="simple": dzieli po prostym wzorcu końca zdania ([.!?]+), usuwa puste
    """
    if not text:
        return []

    if method == "newline":
        parts = [ln.strip() for ln in text.splitlines()]
        return [p for p in parts if p]

    # Prosty podział na zdania po ., !, ? (jeden lub więcej)
    parts = re.split(r"[.!?]+", text)
    # Usuwamy puste i nadmiarowe spacje
    parts = [p.strip() for p in parts if p and p.strip()]
    return parts


def _levenshtein_distance(seq1: Sequence, seq2: Sequence) -> int:
    """
    Odległość Levenshteina dla ogólnej sekwencji (słów lub znaków).
    Implementacja O(n*m) czasu i O(min(n,m)) pamięci.
    Zwraca łączną liczbę operacji (insert, delete, substitute).
    """
    n, m = len(seq1), len(seq2)
    if n == 0:
        return m
    if m == 0:
        return n

    # Upewniamy się, że seq1 jest krótsze — dla oszczędności pamięci
    if n > m:
        seq1, seq2 = seq2, seq1
        n, m = m, n

    previous = list(range(n + 1))
    current = [0] * (n + 1)

    for j in range(1, m + 1):
        current[0] = j
        sj = seq2[j - 1]
        for i in range(1, n + 1):
            cost = 0 if seq1[i - 1] == sj else 1
            current[i] = min(
                previous[i] + 1,  # deletion
                current[i - 1] + 1,  # insertion
                previous[i - 1] + cost,  # substitution
            )
        previous, current = current, previous

    return previous[n]


def wer(
    ref_text: str,
    hyp_text: str,
    lowercase: bool = True,
    strip_punct: bool = False,
    normalize_whitespace: bool = True,
) -> Tuple[float, int, int]:
    """
    Word Error Rate dla całych tekstów.
    Zwraca krotkę: (wer, edits, ref_len), gdzie
    - wer: float w zakresie [0, 1]
    - edits: liczba edycji (Levenshtein) na poziomie słów
    - ref_len: liczba słów w referencji
    """
    ref_norm = normalize_text(ref_text, lowercase, strip_punct, normalize_whitespace)
    hyp_norm = normalize_text(hyp_text, lowercase, strip_punct, normalize_whitespace)

    ref_tokens = tokenize_words(ref_norm)
    hyp_tokens = tokenize_words(hyp_norm)

    ref_len = len(ref_tokens)
    edits = _levenshtein_distance(ref_tokens, hyp_tokens)

    if ref_len == 0:
        # Konwencja: jeśli referencja pusta i hipoteza pusta => WER=0, wpp 1
        return (0.0 if len(hyp_tokens) == 0 else 1.0, edits, ref_len)

    return (edits / ref_len, edits, ref_len)


def cer(
    ref_text: str,
    hyp_text: str,
    lowercase: bool = True,
    strip_punct: bool = False,
    normalize_whitespace: bool = True,
    include_spaces: bool = False,
) -> Tuple[float, int, int]:
    """
    Character Error Rate dla całych tekstów.
    Zwraca krotkę: (cer, edits, ref_len), gdzie ref_len to liczba znaków w referencji
    (bez spacji, jeśli include_spaces=False).
    """
    ref_norm = normalize_text(ref_text, lowercase, strip_punct, normalize_whitespace)
    hyp_norm = normalize_text(hyp_text, lowercase, strip_punct, normalize_whitespace)

    if not include_spaces:
        ref_norm = re.sub(r"\s+", "", ref_norm)
        hyp_norm = re.sub(r"\s+", "", hyp_norm)

    ref_chars = list(ref_norm)
    hyp_chars = list(hyp_norm)

    ref_len = len(ref_chars)
    edits = _levenshtein_distance(ref_chars, hyp_chars)

    if ref_len == 0:
        return (0.0 if len(hyp_chars) == 0 else 1.0, edits, ref_len)

    return (edits / ref_len, edits, ref_len)


def ser(
    ref_text: str,
    hyp_text: str,
    lowercase: bool = True,
    strip_punct: bool = False,
    normalize_whitespace: bool = True,
    sentence_split: str = "simple",  # "simple" lub "newline"
) -> Tuple[float, int, int]:
    """
    Sentence Error Rate.
    - Dzieli oba teksty na zdania (wg sentence_split), normalizuje każde z nich, a następnie
      porównuje odpowiednie pary po indeksie. Zdanie liczone jako błędne, jeśli nie jest
      identyczne z odpowiadającym mu zdaniem w hipotezie.
    - Jeśli w hipotezie brakuje zdań (mniej zdań niż w referencji), brakujące liczone jako błędy.
    - Nadmiarowe zdania w hipotezie nie wpływają na mianownik (klasyczna definicja SER oparta na ref).

    Zwraca: (ser, error_sentences, total_sentences)
    """
    # Ważne: aby nie utracić granic zdań, najpierw DZIELIMY, a dopiero potem
    # ewentualnie usuwamy interpunkcję na poziomie zdań.
    # Dlatego podczas przygotowania do podziału ignorujemy strip_punct.

    ref_for_split = normalize_text(
        ref_text,
        lowercase=lowercase,
        strip_punct=False,
        normalize_whitespace=normalize_whitespace,
    )
    hyp_for_split = normalize_text(
        hyp_text,
        lowercase=lowercase,
        strip_punct=False,
        normalize_whitespace=normalize_whitespace,
    )

    ref_sents_raw = split_sentences(ref_for_split, method=sentence_split)
    hyp_sents_raw = split_sentences(hyp_for_split, method=sentence_split)

    # Następnie normalizujemy każde zdanie z użyciem właściwego strip_punct,
    # tak aby porównanie honorowało ustawienia użytkownika.
    def _norm_sent(s: str) -> str:
        return normalize_text(
            s,
            lowercase=lowercase,
            strip_punct=strip_punct,
            normalize_whitespace=normalize_whitespace,
        )

    ref_sents = [_norm_sent(s) for s in ref_sents_raw]
    hyp_sents = [_norm_sent(s) for s in hyp_sents_raw]

    total = len(ref_sents)
    if total == 0:
        # Konwencja jak wyżej: jeśli brak zdań w ref, to 0 gdy brak także w hyp, inaczej 1
        return (
            0.0 if len(hyp_sents) == 0 else 1.0,
            0 if len(hyp_sents) == 0 else 1,
            total,
        )

    errors = 0
    for i, ref_s in enumerate(ref_sents):
        hyp_s = hyp_sents[i] if i < len(hyp_sents) else None
        if hyp_s is None or hyp_s != ref_s:
            errors += 1

    return (errors / total, errors, total)


__all__ = [
    "normalize_text",
    "tokenize_words",
    "split_sentences",
    "wer",
    "cer",
    "ser",
]
