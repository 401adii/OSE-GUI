from src.SerialComm import SerialComm
from src.CmdInterface import CmdInterface
from src.Ui import Ui


def main():
    serial = SerialComm(port="/dev/ttyUSB0")
    cmd_interface = CmdInterface(serial)
    ui = Ui(cmd_interface)
    ui.run()

if __name__ == "__main__":
    main()