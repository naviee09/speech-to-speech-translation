import torch
from config import Config


class LanguageIdentifier:
    def __init__(self, use_api=False):
        self.use_api = use_api
        self.model = None
        self.tokenizer = None

        if not use_api:
            try:
                self._load_model()
            except:
                self.use_api = True

    def _load_model(self):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        model_name = "papluca/xlm-roberta-base-language-detection"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

    def identify_local(self, text):
        if not self.model:
            return 'en', 0.5

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            confidence, pred = torch.max(probs, dim=-1)

        language_map = self.model.config.id2label
        return language_map[pred.item()], confidence.item()

    def identify(self, text):
        if self.use_api:
            return 'en', 0.5
        else:
            return self.identify_local(text)