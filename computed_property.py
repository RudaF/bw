class ComputedProperty:
    '''
    Caches the return value of getter_func, a property of a class, based on values of the original class
    where the property is defined. 
    '''
    def __init__(self, getter_func:function=None, setter_func:function=None, deleter_func:function=None, properties:list[str]=None, doc:str=None):
        self.property_function = getter_func
        self.setter_func = setter_func
        self.deleter_func = deleter_func
        self.cached_args = properties
        self.cached_args_values_map = {}
        self.property_value = None
        self.__doc__ = doc

    def __get__(self, class_instance, main_class):
        if not self.property_value:
            self._cache_computed_properties(class_instance)
            self.property_value = self.property_function(class_instance)
            return self.property_value
        
        cached_props_changed = [self.cached_args_values_map.get(arg) != getattr(class_instance, arg) for arg in self.cached_args] 
        if any(cached_props_changed):
            self._cache_computed_properties(class_instance)
            self.property_value = self.property_function(class_instance)

        return self.property_value

    def __set__(self, class_instance, new_value):
        self.setter_func(class_instance, new_value)
        self._cache_computed_properties(class_instance)
    
    def __delete__(self, class_instance):
        self.deleter_func(class_instance)

    def setter(self, setter_func):
        return type(self)(self.property_function, setter_func, self.deleter_func, self.cached_args, self.__doc__)

    def deleter(self, deleter_func):
        return type(self)(self.property_function, self.setter_func, deleter_func, self.cached_args, self.__doc__)

    def _cache_computed_properties(self, class_instance):
        for prop in self.cached_args:
            cached_value = getattr(class_instance, prop)
            self.cached_args_values_map[prop] = cached_value


def computed_property(*properties: list[str]) -> ComputedProperty:
    '''
    Recieves a list of string properties and return a decorator function for a class method
    that caches that property based on the parameters passed as arguments. 
    '''
    def decorator(fun: function):
        return ComputedProperty(getter_func=fun, properties=properties, doc=fun.__doc__)
    return decorator
