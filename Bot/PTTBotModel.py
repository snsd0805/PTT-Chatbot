import torch
from torch import nn
from torch.utils.data import DataLoader

class PTTBotModel(nn.Module):
    def __init__(self, tokenizer):
        super(PTTBotModel, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=len(tokenizer), embedding_dim=300, padding_idx=2)
        self.encoder = nn.LSTM(input_size=300, hidden_size=1024, batch_first=True)
        self.decoder = nn.LSTM(input_size=300, hidden_size=1024, batch_first=True)
        self.dense = nn.Linear(in_features=1024, out_features=len(tokenizer))
        self.dropout03 = nn.Dropout(0.3)
        self.dropout05 = nn.Dropout(0.5)
    
    def forward(self, q, a, lenq, lena):
        # (BATCH, 40)
        q = self.embedding(q)
        # (BATCH, 40, 300)

        # (BATCH, 30)
        a = self.embedding(a)
        # (BATCH, 30, 300)

        q = self.dropout03(q)
        a = self.dropout03(a)

        q = nn.utils.rnn.pack_padded_sequence(q, lenq, batch_first=True, enforce_sorted=False)
        out, (h, c) = self.encoder(q)
        

        h = self.dropout03(h)
        c = self.dropout03(c)
        # (BATCH, 30, 512) for output
        # (1, BATCH, 512) for h (最後一個 hidden state)
        # (1, BATCH, 512) for c (最後一個 cell state)
        out, (h, c) = self.decoder(a, (h, c))

        # (BATCH, 30, 1024) for output
        out = self.dense( self.dropout05(out) )

        return out 
