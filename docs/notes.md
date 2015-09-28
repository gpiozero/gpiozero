# Notes

1. BCM pin numbering

    This library uses BCM pin numbering for the GPIO pins, as opposed to BOARD. Unlike the `RPi.GPIO` library, it is not configurable.

    Any pin marked `GPIO` can be used for generic components.

    The BCM pin layout is as follows:

    |            |            |
    |-----------:|:-----------|
    |    3V3     | 5V         |
    |  **GPIO2** | 5V         |
    |  **GPIO3** | GND        |
    |  **GPIO4** | **GPIO14** |
    |        GND | **GPIO15** |
    | **GPIO17** | **GPIO18** |
    | **GPIO27** | GND        |
    | **GPIO22** | **GPIO23** |
    |        3V3 | **GPIO24** |
    | **GPIO10** | GND        |
    |  **GPIO9** | **GPIO25** |
    | **GPIO11** | **GPIO8**  |
    |        GND | **GPIO7**  |
    |        DNC | DNC        |
    |  **GPIO5** | GND        |
    |  **GPIO6** | **GPIO12** |
    | **GPIO13** | GND        |
    | **GPIO19** | **GPIO16** |
    | **GPIO26** | **GPIO20** |
    |        GND | **GPIO21** |

    - *GND = Ground*
    - *3V3 = 3.3 Volts*
    - *5V = 5 Volts*
    - *DNC = Do not connect (special use pins)*

1. Wiring

    All components must be wired up correctly before using with this library.
