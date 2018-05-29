"""
Direct access to pins
---------------------

.. code-block:: python

    # Create a factory
    from gpiozero import MCP23017Factory
    factory = MCP23017Factory()
    # Configure GPA0 as input and pull it up
    gpa0 = factory.pin(0, function='input', pull='up')
    # Configure GPB7 as an output
    gpb7 = factory.pin(15, function='output')
    # Set it to HIGH
    gpb7.state = 1

Integration with devices
------------------------

.. code-block:: python

    # Create a factory
    from gpiozero import MCP23017Factory
    factory = MCP23017Factory()
    # Create a LED object attached to GPB7
    led = LED(15, pin_factory=factory)
    # Create a button object attached to GPB0
    button = Button(8, pin_factory=factory)
    # Reverse GPB0's polarity
    button.pin.polarity = 'reversed'
    # Bind the LED state to the button state
    led.source = button.values

Direct access to registers
++++++++++++++++++++++++++

The factory class exposes the IC registers as properties.

.. code-block:: python

    # Create a factory
    from gpiozero import MCP23017Factory
    factory = MCP23017Factory()
    # Configure GPA0 and GPB7 as inputs, others as outputs
    factory.iodir = [0b00000001, 0b10000000]
    # Pull GPA0 and GPB7 up
    factory.gppu = [0b00000001, 0b10000000]
    # Read GPIO state
    factory.gpio.read()
    # Get GPA0 state
    factory.gpio[0]
    # Set GPB0 state to HIGH
    factory.gpio[8] = 1

Pin numbering
-------------

Here is the mapping of pins between the IC naming and the library numbering.

MCP23008-E/P
++++++++++++

+---------+--------+---------+
| IC name | IC pin | Library |
+=========+========+=========+
| GP0     | 10     | 0       |
+---------+--------+---------+
| GP1     | 11     | 1       |
+---------+--------+---------+
| GP2     | 12     | 2       |
+---------+--------+---------+
| GP3     | 13     | 3       |
+---------+--------+---------+
| GP4     | 14     | 4       |
+---------+--------+---------+
| GP5     | 15     | 5       |
+---------+--------+---------+
| GP6     | 16     | 6       |
+---------+--------+---------+
| GP7     | 17     | 7       |
+---------+--------+---------+

MCP23017-E/SP
+++++++++++++

+---------+--------+---------+
| IC name | IC pin | Library |
+=========+========+=========+
| GPA0    | 21     | 0       |
+---------+--------+---------+
| GPA1    | 22     | 1       |
+---------+--------+---------+
| GPA2    | 23     | 2       |
+---------+--------+---------+
| GPA3    | 24     | 3       |
+---------+--------+---------+
| GPA4    | 25     | 4       |
+---------+--------+---------+
| GPA5    | 26     | 5       |
+---------+--------+---------+
| GPA6    | 27     | 6       |
+---------+--------+---------+
| GPA7    | 28     | 7       |
+---------+--------+---------+
| GPB0    | 1      | 8       |
+---------+--------+---------+
| GPB1    | 2      | 9       |
+---------+--------+---------+
| GPB2    | 3      | 10      |
+---------+--------+---------+
| GPB3    | 4      | 11      |
+---------+--------+---------+
| GPB4    | 5      | 12      |
+---------+--------+---------+
| GPB5    | 6      | 13      |
+---------+--------+---------+
| GPB6    | 7      | 14      |
+---------+--------+---------+
| GPB7    | 8      | 15      |
+---------+--------+---------+

Reference
---------

* `MCP23008 datasheet <http://ww1.microchip.com/downloads/en/DeviceDoc/21919e.pdf>`_
* `MCP23017 datasheet <http://ww1.microchip.com/downloads/en/DeviceDoc/20001952C.pdf>`_

Limitations
-----------

* Doesn't support PWM
* Only support local ICs
* Use a polling thread instead of interrupts

"""

from copy import copy
from threading import Lock
from time import time

from ..exc import PinInvalidPull, PinFixedPull, PinInvalidState, PinError, \
    PinInvalidFunction, PinInvalidEdges, PinInvalidPolarity, \
    PinInvalidBounce, PinInvalidPin
from ..i2c import I2C
from ..mixins import WhenChangedMixin, ValuesMixin
from ..threads import GPIOThread
from . import Factory, Pin


EDGE_FALL = 1
EDGE_RISE = 2
EDGE_BOTH = 3


def get_bit_state(bits, position):
    """Get the state of bit ``position`` in ``bits``.
    """
    return bits[int(position / 8)] & 1 << (position % 8)


class Debouncer:
    """Debounce values passed to it according to ``delay``.
    """

    def __init__(self, delay=0.02):
        #: Timestamp of the last value change
        self.last_change = None
        #: Last raw value seen
        self.last_value = None
        #: Debounced value
        self.value = None
        #: Debouncing delay
        self.delay = delay

    def __call__(self, value, now=None):
        now = now or time()

        if value != self.last_value:
            self.last_change = now
            self.last_value = value

        if now - self.last_change >= self.delay or self.value is None:
            self.value = value

        return self.value


class EdgeDetector:
    """Detect if there is a rising or a falling edge.
    """

    def __init__(self):
        #: Last known state
        self.state = None

    def __call__(self, new_state):
        previous_state = self.state
        self.state = new_state

        if previous_state is None:
            return

        if previous_state and not new_state:
            return EDGE_FALL

        if not previous_state and new_state:
            return EDGE_RISE


class MCP230xxPin(WhenChangedMixin, Pin):
    """A MCP23008 or MCP23017 GPIO pin.
    """

    EDGES = {
        EDGE_FALL: 'falling',
        EDGE_RISE: 'rising',
        EDGE_BOTH: 'both',
    }
    EDGES_NAMES = {v: k for k, v in EDGES.items()}

    def __init__(self, factory, number,
                 function='input', pull='floating', edges='both', bounce=0,
                 polarity='normal'):
        super(MCP230xxPin, self).__init__()
        self.factory = factory
        self.number = number
        self.function = function
        self.pull = pull
        self._edges = EDGE_BOTH
        self.edges = edges
        self.debouncer = self._dummy_debounce
        self.bounce = bounce
        self.polarity = polarity
        self.edge_detector = EdgeDetector()
        self._state = None

    def __repr__(self):
        return 'MCP230xxPin(factory=%r, number=%r, function=%r, pull=%r)' % (
            self.factory, self.number, self.function, self.pull)

    def _set_function(self, value):
        if value == 'input':
            self.factory.iodir[self.number] = 1
        elif value == 'output':
            self.factory.iodir[self.number] = 0
        else:
            raise PinInvalidFunction('Invalid function %r for pin %s of %r'
                                     % (value, self.number, self.factory))

    def _get_function(self):
        return 'input' if self.factory.iodir[self.number] else 'output'

    def _set_state(self, value):
        self.factory.olat[self.number] = value

    def _get_state(self):
        return self.debouncer(self.factory.gpio[self.number]) \
            if self._state is None else self._state

    def _set_pull(self, value):
        if value == 'up':
            self.factory.gppu[self.number] = 1
        elif value == 'floating':
            self.factory.gppu[self.number] = 0
        else:
            raise PinInvalidPull('Invalid pull %r for pin %s of %r'
                                 % (value, self.number, self.factory))

    def _get_pull(self):
        return 'up' if self.factory.gppu[self.number] else 'floating'

    def _dummy_debounce(self, value, now=None):
        return value

    def _set_bounce(self, value):
        if value is not None and value < 0:
            raise PinInvalidBounce('bounce must be 0 or greater')

        if value:
            value /= 1000.
            if isinstance(self.debouncer, Debouncer):
                self.debouncer.delay = value
            else:
                self.debouncer = Debouncer(value)
        else:
            self.debouncer = self._dummy_debounce

    def _get_bounce(self):
        return 0 if self.debouncer == self._dummy_debounce \
            else self.debouncer.delay * 1000

    def _set_edges(self, value):
        if value not in self.EDGES_NAMES:
            raise PinInvalidEdges(
                'Invalid edges %r for pin %s of %r' % (
                    value, self.number, self.factory))

        if self._edges is not None and self.EDGES[self._edges] == value:
            return

        if self.when_changed:
            self._disable_event_detect()

        self._edges = self.EDGES_NAMES[value]

        if self.when_changed:
            self._enable_event_detect()

    def _get_edges(self):
        return self.EDGES[self._edges]

    def _enable_event_detect(self):
        self.factory.subscribe(
            self.number, self._edges, self._call_when_changed)

    def _disable_event_detect(self):
        self.factory.unsubscribe(
            self.number, self._edges, self._call_when_changed)

    def _set_polarity(self, value):
        if value == 'normal':
            self.factory.ipol[self.number] = 0
        elif value == 'reversed':
            self.factory.ipol[self.number] = 1
        else:
            raise PinInvalidPolarity(
                'Invalid polarity %r for pin %r' % (value, self))

    def _get_polarity(self):
        return 'reversed' if self.factory.ipol[self.number] else 'normal'

    polarity = property(
        lambda self: self._get_polarity(),
        lambda self, value: self._set_polarity(value),
        doc="""\
        The input polarity of the pin. When set to ``normal`` (default),
        the value of the input pin reflects the logic state of the input pin.
        When set to ``reversed``, the value of the input pin is the opposite of
        the input pin's logic state.
        """)


class Register(ValuesMixin):
    """Data of an I2C device register.

    This class implements a class descriptor that is attached to
    :class:`.MCP230xxFactory` objects and eases register manipulation.

    """

    # Register instance cache
    CACHE = {}

    def __init__(self, address):
        #: Register address
        self.address = address
        #: :class:`MCP23008Factory` or :class:`MCP23017Factory` instance
        self.factory = None

    def _from_cache(self, factory):
        if factory is None:
            return self

        key = (self.address, factory)

        if key not in self.CACHE:
            # Create a copy of the descriptor object and attach the
            # factory to it.
            self.CACHE[key] = copy(self)
            self.CACHE[key].factory = factory

        return self.CACHE[key]

    def __get__(self, factory, owner):
        """Return a configured register instance.
        """
        return self._from_cache(factory)

    def __set__(self, factory, value):
        """Set register value.
        """
        self._from_cache(factory).write(value)

    def read(self):
        """Read data from register.
        """
        return self.factory.read(self.address)

    @property
    def value(self):
        """Read data from register.
        """
        return self.read()

    def write(self, value):
        """Write data to register.
        """
        self.factory.write(self.address, value)

    def __getitem__(self, position):
        """Read a bit from the register.
        """
        return bool(get_bit_state(self.read(), position))

    def __setitem__(self, position, value):
        """Set the value of a register bit.
        """
        data = self.read()

        if value:
            data[int(position / 8)] |= 1 << (position % 8)
        else:
            data[int(position / 8)] &= ~(1 << (position % 8))

        self.write(data)

    def __repr__(self):
        return 'Register(address=0x%x, factory=%r)' % (
            self.address, self.factory)


class MCP230xxPoller(GPIOThread):
    """Background poller for MCP230xx input pin states.
    """

    def __init__(self, factory, interval=0.001):
        super(MCP230xxPoller, self).__init__()
        #: MCP230xxFactory
        self.factory = factory
        #: Polling interval (seconds)
        self.interval = interval
        #: Callbacks subscribed to state changes
        self.subscribers = {}
        #: Subscribers lock
        self.lock = Lock()

    def subscribe(self, pin, edge, callback):
        """Register a ``callback`` to a specific ``edge`` on a ``pin``.

        When ``pin`` transitions from a high to a low state,
        all callbacks subscribed to ``EDGE_FALL`` are invoked.
        When ``pin`` transitions from a low to a high state,
        all callbacks subscribed to ``EDGE_RISE`` are invoked.
        Subscribers to ``EDGE_BOTH`` are invoked in both cases.
        """
        key = (pin, edge)

        with self.lock:
            subscribers = self.subscribers.get(key) or set()
            subscribers.add(callback)
            self.subscribers[key] = subscribers

    def unsubscribe(self, pin, edge, callback):
        """Unregister a ``callback`` from a specific ``edge`` on a ``pin``.
        """
        key = (pin, edge)

        with self.lock:
            if key in self.subscribers:
                self.subscribers[key].remove(callback)
                if not self.subscribers[key]:
                    del self.subscribers[key]

    def _run_for_pin(self, number, states, now=None):
        pin = self.factory.pin(number)
        state = get_bit_state(states, number)
        pin._state = debounced = pin.debouncer(state, now)
        edge = pin.edge_detector(debounced)

        if edge:
            callbacks = []

            with self.lock:
                for key in ((number, edge), (number, EDGE_BOTH)):
                    callbacks.extend(self.subscribers.get(key, []))

            for callback in callbacks:
                callback()

    def run(self):
        """Run the polling loop.
        """
        for value in self.factory.gpio.values:
            if self.stopping.wait(self.interval):
                break
            if not self.subscribers:
                continue

            states = self.factory.gpio.read()

            for number in range(self.factory.IO_PIN_COUNT):
                self._run_for_pin(number, states)

    def stop(self):
        """Stop the polling thread.
        """
        # Only call parent's stop() when the thread is actually running
        if self.isAlive():
            super(MCP230xxPoller, self).stop()
        # When shutting down the poller, pin must poll their values
        # by themselves.
        for number in range(self.factory.IO_PIN_COUNT):
            self.factory.pin(number)._state = None


class MCP230xxFactory(Factory):
    """Abstract class for MCP23008 and MCP23017 factories.
    """

    #: Define how many I/O pins the device has
    IO_PIN_COUNT = None
    #: Default device address
    DEFAULT_ADDRESS = 0x20

    def __init__(self, address=None, i2c=None,
                 pin_class=MCP230xxPin, poller_class=MCP230xxPoller):
        super(MCP230xxFactory, self).__init__()
        self.address = self.DEFAULT_ADDRESS if address is None else address
        self.i2c = i2c or I2C()
        self.pin_class = pin_class
        self.poller_class = poller_class
        self.register_size = self.IO_PIN_COUNT // 8
        self.poller = None
        self._pins = {}

    def __repr__(self):
        return '%s(address=0x%x, i2c=%r)' % (
            self.__class__.__name__, self.address, self.i2c)

    def read(self, register):
        """Read data from I2C ``register``.
        """
        return self.i2c.read(self.address, register, self.register_size)

    def write(self, register, data):
        """Write ``data`` to I2C ``register``.
        """
        self.i2c.write(self.address, register, data)

    def pin(self, number, **parameters):
        """Create an instance of a pin representing ``spec``.
        """
        if isinstance(number, int) and 0 <= number < self.IO_PIN_COUNT:
            # Get the pin from cache or create it
            if number in self._pins:
                pin = self._pins[number]
            else:
                pin = self._pins[number] = self.pin_class(
                    self, number, **parameters)
            # Update pin parameters
            for name, value in parameters.items():
                if hasattr(pin, name):
                    if getattr(pin, name) != value:
                        setattr(pin, name, value)
                else:
                    raise PinError(
                        'Invalid pin parameter: %s=%r' % (name, value))

            return self._pins[number]

        raise PinInvalidPin('Invalid GPIO pin: %s' % number)

    def subscribe(self, pin, edge, callback):
        """Register a ``callback`` to a specific ``edge`` on a ``pin``.
        """
        if self.poller is None:
            self.poller = self.poller_class(self)
            self.poller.start()
        self.poller.subscribe(pin, edge, callback)

    def unsubscribe(self, pin, edge, callback):
        """Unregister a ``callback`` from a specific ``edge`` on a ``pin``.
        """
        if self.poller:
            self.poller.unsubscribe(pin, edge, callback)
            # Stop the poller if it has no subscribers
            if not self.poller.subscribers:
                self.poller.stop()
                self.poller = None


class MCP23008Factory(MCP230xxFactory):
    """MCP23008 pin factory.
    """

    IO_PIN_COUNT = 8
    iodir = Register(0)
    ipol = Register(0x1)
    gpinten = Register(0x2)
    defval = Register(0x3)
    intcon = Register(0x4)
    iocon = Register(0x5)
    gppu = Register(0x6)
    intf = Register(0x7)
    intcap = Register(0x8)
    gpio = Register(0x9)
    olat = Register(0xa)


class MCP23017Factory(MCP230xxFactory):
    """MCP23017 pin factory.
    """

    IO_PIN_COUNT = 16
    iodir = Register(0)
    ipol = Register(0x2)
    gpinten = Register(0x4)
    defval = Register(0x6)
    intcon = Register(0x8)
    iocon = Register(0xa)
    gppu = Register(0xc)
    intf = Register(0xe)
    intcap = Register(0x10)
    gpio = Register(0x12)
    olat = Register(0x14)
