model = get_model()
model.fit(data, ...)                          # all non-test data
test_score = model.evaluate(test_data, ...)   # touched once, here
