"""
Checks the max timeout on a bank periodically
"""

from time import sleep

__author__ = 'Stu D\'Alessandro'


class NaggingMother(object):
    """
    Does something every half second until something comes over a queue
    """
    def __init__(self):
        self.q = None
        self.bank = None

    def __call__(self, bank, event_queue):
        self.bank = bank
        self.q = event_queue

        while True:
            if self.q.empty() is False:
                break
            self.bank.assert_max_on_time()
            sleep(0.5)
