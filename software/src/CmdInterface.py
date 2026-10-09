from src.SerialComm import SerialComm

class CmdInterface:
    def __init__(self, serial_comm: SerialComm):
        self.serial = serial_comm

    def toggle_red_led(self, enabled: bool) -> None:
        self.serial.write(f"LEDR {int(enabled)}")

    def toggle_green_led(self, enabled: bool) -> None:
        self.serial.write(f"LEDG {int(enabled)}")

    def read_temperature(self) -> int:
        self.serial.write("READANDGET")
        return self.serial.read()

    