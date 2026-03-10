import numpy as np
import torch


print(np.array([1, 2, 3, 4, 5]))

print(torch.tensor([1, 2, 3, 4, 5]))

print(torch.tensor([1, 2, 3, 4, 5]).numpy())

print(torch.tensor([1, 2, 3, 4, 5]).tolist())

print(torch.tensor([1, 2, 3, 4, 5]).to(torch.float32))

print(torch.tensor([1, 2, 3, 4, 5]).to(torch.float64))

print(torch.tensor([1, 2, 3, 4, 5]).to(torch.int32))

print(torch.tensor([1, 2, 3, 4, 5]).to(torch.int64))