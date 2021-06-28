#!/usr/bin/env python
import argparse
import signal
import time
import json
from threading import Thread
from .cli_emitter import CliEmitter
from .cli_listener import CliListener
from .echo_service import EchoService
from .ventilator_windmill import VentilatorWindmill


__author__ = 'neoinsanity'
__all__ = ['DonQuixote']
#
# don_quixote
#

class DonQuixote(object):
    """
    >>> from threading import Thread
    >>> import time
    >>> blueprints = {'blueprints':[
    ...     {'service':'cli_emitter',
    ...     'args':'--output_sock_url tcp://*:9996'},
    ...     {'service':'cli_listener',
    ...     'args':'--input_sock_url tcp://localhost:9996'}
    ... ]}
    >>> foo = DonQuixote(blueprints=blueprints,
    ...                  disable_keyboard=True,
    ...                  verbose=True)
    >>> t = Thread(target=foo.run)
    >>> t.start()
    >>> time.sleep(2)
    Testing 1, 2, 3
    >>> assert t.is_alive()
    >>> foo.kill()
    >>> t.join(2)
    >>> assert not t.is_alive()
    """
    service_map = {
        'cli_emitter': CliEmitter,
        'cli_listener': CliListener,
        'echo_service': EchoService,
        'ventilator_windmill': VentilatorWindmill,
    }


    def __init__(self,
                 file=None,
                 blueprints=None,
                 disable_keyboard=False,
                 verbose=False):
        # load the config file
        self.file = file
        self.blueprints = blueprints
        self.disable_keyboard = disable_keyboard
        self.verbose = verbose

        if file is not None:
            blueprints_json = open(file).read()
            if self.verbose:
                print(blueprints_json)
            blueprints_json = blueprints_json.rstrip('\n\r')
            file_blueprints = json.loads(blueprints_json)
            self._load_blueprints(file_blueprints)
        elif blueprints is not None:
            self._load_blueprints(blueprints)
        else:
            raise ValueError("A blueprint dictionary or file with blueprint "
                             "must be provided.")

        # configure the interrupt handle
        self._stop = False
        signal.signal(signal.SIGINT, self._signal_interrupt_handler)


    def kill(self):
        self._stop = True


    def run(self):
        thread_service_map = dict()

        for service_inst in self.active_services:
            t = Thread(target=service_inst.run)
            t.start()
            assert t.is_alive
            thread_service_map[t] = service_inst

        # todo: raul - this should be replaced with a more console vs not
        # console mode.
        if self.disable_keyboard:
            while(not self._stop):
                time.sleep(1)
        else:
            _ = input('Touch me and we die <return>:')

        for t_key in list(thread_service_map.keys()):
            service = thread_service_map[t_key]
            service.kill()
            for attempt in range(3):
                t_key.join(1)
                if not t_key.is_alive(): break

            if t_key.is_alive():
                print(('Service', service,
                       'has not shutdown, will attempt to force'))
                try:
                    t_key._Thread__stop()
                except:
                    print('Service failed to stop:', service)


    def _load_blueprints(self, blueprints=None):
        assert blueprints

        # create a service instance holder
        self.active_services = list()

        service_list = blueprints["blueprints"]
        for service in service_list:
            service_type = service["service"]
            assert service_type
            args = service['args'].split()

            the_service = None

            service_class = DonQuixote.service_map[service_type]
            assert service_class
            if args is not None:
                the_service = service_class(argv=args)
            else:
                the_service = service_class()

            assert the_service

            self.active_services.append(the_service)


    def _signal_interrupt_handler(self, signum, frame):
        """
        This method is registered with the signal library to ensure handling
        of system interrupts. Initialization of this method is performed
        during __init__ invocation.
        """
        self.kill()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--file',
                            required = True,
                            help='The configuration file.')
    arg_parser.add_argument('--verbose', action='store_true')
    args = arg_parser.parse_args()

    don = DonQuixote(file=args.file,
                     verbose=args.verbose)
    don.run()
