from gre_seat import gre_run
from toefl_seat import toefl_run
import json
import time
import datetime
import os
import traceback

def update():

    print("Start Update !")
    # 更新GRE考位信息
    change_log = gre_run()
    os.system("kill -9 $(pidof /usr/local/bin/geckodriver)")
    os.system("kill -9 $(pidof /usr/lib/firefox/firefox)")
    while change_log == ['更新失败']:
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{time_stamp}] 更新失败，重试中...")
        change_log = gre_run()
        os.system("kill -9 $(pidof /usr/local/bin/geckodriver)")
        os.system("kill -9 $(pidof /usr/lib/firefox/firefox)")
        time.sleep(5)
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{time_stamp}] 更新成功\n {change_log}")
    with open("./GRE_changelog.json", "w") as f:
        json.dump(change_log, f)

    time.sleep(10)

    # 更新TOEFL考位信息
    change_log = toefl_run()
    os.system("kill -9 $(pidof /usr/local/bin/geckodriver)")
    os.system("kill -9 $(pidof /usr/lib/firefox/firefox)")
    while change_log == ['更新失败']:
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{time_stamp}] 更新失败，重试中...")
        change_log = toefl_run()
        os.system("kill -9 $(pidof /usr/local/bin/geckodriver)")
        os.system("kill -9 $(pidof /usr/lib/firefox/firefox)")
        time.sleep(5)
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{time_stamp}] 更新成功\n {change_log}")
    with open("./TOEFL_changelog.json", "w") as f:
        json.dump(change_log, f)

    time.sleep(10)

if __name__ == '__main__':
    while True:
        try:
            update()
            os.system("rm -rf /tmp/rust*")
        except:
            print(traceback.format_exc())
            os.system("kill -9 $(pidof /usr/local/bin/geckodriver)")
            os.system("kill -9 $(pidof /usr/lib/firefox/firefox)")
            os.system("rm -rf /tmp/rust*")
