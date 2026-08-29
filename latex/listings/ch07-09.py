class CustomerTicketModel(keras.Model):
    def __init__(self, num_departments):
        super().__init__()                       # jangan lupa konstruktor induknya
        self.concat_layer = layers.Concatenate()
        self.mixing_layer = layers.Dense(64, activation="relu")
        self.priority_scorer = layers.Dense(1, activation="sigmoid")
        self.department_classifier = layers.Dense(num_departments,
                                                  activation="softmax")

    def call(self, inputs):                      # lintasan maju ditulis di sini
        features = self.concat_layer(
            [inputs["title"], inputs["text_body"], inputs["tags"]])
        features = self.mixing_layer(features)
        return self.priority_scorer(features), self.department_classifier(features)
