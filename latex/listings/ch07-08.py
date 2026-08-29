# Mau menambah keluaran ketiga: taksiran kesulitan tiket.
# TIDAK perlu membangun dan melatih ulang dari nol.
features = model.layers[4].output          # lapis Dense antara tadi
difficulty = layers.Dense(3, activation="softmax", name="difficulty")(features)

new_model = keras.Model(
    inputs=[title, text_body, tags],
    outputs=[priority, department, difficulty])
