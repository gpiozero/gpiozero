=========
Changelog
=========

.. currentmodule:: gpiozero


Release 1.1.0 (2016-02-08)
==========================

* Documentation converted to reST and expanded to include generic classes
  and several more recipes (`#80`_, `#82`_, `#101`_, `#119`_, `#135`_, `#168`_)
* New :class:`LEDBarGraph` class (many thanks to Martin O'Hanlon!) (`#126`_,
  `#176`_)
* New :class:`Pin` implementation abstracts out the concept of a GPIO pin
  paving the way for alternate library support and IO extenders in future
  (`#141`_)
* New :meth:`LEDBoard.blink` method which works properly even when background
  is set to ``False`` (`#94`_, `#161`_)
* New :meth:`RGBLED.blink` method which implements (rudimentary) color fading
  too! (`#135`_, `#174`_)
* New ``initial_value`` attribute on :class:`OutputDevice` ensures consistent
  behaviour on construction (`#118`_)
* New ``active_high`` attribute on :class:`PWMOutputDevice` and :class:`RGBLED`
  allows use of common anode devices (`#143`_, `#154`_)
* Loads of new ADC chips supported (many thanks to GitHub user pcopa!)
  (`#150`_)

.. _#80: https://github.com/RPi-Distro/python-gpiozero/issues/80
.. _#82: https://github.com/RPi-Distro/python-gpiozero/issues/82
.. _#94: https://github.com/RPi-Distro/python-gpiozero/issues/94
.. _#101: https://github.com/RPi-Distro/python-gpiozero/issues/101
.. _#118: https://github.com/RPi-Distro/python-gpiozero/issues/118
.. _#119: https://github.com/RPi-Distro/python-gpiozero/issues/119
.. _#126: https://github.com/RPi-Distro/python-gpiozero/issues/126
.. _#135: https://github.com/RPi-Distro/python-gpiozero/issues/135
.. _#141: https://github.com/RPi-Distro/python-gpiozero/issues/141
.. _#143: https://github.com/RPi-Distro/python-gpiozero/issues/143
.. _#150: https://github.com/RPi-Distro/python-gpiozero/issues/150
.. _#154: https://github.com/RPi-Distro/python-gpiozero/issues/154
.. _#161: https://github.com/RPi-Distro/python-gpiozero/issues/161
.. _#168: https://github.com/RPi-Distro/python-gpiozero/issues/168
.. _#174: https://github.com/RPi-Distro/python-gpiozero/issues/174
.. _#176: https://github.com/RPi-Distro/python-gpiozero/issues/176

Release 1.0.0 (2015-11-16)
==========================

* Debian packaging added (`#44`_)
* :class:`PWMLED` class added (`#58`_)
* ``TemperatureSensor`` removed pending further work (`#93`_)
* :meth:`Buzzer.beep` alias method added (`#75`_)
* :class:`Motor` PWM devices exposed, and :class:`Robot` motor devices exposed
  (`#107`_)

.. _#44: https://github.com/RPi-Distro/python-gpiozero/issues/44
.. _#58: https://github.com/RPi-Distro/python-gpiozero/issues/58
.. _#93: https://github.com/RPi-Distro/python-gpiozero/issues/93
.. _#75: https://github.com/RPi-Distro/python-gpiozero/issues/75
.. _#107: https://github.com/RPi-Distro/python-gpiozero/issues/107

Release 0.9.0 (2015-10-25)
==========================

Fourth public beta

* Added source and values properties to all relevant classes (`#76`_)
* Fix names of parameters in :class:`Motor` constructor (`#79`_)
* Added wrappers for LED groups on add-on boards (`#81`_)

.. _#76: https://github.com/RPi-Distro/python-gpiozero/issues/76
.. _#79: https://github.com/RPi-Distro/python-gpiozero/issues/79
.. _#81: https://github.com/RPi-Distro/python-gpiozero/issues/81

Release 0.8.0 (2015-10-16)
==========================

Third public beta

* Added generic :class:`AnalogInputDevice` class along with specific classes
  for the :class:`MCP3008` and :class:`MCP3004` (`#41`_)
* Fixed :meth:`DigitalOutputDevice.blink` (`#57`_)

.. _#41: https://github.com/RPi-Distro/python-gpiozero/issues/41
.. _#57: https://github.com/RPi-Distro/python-gpiozero/issues/57

Release 0.7.0 (2015-10-09)
==========================

Second public beta

Release 0.6.0 (2015-09-28)
==========================

First public beta

Release 0.5.0 (2015-09-24)
==========================

Release 0.4.0 (2015-09-23)
==========================

Release 0.3.0 (2015-09-22)
==========================

Release 0.2.0 (2015-09-21)
==========================

Initial release
