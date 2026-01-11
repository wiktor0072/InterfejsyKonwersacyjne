import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import sys

# --- KONFIGURACJA ---
# Wybieramy tylko jeden, solidny model do sentymentu od VoiceLab
MODEL_ID = "Voicelab/herbert-base-cased-sentiment"

# Mapowanie wyników modelu
LABELS = {
    0: "NEGATYWNY",
    1: "NEUTRALNY",
    2: "POZYTYWNY"
}

EMOJIS = {
    "NEGATYWNY": "👎",
    "NEUTRALNY": "😐",
    "POZYTYWNY": "👍"
}

print("⏳ Ładowanie modelu sentymentu...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    print("✅ Gotowe!")
except Exception as e:
    print(f"❌ Błąd: {e}")
    sys.exit(1)


def predict_sentiment(text):
    # Tokenizacja
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        logits = model(**inputs).logits

    # Przeliczenie na procenty
    scores = F.softmax(logits, dim=-1)[0]

    results = []
    for i, score in enumerate(scores):
        label = LABELS.get(i, f"KLASA_{i}")
        results.append((label, score.item() * 100))

    # Sortowanie od najbardziej prawdopodobnego
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def print_results(text, results):
    top_label, top_prob = results[0]
    top_emoji = EMOJIS.get(top_label, "")

    print("\n" + "═" * 50)
    print(f"📄 TEKST: \"{text}\"")
    print("─" * 50)
    print(f"💎 WYNIK: {top_emoji} {top_label} ({top_prob:.1f}%)")
    print("─" * 50)

    for label, prob in results:
        bar_len = int(20 * prob / 100)
        bar = '█' * bar_len + '░' * (20 - bar_len)
        prefix = "👉" if prob == top_prob else "  "
        print(f"{prefix} {label:<10} [{bar}] {prob:.1f}%")
    print("═" * 50)


def main_loop():
    print("\n✍️  Program do analizy sentymentu. Wpisz tekst (lub 'q').")

    while True:
        try:
            user_input = input("\n📝 Tekst: ").strip()

            if user_input.lower() in ['q', 'exit', 'koniec']:
                print("Do widzenia!")
                break

            if not user_input:
                continue

            wyniki = predict_sentiment(user_input)
            print_results(user_input, wyniki)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ Błąd: {e}")


if __name__ == "__main__":
    main_loop()