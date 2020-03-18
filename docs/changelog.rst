.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2016-2020 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
..
.. Redistribution and use in source and binary forms, with or without
.. modification, are permitted provided that the following conditions are met:
..
.. * Redistributions of source code must retain the above copyright notice,
..   this list of conditions and the following disclaimer.
..
.. * Redistributions in binary form must reproduce the above copyright notice,
..   this list of conditions and the following disclaimer in the documentation
..   and/or other materials provided with the distribution.
..
.. * Neither the name of the copyright holder nor the names of its contributors
..   may be used to endorse or promote products derived from this software
..   without specific prior written permission.
..
.. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
.. AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
.. IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
.. ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
.. LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
.. CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
.. SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
.. INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
.. CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
.. ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
.. POSSIBILITY OF SUCH DAMAGE.

=========
Changelog
=========

.. currentmodule:: gpiozero

Release 1.5.2 (unreleased)
==========================

* Added :class:`Pibrella` class (thanks to Carl Monk) (`#773`_, `#798`_)
* Added :class:`TrafficpHat` class (thanks to Ryan Walmsley) (`#845`_, `#846`_)
* Allow :class:`Motor` to pass :attr:`~Device.pin_factory` to its child
  :class:`OutputDevice` objects (thanks to Yisrael Dov Lebow) (`#792`_)
* Small SPI exception fix (thanks to Maksim Levental) (`#762`_)
* Warn users when using default pin factory for Servos and Distance Sensors
  (thanks to Sofiia Kosovan and Daniele Procida at the EuroPython sprints)
  (`#780`_, `#781`_)
* Add :attr:`~Servo.pulse_width` property to :class:`Servo` (suggested by
  Daniele Procida at the PyCon UK sprints) (`#795`_, `#797`_)
* Various docs updates

.. _#773: https://github.com/gpiozero/gpiozero/issues/773
.. _#798: https://github.com/gpiozero/gpiozero/issues/798
.. _#792: https://github.com/gpiozero/gpiozero/issues/792
.. _#845: https://github.com/gpiozero/gpiozero/issues/845
.. _#846: https://github.com/gpiozero/gpiozero/issues/846
.. _#762: https://github.com/gpiozero/gpiozero/issues/762
.. _#780: https://github.com/gpiozero/gpiozero/issues/780
.. _#781: https://github.com/gpiozero/gpiozero/issues/781
.. _#795: https://github.com/gpiozero/gpiozero/issues/795
.. _#797: https://github.com/gpiozero/gpiozero/issues/797

Release 1.5.1 (2019-06-24)
==========================

* Added Raspberry Pi 4 data for :func:`pi_info` and :program:`pinout`
* Minor docs updates

Release 1.5.0 (2019-02-12)
==========================

* Introduced pin event timing to increase accuracy of certain devices such as
  the HC-SR04 :class:`DistanceSensor`. (`#664`_, `#665`_)
* Further improvements to :class:`DistanceSensor` (ignoring missed edges).
  (`#719`_)
* Allow :attr:`~Device.source` to take a device object as well as
  :attr:`~Device.values` or other ``values``. See :doc:`Source/Values
  <source_values>`. (`#640`_)
* Added internal device classes :class:`LoadAverage` and :class:`DiskUsage`
  (thanks to Jeevan M R for the latter). (`#532`_, `#714`_)
* Added support for `colorzero`_ with :class:`RGBLED` (this adds a new
  dependency). (`#655`_)
* Added :class:`TonalBuzzer` with :class:`~tones.Tone` API for specifying frequencies
  raw or via MIDI or musical notes. (`#681`_, `#717`_)
* Added :class:`PiHutXmasTree`. (`#502`_)
* Added :class:`PumpkinPi` and :class:`JamHat` (thanks to Claire Pollard).
  (`#680`_, `#681`_, `#717`_)
* Ensured gpiozero can be imported without a valid pin factory set. (`#591`_,
  `#713`_)
* Reduced import time by not computing default pin factory at the point of
  import. (`#675`_, `#722`_)
* Added support for various pin numbering mechanisms. (`#470`_)
* :class:`Motor` instances now use :class:`DigitalOutputDevice` for non-PWM
  pins.
* Allow non-PWM use of :class:`Robot`. (`#481`_)
* Added optional ``enable`` init param to :class:`Motor`. (`#366`_)
* Added ``--xyz`` option to :program:`pinout` command line tool to open
  `pinout.xyz`_ in a web browser. (`#604`_)
* Added 3B+, 3A+ and CM3+ to Pi model data. (`#627`_, `#704`_)
* Minor improvements to :class:`Energenie`, thanks to Steve Amor. (`#629`_,
  `#634`_)
* Allow :class:`SmoothedInputDevice`, :class:`LightSensor` and
  :class:`MotionSensor` to have pull-up configured. (`#652`_)
* Allow input devices to be pulled up or down externally, thanks to Philippe
  Muller. (`#593`_, `#658`_)
* Minor changes to support Python 3.7, thanks to Russel Winder and Rick Ansell.
  (`#666`_, `#668`_, `#669`_, `#671`_, `#673`_)
* Added :func:`~tools.zip_values` source tool.
* Correct row/col numbering logic in :class:`PinInfo`. (`#674`_)
* Many additional tests, and other improvements to the test suite.
* Many documentation corrections, additions and clarifications.
* Automatic documentation class hierarchy diagram generation.
* Automatic copyright attribution in source files.

.. _#640: https://github.com/gpiozero/gpiozero/issues/640
.. _#664: https://github.com/gpiozero/gpiozero/issues/664
.. _#665: https://github.com/gpiozero/gpiozero/issues/665
.. _#719: https://github.com/gpiozero/gpiozero/issues/719
.. _#532: https://github.com/gpiozero/gpiozero/issues/532
.. _#714: https://github.com/gpiozero/gpiozero/issues/714
.. _colorzero: https://colorzero.readthedocs.io/en/stable
.. _#655: https://github.com/gpiozero/gpiozero/issues/655
.. _#681: https://github.com/gpiozero/gpiozero/issues/681
.. _#717: https://github.com/gpiozero/gpiozero/issues/717
.. _#680: https://github.com/gpiozero/gpiozero/issues/680
.. _#502: https://github.com/gpiozero/gpiozero/issues/502
.. _#591: https://github.com/gpiozero/gpiozero/issues/591
.. _#713: https://github.com/gpiozero/gpiozero/issues/713
.. _#675: https://github.com/gpiozero/gpiozero/issues/675
.. _#722: https://github.com/gpiozero/gpiozero/issues/722
.. _#470: https://github.com/gpiozero/gpiozero/issues/470
.. _#481: https://github.com/gpiozero/gpiozero/issues/481
.. _#366: https://github.com/gpiozero/gpiozero/issues/366
.. _pinout.xyz: https://pinout.xyz
.. _#604: https://github.com/gpiozero/gpiozero/issues/604
.. _#627: https://github.com/gpiozero/gpiozero/issues/627
.. _#704: https://github.com/gpiozero/gpiozero/issues/704
.. _#629: https://github.com/gpiozero/gpiozero/issues/629
.. _#634: https://github.com/gpiozero/gpiozero/issues/634
.. _#652: https://github.com/gpiozero/gpiozero/issues/652
.. _#593: https://github.com/gpiozero/gpiozero/issues/593
.. _#658: https://github.com/gpiozero/gpiozero/issues/658
.. _#666: https://github.com/gpiozero/gpiozero/issues/666
.. _#668: https://github.com/gpiozero/gpiozero/issues/668
.. _#669: https://github.com/gpiozero/gpiozero/issues/669
.. _#671: https://github.com/gpiozero/gpiozero/issues/671
.. _#673: https://github.com/gpiozero/gpiozero/issues/673
.. _#674: https://github.com/gpiozero/gpiozero/issues/674

Release 1.4.1 (2018-02-20)
==========================

This release is mostly bug-fixes, but a few enhancements have made it in too:

* Added ``curve_left`` and ``curve_right`` parameters to :meth:`Robot.forward`
  and :meth:`Robot.backward`. (`#306`_ and `#619`_)
* Fixed :class:`DistanceSensor` returning incorrect readings after a long
  pause, and added a lock to ensure multiple distance sensors can operate
  simultaneously in a single project. (`#584`_, `#595`_, `#617`_, `#618`_)
* Added support for phase/enable motor drivers with :class:`PhaseEnableMotor`,
  :class:`PhaseEnableRobot`, and descendants, thanks to Ian Harcombe!
  (`#386`_)
* A variety of other minor enhancements, largely thanks to Andrew Scheller!
  (`#479`_, `#489`_, `#491`_, `#492`_)

.. _#306: https://github.com/gpiozero/gpiozero/issues/306
.. _#386: https://github.com/gpiozero/gpiozero/issues/386
.. _#479: https://github.com/gpiozero/gpiozero/issues/479
.. _#489: https://github.com/gpiozero/gpiozero/issues/489
.. _#491: https://github.com/gpiozero/gpiozero/issues/491
.. _#492: https://github.com/gpiozero/gpiozero/issues/492
.. _#584: https://github.com/gpiozero/gpiozero/issues/584
.. _#595: https://github.com/gpiozero/gpiozero/issues/595
.. _#617: https://github.com/gpiozero/gpiozero/issues/617
.. _#618: https://github.com/gpiozero/gpiozero/issues/618
.. _#619: https://github.com/gpiozero/gpiozero/issues/619

Release 1.4.0 (2017-07-26)
==========================

* Pin factory is now :ref:`configurable from device constructors
  <changing-pin-factory>` as well as command line. NOTE: this is a backwards
  incompatible change for manual pin construction but it's hoped this is
  (currently) a sufficiently rare use case that this won't affect too many
  people and the benefits of the new system warrant such a change, i.e. the
  ability to use remote pin factories with HAT classes that don't accept pin
  assignations (`#279`_)
* Major work on SPI, primarily to support remote hardware SPI (`#421`_,
  `#459`_, `#465`_, `#468`_, `#575`_)
* Pin reservation now works properly between GPIO and SPI devices (`#459`_,
  `#468`_)
* Lots of work on the documentation: :doc:`source/values chapter
  <source_values>`, better charts, more recipes, :doc:`remote GPIO
  configuration <remote_gpio>`, mock pins, better PDF output (`#484`_, `#469`_,
  `#523`_, `#520`_, `#434`_, `#565`_, `#576`_)
* Support for :class:`StatusZero` and :class:`StatusBoard` HATs (`#558`_)
* Added :program:`pinout` command line tool to provide a simple
  reference to the GPIO layout and information about the associated Pi
  (`#497`_, `#504`_) thanks to Stewart Adcock for the initial work
* :func:`pi_info` made more lenient for new (unknown) Pi models (`#529`_)
* Fixed a variety of packaging issues (`#535`_, `#518`_, `#519`_)
* Improved text in factory fallback warnings (`#572`_)

.. _#279: https://github.com/gpiozero/gpiozero/issues/279
.. _#421: https://github.com/gpiozero/gpiozero/issues/421
.. _#434: https://github.com/gpiozero/gpiozero/issues/434
.. _#459: https://github.com/gpiozero/gpiozero/issues/459
.. _#465: https://github.com/gpiozero/gpiozero/issues/465
.. _#468: https://github.com/gpiozero/gpiozero/issues/468
.. _#469: https://github.com/gpiozero/gpiozero/issues/469
.. _#484: https://github.com/gpiozero/gpiozero/issues/484
.. _#497: https://github.com/gpiozero/gpiozero/issues/497
.. _#504: https://github.com/gpiozero/gpiozero/issues/504
.. _#518: https://github.com/gpiozero/gpiozero/issues/518
.. _#519: https://github.com/gpiozero/gpiozero/issues/519
.. _#520: https://github.com/gpiozero/gpiozero/issues/520
.. _#523: https://github.com/gpiozero/gpiozero/issues/523
.. _#529: https://github.com/gpiozero/gpiozero/issues/529
.. _#535: https://github.com/gpiozero/gpiozero/issues/535
.. _#558: https://github.com/gpiozero/gpiozero/issues/558
.. _#565: https://github.com/gpiozero/gpiozero/issues/565
.. _#572: https://github.com/gpiozero/gpiozero/issues/572
.. _#575: https://github.com/gpiozero/gpiozero/issues/575
.. _#576: https://github.com/gpiozero/gpiozero/issues/576

Release 1.3.2 (2017-03-03)
==========================

* Added new Pi models to stop :func:`pi_info` breaking
* Fix issue with :func:`pi_info` breaking on unknown Pi models

Release 1.3.1 (2016-08-31 ... later)
====================================

* Fixed hardware SPI support which Dave broke in 1.3.0. Sorry!
* Some minor docs changes

Release 1.3.0 (2016-08-31)
==========================

* Added :class:`ButtonBoard` for reading multiple buttons in a single
  class (`#340`_)
* Added :class:`Servo` and :class:`AngularServo` classes for controlling
  simple servo motors (`#248`_)
* Lots of work on supporting easier use of internal and third-party pin
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

.. _#248: https://github.com/gpiozero/gpiozero/issues/248
.. _#289: https://github.com/gpiozero/gpiozero/issues/289
.. _#294: https://github.com/gpiozero/gpiozero/issues/294
.. _#295: https://github.com/gpiozero/gpiozero/issues/295
.. _#305: https://github.com/gpiozero/gpiozero/issues/305
.. _#320: https://github.com/gpiozero/gpiozero/issues/320
.. _#340: https://github.com/gpiozero/gpiozero/issues/340
.. _#359: https://github.com/gpiozero/gpiozero/issues/359
.. _#385: https://github.com/gpiozero/gpiozero/issues/385

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
  :class:`~gpiozero.pins.pigpio.PiGPIOPin` (`#180`_)
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

.. _#69: https://github.com/gpiozero/gpiozero/issues/69
.. _#109: https://github.com/gpiozero/gpiozero/issues/109
.. _#114: https://github.com/gpiozero/gpiozero/issues/114
.. _#115: https://github.com/gpiozero/gpiozero/issues/115
.. _#130: https://github.com/gpiozero/gpiozero/issues/130
.. _#140: https://github.com/gpiozero/gpiozero/issues/140
.. _#162: https://github.com/gpiozero/gpiozero/issues/162
.. _#164: https://github.com/gpiozero/gpiozero/issues/164
.. _#175: https://github.com/gpiozero/gpiozero/issues/175
.. _#180: https://github.com/gpiozero/gpiozero/issues/180
.. _#181: https://github.com/gpiozero/gpiozero/issues/181
.. _#182: https://github.com/gpiozero/gpiozero/issues/182
.. _#189: https://github.com/gpiozero/gpiozero/issues/189
.. _#193: https://github.com/gpiozero/gpiozero/issues/193
.. _#222: https://github.com/gpiozero/gpiozero/issues/222
.. _#229: https://github.com/gpiozero/gpiozero/issues/229
.. _#251: https://github.com/gpiozero/gpiozero/issues/251

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

.. _#80: https://github.com/gpiozero/gpiozero/issues/80
.. _#82: https://github.com/gpiozero/gpiozero/issues/82
.. _#94: https://github.com/gpiozero/gpiozero/issues/94
.. _#101: https://github.com/gpiozero/gpiozero/issues/101
.. _#118: https://github.com/gpiozero/gpiozero/issues/118
.. _#119: https://github.com/gpiozero/gpiozero/issues/119
.. _#126: https://github.com/gpiozero/gpiozero/issues/126
.. _#135: https://github.com/gpiozero/gpiozero/issues/135
.. _#141: https://github.com/gpiozero/gpiozero/issues/141
.. _#143: https://github.com/gpiozero/gpiozero/issues/143
.. _#150: https://github.com/gpiozero/gpiozero/issues/150
.. _#154: https://github.com/gpiozero/gpiozero/issues/154
.. _#161: https://github.com/gpiozero/gpiozero/issues/161
.. _#168: https://github.com/gpiozero/gpiozero/issues/168
.. _#174: https://github.com/gpiozero/gpiozero/issues/174
.. _#176: https://github.com/gpiozero/gpiozero/issues/176

Release 1.0.0 (2015-11-16)
==========================

* Debian packaging added (`#44`_)
* :class:`PWMLED` class added (`#58`_)
* ``TemperatureSensor`` removed pending further work (`#93`_)
* :meth:`Buzzer.beep` alias method added (`#75`_)
* :class:`Motor` PWM devices exposed, and :class:`Robot` motor devices exposed
  (`#107`_)

.. _#44: https://github.com/gpiozero/gpiozero/issues/44
.. _#58: https://github.com/gpiozero/gpiozero/issues/58
.. _#93: https://github.com/gpiozero/gpiozero/issues/93
.. _#75: https://github.com/gpiozero/gpiozero/issues/75
.. _#107: https://github.com/gpiozero/gpiozero/issues/107

Release 0.9.0 (2015-10-25)
==========================

Fourth public beta

* Added source and values properties to all relevant classes (`#76`_)
* Fix names of parameters in :class:`Motor` constructor (`#79`_)
* Added wrappers for LED groups on add-on boards (`#81`_)

.. _#76: https://github.com/gpiozero/gpiozero/issues/76
.. _#79: https://github.com/gpiozero/gpiozero/issues/79
.. _#81: https://github.com/gpiozero/gpiozero/issues/81

Release 0.8.0 (2015-10-16)
==========================

Third public beta

* Added generic :class:`AnalogInputDevice` class along with specific classes
  for the :class:`MCP3008` and :class:`MCP3004` (`#41`_)
* Fixed :meth:`DigitalOutputDevice.blink` (`#57`_)

.. _#41: https://github.com/gpiozero/gpiozero/issues/41
.. _#57: https://github.com/gpiozero/gpiozero/issues/57

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
