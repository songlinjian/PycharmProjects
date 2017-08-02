# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Python
import plotly.plotly
import plotly.graph_objs as go

data = [
    go.Box(
        y=[0, 1, 1, 2, 3, 5, 8, 13, 21]  # 9个数据
    )
]
plotly.offline.plot(data)  # 离线绘图
