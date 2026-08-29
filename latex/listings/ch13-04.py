sampling_rate = 6        # one sample per hour (data is every 10 minutes)
sequence_length = 120    # five days of hourly readings
delay = sampling_rate * (sequence_length + 24 - 1)

train_dataset = keras.utils.timeseries_dataset_from_array(
    raw_data[:-delay],
    targets=temperature[delay:],
    sampling_rate=sampling_rate,
    sequence_length=sequence_length,
    shuffle=True,
    batch_size=256,
    start_index=0,
    end_index=num_train_samples,
)
