model = get_model()
model.fit(x_train, y_train, epochs=130, batch_size=16, verbose=0)

test_mse, test_mae = model.evaluate(x_test, y_test)
predictions = model.predict(x_test)
print(f"test MAE {test_mae:.2f}   first prediction {predictions[0][0]:.2f}")
