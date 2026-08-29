class WordTokenizer(CharTokenizer):
    def standardize(self, inputs):
        inputs = inputs.lower()
        return "".join(c for c in inputs if c not in string.punctuation)

    def split(self, inputs):
        return re.findall(r"\w+", inputs)
