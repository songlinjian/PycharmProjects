# encoding:utf-8

"""
This program parse the atlas measurement result in json format.

Author : Davey@BII
"""

import json
import sys
import os
import gc

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
