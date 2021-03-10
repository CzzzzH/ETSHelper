import plotly.graph_objects as go
import plotly.io as pio
import os

def get_query_pic(data, user_id):
    head_colors = ['rgb(255, 170, 170)', 'rgb(252, 219, 219)', 'rgb(255, 170, 170)', 'rgb(252, 219, 219)', 'rgb(255, 170, 170)']
    cell_colors = ['rgb(200, 210, 255)', 'rgb(219, 227, 252)', 'rgb(200, 210, 255)', 'rgb(219, 227, 252)', 'rgb(200, 210, 255)']
    cell_data = [[], [], [], [], []]
    for site in data:
        cell_data[0].append(site['time'].strftime('%Y-%m-%d %H:%M:%S') + " " + site['day'])
        cell_data[1].append(site['city'])
        cell_data[2].append(site['location'])
        cell_data[3].append(site['site'])
        if site['state'] == 0: cell_data[4].append('暂满')
        elif site['state'] == 1: cell_data[4].append('有位')
        else: cell_data[4].append('截止')
    layout = {
            'autosize' : True,
            'width' : 1000,
            'height' : 30 + 25 * len(data),
            'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0}
            }
    fig = go.Figure(data=[go.Table(
                        columnorder=[1, 2, 3, 4, 5],
                        columnwidth=[280, 100, 400, 120, 100],
                        header=dict(
                            values=[['<b>时间</b>'], ['<b>城市</b>'], ['<b>考场</b>'], ['<b>考点编号</b>'], ['<b>考位状态</b>']],
                            fill_color=head_colors,
                            height=30),
                        cells=dict(
                            values=cell_data,
                            fill_color=cell_colors,
                            height=25))],
                    layout=layout)
    #os.system('xvfb -run -a /root/orca-1.2.1-x86_64.AppImage "$@"')
    pio.write_image(fig, f'/root/MiraiOK/plugins/CQHTTPMirai/images/{user_id}.png', width=1000, height=30 + 25 * len(data), scale=1)
    #os.system('kill -9 $(pidof /root/orca-1.2.1-x86_64.AppImage)')
    #os.system('kill -9 $(pidof /tmp/.mount_orcaA5y95l/app/orca)')