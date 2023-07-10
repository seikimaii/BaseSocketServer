import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as ex
from datetime import datetime, timedelta
import pandas as pd
import datashader as ds
from datashader import transfer_functions as tf

# 創建Dash應用程式
app = dash.Dash(__name__)

import numpy as np
N = int(1e6) # Number of points

# df = pd.DataFrame(dict(x=np.arange(N),
#                        y=np.arange(N)))
# print(df.head())


# 创建一个示例数据集
gt = [datetime(2023, 7, 10, 14, 31, 0) - timedelta(seconds=i) for i in range(N)]
x = np.array(gt, dtype=np.datetime64)#[1,2,3,4,5]
# y = np.arange(N)
y = np.random.random(N) * 300#[1,2,3,4,5]
# z = [[1, 2, 3, 4, 5],
#      [6, 7, 8, 9, 10],
#      [11, 12, 13, 14, 15],
#      [16, 17, 18, 19, 20],
#      [21, 22, 23, 24, 25]]

df = pd.DataFrame(dict(x=x, y=y))

# 使用Datashader创建热力图
# cvs = ds.Canvas(plot_width=400, plot_height=400)
# agg = cvs.polygons(df, 'x', 'y')



# 创建Plotly图表
fig = go.Figure()

# 创建一个热力图的Plotly图像对象
scatter = go.Scatter(x=x, y=y, mode='lines')

# 将Datashader的图像添加为Plotly图表的背景图像
# fig.add_layout_image(
#     dict(
#         source=img.data,
#         xref="x",
#         yref="y",
#         x=0,
#         y=0,
#         sizex=img.shape[1],
#         sizey=img.shape[0],
#         sizing="stretch",
#         opacity=1,
#         layer="below"
#     )
# )

# 添加热力图到图表中
fig.add_trace(scatter)

# 显示图表
# fig.show()


# 創建Layout並添加散點圖
layout = go.Layout(
    title='Real-time Scatter Chart',
    xaxis=dict(
        rangeslider=dict(visible=True, thickness=0.1, range=[datetime(2023, 7, 10, 14, 31, 0) - timedelta(seconds=N), datetime(2023, 7, 10, 14, 31, 0)]),
        # range=[-1, int(1e6)+10]
    ),
    hovermode='x unified',
    # yaxis=dict(
    #     title='Value'
    # )
)
# fig.update_layout(dragmode="zoom")

# 創建Figure並設定Layout和資料
# fig = go.Figure(data=[data], layout=layout)

# fig = ex.imshow(agg)

# 在Dash中顯示散點圖
app.layout = html.Div(children=[
    dcc.Graph(
        id='scatter-chart',
        figure=fig
    )
])

# 監聽圖表的縮放事件
@app.callback(
    dash.dependencies.Output('scatter-chart', 'figure'),
    [dash.dependencies.Input('scatter-chart', 'relayoutData')], prevent_initial_call=True
)
def update_chart(relayout_data):
    print(relayout_data)
    # {'xaxis.range[0]': 283308.15917625854, 
    #  'xaxis.range[1]': 366775.1704122136, 
    #  'yaxis.range[0]': 0.4752995904628925, 
    #  'yaxis.range[1]': 0.755134547081599}
    if 'autosize' in relayout_data or 'xaxis.autorange' in relayout_data:
        # 首次載入圖表時，不做任何改變
        df2 = df.set_index('x').asfreq('1D')
        x = df2.index
        y = df2.y
        updated_data = go.Scatter(
                    x=x,
                    y=y,
                    mode='lines'
                )
        updated_fig = go.Figure(data=[updated_data], layout=layout)
        print("HAHAHAH")
        return updated_fig
    

    else:
        # 檢查是否有縮放事件發生
        if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
            x_range_start = relayout_data['xaxis.range[0]']
            x_range_end = relayout_data['xaxis.range[1]']
        
        elif 'xaxis.range' in relayout_data:
            x_range_start = relayout_data['xaxis.range'][0]
            x_range_end = relayout_data['xaxis.range'][1]
            
        else:
            return fig
        x_range_start = pd.Timestamp(x_range_start)
        x_range_end = pd.Timestamp(x_range_end)
        x_range_duration = x_range_end - x_range_start

        df2 = df.set_index('x')
        mask = (df2.index < x_range_end) & (df2.index > x_range_start)
        df2 = df2[mask]
        print(x_range_duration)

        if x_range_duration < timedelta(hours=2):
            # 縮放到一小時範圍內，顯示每秒的資料
            # mask = (df['x'].values > x_range_start) & (df['x'] < x_range_end) & (df['x'].values % 2 ==0)
            df2 = df2.asfreq('30S')
            pass
        
        elif x_range_duration < timedelta(hours=24):
            # mask = (df['x'].values > x_range_start) & (df['x'] < x_range_end) & (df['x'].values % 10 == 0)
            df2 = df2.asfreq('1T')

        elif x_range_duration < timedelta(days=7):
            # 縮放到六小時範圍內，顯示每分鐘的資料
            # mask = (df['x'].values > x_range_start) & (df['x'] < x_range_end) & (df['x'].values % 20 ==0)
            df2 = df2.asfreq("1H")

        elif x_range_duration < timedelta(days=30):
            # mask = (df['x'].values > x_range_start) & (df['x'] < x_range_end) & (df['x'].values % 60 ==0)
            df2 = df2.asfreq("6H")
        elif x_range_duration < timedelta(weeks=5):
            # mask = (df['x'].values > x_range_start) & (df['x'] < x_range_end) & (df['x'].values % 400 ==0)
            df2 = df2.asfreq("1D")
        else:
            # 縮放超過六小時，顯示每小時的資料
            # mask = (df['x'].values > x_range_start) & (df['x'] < x_range_end) & (df['x'].values % 2500 ==0)
            df2 = df.set_index('x').asfreq('1D')
            pass

        # 更新圖表的資料
        x = df2.index
        y = df2.y
        updated_data = go.Scatter(
                                    x=x,
                                    y=y,
                                    mode='lines'
                                )
        updated_fig = go.Figure(data=[updated_data], layout=layout)
        return updated_fig
        
        

if __name__ == '__main__':
    app.run_server(debug=True)
