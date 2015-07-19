"""
This module includes the classes for GPIO Fire channel control on a Raspberry Pi
GPIOFireChannel describes one channel and provides on-time checking and shutdown
GPIOFireBank describes a collection of GPIOFireChannel objects and runs a thread that checks each that it has
not been on for too long.
"""
import threading
from time import time

__author__ = 'Stu D\'alessandro'


# Install Raspberry Pi GPIO class
gpio_present = True
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Unable to import the Raspberry Pi GPIO library")
    gpio_present = False

max_channels = 24


class GPIOFireChannel:
    """ Manages one channel and timeouts"""
    def __init__(self, channel_num=0, channel_offset=2, max_on_time=3):
        """
        Sets channel defaults
        :param channel_num: GPIO channel number
        :param max_on_time: maximum time to allow the output to be turned on
        :return: channel number
        """
        self.cur_state = 0
        self.activated_at = 0  # the date time when this channel was activated
        self.gpio_channel = 0  # do nothing
        self.set_gpio_channel(channel_num)
        self.channel_offset = channel_offset
        self.max_on_time = float(max_on_time)
        self.set_state()

    def set_gpio_channel(self, channel_num):
        """
        Sets teh GPIO channel number to be managed by this object
        :param channel_num: GPIO channel number, 1-based
        :return: channel number
        """
        if channel_num > 0:
            self.gpio_channel = channel_num
        return self.gpio_channel

    def set_max_on_time(self, new_max_time=3):
        """
        Updates the max on time in seconds for this channel
        :param new_max_time: max on time in seconds for this channel
        :return: new max on time
        """
        self.max_on_time = float(new_max_time)
        return self.max_on_time

    def set_state(self, new_state=0):
        """
        Sets the channel on (1) or off (0)
        :param new_state: 0 or 1
        :return: current state
        """
        self.cur_state = 1 if new_state > 0 else 0

        # set or clear the activation time
        if self.cur_state > 0:
            self.activated_at = time()
        else:
            self.activated_at = 0

        if gpio_present:
            GPIO.output(self.gpio_channel - 1 + self.channel_offset, self.cur_state)

        return self.cur_state

    def assert_max_time(self):
        """
        Checks how long this channel has been on and turns it off if time has expired
        :return: state of this channel after this call
        """
        if self.activated_at > 0:
            now = time()
            if (now - self.activated_at) > self.max_on_time:
                self.set_state(0)
        return self.cur_state


class GPIOFireBank:
    """ Manages turning multiple rPI GPIO channels on and off.
    This class also enforces a maximum on-time for all channels """
    def __init__(self, num_channels=24, max_on_time=3):
        """
        :param num_channels: total number of channels to manage
        :param max_on_time: The maximum time that any channel may be on for
        :return: nil
        """
        self.channel_offset = 2  # Added to channel number to map to first used GPIO channel

        # Configure GPIO interface
        if gpio_present:
            GPIO.setmode(GPIO.BCM)  # GPIO.BCM for IO pins, GPIO.BOARD for connector pins
            GPIO.setwarnings(False)
            for ch in range(0, num_channels):
                GPIO.setup(ch + self.channel_offset, GPIO.OUT)

        self.num_channels = 0
        self.max_on_time = max_on_time
        self.channels = []
        for i in range(num_channels):
            ch = GPIOFireChannel(i, self.max_on_time)
            self.channels.append(ch)
            self.num_channels += 1

    def set_channel_state(self, channel_num, state):
        """
        TUrns one channel on or off
        :param channel_num: 1-based, from 1 to self.num_channels
        :param state: 0 - off, 1 - on
        :return: channel number or False
        """
        result = False
        if channel_num <= self.num_channels:
            self.channels[channel_num].set_state(state)
            result = channel_num
        return result

    def kill(self):
        """
        Turn all channels off
        :return: nil
        """
        for channel in self.channels:
            channel.set_state(0)

    def blow(self):
        """
        Turn all channels on (max on time applies)
        :return: nil
        """
        for channel in self.channels:
            channel.set_state(1)

    def set_max_on_time(self, new_max_time):
        """
        Updates the max time that channels will remain on
        :param new_max_time: new max on time in seconds
        :return: new max on time
        """
        for channel in self.channels:
            channel.set_max_on_time(new_max_time)
        return new_max_time

    def assert_max_on_time(self):
        """
        Checks all channels for max on time, forcing off if they exceed this time
        :return: nil
        """
        for channel in self.channels:
            channel.assert_max_time()
