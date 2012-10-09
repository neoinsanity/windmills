__author__ = 'neoinsanity'


class Miller(object):
    """
    This is a a min-in helper library.
    """


    def _invoke_method_on_bases(self, func_name=None, *args, **kargs):
        """
        This helper method will walk the base class hierarchy to invoke a
        method if it exists for the given base class.

        Keyword Arguments:
        func_name -- the name of the function to invoke, must not be None.

        Failure to provide a func_name will raise a ValueError
        >>> foo = Miller()
        >>> foo._invoke_method_on_bases()
        Traceback (most recent call last):
        ...
        ValueError: No func_name provided in _invoke_method_on_bases invocation.

        If a method name is supplied for a method that does not exist,
        the _invoke_method_on_bases will raise no exception.
        >>> foo._invoke_method_on_bases(func_name='the_func')

        A complete example:
        Declare a Miller derived child class with a target function,.
        >>> class Bar(Miller):
        ...     def the_func(self, a_key=None):
        ...         print 'a_key:', a_key
        >>> bar = Bar()
        >>> kwargs={'a_key':'a value'}
        >>> bar._invoke_method_on_bases(func_name='the_func', **kwargs)
        a_key: a value
        >>> bar._invoke_method_on_bases(func_name='the_func', a_key='a value')
        a_key: a value
        """
        if func_name is None:
            raise ValueError(
                'No func_name provided in _invoke_method_on_bases invocation.')
        base = self.__class__ # The root in the chain
        while base is not None and base is not object:
            if func_name in base.__dict__:
                func = getattr(base, func_name)
                func(self, *args, **kargs)
            base = base.__base__ # iterate to the next base class
