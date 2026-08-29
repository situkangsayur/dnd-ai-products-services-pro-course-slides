class LinearModel(torch.nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.W = torch.nn.Parameter(torch.rand(input_dim, output_dim))
        self.b = torch.nn.Parameter(torch.zeros(output_dim))

    def forward(self, inputs):
        return torch.matmul(inputs, self.W) + self.b

model = LinearModel(2, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

def training_step(inputs, targets):
    loss = mean_squared_error(targets, model(inputs))
    loss.backward()        # 1. compute gradients
    optimizer.step()       # 2. update the weights
    model.zero_grad()      # 3. clear, ready for the next batch
    return loss
