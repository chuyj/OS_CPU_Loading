#! /usr/bin/env python3
import os
import time
import json
import libvirt
import tornado.web
import tornado.gen
import tornado.ioloop
import tornado.process
from pprint import pprint

info = []
cput1 = {'Guest1': 0, 'Guest2': 0}
preTime = 1

def getState(state):
    if state == libvirt.VIR_DOMAIN_NOSTATE:
        return 'NOSTATE'
    elif state == libvirt.VIR_DOMAIN_RUNNING:
        return 'RUNNING'
    elif state == libvirt.VIR_DOMAIN_BLOCKED:
        return 'BLOCKED'
    elif state == libvirt.VIR_DOMAIN_PAUSED:
        return 'PAUSED'
    elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
        return 'SHUTDOWN'
    elif state == libvirt.VIR_DOMAIN_SHUTOFF:
        return 'SHUTOFF'
    elif state == libvirt.VIR_DOMAIN_CRASHED:
        return 'CASHED'
    elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
        return 'PMSUSPENDED'
    else:
        return 'UNKNOWN'

def getLoading():
    conn = libvirt.open('qemu:///system')
    domains = conn.listAllDomains()
    global info
    global preTime
    curTime  = time.time()
    delta = curTime - preTime
    preTime = curTime
    info = []
    cput2 = {}
    for domain in domains:
        name = domain.name()
        ID = domain.ID()
        ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        ip = ifaces['ens3']['addrs'][0]['addr']
        cpus = domain.maxVcpus()
        state, reason = domain.state()
        state = getState(state)
        cpu_stat = domain.getCPUStats(True)
        global cput1
        cput2[name] = cpu_stat[0]['cpu_time']
        loading = (cput2[name] - cput1[name]) / (10000000 * cpus * delta)
        loading = round(loading, 1)
        info.append({'ID':ID, 'Name':name, 'IP':ip, 'State':state, 'Loading':str(loading) + "%"})
    conn.close()
    return info, cput2

class LoadHandler(tornado.web.RequestHandler):
    #@tornado.web.asynchronous
    def get(self):
        self.write({"results":info})
    def post(self):
        ip = self.get_argument('ip', '0')
        loading = self.get_argument('loading', '0')
        time = self.get_argument('time', '0')
        self.finish()
        cmd = "./cpu_load_process.py -ip " + str(ip) + " -i " + str(loading) + " -t " + str(time)
        print(cmd)
        tornado.process.Subprocess(cmd.split())

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("./template/index.html", title="FUCK")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),    
        (r"/loading", LoadHandler),    
        (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": "template/images/"}),
        (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": "template/assets/"}),
    ])

def tick():
    global info, cput1
    info, cput1 = getLoading()

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.PeriodicCallback(tick, 1000).start();
    tornado.ioloop.IOLoop.current().start()
