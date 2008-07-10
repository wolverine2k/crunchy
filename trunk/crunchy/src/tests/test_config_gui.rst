config_gui.py tests
===================

    >>> from src.plugins.config_gui import *
    
This was first suggested by André on the crunchy-discuss mailing list. This
implementation is by Johannes.

Note from Johannes: this is the first time I have ever tried to code my tests first, so
it might be a little haphazard.

Basic Architecture
------------------

There are a number of classes in config_gui.py that do the heavy lifting. The most important
are ConfigOption and ConfigWidget. ConfigOption and its subclasses make up the model, while
ConfigWidget and its subclasses implement the view.

ConfigOption
------------

The ConfigOption init method takes two arguments: a string to act as a key and another value that
represents the default (or initial) value of the option. Some subclasses of ConfigOption may also take
other arguments, but these two are always required.
When a new instance of ConfigOption is created it is registered in a special class variable:

    >>> obj = ConfigOption("test_key", "test_value")
    >>> obj == ConfigOption.all_options["test_key"]
    True
    
The initial value given in the constructor can be retrieved using the get() method:

    >>> obj.get()
    'test_value'
    
And the value can be changed using the set() method:

    >>> obj.set("another value")
    >>> obj.get()
    'another value'
    
Initially the only functional subclass of ConfigOption will be MultiOption.
MultiOption represents an option where the user can choose the value from a (fixed) list.

    >>> obj2 = MultiOption("things", "boo", ["foo", "boo", "bar"])
    >>> obj2.get()
    'boo'
    >>> obj2.get_values()
    ['foo', 'boo', 'bar']
    
ConfigWidget
------------

ConfigWidget is the superclass for all the different configuration widgets.
The constructor for a ConfigWidget takes an instance of an appropriate underlying
ConfigOption subclass.
    
    >>> obj3 = ConfigWidget(obj)

ConfigWidget instances have render() methods that render the widget to a form
(including all the necessary javascript).

Similar to ConfigOption, the only subclass of ConfigWidget deals with MCOs (like MCQs...).

    >>> obj4 = MultiChoiceWidget(obj2)
    
Lets render this to stdout:

    >>> import sys
    >>> obj4.render(sys.stdout)
    <input type="radio" name="things" value="foo"  />foo<br />
    <input type="radio" name="things" value="boo" checked="checked"  />boo<br />
    <input type="radio" name="things" value="bar"  />bar<br />

    

