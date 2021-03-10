from gre_seat import gre_run
from toefl_seat import toefl_run
import nonebot
import json

@nonebot.scheduler.scheduled_job('interval', seconds=30)
async def get_seats_change():

    def filter(change_log, condition):
        months = []
        cities = []
        for token in condition:
            if token[0].isdigit(): months.append(token[0:-1])
            else: cities.append(token)
        new_change_log = []
        for item in change_log:
            content = item.split(" ")
            if (len(content) < 2): new_change_log.append(item)
            else:
                month = content[0].split('-')[1]
                if (len(cities) == 0 or content[3] in cities) and (len(months) == 0 or month in months) : new_change_log.append(item)
        return new_change_log

    bot = nonebot.get_bot()
    exams = ['GRE', 'TOEFL']
    space_list = []
    for exam in exams:
        with open(f'./{exam}_changelog.json', 'r') as f:
            change_log = json.load(f)
        with open(f'./{exam}_changelog.json', 'w') as f:
            json.dump(space_list, f)

        if len(change_log) > 1:
            with open(f'./{exam}_userdata.json', 'r') as f:
                dic = json.load(f)
            for (user_id, condition) in dic.items():
                msg = filter(change_log, condition)
                if len(msg) > 1: await bot.send_private_msg(user_id=int(user_id), message='\n'.join(msg))
