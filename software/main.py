import serial

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1.0)
data = "LEDR 0".encode("utf-8")
ser.write(data)