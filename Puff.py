""" This is the main module for Puff - which receives commands over Ethernet and turns cannon channels on or off """

from GPIOFireBank import GPIOFireChannel, GPIOFireBank
from socket import *
import sys, getopt

__author__ = 'Stu D\'Alessandro'


def main(argv):
    """
    Initializes and runs the Puff program
    :return: 0 or 1
    """
    host = ''
    port = 4444
    bufsize = 1024
    addr = (host, port)

    # process command line arguments
    try:
        opts, args = getopt.getopt(argv, 'a:p:')
    except getopt.GetoptError:
        print 'Usage puff -a 192.168.1.144 -p 4444'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-a':
            host = arg
            print 'Using host address {0}'.format(host)
        elif opt == '-p':
            port = int(arg)
            print 'Using host port {0}'.format(port)

    banks = GPIOFireBank(18)

    # Open socket
    ss = socket(AF_INET, SOCK_STREAM)
    ss.bind(addr)
    ss.listen(1)
    while True:
        print "Listening on host {0}, port {1}".format(host, port)
        cs, addr = ss.accept() # blocking
        print 'Connected from client at addr'
        while True:
            mssg = cs.recv(bufsize)
            if not mssg:
                break
            else:
                print "Message: {0}".format(mssg)
            cs.send(mssg)
        cs.close()
    ss.close()
    return 0

if __name__ == '__main__':
    main(sys.argv[1:])
