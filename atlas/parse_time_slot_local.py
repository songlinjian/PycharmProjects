# atlas_perse.py
# -*- coding: utf-8 -*-

"""
This program parse the atlas measurement result in json format.

Author : Davey@BII
"""

import json
import sys
from datetime import datetime
import gc
import ssl
import os


# close the SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Constant
udp_measurement_set = [
    8552181,
    8552260,
    8552342,
    8552376,
    8552414,
    8552432,
    8552458,
    8552473,
    8552494,
    8552519,
    8552540,
    8552562,
    8552592,
    8552611,
    8552632,
    8552660,
    8552689,
    8552708,
    8552732,
    8552746,
    8552768,
    8552788,
    8552802,
    8552827,
    8552846]
START = 1494219600
END = 1495756799
Interval = 7200
Rate_gate =0.1

# Variable definition
Time_set = []
Rate_set = []
Num_m = 0

# Class definition


class Measurement:  # measurement for one server
    start_time = 1494219600
    end_time = 1495756799
    measure_list = []
    measure_id = 0
    # src_addr_dict = {} # {src_addr, num_connected}
    probe_info = {}  # {prb_id:{"src_addr":[], "num_conn","num_failure"}}
    weak_probes_list = []  # [prb_id]

    def __init__(self, id):
        self.measure_id = id
        self.measure_list = []
        self.probe_info = {}
        self.weak_probes_list = []

    def failure_rate(self, start, end):
        num_timeout = 0
        num_connected = 0
        num_unreach = 0
        num_unknown = 0
        num_all = 0
        size = 0
        probe_set = []
        for conn in self.measure_list:
            if self.weak_probes_list.count(conn["prb_id"]) == 1:
                continue
            if (conn["timestamp"] >= start) and (conn["timestamp"] < end):
                num_all = num_all + 1
                if size < conn["p_size"]:
                    size = conn["p_size"]
                if conn["status"] == "timeout":
                    if probe_set.count(conn["prb_id"]) == 0:
                        probe_set.append(conn["prb_id"])
                    num_timeout = num_timeout + 1
                elif conn["status"] == "connected":
                    num_connected = num_connected + 1
                elif conn["status"] == "network unreachable":
                    num_unreach = num_unreach + 1
                elif conn["status"] == "unknown":
                    num_unknown = num_unknown + 1
        if num_all == 0:
            # print("Warnning : no connection")
            fail_r = 1
        else:
            fail_r = (float(num_timeout) / float(num_all))
        # print size
        return fail_r, size, num_all, num_timeout, probe_set

    def add(self, conn):
        self.measure_list.append(conn)

    def find_weak_prob(self):
        for i in self.probe_info:
            if i in [17901, 12786, 14544]:
                self.weak_probes_list.append(i)
                continue
            if float(self.probe_info[i]["num_failure"]) / \
                    float(self.probe_info[i]["num_conn"]) > 0.8:
                self.weak_probes_list.append(i)
        return len(self.weak_probes_list)
# Function definition


def build_measure(data, m):
    for p in data:
        # if not(m.probe_info.has_key(p["prb_id"])): #has_key is the function
        # of dict in python2
        if not(p["prb_id"] in m.probe_info):
            # initialize the probe address in the dict
            m.probe_info[p["prb_id"]] = {"src_addr": [
                p["from"]], "num_conn": 1, "num_failure": 0}
        else:
            m.probe_info[p["prb_id"]]["num_conn"] += 1
            if m.probe_info[p["prb_id"]]["src_addr"].count(p["from"]) == 0:
                m.probe_info[p["prb_id"]]["src_addr"].append(p["from"])
        # if p.has_key("error"): # error
        if ("error" in p):
            m.probe_info[p["prb_id"]]["num_failure"] += 1
            # json.dumps() convert python tpye to json string
            status = json.dumps(p["error"])
            # got error status
            if status == '{"timeout": 5000}':
                dst_addr = p["dst_addr"]
                conn = {
                    "src_addr": p["from"],
                    "dst_addr": dst_addr,
                    "timestamp": p["timestamp"],
                    "prb_id": p["prb_id"],
                    "rtt": 0,
                    "p_size": 0,
                    "status": "timeout"}
            elif status == '{"socket": "connect failed Network is unreachable"}':
                dst_addr = p["dst_name"]
                conn = {
                    "src_addr": p["from"],
                    "dst_addr": dst_addr,
                    "timestamp": p["timestamp"],
                    "prb_id": p["prb_id"],
                    "rtt": 0,
                    "p_size": 0,
                    "status": "network unreachable"}
            else:
                dst_addr = "0::0"
                print("unkonw error")
                conn = {
                    "src_addr": p["from"],
                    "dst_addr": dst_addr,
                    "timestamp": p["timestamp"],
                    "prb_id": p["prb_id"],
                    "rtt": 0,
                    "p_size": 0,
                    "status": "unknown"}

        else:  # no error
            dst_addr = p["dst_addr"]
            status = " rtt: " + str(p["result"]["rt"]) + \
                ", size=" + str(p["result"]["size"]) + \
                ", prb_id:" + str(p["prb_id"])
            # x = time.localtime(p["timestamp"])
            conn = {
                "src_addr": p["from"],
                "dst_addr": dst_addr,
                "timestamp": p["timestamp"],
                "prb_id": p["prb_id"],
                "rtt": p["result"]["rt"],
                "p_size": p["result"]["size"],
                "status": "connected"}
        m.add(conn)
# Main definition


def timestamp2string(timeStamp):
    try:
        d = datetime.fromtimestamp(timeStamp)
        str1 = d.strftime("%Y-%m-%d %H:%M:%S")
        # 2015-08-28 16:43:37.283000'
        return str1
    except Exception as e:
        print e
        return ''


def print_time_slot(path):
    global Num_m, Time_set, Rate_set

    # consider the exception of network failure and timeout
    timeout = 3
    print "start to parse ", path
    with open(path) as json_file:
        # json.load() convert json string to python type
        data = json.load(json_file)
        if data[0]["proto"] == "TCP":
            return
        else:
            print "start to parse ", data[0]["msm_id"], data[0]["dst_addr"]
            Num_m += 1

    # build the measurement
    m = Measurement(data[0]["msm_id"])
    build_measure(data, m)  # convert raw data into measure format
    m.find_weak_prob()

    print("the number of prb_id: ", len(m.probe_info))
    print("the number of weak probe: ", len(m.weak_probes_list))
    print "the number of measurement", len(m.measure_list)

    # start to parse
    t = START
    i = 0
    while t < END:
        rate, size, num_all, num_timeout, probe_set = m.failure_rate(
            t, t + Interval)
        # print size , rate , datetime.fromtimestamp(t)
        # print timestamp2string(t), size, rate, num_all, num_timeout,
        # probe_set
        if Num_m == 1:
            Time_set.append(timestamp2string(t))
            if rate > Rate_gate and size <1200 :
                Rate_set.append([])
            else:
                Rate_set.append([[size, float('%.4f' % rate), m.measure_id]])
        else:
            if rate > Rate_gate and size <1200 :
                pass
            else:
                Rate_set[i].append([size, float('%.4f' % rate), m.measure_id])
        i += 1
        if i>150:
            break
        t += Interval
    del m, data, json_file
    gc.collect()


def main(argv=None):
    global Num_m, Time_set, Rate_set
    if argv is None:
        argv = sys.argv

    data_home = unicode('E:\\工作\\Dev\\python\\Atlas\\bii\\data\\', "utf8")
    # go through all files in a directory
    for root, dirs, files in os.walk(data_home):
        for filename in files:
            path = data_home + filename
            if int(
                filter(
                    str.isdigit,
                    filename.encode('gbk'))) in [
                8552432,
                8552458,
                8552519,
                    8552540]:
                continue
            else:
                print_time_slot(path)
    average = []
    for j in range(len(Rate_set)):
        summ = 0
        for i in Rate_set[j]:
            summ = summ + i[1]
            if len(Rate_set[j]) == 0:
                l = 0.01
            else:
                l = len(Rate_set[j])
        average.append([i[0], float('%.4f' % (float(summ) / l))])
    print 'the number of available measurement: ', Num_m
    for i in range(len(Rate_set)):
        # print Time_set[i], Rate_set[i], i, average[i][0], average[i][1]
        print Time_set[i], average[i][0], average[i][1]



if __name__ == "__main__":
    sys.exit(main())

"""
Coding Reference

https://docs.python.org/3/library/datetime.html
http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431937554888869fb52b812243dda6103214cd61d0c2000
http://blog.csdn.net/xiaobing_blog/article/details/12591917

"""
