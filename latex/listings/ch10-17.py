embedding_model = keras.Model(inputs=model.input,
                              outputs=model.layers[-2].output)   # before the classifier
embeddings = embedding_model.predict(dataset)

from sklearn.manifold import TSNE
projected = TSNE(n_components=2, init="pca").fit_transform(embeddings)

plt.scatter(projected[:, 0], projected[:, 1], c=labels, s=4, cmap="coolwarm")
