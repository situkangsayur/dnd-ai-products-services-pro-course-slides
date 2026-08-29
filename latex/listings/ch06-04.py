model.quantize("int8")      # compress each weight down to a single byte
model.export("path/to/location", format="onnx")
