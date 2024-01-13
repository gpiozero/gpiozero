"""
Provides access to the gpiozero entry points:

.. code-block:: python
    from gpiozero.ep import PinFactory_entry_points
    
    for ep in PinFactory_entry_points:
        ...

"""

from importlib.metadata import entry_points

try: #dict interface deprecated in Python 3.12
    PinFactory_entry_points = entry_points(group='gpiozero_pin_factories')
except TypeError: #selectable entrypoints only available from Python 3.10
    PinFactory_entry_points = entry_points()['gpiozero_pin_factories']