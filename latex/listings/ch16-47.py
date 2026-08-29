for prompts in dataset:
    responses = model.generate(prompts)
    rewards = reward_model.predict(responses)
    good_responses = []
    for response, score in zip(responses, rewards):
        if score > cutoff:
            good_responses.append(response)
    model.fit(good_responses)
