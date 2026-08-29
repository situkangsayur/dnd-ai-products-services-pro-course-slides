import tensorflow as tf
from keras import optimizers

optimizer = optimizers.SGD(learning_rate=1e-3)

def one_training_step(model, images_batch, labels_batch):
    with tf.GradientTape() as tape:
        predictions = model(images_batch)                       # forward
        loss = ops.sparse_categorical_crossentropy(labels_batch, predictions)
        average_loss = ops.mean(loss)                           # loss
    gradients = tape.gradient(average_loss, model.weights)      # gradients
    optimizer.apply_gradients(zip(gradients, model.weights))    # update
    return average_loss
