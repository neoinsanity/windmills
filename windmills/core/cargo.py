from gevent import spawn

__author__ = 'Raul Gonzalez'


class Cargo(object):
    def __init__(self, delivery_handle=None, socket_config=None):
        """

        :param delivery_handle:
        :type delivery_handle: DeliveryHandle
        :param socket_config:
        :type socket_config: super_core.InputSocketConfig
        """
        #: The handle to the
        self._delivery_handle = delivery_handle
        self._socket_config = socket_config

    @property
    def socket_config(self):
        """

        :return:
        :rtype: super_core.InputSocketConfig
        """
        return self._socket_config

    def send(self, crate=None):
        """

        :param crate:
        :type crate: Crate
        :return:
        :rtype: Crate
        """
        spawn(self._delivery_handle, crate=crate)

