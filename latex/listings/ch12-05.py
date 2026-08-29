def to_grid(box):
    x, y, w, h = box
    cx, cy = (x + w / 2) * grid_size, (y + h / 2) * grid_size   # centre, in cells
    ix, iy = int(cx), int(cy)                                   # which cell
    return (ix, iy), (cx - ix, cy - iy, w, h)                   # offset within it

def from_grid(loc, box):
    (xi, yi), (x, y, w, h) = loc, box
    x = (xi + x) / grid_size - w / 2
    y = (yi + y) / grid_size - h / 2
    return (x, y, w, h)
