from gevent import spawn, joinall
import zmq.green as zmq
from windmills.utility_service import CliListener
from windmills.core.crate import Crate

from windmill_test_case import WindmillTestCase

__author__ = 'Raul Gonzalez'


class TestCliListener(WindmillTestCase):
  def setUp(self):
    self.zmq_ctx = zmq.Context()
    pair_out_sock = self.zmq_ctx.socket(zmq.PAIR)
    pair_out_sock.bind('tcp://*:60053')
    push_out_sock = self.zmq_ctx.socket(zmq.PUSH)
    push_out_sock.bind('tcp://*:6678')
    pub_out_sock = self.zmq_ctx.socket(zmq.PUB)
    pub_out_sock.bind('tcp://*:6679')

    self.sock_map = {
      'PAIR': pair_out_sock,
      'PUSH': push_out_sock,
      'PUB': push_out_sock
    }

  def tearDown(self):
    for sock in self.sock_map.values():
      sock.close()

    self.zmq_ctx.destroy()

  def test_cli_default_behavior(self):
    argv = '--verbose'
    cli_listener = CliListener(argv=argv)

    g = spawn(cli_listener.run)

    crate = Crate(call_ctx={}, msg_ctx={}, msg_data='hello')

    self.sock_map['PAIR'].send(crate.dump)

    res = joinall([g, ], timeout=2)
    print '+++++ This is the result:', res
