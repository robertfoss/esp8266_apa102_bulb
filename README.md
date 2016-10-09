# esp8266_apa102_bulb
ESP8266 based animated APA102 bulbs.


## PCB model ##

![Alt text](/../media/v4.1_3d_model_front.png?raw=true "v4.1: 3D render of the PCB")


## Schematic ##

![Alt text](/../media/v3.1_schematic.png?raw=true "v3.1: Schematic")


## Assembled v2 hardware ##

![Alt text](/../media/v2_95pct_assembled.jpg?raw=true "v2: 95% assembled")
![Alt text](/../media/v2_running.jpg?raw=true "v2: Assembled and running over WiFi")
![Alt text](/../media/v2_hanging.jpg?raw=true "v2: Hanging and running over WiFi")

## Changelog

v4.1
 * Added missing silkscreen
 * Switched from EBC to BEC NPN transistor, to match S8050 part.
 * Changed C7/C8/C10 footprints from 0603->0805
 * Reduced GND pad size of U4 (3.3V LDO)

v4:
 * Reworked inter-pcb connections to minimize gap between leds.
 * Changed APA102 -> GPIO pin mapping.
 * Cost optimized board to fit within 10x10cm envelope.
