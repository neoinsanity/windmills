#!/usr/bin/env python
from email.mime.text import MIMEText
from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ListType
from smtplib import SMTP, SMTPAuthenticationError, SMTPServerDisconnected
from windmills.lib import Brick
import json
import logging
import os
import schematics.base
import socket
import sys


__author__ = 'neoinsanity'

###
# email_windmill
#

class EmailRequest(Model):
    msg = StringType(max_length=50000, required=True)
    sender = StringType(max_length=256, required=True)
    subject = StringType(max_length=256, required=True)
    to = ListType(StringType(max_length=256), required=True)


class EmailWindmill(Brick):
    SENDGRID_USERNAME = os.getenv('SENDGRID_USERNAME')
    SENDGRID_PASSWORD = os.getenv('SENDGRID_PASSWORD')
    SMTPHOST = "smtp.sendgrid.net"
    SMTPPORT = 587


    def __init__(self, **kwargs):
        # !!!!! todo: raul - replace with real configurable logging !!!!!
        verbose = kwargs.get('verbose', False)
        log_level = logging.ERROR
        if verbose:
            log_level = logging.DEBUG
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.basicConfig(
            filename='/tmp/email_windmill.log',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=log_level)
        self.log = logging.getLogger('EmailWindmill')
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # setup the initial default configuration
        self.user_name = self.SENDGRID_USERNAME
        self.password = self.SENDGRID_PASSWORD
        self.host = self.SMTPHOST
        self.port = self.SMTPPORT

        self.input_recv_handler = self._email_recv_handler

        # signal Brick not to configure output socket
        self.CONFIGURE_OUTPUT = False
        Brick.__init__(self, **kwargs)


    def configuration_options(self, arg_parser=None):
        assert arg_parser


    def configure(self, args=None):
        assert args

        if self.verbose:
            self.log.info('EmailWindmill configured...')


    def _email_recv_handler(self, sock):
        request_json = None
        try:
            request_json = self._input_sock.recv()

            if self.verbose:
                print 'Request:', request_json

            email_request = json.loads(request_json)
            payload = email_request['payload']

            validator = EmailRequest(**payload)
            try:
                validator.validate(validate_all=True)
            except schematics.base.ModelException, e:
                self.log.error('schematics.base.ModelException: %s, while processing %s'
                               % (e, payload))
                return

            sender = payload['sender']
            receivers = payload['to']

            email_msg = MIMEText(payload['msg'])

            email_msg['Subject'] = payload['subject']
            email_msg['From'] = sender
            email_msg['To'] = ', '.join(receivers) # create string list of recipients

            mail_client = SMTP(self.host, self.port)
            mail_client.login(self.user_name, self.password)
            mail_client.sendmail(sender, receivers, email_msg.as_string())
            mail_client.quit()

        except AttributeError, e:
            self.log.error('AttributeError: %s, while processing: %s' % (e, request_json))
        except SMTPAuthenticationError, e:
            self.log.error('SMTPAuthenticationError: %s' % e)
        except SMTPServerDisconnected, e:
            self.log.error('SMTPServerDisconnected: %s' % e)
        except socket.error, e:
            self.log.error('socket.error: %s' % e)
        except TypeError, e:
            self.log.error('TypeError: %s, while processing: %s' % (e, request_json))
        except ValueError, e:
            self.log.error('ValueError: %s, while processing: %s' % (e, request_json))
        except:
            self.log.error("Unexpected error:", sys.exc_info()[0])


if __name__ == '__main__':
    argv = sys.argv
    email_windmill = EmailWindmill(argv=argv)
    email_windmill.run()
