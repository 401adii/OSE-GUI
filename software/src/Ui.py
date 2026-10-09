from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QWidget
    )
from src.CmdInterface import CmdInterface
import time

class Ui():
    def __init__(self, cmd_interface: CmdInterface):
        self._app = QApplication([])
        self._main_window = QMainWindow()
        self._cmd = cmd_interface

        red_led_button = QPushButton("Red Led")
        green_led_button = QPushButton("Green Led")
        get_temp_button = QPushButton("Get Temperature")
        
        self._is_red_led_toggled = False
        self._is_green_led_toggled = False
        self._last_read_temperature = "???"
        
        self.label = QLabel(f"Temperature: {self._last_read_temperature} °C")
        
        layout = QVBoxLayout()
        layout.addWidget(red_led_button)
        layout.addWidget(green_led_button)
        layout.addWidget(get_temp_button)
        layout.addWidget(self.label)

        red_led_button.clicked.connect(self._toggle_red_led)
        green_led_button.clicked.connect(self._toggle_green_led)
        get_temp_button.clicked.connect(self._get_temp)
        
        self._cmd.toggle_red_led(self._is_red_led_toggled)
        time.sleep(0.1)
        self._cmd.toggle_green_led(self._is_green_led_toggled)

        container = QWidget()
        container.setLayout(layout)

        self._main_window.setCentralWidget(container)
    
        self._main_window.show()

    def _toggle_red_led(self) -> None:
        self._is_red_led_toggled = not self._is_red_led_toggled
        self._cmd.toggle_red_led(self._is_red_led_toggled)

    def _toggle_green_led(self) -> None:
        self._is_green_led_toggled = not self._is_green_led_toggled
        self._cmd.toggle_green_led(self._is_green_led_toggled)

    def _get_temp(self) -> None:
        self._last_read_temperature = self._cmd.read_temperature()
        self.label.setText(f"Temperature: {self._last_read_temperature} °C")

    def run(self) -> None:
        self._app.exec()        