import jittor as jt
import network
from jittor import Module
from jittor import nn
from jittor import transform
from dataset import captcha_data

captcha_type = 'TOEFL' # GRE / TOEFL
batch_size = 64
base_learning_rate = 0.001
max_epoch = 200
model_path = f'./model/{captcha_type}/model.pth'
num_class = 26
num_char = 4
img_width = 96
img_height = 30
jt.flags.use_cuda = 0

def calculat_acc(output, target):
    output, target = output.view(-1, num_class), target.view(-1, num_class)
    output = nn.softmax(output, dim=1)
    output = jt.argmax(output, dim=1)[0]
    target = jt.argmax(target, dim=1)[0]
    output, target = output.view(-1, num_char), target.view(-1, num_char)
    pic_correct = word_correct = 0
    for i in range(batch_size):
        flag = True
        for j in range(num_char):
            if jt.ops.equal(output[i][j], target[i][j]).data[0] == True: word_correct = word_correct + 1
            else: flag = False
        if flag == True: pic_correct = pic_correct + 1
    return pic_correct / batch_size, word_correct / (batch_size * num_char)

def train():
    transforms = transform.Compose([transform.to_tensor])
    train_dataset = captcha_data(f'./data/{captcha_type}/train', transform=transforms, batch_size=batch_size, num_workers=0, shuffle=True, drop_last=True)
    eval_dataset = captcha_data(f'./data/{captcha_type}/eval', transform=transforms,  batch_size=batch_size, num_workers=0, shuffle=True, drop_last=True)
    model = network.Model(width=img_width, height=img_height)
    optimizer = jt.optim.Adam(model.parameters(), lr=base_learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    for epoch in range(max_epoch):
        print(f'Epoch: {epoch + 1}')
        loss_history = []
        word_acc_history = []
        pic_acc_history = []
        model.train()
        for img, target in train_dataset:
            img = jt.array(img)
            target = jt.array(target)
            output = model(img)
            target = jt.transpose(target)
            loss = criterion(output, target)
            optimizer.step(loss)
            pic_acc, word_acc = calculat_acc(output, target)
            word_acc_history.append(word_acc)
            pic_acc_history.append(pic_acc)
            loss_history.append(loss.data[0])
        print("训练集：")
        print(f'当前损失率: {jt.array(loss_history).mean()}')
        print(f'当前字母准确率: {jt.array(word_acc_history).mean()}')
        print(f'当前图片准确率: {jt.array(pic_acc_history).mean()}\n')

        loss_history = []
        word_acc_history = []
        pic_acc_history = []
        model.eval()
        for img, target in eval_dataset:
            img = jt.array(img)
            target = jt.array(target)
            output = model(img)
            target = jt.transpose(target)
            loss = criterion(output, target)
            pic_acc, word_acc = calculat_acc(output, target)
            word_acc_history.append(word_acc)
            pic_acc_history.append(pic_acc)
            loss_history.append(loss.data[0])
        print("验证集：")
        print(f'当前损失率: {jt.array(loss_history).mean()}')
        print(f'当前字母准确率: {jt.array(word_acc_history).mean()}')
        print(f'当前图片准确率: {jt.array(pic_acc_history).mean()}\n')

        model.save(model_path)

if __name__=="__main__":
    train()
