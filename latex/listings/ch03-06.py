import torch                      # the package is 'torch', not 'pytorch'

x = torch.zeros(size=(2, 1))
x[0, 0] = 1.0                       # ASSIGNABLE — unlike TensorFlow

p = torch.nn.parameter.Parameter(data=x)     # marks this as trained state

f = torch.cat((torch.ones((2, 2)), x), dim=0)   # note: 'dim', not 'axis'
