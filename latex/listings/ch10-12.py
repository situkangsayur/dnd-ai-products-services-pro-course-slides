# one number per channel: how important that channel is to the top class
pooled_grads = np.mean(grads, axis=(0, 1, 2))

last_conv_layer_output = last_conv_layer_output[0].copy()
for i in range(pooled_grads.shape[-1]):
    last_conv_layer_output[:, :, i] *= pooled_grads[i]      # weight each channel

heatmap = np.mean(last_conv_layer_output, axis=-1)          # average across channels
