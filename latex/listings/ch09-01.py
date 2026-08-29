x = ...                        # some input tensor
residual = x                   # save a reference: this is the residual
x = block(x)                   # this block may be destructive or noisy - fine
x = add([x, residual])         # the output now always retains the full input
