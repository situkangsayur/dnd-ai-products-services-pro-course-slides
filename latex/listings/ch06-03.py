model.export("path/to/location",
             format="onnx")

ort_session = onnxruntime.InferenceSession(
    "path/to/location")
predictions = ort_session.run(None, input_data)
