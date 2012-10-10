"""The Miller class which provides the mix-in enabling tools."""
__author__ = 'neoinsanity'


class Miller(object):
    """This is a a mix-in helper library."""


    def __create_property_bag__(self):
        """
        This method will create a property bag that can be used to assign
        attributes.

        Return:
        >>>
        """
        return type('_property_bag', (object,), dict())


    def __invoke_method_on_bases__(self, func_name=None, *args, **kwargs):
        """
        This helper method will walk the base class hierarchy to invoke a
        method if it exists for the given base class.

        Keyword Arguments:
        func_name -- the required name of the function to invoke.
        *args     -- an optional list of arguments to pass to the named
                     function.
        **kwargs  -- an optional dictionary of arguments to pass to the named
                     function.

        Return: None

        Raises:
        ValueError: __invoke_method_on_bases__-func_name parameter required

        To utilize this method, a function name must be provided. Failure to
        do so will result in an exception being thrown.
        >>> foo = Miller()
        >>> foo.__invoke_method_on_bases__()
        Traceback (most recent call last):
        ...
        ValueError: __invoke_method_on_bases__-func_name parameter required

        If a method name is supplied for a method that does not exist,
        the __invoke_method_on_bases__ will raise no exception.
        >>> foo.__invoke_method_on_bases__(func_name='the_func')

        A complete example:
        Declare a Miller derived child class with a target function,
        Note: It is possible to have more than one proginator class with the
        target function defined. The __invoke_method_on_bases__ will execute
        the function on each of the base classes.

        >>> class Bar(Miller):
        ...     def the_func(self, a_key=None):
        ...         print 'a_key:', a_key
        >>> bar = Bar()

        With an instance of a Miller child class, we can invoke the method in
         two ways, as exampled below.

        >>> # Create an keyword argument dictionary or argument list
        >>> kwargs={'a_key':'a value'}
        >>> bar.__invoke_method_on_bases__(func_name='the_func', **kwargs)
        a_key: a value

        >>> # Simply pass the argument keyword and value
        >>> bar.__invoke_method_on_bases__(func_name='the_func',
        ...                                a_key='a value')
        a_key: a value
        """
        if func_name is None:
            raise ValueError(
                '__invoke_method_on_bases__-func_name parameter required')
        base = self.__class__ # The root in the chain
        while base is not None and base is not object:
            if func_name in base.__dict__:
                func = getattr(base, func_name)
                func(self, *args, **kwargs)
            base = base.__base__ # iterate to the next base class

