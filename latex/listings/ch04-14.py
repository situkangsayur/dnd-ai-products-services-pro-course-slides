model = get_model()
model.fit(x_train, y_train, epochs=130,
          batch_size=16, verbose=0)
mse, mae = model.evaluate(x_test, y_test)
