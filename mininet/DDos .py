from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
from datetime import datetime
from random import randrange, choice

class MyTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s4 = self.addSwitch('s4', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s5 = self.addSwitch('s5', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s6 = self.addSwitch('s6', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s7 = self.addSwitch('s7', cls=OVSKernelSwitch, protocols='OpenFlow13')

        h1 = self.addHost('h1', ip="10.0.0.1/24")
        h2 = self.addHost('h2', ip="10.0.0.2/24")
        h3 = self.addHost('h3', ip="10.0.0.3/24")
        h4 = self.addHost('h4', ip="10.0.0.4/24")
        h5 = self.addHost('h5', ip="10.0.0.5/24")
        h6 = self.addHost('h6', ip="10.0.0.6/24")
        h7 = self.addHost('h7', ip="10.0.0.7/24")
        h8 = self.addHost('h8', ip="10.0.0.8/24")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(h5, s3)
        self.addLink(h6, s3)
        self.addLink(h7, s4)
        self.addLink(h8, s4)
        self.addLink(s1, s5)
        self.addLink(s2, s5)
        self.addLink(s3, s6)
        self.addLink(s4, s6)
        self.addLink(s5, s7)
        self.addLink(s6, s7)

def ip_generator():
    ip = ".".join(["10", "0", "0", str(randrange(1, 9))])
    return ip

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.0.101', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h5 = net.get('h5')
    h6 = net.get('h6')
    h7 = net.get('h7')
    h8 = net.get('h8')

    hosts = [h1, h2, h3, h4, h5, h6, h7, h8]

    h1.cmd('cd /home/mininet/webserver')
    h1.cmd('sudo python3 -m http.server 80 &')

    src = choice(hosts)
    dst = ip_generator()
    print("--------------------------------------------------------------------------------")
    print("Performing ICMP (Ping) Flood")
    print("--------------------------------------------------------------------------------")
    src.cmd("timeout 20s hping3 -1 -V -d 120 -w 64 -p 80 --rand-source --flood {}".format(dst))
    sleep(100)

    src = choice(hosts)
    dst = ip_generator()
    print("--------------------------------------------------------------------------------")
    print("Performing UDP Flood")
    print("--------------------------------------------------------------------------------")
    src.cmd("timeout 20s hping3 -2 -V -d 120 -w 64 --rand-source --flood {}".format(dst))
    sleep(100)

    src = choice(hosts)
    dst = ip_generator()
    print("--------------------------------------------------------------------------------")
    print("Performing TCP-SYN Flood")
    print("--------------------------------------------------------------------------------")
    src.cmd('timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 10.0.0.1')
    sleep(100)

    src = choice(hosts)
    dst = ip_generator()
    print("--------------------------------------------------------------------------------")
    print("Performing LAND Attack")
    print("--------------------------------------------------------------------------------")
    src.cmd("timeout 20s hping3 -1 -V -d 120 -w 64 --flood -a {} {}".format(dst, dst))
    sleep(100)
    print("--------------------------------------------------------------------------------")

    net.stop()

if __name__ == '__main__':
    start = datetime.now()
    setLogLevel('info')
    startNetwork()
    end = datetime.now()
    print(end - start)
