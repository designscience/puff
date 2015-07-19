""" This is the main module for Puff - which receives commands over Ethernet and turns cannon channels on or off """

from GPIOFireBank import GPIOFireChannel, GPIOFireBank
from socket import *
from time import sleep
from NaggingMother import NaggingMother
import threading
from Queue import Queue
from re import search
import sys
import getopt
import re

__author__ = 'Stu D\'Alessandro'


def parse_and_execute(data, bank):
    """
    Parses and executes commands from a data string
    :param data: command data from stream - may include more than one command or partial commands
    :param bank: GPIOFireBank object
    :return: remainder of data string (partial command) or empty string
    """
    pattern = re.compile("\$(\D+):(\d+)\|([0-9:]+)#")
    try:
        while True:
            message = pattern.search(data)
            if message is not None:
                command = message.group(1)
                version = message.group(2)
                params = message.group(3)
                data = data[message.end(0):]
                # print "Message end: {0} Command: {1}, params: {2}, data now {3}".format(message.end(0), command, params, data)
                execute(command, version, params, bank)
            else:
                data = ""
                break
    except KeyboardInterrupt:
        raise
    # print "Returning data: {0}".format(data)
    return data


def execute(cmnd, ver, paramz, bank):
    """
    Executes (or ignores) a command passed
    :param cmnd: the command verb
    :param ver: the command version (numeric)
    :param paramz: the command parameters (colon-delimited)
    :param bank: the GPIOFireBank object
    :return: True if command executed else false
    """
    # TODO: add version handling and more commands
    if cmnd == 'bnx':
        terms = paramz.split(':')
        try:
            count = int(terms[0])
            for i in range(1, count):
                bank.set_channel_state(i, int(terms[i]))
        except IndexError:
            print "Index out of range in execute()"


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
    channel_offset = 2  # channel_offset
    mssg = ""

    test_toggle = False

    # process command line arguments
    try:
        opts, args = getopt.getopt(argv, 'a:p:c:o:')
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
            print 'Number of channels set to {0}'.format(num_channels)
        elif opt == '-o':
            channel_offset = int(arg)
            print 'GPIO channel offset set to {0}'.format(channel_offset)

    # Set up fire banks
    fire_bank = GPIOFireBank(num_channels, 3, channel_offset)

    # setup watchdog on fire bank
    mom = NaggingMother()
    call_your_mother = Queue(16)
    watchdog = threading.Thread(target=mom, args=(fire_bank, call_your_mother))
    watchdog.start()

    # Open socket
    ss = socket(AF_INET, SOCK_STREAM)
    ss.bind(addr)
    while running:
        ss.listen(1)
        print "Listening on host {0}, port {1}".format(local_addr, port)
        try:
            cs, addr = ss.accept()  # blocking
        except (KeyboardInterrupt, SystemExit):
            break
        print 'Connected from client at addr'
        while True:
            try:
                mssg += cs.recv(bufsize)
            except error:
                print "Lost connection to host process. Waiting for new connection..."
                fire_bank.kill()
                break
            except (KeyboardInterrupt, SystemExit):
                running = False
                break
            if not mssg:
                print "Null data received."
                fire_bank.kill()
                break
            else:
                # print "Message: {0}".format(mssg)
                mssg = parse_and_execute(mssg, fire_bank)

        cs.close()
    ss.close()

    # shut down the watchdog thread
    call_your_mother.put('exit')
    print "Shutting down..."
    watchdog.join()
    return 0

if __name__ == '__main__':
    main(sys.argv[1:])
