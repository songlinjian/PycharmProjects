# encoding: utf-8
# bar.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab
from matplotlib import rcParams

# function defination

# 标上数值


def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.,
                 1.03 * height, '%s' % float(height))


def set_bar_color(z_list, barlist):
    for i, rname in enumerate(z_list):
        if rname == 'bii.yeti-dns.org.':
            barlist[i].set_color('b')
        elif rname == 'wide.yeti-dns.org.':
            barlist[i].set_color('r')
        elif rname == 'tisf.yeti-dns.org.':
            barlist[i].set_color('y')


def plot_bar(x_list, y_list, z_list, soa):
    # m_y_list= [x/60 for x in y_list]
    fig1 = plt.figure(2)
    plt.ylabel("latency(min)")
    rects = plt.bar(range(len(y_list)), [y + 10 for y in y_list], width=0.8)
    set_bar_color(z_list, rects)
    # plt.legend((rects,),(u"WIDE",u"BII","TISF"))
    autolabel(rects)
    plt.title('the latency of SOA-' + soa + ' update')
    # plt.xticks(rotation=30)
    plt.xticks(range(len(y_list)), x_list)
    fig1.autofmt_xdate()  # 自动调节x label的斜率
    plt.show()
    # plt.savefig('figure-'+soa+'.png')