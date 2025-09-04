# Raspberry Pi Hydroponics (Prototype)

A Raspberry Pi–driven hydroponics prototype to automatically water plants using DC water pumps, based on soil moisture readings.

Hardware context:
- H-bridge motor driver controlling pumps (IN1 = GPIO20, IN2 = GPIO21)
- MCP3008 ADC on SPI reading the analog output of the “Capacitive Moisture Sensor v2.0”

Project scope:
- Early prototyping focused on reading moisture values and experimenting with simple threshold-based watering.
- Code and wiring are expected to evolve; calibration, reliability, and logging will be iterated on as the prototype matures.
