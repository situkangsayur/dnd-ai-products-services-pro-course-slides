keras.distribution.list_devices()
# ["gpu:0", "gpu:1", ...]

keras.distribution.set_distribution(
    keras.distribution.DataParallel(["gpu:0", "gpu:1"])
)
