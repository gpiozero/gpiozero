"""
Provides access to the gpiozero entry points:

.. code-block:: python
    from gpiozero.ep import PinFactory_entry_points
    
    for ep in PinFactory_entry_points:
        ...

"""

from importlib.metadata import entry_points

PinFactory_entry_points = entry_points(group='gpiozero_pin_factories')