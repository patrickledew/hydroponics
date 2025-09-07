import gpiozero
import asyncio

class MoistureSensor():
    def __init__(self, channel=0):
        # MCP3008 required for A/D conversion
        # https://learn.adafruit.com/assets/30456
        # VDD -> 3.3V
        # VREF -> 3.3V
        # AGND -> Pi GND
        # DGND -> Pi GND
        self.sensor = gpiozero.MCP3008(channel)

    def read_value(self):
        return 1 - self.sensor.value
        
    async def get_moisture_level(self):
        """Get moisture level as a percentage (0-100)"""
        # Convert the raw value (0-1) to a percentage
        raw_value = self.read_value()
        return int(raw_value * 100)
