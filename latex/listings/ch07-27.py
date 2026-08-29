loss_fn = keras.losses.SparseCategoricalCrossentropy()
loss_tracker = keras.metrics.Mean(name="loss")

class CustomModel(keras.Model):
    def train_step(self, data):
        inputs, targets = data
        with tf.GradientTape() as tape:
            predictions = self(inputs, training=True)   # self, bukan model
            loss = loss_fn(targets, predictions)
        gradients = tape.gradient(loss, self.trainable_weights)
        self.optimizer.apply(gradients, self.trainable_weights)
        loss_tracker.update_state(loss)
        return {"loss": loss_tracker.result()}          # nama metrik -> nilainya

    @property
    def metrics(self):
        return [loss_tracker]      # didaftarkan agar reset_state() dipanggil otomatis
                                   # di awal tiap epoch dan di awal evaluate()
