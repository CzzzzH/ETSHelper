

# ETSHelper

A useful QQ chatbot used for querying  GRE/TOEFL test seats in mainland China.


### Introduction

The bot is based on [Nonebot](https://github.com/howmanybots/onebot) (A asynchronous framework of QQ chatbot) and [Jittor](https://github.com/Jittor/Jittor) (A Just-in-time(JIT) deep learning framework). The former provides communication services for the bot , and the latter helps crack captcha on the website.

### Usage

1. You need construct dataset with captcha data on the official test registration website and [install Jittor](https://cg.cs.tsinghua.edu.cn/jittor/download/). Then train the model.
2. Start to get GRE/TOEFL test seats status with gre_seat.py / toefl_seat.py. Selenium and mysql is required in this process..
3. Deploy your own QQ chatbot with software supported by Nonebot.  (e.g. [Mirai](https://github.com/mamoe/mirai))
4. Run bot.py to start the query service.

### Demo 
You can add the demo bot (QQ:2758720749) for instant querying service.

**This bot is currently unavailable in terms of the change of the ETS official website, so the bot and this repository is waiting for update. **

<img src="./demo.JPG" alt="demo" style="zoom: 33%;" />