import sys
import os
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

SENTIMENT_AVAILABLE = False
tokenizer = None
model = None
torch = None
F = None

LABELS = {0: "negative", 1: "neutral", 2: "positive"}

try:
    import torch as _torch
    import torch.nn.functional as _F
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    torch = _torch
    F = _F

    MODEL_ID = "Voicelab/herbert-base-cased-sentiment"
    logger.info("Loading sentiment model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    SENTIMENT_AVAILABLE = True
    logger.info("Sentiment model loaded successfully")
except ImportError as e:
    logger.warning(f"Sentiment analysis not available: {e}")
except Exception as e:
    logger.warning(f"Failed to load sentiment model: {e}")


class SentimentService:
    def __init__(self):
        if not SENTIMENT_AVAILABLE:
            raise ImportError(
                "Sentiment model not available. Install: uv pip install torch transformers"
            )

    def analyze(self, text: str) -> Tuple[str, float]:
        inputs = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        with torch.no_grad():
            logits = model(**inputs).logits

        scores = F.softmax(logits, dim=-1)[0]

        max_idx = scores.argmax().item()
        max_score = scores[max_idx].item()
        label = LABELS.get(max_idx, "neutral")

        return label, max_score


sentiment_service: Optional[SentimentService] = None


def get_sentiment_service() -> Optional[SentimentService]:
    global sentiment_service
    if sentiment_service is None and SENTIMENT_AVAILABLE:
        try:
            sentiment_service = SentimentService()
        except Exception:
            return None
    return sentiment_service


def analyze_sentiment(text: str) -> Optional[Tuple[str, float]]:
    service = get_sentiment_service()
    if service:
        return service.analyze(text)
    return None
