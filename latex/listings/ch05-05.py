k = 3
num_validation_samples = len(data) // k
np.random.shuffle(data)
validation_scores = []

for fold in range(k):
    validation_data = data[num_validation_samples * fold :
                           num_validation_samples * (fold + 1)]
    training_data = np.concatenate(
        [data[: num_validation_samples * fold],
         data[num_validation_samples * (fold + 1) :]])

    model = get_model()            # a BRAND-NEW, untrained model every fold
    model.fit(training_data, ...)
    validation_scores.append(model.evaluate(validation_data, ...))

validation_score = np.average(validation_scores)
