#!/usr/bin/env python
import argparse
import json
from cli_emitter import CliEmitter
from cli_listener import CliListener
from ventilator_windmill import VentilatorWindmill

import unicodedata


__author__ = 'neoinsanity'


class ConfigInstantiator():
    def __init__(self, file=None):
        """
        """
        # load the config file
        assert file

        config_json = open(file).read()
        print config_json
        config = json.loads(config_json)

        # create a service instance holder
        active_services = list()

        service_list = config["configuration"]
        for service in service_list:
            service_type = service["service"]
            assert service_type
            args = service['args'].split()
            assert args

            the_service = None

            if service_type == 'cli_listener':
                the_service = CliListener(argv=args)

            if service_type == 'ventilator-windmill':
                the_service = VentilatorWindmill(argv=args)

            if service_type == 'cli-emitter':
                the_service = CliEmitter(argv=args)

            assert the_service

            active_services.append(the_service)

    def run(self):
        pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--file', help='The configuration file.')
    args = arg_parser.parse_args()

    assert args.file

    config_instantiator = ConfigInstantiator(file=args.file)
    config_instantiator.run()
