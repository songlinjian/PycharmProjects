#!/usr/bin/env python
# coding: utf-8

import ConfigParser
import os
import re
import SocketServer

import dnslib
import gevent
from gevent import monkey

monkey.patch_all()
from gevent.queue import Queue
import pylru
import dns.message
import dns.rrset
import dns.query
import struct
import socket




# try dnspython module here
def dns_forward(dns_message):

    response = dns.query.tcp(dns_message, dns_default)
    # return a dns.message.Message object to wireformat data
    return response.to_wire()


# read the DNS wireformat data and reply
def handler(data, addr, sock):
    dns_message = dns.message.from_wire(data)
    qname = dns_message.question[0].name
     # 在LRUCache中查找缓存过域名的DNS应答包
    response = DNSServer.dns_cache.get(qname)

    print 'qname =', qname, 'response =', response

    # if response:
    # # 若应答已在缓存中，直接替换id后返回给用户
    #     response[:2] = data[:2]
    #     sock.sendto(response, addr)
    # else:
    #     # 若应答不在缓存中，forward 到默认的递归服务器中查询
    print 'forward the query to ', dns_default
    dns_response_wire = dns_forward(dns_message)

            #answers, soa = query(str(qname).rstrip('.'))
            #answer_dns = pack_dns(dns, answers, soa)

            # 将查询到的应答包放入LRUCache以后使用
    #DNSServer.dns_cache[qname] = dns_response_wire
            # 返回
    #sock.sendto(dns_response_wire, addr)
    print 'Accept new connection from : ', addr
    sock.sendall(dns_response_wire)


def _init_cache_queue():
    while True:
        data, addr, sock = DNSServer.deq_cache.get()
        print data
        gevent.spawn(handler, data, addr, sock)


class DNSHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # 若缓存队列没有存满，把接收到的包放进缓存队列中（存满则直接丢弃包）
        if not DNSServer.deq_cache.full():
            # from RFC1035: The message is prefixed with a two byte length field which gives the message length, excluding the two byte length field.
            wire_data =  self.request.recv(2048)
            print struct.unpack("h",socket.ntohs(wire_data[:2]))
            wire_message = wire_data[2:]
            print len(wire_message)
            # 缓存队列保存元组：(请求包，请求地址，sock)
            DNSServer.deq_cache.put(
                (wire_message, self.client_address[0], self.request))


class DNSServer(object):
    @staticmethod
    def start():
        # 缓存队列，收到的请求都先放在这里，然后从这里拿数据处理
        DNSServer.deq_cache = Queue(
            maxsize=deq_size) if deq_size > 0 else Queue()
        # LRU Cache，使用近期最少使用覆盖原则
        DNSServer.dns_cache = pylru.lrucache(lru_size)

        # 启动协程，循环处理缓存队列
        gevent.spawn(_init_cache_queue)

        # 启动DNS服务器
        print 'Start DNS server at %s:%d\n' % (ip, port)
        dns_server = SocketServer.TCPServer((ip, port), DNSHandler)
        dns_server.serve_forever()


def load_config(filename):
    with open(filename, 'r') as fc:
        cfg = ConfigParser.ConfigParser()
        cfg.readfp(fc)

    return dict(cfg.items('DEFAULT'))


if __name__ == '__main__':
    # 读取配置文件
    #config_file = os.path.basename(__file__).split('.')[0] + '.ini'
    config_file =  'apple_dns.ini'
    config_dict = load_config(config_file)

    ip, port = config_dict['ip'], int(config_dict['port'])
    deq_size, lru_size = int(
        config_dict['deq_size']), int(
        config_dict['lru_size'])
    db = config_dict['db']
    dns_default = config_dict['dns']

    # 启动服务器
    DNSServer.start()
