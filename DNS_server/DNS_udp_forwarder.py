#!/usr/bin/env python
# coding: utf-8

import ConfigParser
from gevent.server import DatagramServer
from gevent import monkey
import dns.resolver
import dns.message
import dns.rrset
import dns.query
import dns.flags
import time
import socket
monkey.patch_all()


#
# try dnspython module here
def dns_forward(dns_message):

    ans = dns.query.udp(dns_message, dns_default)

    print ans.question[0].name
    for i in ans.answer:
        print i.to_text()
    # return a dns.message.Message object
    return ans

def truncate_ans(dns_message):
    # Make a message which is a response for the specified query. The message returned is really a response skeleton; it has all of the infrastructure required of a response, but none of the content.
    r = dns.message.make_response(dns_message, our_payload=512)
    # set TC bit
    r.flags += dns.flags.TC
    return r


# read the DNS wire format data and reply
def forward(data, addr, sock):
    dns_message = dns.message.from_wire(data)
    qname = dns_message.question[0].name
    qtype = dns_message.question[0].rdtype
    qclass = dns_message.question[0].rdclass
    # note: the id of the query(qid) should be record in case the query is hit
    # the cache. The id of the cached answer will be replace by this new qid
    qid = dns_message.id
    # check the cache
    ans = DNSServer.cache.get((qname, qtype, qclass))
    # if cache miss
    if ans is None:
        print 'Cache miss! Forward the query to', dns_default
        dns_ans = dns_forward(dns_message)
        ans = dns.resolver.Answer(qname, qtype, qclass, dns_ans)
        DNSServer.cache.put((qname, qtype, qclass), ans)
        print 'Cache max_size is :', DNSServer.cache.max_size
        print 'Cache len is :', len(DNSServer.cache.data)

    # if cache hit
    else:
        print 'Cache hit! Good!!!'
        ans.response.id = qid
    dns_ans_wire = ans.response.to_wire()
    UDP_DNS_wire = dns_ans_wire

    # if truncation or not
    qlen = len(dns_ans_wire)
    print 'qlen=', qlen
    if qlen <= 100:
        print 'qlen <= 100'
        sock.sendto(UDP_DNS_wire, addr)
    else:
        print 'qlen > 100, too big, truncate the response'
        trun_dns_ans = truncate_ans(dns_message)
        sock.sendto(UDP_DNS_wire, addr)
        print "fragmentation may be dropped"
        time.sleep(2)
        sock.sendto(trun_dns_ans.to_wire(), addr)


class DNSHandle(DatagramServer):
    def handle(self, message, address):
        # 若缓存队列没有存满，把接收到的包放进缓存队列中（存满则直接丢弃包）
        #wire_data = socket.recv(4096)
        forward(message, address, self.socket)

class DNSServer(object):
    @staticmethod
    def start():
        # 缓存队列，收到的请求都先放在这里，然后从这里拿数据处理
        DNSServer.cache = dns.resolver.LRUCache(lru_size)

        # 启动DNS服务器
        print 'Start DNS server at %s:%d\n' % (ip, port)
        # gevent example in https://github.com/gevent/gevent/blob/master/examples/udp_server.py
        DNSHandle(':9953').serve_forever()



def load_config(filename):
    with open(filename, 'r') as fc:
        cfg = ConfigParser.ConfigParser()
        cfg.readfp(fc)

    return dict(cfg.items('DEFAULT'))


if __name__ == '__main__':
    # 读取配置文件
    timer = 0
    config_file = 'apple_dns.ini'
    config_dict = load_config(config_file)

    ip, port = config_dict['ip'], int(config_dict['port'])
    deq_size, lru_size = int(
        config_dict['deq_size']), int(
        config_dict['lru_size'])
    db = config_dict['db']
    dns_default = config_dict['dns']

    # 启动服务器
    DNSServer.start()
