from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QWidget,
    QDoubleSpinBox
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
        self._lower_threshold = 23
        self._upper_threshold = 30

        # Labels
        self.temperature_label = QLabel(f"Temperature: {self._temperature}°C")

        # Layout
        layout = QVBoxLayout()
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
    
    def _read_temperature(self):
        self._temperature = self._cmd.read_temperature()
        self.temperature_label.setText(f"Temperature: {self._temperature}°C")
        self._evaluate_thresholds()

    def _evaluate_thresholds(self):
        if self._temperature == -1:
            return
        
        if self._temperature <= self._lower_threshold:
            if not self._red_state:
                self._red_state = True
                self._cmd.toggle_red_led(True)
            if self._green_state:
                self._green_state = False
                self._cmd.toggle_green_led(False)
        
        elif self._temperature >= self._upper_threshold:
            if not self._green_state:
                self._green_state = True
                self._cmd.toggle_green_led(True)
            if self._red_state:
                self._red_state = False
                self._cmd.toggle_red_led(False)
        else:
            self._red_state = False
            self._cmd.toggle_red_led(False)
            self._green_state = False
            self._cmd.toggle_green_led(False)


                