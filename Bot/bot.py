from urllib import response
from cairo import Filter
from telegram import Update
import torch
from PTTBotModel import PTTBotModel
from tokenizer import Tokenizer
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

TOKEN = ""

class PTTBot():
    def __init__(self):
        self.updater = Updater(token=TOKEN, use_context=True)
        self.dispacher = self.updater.dispatcher
        self.dispacher.add_handler(MessageHandler(Filters.text, self.response))
        self.loadModel()

    def start(self):
        self.updater.start_polling()
        print("start...")
    
    def loadModel(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using {self.device} device")

        print("[INFO] 載入 tokenizer")
        self.tokenizer = Tokenizer()

        print("[INFO] 載入 model")
        self.model = PTTBotModel(self.tokenizer).to(self.device)
        self.model.load_state_dict(torch.load('./char_based_state.pt'))
    
    def predict(self, q):
        self.model.eval()
        QTokens = self.tokenizer.chars_to_tokens(q)
        QTokens = [ self.tokenizer.char_index['<sos>'] ] + QTokens + [ self.tokenizer.char_index['<end>'] ]
        lenq = len(QTokens)
        QTokens += [ self.tokenizer.char_index['<pad>'] ] * (40-len(QTokens))
        
        QTokens = torch.tensor(QTokens).unsqueeze(0)
        lenq = torch.tensor([lenq])
        lena = torch.tensor([])

        ans = []
        with torch.no_grad():
            QTokens = QTokens.to(self.device)

            a = [0]*30
            a[0] = 0        # <sos>
            a = torch.tensor(a).unsqueeze(0).to(self.device)

            for i in range(30):
                out = self.model(QTokens, a, lenq, lena)
                out = out.view(-1, out.shape[-1])
                out_predict = torch.argmax(out, dim=1)
                if i!=29:
                    a[0][i+1] = out_predict[i]

            words = self.tokenizer.tokens_to_chars(a[0])
            for word in words:
                if word not in ['<sos>', '<pad>', '<end>']:
                    ans.append(word)
        return ans


    def response(self, update, context):
        user = update.effective_chat
        q = update.message.text

        prediction = self.predict(q)
        
        msg = "".join(prediction)
        context.bot.send_message(
            chat_id=user.id,
            text=msg
        )

if __name__ == '__main__':

    bot = PTTBot()
    bot.start()
