# encoding:utf-8

"""
This program parse the atlas measurement result in json format.

Author : Davey@BII
"""

import json
import sys
import urllib
import urllib2
import gc
import ssl

# close the SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# constant definition

START = 1494219600
END = 1495756799
Interval = 7200
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

# variable definition
Size_con = {}
Size_fail = {}


# Class definition
# measurement for one server


class Measurement:
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
            # print("Warning : no connection")
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
        if not (p["prb_id"] in m.probe_info):
            # initialize the probe address in the dict
            m.probe_info[p["prb_id"]] = {"src_addr": [
                p["from"]], "num_conn": 1, "num_failure": 0}
        else:
            m.probe_info[p["prb_id"]]["num_conn"] += 1
            if m.probe_info[p["prb_id"]]["src_addr"].count(p["from"]) == 0:
                m.probe_info[p["prb_id"]]["src_addr"].append(p["from"])
        # if p.has_key("error"): # error
        if "error" in p:
            m.probe_info[p["prb_id"]]["num_failure"] += 1
            # json.dumps() convert python type to json string
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
                print("unknown error")
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
            # status = " rtt: " + str(p["result"]["rt"]) + \
            #    ", size=" + str(p["result"]["size"]) + \
            #    ", prb_id:" + str(p["prb_id"])

            conn = {
                "src_addr": p["from"],
                "dst_addr": dst_addr,
                "timestamp": p["timestamp"],
                "prb_id": p["prb_id"],
                "rtt": p["result"]["rt"],
                "p_size": p["result"]["size"],
                "status": "connected"}
        m.add(conn)


def parse_print(url):
    timeout = 3
    print "start to parse ", url
    while timeout > 0:
        try:
            json_file = urllib2.urlopen(url).read()
        except urllib2.HTTPError as e:
            print 'HTTPError'
            print 'Error code: ', e.code
            print 'Error reason: ', e.reason
        except urllib2.URLError as e:
            print 'URLError'
            print 'Error reason: ', e.reason
        else:
            break
        timeout = timeout - 1
    if timeout < 0:
        return
    # json.load() convert json string to python type
    data = json.loads(json_file)
    if data[0]["proto"] == "TCP":
        print "Error : TCP was found"
        return
    else:
        print "start to parse ", data[0]["msm_id"], data[0]["dst_addr"]
    m = Measurement(data[0]["msm_id"])
    build_measure(data, m)  # convert raw data into measure format
    m.find_weak_prob()

    t = START
    size_all = {}
    size_timeout = {}
    while t < END:
        rate, size, num_all, num_timeout, probe_set = m.failure_rate(
            t, t + Interval)
        if size in size_all:
            size_all[size] += num_all
            size_timeout[size] += num_timeout
        else:
            size_all[size] = num_all
            size_timeout[size] = num_timeout
        if size in Size_con:
            Size_con[size] += num_all
            Size_fail[size] += num_timeout
        else:
            Size_con[size] = num_all
            Size_fail[size] = num_timeout
        # print size , rate , datetime.fromtimestamp(t)
        t = t + Interval
    size_all.pop(0)
    size_timeout.pop(0)
    print size_all
    print size_timeout
    # print size_all, size_timeout
    for i in size_all:
        print "Failure rate (", i, ") : ", float(size_timeout[i]) / float(size_all[i])
    print "the number of prb_id: ", len(m.probe_info)
    print "the number of weak probe: ", len(m.weak_probes_list)
    del m, data, json_file
    gc.collect()


# Main definition


def main(argv=None):
    if argv is None:
        argv = sys.argv

    # go through all links in Atlas
    for msm_id in udp_measurement_set:
        if msm_id in [8552432, 8552458]:
            continue
        else:
            url = 'https://atlas.ripe.net/api/v2/measurements/%s/results/' \
                  '?start=1494201600&stop=1495756799&format=json' % msm_id
            parse_print(url)
    Size_con.pop(0)
    Size_fail.pop(0)
    for i in Size_con:
        print "Failure rate (", i, ") : ", Size_fail[i], Size_con[i], float(Size_fail[i]) / float(Size_con[i])


if __name__ == "__main__":
    sys.exit(main())
