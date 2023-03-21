import torch
import torch.nn as nn
from models.convolutional_models import CausalConvGenerator
from models.recurrent_models import LSTMGenerator

class ENIACGenerator(nn.Module):
    def __init__(self, in_dim, num_passwd = 6,type='lstm') -> None:
        
        super().__init__()
        if type == 'cnn':
            self.base_netG = CausalConvGenerator(noise_size=in_dim, output_size=num_passwd, n_layers=8, n_channel=10, kernel_size=8, dropout=0.2)
        else:
            self.base_netG = LSTMGenerator(in_dim=in_dim, out_dim=num_passwd, hidden_dim=32)

        
    def forward(self, input):
        import pdb
        pdb.set_trace()
        peaks = self.base_netG(input) # [batch_size, seq_len, num_peaks]

        return 1
        