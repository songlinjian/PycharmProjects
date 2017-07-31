# encoding:utf-8

import urllib2
import urllib
import json
import ssl


# close the SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

f = open("out.txt", "w")
url = 'https://atlas.ripe.net/api/v2/measurements/8552181/results/?start=1494201600&stop=1495756799&format=json'
url = 'http://songsearch.kugou.com/song_search_v2?keyword=周杰伦&pagesize=1'

timeout = 3
while timeout > 0:
    print timeout
    try:
        atlas_html = urllib.urlopen(url).read()
    except urllib.HTTPError as e:
        print 'HTTPError'
        print 'Error code: ', e.code
        print 'Error reason: ', e.reason
    except urllib.URLError as e:
        print 'URLError'
        print 'Error reason: ', e.reason
    else:
        print atlas_html
        print json.loads(atlas_html)
        break
    timeout = timeout - 1

f.close()

# atlas_JSON = json.loads(atlas_html)
#
# print atlas_JSON
