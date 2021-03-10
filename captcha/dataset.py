import os
import jittor as jt
from PIL import Image
from jittor import dataset
from jittor import transform

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def img_loader(img_path):
    img = Image.open(img_path)
    return img.convert('RGB')

def make_dataset(data_path, alphabet, num_class, num_char):
    img_names = os.listdir(data_path)
    samples = []
    for img_name in img_names:
        img_path = os.path.join(data_path, img_name)
        label = img_name.split("_")[0]
        target = []
        for char in label:
            vec = [0] * num_class
            if (vec[0] < 0): print(vec)
            vec[alphabet.find(char)] = 1
            target += vec
        samples.append((img_path, target))
    return samples

class captcha_data(dataset.Dataset):
    def __init__(self, data_path, num_class=26, num_char=4,
                 transform=None, target_transform=None, alphabet=ALPHABET,
                 batch_size=64, shuffle=False, drop_last=True, num_workers=0):
        super().__init__()
        self.data_path = data_path
        self.num_class = num_class
        self.num_char = num_char
        self.transform = transform
        self.target_transform = target_transform
        self.alphabet = alphabet
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.drop_last = drop_last
        self.num_workers = num_workers
        self.samples = make_dataset(self.data_path, self.alphabet,
                                    self.num_class, self.num_char)
        length = len(self.samples)
        self.set_attrs(total_len=length)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        img_path, target = self.samples[index]
        img = img_loader(img_path)
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return img, target