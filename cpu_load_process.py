#! /usr/bin/env python3

import os
import sys
import libvirt
import argparse
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('-ip', required=True)
parser.add_argument('-i', required=True, type=int)
parser.add_argument('-t', required=True)

args = parser.parse_args()

conn = libvirt.open('qemu:///system')
domains = conn.listAllDomains()
for domain in domains:
    ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    if ifaces['ens3']['addrs'][0]['addr'] == args.ip or domain.name() == args.ip:
        cpus = domain.maxVcpus()
        cmd = 'ssh ' + args.ip + ' "cpulimit -q -l ' + str(cpus * args.i) + ' -- ~/stress ' + args.t + '"'
        os.system(cmd)
conn.close()

