import jittor as jt
from jittor import Module
from jittor import nn

class Model(Module):
    def __init__(self, width, height, num_class=26, num_char=4):
        super(Model, self).__init__()
        self.num_class = num_class
        self.num_char = num_char
        self.width = width
        self.height = height
        self.conv = nn.Sequential(  
            # Layer 1
            nn.Conv(3, 16, 3, padding=(1, 1)),
            nn.Pool(2, stride=2, op='maximum'),
            nn.BatchNorm(16),
            nn.ReLU(),
            nn.Dropout(),
            # Layer 2
            nn.Conv(16, 64, 3, padding=(1, 1)),
            nn.Pool(2, stride=2, op='maximum'),
            nn.BatchNorm(64),
            nn.ReLU(),
            nn.Dropout(),
            # Layer 3
            nn.Conv(64, 512, 3, padding=(1, 1)),
            nn.Pool(2, stride=2, op='maximum'),
            nn.BatchNorm(512),
            nn.ReLU(),
            nn.Dropout(),
            # Layer 4
            nn.Conv(512, 512, 3, padding=(1, 1)),
            nn.Pool(2, stride=2, op='maximum'),
            nn.BatchNorm(512),
            nn.ReLU(),
            nn.Dropout(),
        )
        self.first_full_connect = nn.Linear(512 * (width // 16) * (height // 16), 128 * (width // 16) * (height // 16))
        self.drop_out = nn.Dropout()
        self.second_full_connect = nn.Linear(128 * (width // 16) * (height // 16), self.num_class * self.num_char)
    
    def execute(self, x):
        x = self.conv(x)
        x = x.view(-1, 512 * (self.width // 16) * (self.height // 16))
        x = self.first_full_connect(x)
        x = self.drop_out(x)
        x = self.second_full_connect(x)
        return x
