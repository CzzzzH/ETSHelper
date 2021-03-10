import jittor as jt
import captcha.network
from jittor import nn
from jittor import transform
from captcha.dataset import captcha_data

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
jt.flags.use_cuda = 0

def predict(captcha_type, width, height, num_char=4, num_class=26):
    transforms = transform.Compose([transform.to_tensor])
    model_path = f'./captcha/model/{captcha_type}/model'
    predict_dataset = captcha_data('./captcha/predict', transform=transforms, batch_size=1,
                                 num_workers=0, shuffle=True, drop_last=True)

    model = captcha.network.Model(width, height)
    model.eval()
    model.load(model_path)
    for img, target in predict_dataset:
        output = model(img)
        output = output.view(-1, num_class)
        output = nn.softmax(output, dim=1)
        output = jt.argmax(output, dim=1)[0]
        output = output.view(-1, num_char)
        str = ''.join(ALPHABET[i] for i in output.data[0])
        return str

if __name__=="__main__":
    predict('TOEFL', 96, 30)
