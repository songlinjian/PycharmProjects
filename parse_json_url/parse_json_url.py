# encoding:utf-8

import urllib2
import urllib
import json
import ssl


ssl._create_default_https_context = ssl._create_unverified_context  # close the SSL verification

f = open("out.txt", "w")
url = 'https://atlas.ripe.net/api/v2/measurements/8552181/results/?start=1494201600&stop=1495756799&format=json'
atlas_html = urllib.urlopen(url).read()


print >>f, atlas_html

f.close()

# atlas_JSON = json.loads(atlas_html)
#
# print atlas_JSON
