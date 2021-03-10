from nonebot import on_command, CommandSession
from plot import get_query_pic
from aiocqhttp import MessageSegment
import json
import mysql.connector

@on_command('help', aliases=('HELP', '帮助'))
async def Help(session: CommandSession):
    res = "欢迎使用ETS Helper! \n" \
          "查询GRE/TOEFL考位请发送如下句子（参数之间用空格隔开）: \n" \
          "[查GRE/查TOEFL] [城市1] [城市2] ... [月份1] [月份2] ... \n" \
          "[例：查GRE 北京 上海 8月 9月] \n" \
          "开启/关闭考位变化通知推送请发送如下句子（参数之间用空格隔开）: \n" \
          "[开启考位通知/关闭考位通知] [TOEFL/GRE] [城市1] [城市2] ... [月份1] [月份2] ... \n" \
          "[例：开启考位通知 TOEFL 北京 上海 8月 9月] \n" \
          "** 若参数不填写城市/月份默认勾选所有城市/月份 ** \n" \
          "祝各位使用愉快~"
    await session.send(res)

@on_command('TEST_IMAGE')
async def GRE(session: CommandSession):
    await session.send(MessageSegment.image(f'/root/MiraiOK/plugins/CQHTTPMirai/images/test.jpg'))

@on_command('GRE', aliases=('查GRE', '查询GRE考位', 'GRE考位'))
async def GRE(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    user_id = session.ctx['user_id']
    condition = stripped_arg.split(' ')
    if condition[0] == '': condition = []
    await session.send("正在查询中，请耐心等候qwq...")
    res = await query_seats('GRE', condition, user_id)
    if res == '[图片]': await session.send(MessageSegment.image(f'/root/MiraiOK/plugins/CQHTTPMirai/images/{user_id}.png'))
    else:
        for buf in res: await session.send('\n'.join(buf))

@on_command('TOEFL', aliases=('查TOEFL', '查询TOEFL考位', 'TOEFL考位', '托福', '查托福', '查询托福考位', '托福考位'), privileged=True)
async def TOEFL(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    user_id = session.ctx['user_id']
    condition = stripped_arg.split(' ')
    if condition[0] == '': condition = []
    await session.send("正在查询中，请耐心等候qwq...")
    res = await query_seats('TOEFL', condition, user_id)
    if res == '[图片]': await session.send(MessageSegment.image(f'/root/MiraiOK/plugins/CQHTTPMirai/images/{user_id}.png'))
    else:
        print(res)
        for buf in res: await session.send('\n'.join(buf))

@on_command('开启考位通知')
async def open_notice(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if not stripped_arg or stripped_arg.split(' ')[0] != 'TOEFL' and stripped_arg.split(' ')[0] != 'GRE':
        await session.send("输入的参数不对呢，或许是忘了说考试类型? [例：开启考位通知 TOEFL 北京 上海 8月 9月] ")
    else:
        user_id = session.ctx['user_id']
        contest = stripped_arg.split(' ')[0]
        condition = stripped_arg.split(' ')[1:]
        with open(f'/root/ETSHelper/{contest}_userdata.json', 'r') as f:
            dic = json.load(f)
        dic[f'{user_id}'] = condition
        with open(f'/root/ETSHelper/{contest}_userdata.json', 'w') as f:
            json.dump(dic, f)
        await session.send("开启考位通知成功！")

@on_command('关闭考位通知')
async def close_notice(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if not stripped_arg or stripped_arg.split(' ')[0] != 'TOEFL' and stripped_arg.split(' ')[0] != 'GRE':
        await session.send("输入的参数不对呢，或许是忘了说考试类型? [例：关闭考位通知 TOEFL] ")
    else:
        user_id = session.ctx['user_id']
        contest = stripped_arg.split(' ')[0]
        with open(f'/root/ETSHelper/{contest}_userdata.json', 'r') as f:
            dic = json.load(f)
        if f'{user_id}' in dic: del dic[f'{user_id}']
        with open(f'/root/ETSHelper/{contest}_userdata.json', 'w') as f:
            json.dump(dic, f)
        await session.send("关闭考位通知成功！")

async def query_seats(exam, condition, user_id):

    # Use any database you like to store the info
    db = mysql.connector.connect(
        host="localhost",
        user="ETSHelper",
        password="_Yitiaoxianyu",
        database="ETS"
    )
    cursor = db.cursor(dictionary=True)
    cities = []
    months = []
    if exam == 'GRE': table = "GRE_seats"
    else: table = "TOEFL_seats"
    print(condition)
    for token in condition:
        if token[0].isdigit(): months.append("MONTH(time)=" + token[0:-1])
        else: cities.append("city= '" + token + "'")
    if len(cities) == 0 and len(months) == 0:
        syntax = f'SELECT * FROM {table} WHERE state=1 ORDER BY time;'
    elif (len(cities) == 0):
        time_condition = ' OR '.join(months)
        syntax = f'SELECT * FROM {table} WHERE ({time_condition}) AND state=1 ORDER BY time;'
    elif (len(months) == 0):
        city_condition = ' OR '.join(cities)
        syntax = f'SELECT * FROM {table} WHERE ({city_condition}) AND state=1 ORDER BY time;'
    else:
        city_condition = ' OR '.join(cities)
        time_condition = ' OR '.join(months)
        syntax = f'SELECT * FROM {table} WHERE ({city_condition}) AND ({time_condition}) AND state=1 ORDER BY time;'
    print(syntax)
    cursor.execute(syntax)
    res = cursor.fetchall()
    if (len(res) == 0): ans = [['没有查询到任何可以报名的考位！']]
    else:
        i = 0
        ans = [['查询结果如下：']]
        for data in res:
            i = i + 1
            if data['state'] == 0: data['state'] = '暂满'
            elif data['state'] == 1: data['state'] = '有位'
            else: data['state'] = '截止'
            if i % 10 == 0: ans.append([])
            ans[i // 10].append(f'{data["time"]} {data["day"]} {data["city"]} {data["location"]} {data["site"]} {data["state"]}')
    '''
    else:
        get_query_pic(res, user_id)
        return '[图片]'
    '''
    return ans