random_train_labels = train_labels[:]        # copy
np.random.shuffle(random_train_labels)       # destroy every input-target relation

model.fit(train_images, random_train_labels,
          epochs=100, batch_size=128, validation_split=0.2)
