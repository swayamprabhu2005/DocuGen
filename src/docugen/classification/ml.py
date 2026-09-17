"""Optional traditional CPU-friendly ML classifier using scikit-learn."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("docugen.classification.ml")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MLDocumentClassifier:
    """Optional document type classifier based on TF-IDF and Naive Bayes."""

    def __init__(self) -> None:
        self._pipeline: Optional[Any] = None
        self._is_trained = False

    @property
    def is_available(self) -> bool:
        """Check if scikit-learn is installed in current Python environment."""
        return SKLEARN_AVAILABLE

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def train(self, training_data: List[Tuple[Dict[str, Any], str]]) -> None:
        """Train the classifier on (input_dict, document_type) pairs."""
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for ML classification. Install it with `pip install docugen-ai[ml]`."
            )

        texts: List[str] = []
        labels: List[str] = []

        for data, doc_type in training_data:
            text_repr = " ".join(f"{k} {v}" for k, v in data.items() if isinstance(v, (str, int, float)))
            texts.append(text_repr)
            labels.append(doc_type)

        self._pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", MultinomialNB()),
            ]
        )
        self._pipeline.fit(texts, labels)
        self._is_trained = True

    def predict(self, data: Dict[str, Any]) -> Optional[Tuple[str, float]]:
        """Predict document type from input dictionary."""
        if not self._is_trained or not self._pipeline:
            return None

        text_repr = " ".join(f"{k} {v}" for k, v in data.items() if isinstance(v, (str, int, float)))
        preds = self._pipeline.predict([text_repr])
        probs = self._pipeline.predict_proba([text_repr])
        best_prob = max(probs[0])
        return str(preds[0]), float(best_prob)
