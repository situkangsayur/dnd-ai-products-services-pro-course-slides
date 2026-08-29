def fit(model, images, labels, epochs, batch_size=128):
    for epoch in range(epochs):
        print(f"Epoch {epoch}")
        gen = BatchGenerator(images, labels, batch_size)
        for i in range(gen.num_batches):
            images_batch, labels_batch = gen.next()
            loss = one_training_step(model, images_batch, labels_batch)
            if i % 100 == 0:
                print(f"  loss at batch {i}: {loss:.2f}")
