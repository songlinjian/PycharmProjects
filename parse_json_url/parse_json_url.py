# encoding:utf-8

import urllib2
import urllib
import json
import ssl


# close the SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

f = open("out.txt", "w")
url = 'https://atlas.ripe.net/api/v2/measurements/8552181/results/?start=1494201600&stop=1495756799&format=json'
timeout = 3
while timeout > 0:
    try:
        atlas_html = urllib.urlopen(url).read()
    except urllib.error.HTTPError as e:
        print 'HTTPError'
        print(e.code)
    except urllib.error.URLError as e:
        print 'URLError'
        print(e.code)
    timeout = timeout-1

print >>f, atlas_html

f.close()

# atlas_JSON = json.loads(atlas_html)
#
# print atlas_JSON
