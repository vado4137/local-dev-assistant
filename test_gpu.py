import torch
print(f"Ist CUDA verfügbar? {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Grafikkarte: {torch.cuda.get_device_name(0)}")
