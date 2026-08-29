objective = kt.Objective(
    name="val_accuracy",
    direction="max",
)

tuner = kt.BayesianOptimization(
    build_model,
    objective=objective,
    ...
)
