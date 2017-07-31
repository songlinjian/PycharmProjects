# atlas_perse.py
# -*- coding: utf-8 -*-

"""
This program parse the atlas measurement result in json format.

Author : Davey@BII
"""

import json
import sys
import time
from datetime import datetime

# variable definition

START = 1494219600
END = 1495756799
Intervel = 7200

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
            print("Warnning : no connection")
            fail_r = 1
        else:
            fail_r = (float(num_timeout) / float(num_all))
        # print size
        return (fail_r, size, num_all, num_timeout, probe_set)

    def add(self, conn):
        self.measure_list.append(conn)

    def find_weak_prob(self):
        for i in self.probe_info:
            if i in [17901, 12786, 14544]:
                self.weak_probes_list.append(i)
                continue
            if float(self.probe_info[i]["num_failure"]) / float(self.probe_info[i]["num_conn"]) > 0.8:
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
                conn = {"src_addr": p["from"], "dst_addr": dst_addr, "timestamp": p[
                    "timestamp"], "prb_id": p["prb_id"], "rtt": 0, "p_size": 0, "status": "timeout"}
            elif status == '{"socket": "connect failed Network is unreachable"}':
                dst_addr = p["dst_name"]
                conn = {"src_addr": p["from"], "dst_addr": dst_addr, "timestamp": p[
                    "timestamp"], "prb_id": p["prb_id"], "rtt": 0, "p_size": 0, "status": "network unreachable"}
            else:
                dst_addr = "0::0"
                print("unkonw error")
                conn = {"src_addr": p["from"], "dst_addr": dst_addr, "timestamp": p[
                    "timestamp"], "prb_id": p["prb_id"], "rtt": 0, "p_size": 0, "status": "unknown"}

        else:  # no error
            dst_addr = p["dst_addr"]
            status = " rtt: " + str(p["result"]["rt"]) + \
                ", size=" + str(p["result"]["size"]) + \
                ", prb_id:" + str(p["prb_id"])
            #x = time.localtime(p["timestamp"])
            conn = {"src_addr": p["from"], "dst_addr": dst_addr, "timestamp": p["timestamp"], "prb_id": p[
                "prb_id"], "rtt": p["result"]["rt"], "p_size": p["result"]["size"], "status": "connected"}
        m.add(conn)
# Main definition


def timestamp2string(timeStamp):
    try:
        d = datetime.fromtimestamp(timeStamp)
        str1 = d.strftime("%Y-%m-%d %H:%M:%S.%f")
        # 2015-08-28 16:43:37.283000'
        return str1
    except Exception as e:
        print e
        return ''


def main(argv=None):
    if argv is None:
        argv = sys.argv
    data_home = unicode('E:\\工作\\Dev\\python\\Atlas\\bii\\data\\', "utf8")

    with open(data_home+'/RIPE-Atlas-measurement-8552768.json') as json_file:
        # json.load() convert json string to python tpye
        data = json.load(json_file)
    m = Measurement(8552181)
    build_measure(data, m)  # convert raw data into measure format
    m.find_weak_prob()
    # print len(m.measure_list)
    # print len(m.src_addr_dict)

    t = START
    while (t < END):
        rate, size, num_all, num_timeout, probe_set = m.failure_rate(
            t, t + Intervel)
        # print size , rate , datetime.fromtimestamp(t)
        print timestamp2string(t), size, rate, num_all, num_timeout, probe_set
        t = t + Intervel
        # print size ,rate
    # for i in m.probe_info:
    # print i, m.probe_info[i]["src_addr"], m.probe_info[i]["num_conn"],
    # m.probe_info[i]["num_failure"]
    print("the number of prb_id: ", len(m.probe_info))
    print("the number of weak probe: ", len(m.weak_probes_list))
    # print "there are " + str(i) + " measurements"
    # print "the Lenght of src_addr_dict: " + str(len(m.src_addr_dict))
    # print m.src_addr_dict


if __name__ == "__main__":
    sys.exit(main())

"""
Coding Reference

https://docs.python.org/3/library/datetime.html
http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001431937554888869fb52b812243dda6103214cd61d0c2000
http://blog.csdn.net/xiaobing_blog/article/details/12591917

"""
