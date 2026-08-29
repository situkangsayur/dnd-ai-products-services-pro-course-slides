model.compile(
    optimizer="adam",
    loss=["mean_squared_error",
          "sparse_categorical_crossentropy"],
    metrics=[["mean_absolute_error"],
             ["accuracy"]])

model.fit(
    [title_data, text_body_data, tags_data],
    [priority_data, department_data],
    epochs=1)
