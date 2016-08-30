=========
Changelog
=========

.. currentmodule:: gpiozero


Release 1.3.0 (2016-08-31)
==========================

* Added :class:`ButtonBoard` for reading multiple buttons in a single
  class (`#340`_)
* Added :class:`Servo` and :class:`AngularServo` classes for controlling
  simple servo motors (`#248`_)
* Lots of work on supporting easier use of internal and third-part pin
  implementations (`#359`_)
* :class:`Robot` now has a proper :attr:`~Robot.value` attribute (`#305`_)
* Added :class:`CPUTemperature` as another demo of "internal" devices (`#294`_)
* A temporary work-around for an issue with :class:`DistanceSensor` was
  included but a full fix is in the works (`#385`_)
* More work on the documentation (`#320`_, `#295`_, `#289`_, etc.)

Not quite as much as we'd hoped to get done this time, but we're rushing to
make a Raspbian freeze. As always, thanks to the community - your suggestions
and PRs have been brilliant and even if we don't take stuff exactly as is, it's
always great to see your ideas. Onto 1.4!

.. _#248: https://github.com/RPi-Distro/python-gpiozero/issues/248
.. _#289: https://github.com/RPi-Distro/python-gpiozero/issues/289
.. _#294: https://github.com/RPi-Distro/python-gpiozero/issues/294
.. _#295: https://github.com/RPi-Distro/python-gpiozero/issues/295
.. _#305: https://github.com/RPi-Distro/python-gpiozero/issues/305
.. _#320: https://github.com/RPi-Distro/python-gpiozero/issues/320
.. _#340: https://github.com/RPi-Distro/python-gpiozero/issues/340
.. _#359: https://github.com/RPi-Distro/python-gpiozero/issues/359
.. _#385: https://github.com/RPi-Distro/python-gpiozero/issues/385

Release 1.2.0 (2016-04-10)
==========================

* Added :class:`Energenie` class for controlling Energenie plugs (`#69`_)
* Added :class:`LineSensor` class for single line-sensors (`#109`_)
* Added :class:`DistanceSensor` class for HC-SR04 ultra-sonic sensors (`#114`_)
* Added :class:`SnowPi` class for the Ryanteck Snow-pi board (`#130`_)
* Added :attr:`~Button.when_held` (and related properties) to :class:`Button`
  (`#115`_)
* Fixed issues with installing GPIO Zero for python 3 on Raspbian Wheezy
  releases (`#140`_)
* Added support for lots of ADC chips (MCP3xxx family) (`#162`_) - many thanks
  to pcopa and lurch!
* Added support for pigpiod as a pin implementation with
  :class:`~gpiozero.pins.pigpiod.PiGPIOPin` (`#180`_)
* Many refinements to the base classes mean more consistency in composite
  devices and several bugs squashed (`#164`_, `#175`_, `#182`_, `#189`_,
  `#193`_, `#229`_)
* GPIO Zero is now aware of what sort of Pi it's running on via :func:`pi_info`
  and has a fairly extensive database of Pi information which it uses to
  determine when users request impossible things (like pull-down on a pin with
  a physical pull-up resistor) (`#222`_)
* The source/values system was enhanced to ensure normal usage doesn't stress
  the CPU and lots of utilities were added (`#181`_, `#251`_)

And I'll just add a note of thanks to the many people in the community who
contributed to this release: we've had some great PRs, suggestions, and bug
reports in this version. Of particular note:

* Schelto van Doorn was instrumental in adding support for numerous ADC chips
* Alex Eames generously donated a RasPiO Analog board which was extremely
  useful in developing the software SPI interface (and testing the ADC support)
* Andrew Scheller squashed several dozen bugs (usually a day or so after Dave
  had introduced them ;)

As always, many thanks to the whole community - we look forward to hearing from
you more in 1.3!

.. _#69: https://github.com/RPi-Distro/python-gpiozero/issues/69
.. _#109: https://github.com/RPi-Distro/python-gpiozero/issues/109
.. _#114: https://github.com/RPi-Distro/python-gpiozero/issues/114
.. _#115: https://github.com/RPi-Distro/python-gpiozero/issues/115
.. _#130: https://github.com/RPi-Distro/python-gpiozero/issues/130
.. _#140: https://github.com/RPi-Distro/python-gpiozero/issues/140
.. _#162: https://github.com/RPi-Distro/python-gpiozero/issues/162
.. _#164: https://github.com/RPi-Distro/python-gpiozero/issues/164
.. _#175: https://github.com/RPi-Distro/python-gpiozero/issues/175
.. _#180: https://github.com/RPi-Distro/python-gpiozero/issues/180
.. _#181: https://github.com/RPi-Distro/python-gpiozero/issues/181
.. _#182: https://github.com/RPi-Distro/python-gpiozero/issues/182
.. _#189: https://github.com/RPi-Distro/python-gpiozero/issues/189
.. _#193: https://github.com/RPi-Distro/python-gpiozero/issues/193
.. _#222: https://github.com/RPi-Distro/python-gpiozero/issues/222
.. _#229: https://github.com/RPi-Distro/python-gpiozero/issues/229
.. _#251: https://github.com/RPi-Distro/python-gpiozero/issues/251

Release 1.1.0 (2016-02-08)
==========================

* Documentation converted to reST and expanded to include generic classes
  and several more recipes (`#80`_, `#82`_, `#101`_, `#119`_, `#135`_, `#168`_)
* New :class:`CamJamKitRobot` class with the pre-defined motor pins for the new
  CamJam EduKit
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
