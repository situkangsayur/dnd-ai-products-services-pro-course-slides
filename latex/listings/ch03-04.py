import torch                      # paketnya 'torch', bukan 'pytorch'

x = torch.zeros(size=(2, 1))
x[0, 0] = 1.0                       # BISA ditugasi - beda dari TensorFlow

p = torch.nn.parameter.Parameter(data=x)      # penanda: ini keadaan terlatih

f = torch.cat((torch.ones((2, 2)), x), dim=0) # perhatikan: 'dim', bukan 'axis'

input_var = torch.tensor(3.0, requires_grad=True)
result = torch.square(input_var)
result.backward()                   # mengisi input_var.grad
print(input_var.grad)

input_var.grad = None               # WAJIB: gradien menumpuk kalau tidak dinolkan
