# Prosty kalkulator WER / SER / CER

Ten projekt dostarcza prosty program w Pythonie do porównywania dwóch tekstów: referencyjnego (oryginalnego) i transkrybowanego (hipotezy), oraz obliczania metryk:

-   WER (Word Error Rate)
-   SER (Sentence Error Rate)
-   CER (Character Error Rate)

Bez zewnętrznych zależności — czysty Python 3.8+.

## Jak używać

Minimalny przykład (bez plików):

```bash
python3 cli.py --ref "Ala ma kota" --hyp "Ala ma kotka"
```

Z plikami:

```bash
python3 cli.py --ref-file ref.txt --hyp-file hyp.txt
```

Przydatne opcje:

-   `--strip-punct` – usuń interpunkcję przed obliczeniami
-   `--no-lowercase` – nie zamieniaj na małe litery
-   `--no-normalize-ws` – nie normalizuj białych znaków
-   `--sentence-split {simple,newline}` – metoda dzielenia na zdania dla SER (domyślnie `simple` dzieli po . ! ?)
-   `--cer-include-spaces` – licz CER razem ze spacjami (domyślnie spacje są ignorowane)

Uwaga dot. `--strip-punct` i SER: narzędzie najpierw dzieli tekst na zdania, a dopiero potem
stosuje usuwanie interpunkcji na poziomie zdań. Dzięki temu granice zdań nie znikają, nawet
jeśli włączysz `--strip-punct`. Jeżeli Twoje dane są wielozdaniowe w osobnych liniach, możesz
rozważyć `--sentence-split newline`.

## Definicje i założenia

-   WER: odległość Levenshteina na poziomie słów, podzielona przez liczbę słów w referencji.
-   CER: odległość Levenshteina na poziomie znaków, podzielona przez liczbę znaków w referencji (domyślnie bez spacji).
-   SER: odsetek zdań różniących się od odpowiadających im zdań hipotezy (porównywane 1:1 po indeksie). Liczba zdań w mianowniku pochodzi wyłącznie z referencji; brakujące zdania w hipotezie są liczone jako błędy; nadmiarowe zdania w hipotezie nie zwiększają mianownika.

### Puste przypadki (konwencje)

-   Jeśli referencja ma 0 słów/znaków/zdań:
    -   Jeżeli hipoteza też jest pusta – metryka zwraca 0.0
    -   W przeciwnym razie – metryka zwraca 1.0 (100%)

## Przykład

```bash
python3 cli.py --ref "Ala ma kota" --hyp "Ala ma kotka"
```

Wyjście (może się minimalnie różnić w zależności od normalizacji):

```
WER: 33.33% (edits: 1 / words: 3)
SER: 100.00% (error sentences: 1 / total sentences: 1; split=simple)
CER: 10.00% (edits: 1 / chars: 10)
```

## Struktura

-   `metrics.py` – implementacja metryk (Levenshtein, WER, SER, CER) i prosta normalizacja.
-   `cli.py` – interfejs wiersza poleceń.

## Wymagania

-   Python 3.8 lub nowszy

## Licencja

MIT
