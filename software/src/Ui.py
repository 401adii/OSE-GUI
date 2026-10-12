from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QWidget
    )
from src.CmdInterface import CmdInterface
import time

class Ui(QMainWindow):
    def __init__(self, cmd: CmdInterface):
        super().__init__()
        
        self._cmd = cmd

        self.setWindowTitle("Temperature Alert System")

        # Private state variables
        self._temperature = -1
        self._red_state = False
        self._green_state = False
        
        # Buttons
        self.red_led_button = QPushButton("Red Led")
        self.green_led_button = QPushButton("Green Led")
        self.temperature_button = QPushButton("Read Temperature")

        # Labels
        self.temperature_label = QLabel(f"Temperature: {self._temperature}°C")

        # Signals
        self.red_led_button.clicked.connect(self._toggle_red)        
        self.green_led_button.clicked.connect(self._toggle_green)
        self.temperature_button.clicked.connect(self._read_temperature)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.red_led_button)
        layout.addWidget(self.green_led_button)
        layout.addWidget(self.temperature_button)
        layout.addWidget(self.temperature_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _toggle_red(self):
        self._red_state = not self._red_state
        self._cmd.toggle_red_led(self._red_state)
    
    def _toggle_green(self):
        self._green_state = not self._green_state
        self._cmd.toggle_green_led(self._green_state)
    
    def _read_temperature(self):
        self._temperature = self._cmd.read_temperature()
        self.temperature_label.setText(f"Temperature: {self._temperature}°C")