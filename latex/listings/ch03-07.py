input_var = torch.tensor(3.0, requires_grad=True)
result = torch.square(input_var)
result.backward()                   # populates input_var.grad
print(input_var.grad)

input_var.grad = None               # REQUIRED — gradients accumulate otherwise
