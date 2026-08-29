affine2(affine1(x)) == (W2 @ W1) @ x + (W2 @ b1 + b2)
#                     \_________/         \______________/
#                      one matrix           one vector
