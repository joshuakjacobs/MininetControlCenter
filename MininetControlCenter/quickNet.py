#!/usr/bin/python
#__author__ = "Joshua K Jacobs, 2015"
#__email__ = "joshuajac.2011@my.bristol.ac.uk"

from mininet.net import Mininet
from mininet.node import Controller,RemoteController,RYU
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import re
import subprocess


def switchfinder(text):
    """Regex to locate switch-switch connections in user input
    Saves them as an array pair in an array

    :param text:
    :return:
    """
    m=re.findall('(s\d{1,5})', text)
    array=[[i] for i in m]
    iterator=iter(array)
    array2=[c+next(iterator)for c in iterator]
    return array2


def linkfinder(text):
    """Regex to find host-switch connections in user input
    Saves them as an array pair in an array

    :param text:
    :return:
    """
    m=re.findall('([sh]\d{1,5})', text)
    array = [[i] for i in m]
    iterator=iter(array)
    array3=[c+next(iterator)for c in iterator]
    return array3


def quickNet(switchnum,hostnum,links):

    """Main work function.
    Creates matching host/switch objects to their string names, stores them in dictionaries.
    Adds links by checking said dictionaries
    Creates the topology using the Mininet API

    :param switchnum:
    :param hostnum:
    :param links:
    """
    net = Mininet(controller=None, autoSetMacs=True)

    host=[]
    switch=[]

    hostdict={}
    switchdict={}

    info('*** Adding controller\n')
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633 )

    info('*** Adding hosts\n')
    for h in range(hostnum):
        host.append(h)
        host[h]= net.addHost('h%s' % (h + 1))
        hostdict[('h%s'%(h+1))]=host[h]

    info('*** Adding switch\n')
    for s in range(switchnum):
        switch.append(s)
        switch[s]=net.addSwitch('s%s' % (s + 1),protocols="OpenFlow13")
        switchdict[('s%s'%(s+1))]=switch[s]

    info('*** Creating links\n')
    for l in links:  # loops through switch and host dictionaries to check if any of them match the requires links
        nodeA= switchdict.get(l[0]) or switchdict.get(l[1]) or hostdict.get(l[0]) or hostdict.get(l[1])
        nodeB= hostdict.get(l[1]) or hostdict.get(l[0]) or switchdict.get(l[1]) or switchdict.get(l[0])

    try:
            net.addLink(nodeA, nodeB)
    except:
        print 'An error has occured connecting nodes,cleaning up and exiting'
        subprocess.call('sudo mn -c', shell=True)
        exit()

    info('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI( net )

    info('*** Stopping network')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    switchnum = int(raw_input('Enter number of switches needed:'))
    hostnum = int(raw_input('Enter number of hosts needed:'))
    links = raw_input('Enter all node links:\n')
    links = linkfinder(links)
    quickNet(switchnum, hostnum, links)



