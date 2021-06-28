#!/usr/bin/env python
from .lib import Scaffold
import sys
from zmq import DEALER, POLLIN, RCVMORE, ROUTER, SNDMORE, ZMQError


__author__ = 'neoinsanity'
__all__ = ['RouterDealerWindmill']
#
# req-rep-broker-windmill
#

class RouterDealerWindmill(Scaffold):
    """

    """


    def __init__(self, **kwargs):
        # setup the initial default settings
        self.router_sock_url = 'tcp://*:8888'
        self.dealer_sock_url = 'tcp://*:8889'

        self._router_sock = None
        self._dealer_sock = None

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser

        arg_parser.add_argument('--router_sock_url',
                                default=self.router_sock_url,
                                help="Set the url address for router.")
        arg_parser.add_argument('--dealer_sock_url',
                                default=self.dealer_sock_url,
                                help='Set the url address for dealer')


    def configure(self, args=None):
        assert args

        router_sock = self.zmq_ctx.socket(ROUTER)
        router_sock.bind(self.router_sock_url)
        self._router_sock = router_sock

        dealer_sock = self.zmq_ctx.socket(DEALER)
        dealer_sock.bind(self.dealer_sock_url)
        self._dealer_sock = dealer_sock

        self.log.info('Configured Router Dealer Windmill ...')


    def run(self):
        self._stop = False

        self.log.info('Beginning run with state: %s', str(self))

        loop_count = 0
        front_end_loop = 0
        back_end_loop = 0
        while(not self._stop):
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat))
                loop_count += 1
                if self.monitor_stream and (loop_count % 1000) == 0:
                    self.log.info('loop(%s)', loop_count)

                if socks.get(self._router_sock) == POLLIN:
                    msg = self._router_sock.recv()
                    more = self._router_sock.getsockopt(RCVMORE)
                    if more:
                        self._dealer_sock.send(msg, more)
                    else:
                        self._dealer_sock.send(msg)
                    if self.monitor_stream:
                        front_end_loop += 1
                        if(front_end_loop % 10) == 0:
                            self.log.info('d:%s-%s', front_end_loop, msg)

                if socks.get(self._dealer_sock) == POLLIN:
                    msg = self._dealer_sock.recv()
                    more = self._dealer_sock.getsockopt(RCVMORE)
                    if more:
                        self._router_sock.send(msg, SNDMORE)
                    else:
                        self._router_sock.send(msg)
                    if self.monitor_stream:
                        back_end_loop += 1
                        self.log.info('r:%s-%s', back_end_loop, msg)

            except ZMQError as ze:
                if ze.errno == 4: # known exception due to keyboard ctrl+c
                    self.log.info('System interrupt detected.')
                else: # exit hard on unhandled exception
                    self.log.error('Unhandled exception in run exectuion:%d - %s',
                                   ze.errno, ze.strerror)


if __name__ == '__main__':
    argv = sys.argv
    broker = RouterDealerWindmill(argv=argv)
    broker.run()
