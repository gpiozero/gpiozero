from threading import Thread, Event

from RPi import GPIO


class GPIODeviceError(Exception):
    pass


class GPIODevice(object):
    def __init__(self, pin=None):
        if pin is None:
            raise GPIODeviceError('No GPIO pin number given')
        self._pin = pin

    @property
    def pin(self):
        return self._pin


_GPIO_THREADS = set()
def _gpio_threads_shutdown():
    while _GPIO_THREADS:
        for t in _GPIO_THREADS.copy():
            t.stop()


class GPIOThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        super(GPIOThread, self).__init__(group, target, name, args, kwargs)
        self.stopping = Event()
        self.daemon = True

    def start(self):
        self.stopping.clear()
        _GPIO_THREADS.add(self)
        super(GPIOThread, self).start()

    def stop(self):
        self.stopping.set()
        self.join()
        _GPIO_THREADS.discard(self)

