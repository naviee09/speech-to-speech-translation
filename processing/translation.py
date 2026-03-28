import torch
from config import Config


class TranslationEngine:
    def __init__(self, target_lang=Config.TARGET_LANGUAGE, use_api=False):
        self.target_lang = target_lang
        self.use_api = use_api
        self.model = None
        self.tokenizer = None

        if not use_api:
            try:
                self._load_model()
            except:
                self.use_api = True

    def _load_model(self):
        from transformers import MarianMTModel, MarianTokenizer
        model_name = f"Helsinki-NLP/opus-mt-mul-{self.target_lang}"
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate_local(self, text):
        if not self.model or not text:
            return text

        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = self.model.generate(**inputs)

        translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated

    def translate(self, text):
        if not text:
            return ""

        if self.use_api:
            return text
        else:
            return self.translate_local(text)