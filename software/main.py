import signal
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from src.SerialComm import SerialComm
from src.CmdInterface import CmdInterface
from src.Ui import Ui

def main():
    app = QApplication([])

    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())
    
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(200)

    serial = SerialComm(port="/dev/ttyUSB0")
    cmd_interface = CmdInterface(serial)
    ui = Ui(cmd=cmd_interface)
    ui.show()
    
    app.exec()

if __name__ == "__main__":
    main()