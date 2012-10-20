#!/usr/bin/env python
import argparse
import json
from threading import Thread
from cli_emitter import CliEmitter
from cli_listener import CliListener
from ventilator_windmill import VentilatorWindmill


__author__ = 'neoinsanity'
__all__ = ['DonQuixote']
#
# don_quxote
#

class DonQuixote():
    service_map = {
        'cli_emitter': CliEmitter,
        'cli_listener': CliListener,
        'ventilator_windmill': VentilatorWindmill
    }


    def __init__(self, file=None, verbose=False):
        """
        """
        # load the config file
        assert file
        self.file = file
        self.verbose = verbose

        config_json = open(file).read()
        config = json.loads(config_json)
        if self.verbose:
            print config_json

        # create a service instance holder
        self.active_services = list()

        service_list = config["configuration"]
        for service in service_list:
            service_type = service["service"]
            assert service_type
            args = service['args'].split()
            assert args

            the_service = None

            service_class = DonQuixote.service_map[service_type]
            assert service_class
            the_service = service_class(argv=args)

            assert the_service

            self.active_services.append(the_service)


    def run(self):
        thread_service_map = dict()

        for service_inst in self.active_services:
            t = Thread(target=service_inst.run)
            t.start()
            assert t.is_alive
            thread_service_map[t] = service_inst

        _ = raw_input('Touch me and we die <return>:')

        for t_key in thread_service_map.keys():
            service = thread_service_map[t_key]
            service.kill()
            for attempt in range(3):
                t_key.join(1)
                if not t_key.is_alive(): break

            if t_key.is_alive():
                print ('Service', service,
                       'has not shutdown, will attempt to force')
                try:
                    t_key._Thread__stop()
                except:
                    print 'Service failed to stop:', service


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--file', help='The configuration file.')
    arg_parser.add_argument('--verbose', action='store_true')
    args = arg_parser.parse_args()

    assert args.file

    don = DonQuixote(file=args.file,
                     verbose=args.verbose)
    don.run()
