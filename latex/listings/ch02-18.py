import tensorflow as tf
from keras import optimizers

optimizer = optimizers.SGD(learning_rate=1e-3)

def one_training_step(model, images_batch, labels_batch):
    with tf.GradientTape() as tape:
        predictions = model(images_batch)
        loss = ops.sparse_categorical_crossentropy(labels_batch, predictions)
        average_loss = ops.mean(loss)
    gradients = tape.gradient(average_loss, model.weights)
    optimizer.apply_gradients(zip(gradients, model.weights))
    return average_loss

def fit(model, images, labels, epochs, batch_size=128):
    for epoch in range(epochs):
        print(f"Epoch {epoch}")
        gen = BatchGenerator(images, labels, batch_size)
        for i in range(gen.num_batches):
            images_batch, labels_batch = gen.next()
            loss = one_training_step(model, images_batch, labels_batch)
            if i % 100 == 0:
                print(f"  loss at batch {i}: {loss:.2f}")
