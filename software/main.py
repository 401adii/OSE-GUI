from src.SerialComm import SerialComm
from src.CmdInterface import CmdInterface
from src.Ui import Ui
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication([])
    serial = SerialComm(port="/dev/ttyUSB0")
    cmd_interface = CmdInterface(serial)
    ui = Ui(cmd=cmd_interface)
    ui.show()
    app.exec()

if __name__ == "__main__":
    main()