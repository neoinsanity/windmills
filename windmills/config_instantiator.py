#!/usr/bin/env python
import argparse
import json
from threading import Thread
from cli_emitter import CliEmitter
from cli_listener import CliListener
from ventilator_windmill import VentilatorWindmill


__author__ = 'neoinsanity'


class ConfigInstantiator():
    service_map = {
        'cli_emitter': CliEmitter,
        'cli_listener': CliListener,
        'ventilator_windmill': VentilatorWindmill
    }


    def __init__(self, file=None):
        """
        """
        # load the config file
        assert file

        # configure the interrupt handling
        self._stop = False
        #signal.signal(signal.SIGINT, self._signal_interrupt_handler)

        config_json = open(file).read()
        print config_json
        config = json.loads(config_json)

        # create a service instance holder
        self.active_services = list()

        service_list = config["configuration"]
        for service in service_list:
            service_type = service["service"]
            assert service_type
            args = service['args'].split()
            assert args

            the_service = None

            service_class = ConfigInstantiator.service_map[service_type]
            assert service_class
            the_service = service_class(argv=args)

            assert the_service

            self.active_services.append(the_service)

        for service_inst in self.active_services:
            t = Thread(target=service_inst.run)
            t.start()
            assert t.is_alive


    def run(self):
        pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--file', help='The configuration file.')
    args = arg_parser.parse_args()

    assert args.file

    config_instantiator = ConfigInstantiator(file=args.file)
    config_instantiator.run()
