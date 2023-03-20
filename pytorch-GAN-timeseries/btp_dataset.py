import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
import pandas as pd
import numpy as np
import pickle


class BtpDataset(Dataset):
    """Btp time series dataset."""
    def __init__(self, csv_file, normalize=True):
        """
        Args:
            csv_file (string): path to csv file
            normalize (bool): whether to normalize the data in [-1,1]
        """
        df = pd.read_csv(csv_file, sep=";")
        df['Timestamp'] = pd.to_datetime(df["data_column"].map(str) + " " + df["orario_column"], dayfirst=True)
        df = df.drop(['data_column', 'orario_column'], axis=1).set_index("Timestamp")
        btp_price = df.BTP_Price
        import pdb
        pdb.set_trace()
        data = torch.from_numpy(np.expand_dims(np.array([group[1] for group in btp_price.groupby(df.index.date)]), -1)).float()
        self.data = self.normalize(data) if normalize else data
        self.seq_len = data.size(1)
        
        #Estimates distribution parameters of deltas (Gaussian) from normalized data
        original_deltas = data[:, -1] - data[:, 0]
        self.original_deltas = original_deltas
        self.or_delta_max, self.or_delta_min = original_deltas.max(), original_deltas.min() 
        deltas = self.data[:, -1] - self.data[:, 0]
        self.deltas = deltas
        self.delta_mean, self.delta_std = deltas.mean(), deltas.std()
        self.delta_max, self.delta_min = deltas.max(), deltas.min()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def normalize(self, x):
        """Normalize input in [-1,1] range, saving statics for denormalization"""
        self.max = x.max()
        self.min = x.min()
        return (2 * (x - x.min())/(x.max() - x.min()) - 1)
    
    def denormalize(self, x):
        """Revert [-1,1] normalization"""
        if not hasattr(self, 'max') or not hasattr(self, 'min'):
            raise Exception("You are calling denormalize, but the input was not normalized")
        return 0.5 * (x*self.max - x*self.min + self.max + self.min)
    
    def sample_deltas(self, number):
        """Sample a vector of (number) deltas from the fitted Gaussian"""
        return (torch.randn(number, 1) + self.delta_mean) * self.delta_std
    
    def normalize_deltas(self, x):
        return ((self.delta_max - self.delta_min) * (x - self.or_delta_min)/(self.or_delta_max - self.or_delta_min) + self.delta_min)
    

class ENIACDataset(BtpDataset):
    def __init__(self, data_path, normalize=True):
        with open(data_path, 'rb') as f:
            X, y = pickle.load(f)
        
        data = [torch.from_numpy(np.sum(x, -1)).float().unsqueeze(-1) for x in X]
        self.data = [self.normalize(x) for x in data] if normalize else data
        self.seq_len = min([x.size(1) for x in data])
    
    @staticmethod
    def collate_fn(samples):
        batch = pad_sequence(samples).permute(1, 0, 2)
        return batch