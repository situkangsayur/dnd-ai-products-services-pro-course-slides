heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)

heatmap = np.uint8(255 * heatmap)
jet_colors = cm.get_cmap("jet")(np.arange(256))[:, :3]
jet_heatmap = keras.utils.array_to_img(jet_colors[heatmap])
jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
jet_heatmap = keras.utils.img_to_array(jet_heatmap)

superimposed_img = jet_heatmap * 0.4 + img
keras.utils.array_to_img(superimposed_img).save("elephant_cam.jpg")
