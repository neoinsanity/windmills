#!/usr/bin/env python
import sys
from lib import Scaffold
from zmq import POLLIN, RCVMORE, ROUTER, SNDMORE, ZMQError


__author__ = 'neoinsanity'
#
# req-rep-broker-windmill
#

class ReqRepBrokerWindmill(Scaffold):
    """

    """


    def __init__(self, **kwargs):
        # setup the initial default settings
        self.router_sock_url = 'tcp://*.8888'
        self.dealer_sock_url = 'tcp://*.8889'

        self._router_sock = None
        self._dealer_sock = None

        Scaffold.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser

        arg_parser.add_argument('--router_sock_url',
                                default=self._router_sock,
                                help="Set the url address for router.")
        arg_parser.add_argument('--dealer_sock_url',
                                default=self._dealer_sock,
                                help='Set the url address for dealer')


    def configure(self, args=None):
        assert args
        property_list = ['router_sock_url', 'dealer_sock_url']
        self.__copy_property_values__(args, self, property_list=property_list)

        router_sock = self.zmq_ctx.socket(ROUTER)
        router_sock.bind(self.router_sock_url)


    def run(self):
        self._stop = False

        if self.verbose:
            print 'Beginning run with state:', str(self)

        loop_count = 0
        front_end_loop = 0
        back_end_loop = 0
        while(not self._stop):
            try:
                socks = dict(self._poll.poll(timeout=self.heartbeat))
                loop_count += 1
                if self.monitor_stream and (loop_count % 1000) == 0:
                    sys.stdout.write('loop(%s)' % loop_count)
                    sys.stdout.flush()

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
                            print '.', front_end_loop, '-', msg, '-'

                if socks.get(self._dealer_sock) == POLLIN:
                    msg = self._dealer_sock.recv()
                    more = self._dealer_sock.getsockopt(RCVMORE)
                    if more:
                        self._router_sock.send(msg, SNDMORE)
                    else:
                        self._router_sock.send(msg)
                    if self.monitor_stream:
                        back_end_loop += 1
                        if(back_end_loop % 10) == 0:
                            print '.', back_end_loop, '-', msg, '-'

            except ZMQError, ze:
                if ze.errno == 6: # known exception due to keyboard ctrl+c
                    if self.verbose:
                        print 'System interrupt detected.'
                else: # exit hard on unhandled exception
                    print ('Unhandled exception in run exectuion:%d - %s'
                           % (ze.errno, ze.strerror))


if __name__ == '__main__':
    argv = sys.argv
    broker = ReqRepBrokerWindmill(argv=argv)
    broker.run()
