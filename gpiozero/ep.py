"""
Provides access to the gpiozero entry points:

.. code-block:: python
    from gpiozero.ep import PinFactory_entry_points
    
    for ep in PinFactory_entry_points:
        ...

"""

from importlib.metadata import entry_points

#prefix _ will stop this being imported via from ep import * if anyone tries
def _get_entry_points(group): 
    try: #dict interface deprecated in Python 3.12
        _entry_points = entry_points(group=group)
    except TypeError: #selectable entrypoints only available from Python 3.10
        _entry_points = entry_points()[group]
    return _entry_points    

PinFactory_entry_points = _get_entry_points(group='gpiozero_pin_factories')
MockPinClass_entry_points = _get_entry_points(group='gpiozero_mock_pin_classes')