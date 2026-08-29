activations = activation_model.predict(img_tensor)   # a list of nine arrays

first_layer_activation = activations[0]
print(first_layer_activation.shape)

import matplotlib.pyplot as plt
plt.matshow(first_layer_activation[0, :, :, 5], cmap="viridis")   # the sixth channel
