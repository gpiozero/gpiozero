from gpiozero import HumidityTemperatureSensor
from time import sleep

sensor = HumidityTemperatureSensor(4)

while True:
    reading = sensor.reading
    if reading.temperature is not None:
        print(f"Temperature: {reading.temperature:.1f}°C  Humidity: {reading.humidity:.1f}%")
    else:
        print("Waiting for sensor...")
    sleep(3)
