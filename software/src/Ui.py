from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QWidget
    )
from PySide6.QtCore import QTimer
from src.CmdInterface import CmdInterface
import time


class Ui(QMainWindow):
    global TEMPERATURE_POLLING_MS
    TEMPERATURE_POLLING_MS = 1000

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

        # Labels
        self.temperature_label = QLabel(f"Temperature: {self._temperature}°C")

        
        # Signals
        self.red_led_button.clicked.connect(self._toggle_red)        
        self.green_led_button.clicked.connect(self._toggle_green)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.red_led_button)
        layout.addWidget(self.green_led_button)
        layout.addWidget(self.temperature_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Init calls
        self._cmd.read_temperature()
        time.sleep(0.01) # Delays, because it breaks without them
        self._cmd.toggle_red_led(self._red_state)
        time.sleep(0.01)
        self._cmd.toggle_green_led(self._green_state)

        # Timer for repeated temperature polling
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._read_temperature)
        self._timer.start(TEMPERATURE_POLLING_MS)

    def _toggle_red(self):
        self._red_state = not self._red_state
        self._cmd.toggle_red_led(self._red_state)
    
    def _toggle_green(self):
        self._green_state = not self._green_state
        self._cmd.toggle_green_led(self._green_state)
    
    def _read_temperature(self):
        self._temperature = self._cmd.read_temperature()
        self.temperature_label.setText(f"Temperature: {self._temperature}°C")