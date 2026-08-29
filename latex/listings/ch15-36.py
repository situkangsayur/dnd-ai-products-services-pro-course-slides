# source_mask marks the non-padding tokens: (batch_size, source_length)
source_mask = source != 0

# upranked inside the layer to broadcast across every target position
mask = source_mask[:, None, :]   # (batch_size, 1, source_length)
