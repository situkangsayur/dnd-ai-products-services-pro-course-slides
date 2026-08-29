model.export("path/to/location",
             format="tf_saved_model")

reloaded = tf.saved_model.load("path/to/location")
predictions = reloaded.serve(input_data)
