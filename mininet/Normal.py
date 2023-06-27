from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep

from datetime import datetime
from random import randrange, choice

class MyTopo(Topo):
    def build(self):
        switches = []
        hosts = []

        for i in range(7):
            switch = self.addSwitch('s{}'.format(i + 1), cls=OVSKernelSwitch, protocols='OpenFlow13')
            switches.append(switch)

        for i in range(8):
            host = self.addHost('h{}'.format(i + 1), cpu=1.0/20, mac="00:00:00:00:00:0{}".format(i + 1), ip="10.0.0.{}/24".format(i + 1))
            hosts.append(host)

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])
        self.addLink(hosts[2], switches[1])
        self.addLink(hosts[3], switches[1])
        self.addLink(hosts[4], switches[2])
        self.addLink(hosts[5], switches[2])
        self.addLink(hosts[6], switches[3])
        self.addLink(hosts[7], switches[3])

        self.addLink(switches[0], switches[4])
        self.addLink(switches[1], switches[4])
        self.addLink(switches[2], switches[5])
        self.addLink(switches[3], switches[5])
        self.addLink(switches[4], switches[6])
        self.addLink(switches[5], switches[6])

def ip_generator():
    ip = ".".join(["10", "0", "0", str(randrange(1, 9))])
    return ip
        
def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.0.101', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)
    net.start()
    
    hosts = [net.get('h{}'.format(i + 1)) for i in range(8)]    
    print("--------------------------------------------------------------------------------")    
    print("Generating traffic ...")    
    hosts[0].cmd('cd /home/mininet/webserver')
    hosts[0].cmd('sudo python3 -m http.server 80 &')
    hosts[0].cmd('iperf -s -p 5050 &')
    hosts[0].cmd('iperf -s -u -p 5051 &')
    sleep(2)
    for host in hosts:
        host.cmd('cd /home/mininet/Downloads')
        
    for i in range(600):
        print("--------------------------------------------------------------------------------")    
        print("Iteration n {} ...".format(i + 1))
        print("--------------------------------------------------------------------------------") 
        
        for j in range(8):
            src = choice(hosts)
            dst = ip_generator()
            
            if j < 7:
                print("Generating ICMP traffic between {} and h{} and TCP/UDP traffic between {} and h1".format(src, (dst.split('.'))[3], src))
                src.cmd("ping {} -c 100 &".format(dst))
                src.cmd("iperf -p 5050 -c 10.0.0.1")
                src.cmd("iperf -p 5051 -u -c 10.0.0.1")
            else:
                print("Generating ICMP traffic between {} and h{} and TCP/UDP traffic between {} and h1".format(src, (dst.split('.'))[3], src))
                src.cmd("ping {} -c 100".format(dst))
                src.cmd("iperf -p 5050 -c 10.0.0.1")
                src.cmd("iperf -p 5051 -u -c 10.0.0.1")
            
            print("{} downloading index.html from h1".format(src))
            src.cmd("wget http://10.0.0.1/index.html")
            print("{} downloading test.zip from h1".format(src))
            src.cmd("wget http://10.0.0.1/test.zip")
        
        hosts[0].cmd("rm -f *.* /home/mininet/Downloads")
        
    print("--------------------------------------------------------------------------------")  
    net.stop()

if __name__ == '__main__':
    start = datetime.now()
    setLogLevel('info')
    startNetwork()
    end = datetime.now()
    print(end - start)
