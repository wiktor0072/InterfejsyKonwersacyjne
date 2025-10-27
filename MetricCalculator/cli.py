#!/usr/bin/env python3
"""
cli.py

Prosty interfejs CLI do obliczania WER, SER i CER między tekstem referencyjnym
(oryginalnym) a hipotezą (transkrypcją).

Przykład użycia:
    python cli.py --ref "Ala ma kota" --hyp "Ala ma kotka"

Lub z plików:
    python cli.py --ref-file ref.txt --hyp-file hyp.txt
"""
import argparse
import sys
from typing import Tuple

from metrics import wer, cer, ser


def read_text_args(args: argparse.Namespace) -> Tuple[str, str]:
    if args.ref_file and args.hyp_file:
        try:
            with open(args.ref_file, "r", encoding="utf-8") as f:
                ref_text = f.read()
            with open(args.hyp_file, "r", encoding="utf-8") as f:
                hyp_text = f.read()
            return ref_text, hyp_text
        except FileNotFoundError as e:
            print(f"Błąd: Plik nie istnieje: {e}", file=sys.stderr)
            sys.exit(2)
    elif args.ref is not None and args.hyp is not None:
        return args.ref, args.hyp
    else:
        print("Musisz podać albo --ref i --hyp, albo --ref-file i --hyp-file.", file=sys.stderr)
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Oblicz WER, SER i CER dla pary tekstów (referencja vs hipoteza)."
    )
    src = parser.add_argument_group("Źródło danych")
    src.add_argument("--ref", type=str, help="Tekst referencyjny (oryginalny)")
    src.add_argument("--hyp", type=str, help="Tekst hipotezy (transkrypcja)")
    src.add_argument("--ref-file", type=str, help="Ścieżka do pliku z tekstem referencyjnym")
    src.add_argument("--hyp-file", type=str, help="Ścieżka do pliku z tekstem hipotezy")

    norm = parser.add_argument_group("Normalizacja")
    norm.add_argument("--no-lowercase", dest="lowercase", action="store_false", help="Nie zamieniaj na małe litery")
    norm.add_argument("--strip-punct", action="store_true", help="Usuń interpunkcję przed obliczeniami")
    norm.add_argument("--no-normalize-ws", dest="normalize_whitespace", action="store_false", help="Nie normalizuj białych znaków")

    serg = parser.add_argument_group("Ustawienia SER/CER")
    serg.add_argument("--sentence-split", choices=["simple", "newline"], default="simple", help="Metoda dzielenia na zdania dla SER")
    serg.add_argument("--cer-include-spaces", action="store_true", help="Uwzględniaj spacje w CER")

    args = parser.parse_args()

    ref_text, hyp_text = read_text_args(args)

    w, w_edits, w_ref = wer(
        ref_text,
        hyp_text,
        lowercase=args.lowercase if hasattr(args, "lowercase") else True,
        strip_punct=args.strip_punct,
        normalize_whitespace=args.normalize_whitespace if hasattr(args, "normalize_whitespace") else True,
    )

    s, s_err, s_tot = ser(
        ref_text,
        hyp_text,
        lowercase=args.lowercase if hasattr(args, "lowercase") else True,
        strip_punct=args.strip_punct,
        normalize_whitespace=args.normalize_whitespace if hasattr(args, "normalize_whitespace") else True,
        sentence_split=args.sentence_split,
    )

    c, c_edits, c_ref = cer(
        ref_text,
        hyp_text,
        lowercase=args.lowercase if hasattr(args, "lowercase") else True,
        strip_punct=args.strip_punct,
        normalize_whitespace=args.normalize_whitespace if hasattr(args, "normalize_whitespace") else True,
        include_spaces=args.cer_include_spaces,
    )

    def pct(x: float) -> str:
        return f"{x * 100:.2f}%"

    print("WER:", pct(w), f"(edits: {w_edits} / words: {w_ref})")
    print("SER:", pct(s), f"(error sentences: {s_err} / total sentences: {s_tot}; split={args.sentence_split})")
    print("CER:", pct(c), f"(edits: {c_edits} / chars: {c_ref}{' incl. spaces' if args.cer_include_spaces else ''})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
