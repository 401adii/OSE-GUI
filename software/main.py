import signal
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from src.SerialComm import SerialComm
from src.CmdInterface import CmdInterface
from src.Ui import Ui

def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        print("usage: python3 main.py <serial-port>")
        sys.exit(1)

    app = QApplication([])

    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(200)
    try:
        serial = SerialComm(port=port)
    except Exception as e:
        print(f"Could not open {port}: {e}")
        sys.exit(1)

    cmd_interface = CmdInterface(serial)
    ui = Ui(cmd=cmd_interface)
    ui.show()
    
    app.exec()

if __name__ == "__main__":
    main()