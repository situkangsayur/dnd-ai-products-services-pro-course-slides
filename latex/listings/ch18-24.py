# a fixed factor
optimizer = keras.optimizers.Adam(learning_rate=1e-3, loss_scale_factor=10)

# or let the optimizer work it out
optimizer = keras.optimizers.LossScaleOptimizer(
    keras.optimizers.Adam(learning_rate=1e-3)
)
