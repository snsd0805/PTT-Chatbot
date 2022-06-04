import torch
import pickle

class Tokenizer():
    def __init__(self):
        with open('./char_index.pkl', 'rb') as fp:
            self.char_index = pickle.load(fp)
        with open('./index_char.pkl', 'rb') as fp:
            self.index_char = pickle.load(fp)
        
    def __len__(self):
        return len(self.char_index)

    def chars_to_tokens(self, chars):
        ans = []
        for ch in chars:
            if ch in self.char_index:
                ans.append( self.char_index[ch] )
            else:
                ans.append( self.char_index['<unk>'] )
        return ans
    
    def tokens_to_chars(self, tokens):
        if type(tokens) is torch.Tensor:
            tokens = tokens.tolist()
        ans = []
        for token in tokens:
            ans.append( self.index_char[token] )
        return ans
