import nonebot
import config

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_plugin("query_seats.py")
    nonebot.load_plugin("notice.py")
    nonebot.run()
