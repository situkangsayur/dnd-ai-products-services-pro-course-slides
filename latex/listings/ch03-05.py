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
    predictions = model(inputs)
    loss = mean_squared_error(targets, predictions)
    loss.backward()        # 1. hitung gradien
    optimizer.step()       # 2. perbarui bobot
    model.zero_grad()      # 3. nolkan, siap batch berikutnya
    return loss
