""" This is the main module for Puff - which receives commands over Ethernet and turns cannon channels on or off """

from GPIOFireBank import GPIOFireChannel, GPIOFireBank
from socket import *
from time import sleep
from NaggingMother import NaggingMother
import threading
from Queue import Queue
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
    local_addr = gethostbyname(gethostname())
    running = True # keep running until this is set false
    num_channels = 18

    test_toggle = False

    # process command line arguments
    try:
        opts, args = getopt.getopt(argv, 'a:p:c:')
    except getopt.GetoptError:
        print 'Usage puff -a 192.168.1.144 -p 4444 -c 24'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-a':
            host = arg
            local_addr = arg
            print 'Using host address {0}'.format(host)
        elif opt == '-p':
            port = int(arg)
            print 'Using host port {0}'.format(port)
        elif opt == '-c':
            num_channels = int(arg)
            print 'Number of channels set to {0)'.format(num_channels)

    # Set up fire banks
    banks = GPIOFireBank(num_channels)

    # TODO: testing only, remove!
    banks.blow()
    sleep(1)
    banks.kill()

    # setup watchdog on fire bank
    mom = NaggingMother()
    call_your_mother = Queue(16)
    watchdog = threading.Thread(target=mom, args=(banks, call_your_mother))
    watchdog.start()

    # Open socket
    ss = socket(AF_INET, SOCK_STREAM)
    ss.bind(addr)
    while running:
        ss.listen(1)
        print "Listening on host {0}, port {1}".format(local_addr, port)
        cs, addr = ss.accept() # blocking
        print 'Connected from client at addr'
        while True:
            try:
                mssg = cs.recv(bufsize)
            except error:
                print "Lost connection to host process. Waiting for new connection..."
                break
            if not mssg:
                print "Null data received. Stopping program."
                running = False
                break
            else:
                print "Message: {0}".format(mssg)

            # TODO: testing only. Replace with message processing
            cs.send(mssg)
            if test_toggle:
                banks.blow()
            else:
                banks.kill()
            test_toggle = not test_toggle
        cs.close()
    ss.close()

    # shut down the watchdog thread
    call_your_mother.put('exit')
    print "Shutting down..."
    watchdog.join()
    return 0

if __name__ == '__main__':
    main(sys.argv[1:])
