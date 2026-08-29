import keras_hub

backbone = keras_hub.models.Backbone.from_preset("...")
backbone.enable_lora(rank=8)
