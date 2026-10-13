from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QDoubleSpinBox
)
from PySide6.QtCore import QTimer
from src.CmdInterface import CmdInterface

TEMPERATURE_POLLING_MS = 1000

class Ui(QMainWindow):
    def __init__(self, cmd: CmdInterface):
        super().__init__()
        
        self._cmd = cmd

        self.setWindowTitle("Temperature Alert System")

        # Private state variables
        self._temperature = -1
        self._red_state = False
        self._green_state = False
        self._lower_threshold = 23.0
        self._upper_threshold = 30.0

        # Labels
        self.temperature_label = QLabel(f"Temperature: {self._temperature}°C")

        # Spinboxes
        self._lower_spinbox = QDoubleSpinBox()
        self._lower_spinbox.setRange(-50.0, 150.0)
        self._lower_spinbox.setValue(self._lower_threshold)
        self._lower_spinbox.setSingleStep(0.5)

        self._upper_spinbox = QDoubleSpinBox()
        self._upper_spinbox.setRange(-50.0, 150.0)
        self._upper_spinbox.setValue(self._upper_threshold)
        self._upper_spinbox.setSingleStep(0.5)

        # Enforce initial boundaries so they don't overlap on startup
        self._lower_spinbox.setMaximum(self._upper_threshold - 0.5)
        self._upper_spinbox.setMinimum(self._lower_threshold + 0.5)

        # Signals
        self._lower_spinbox.valueChanged.connect(self._update_lower_threshold)
        self._upper_spinbox.valueChanged.connect(self._update_upper_threshold)

        # Layouts
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(QLabel("Lower threshold (°C):"))
        lower_layout.addWidget(self._lower_spinbox)

        upper_layout = QHBoxLayout()
        upper_layout.addWidget(QLabel("Upper threshold (°C):"))
        upper_layout.addWidget(self._upper_spinbox)

        layout = QVBoxLayout()
        layout.addWidget(self.temperature_label)
        layout.addLayout(lower_layout)
        layout.addLayout(upper_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Init calls
        self._cmd.read_temperature()
        self._cmd.toggle_red_led(self._red_state)
        self._cmd.toggle_green_led(self._green_state)

        # Timer for repeated temperature polling
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._read_temperature)
        self._timer.start(TEMPERATURE_POLLING_MS)
    
    def _read_temperature(self):
        self._temperature = self._cmd.read_temperature()
        self.temperature_label.setText(f"Temperature: {self._temperature}°C")
        self._evaluate_thresholds()

    def _update_lower_threshold(self, value):
        self._lower_threshold = value
        self._upper_spinbox.setMinimum(value + 0.5)
        self._evaluate_thresholds()

    def _update_upper_threshold(self, value):
        self._upper_threshold = value
        self._lower_spinbox.setMaximum(value - 0.5)
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
            if self._red_state:
                self._red_state = False
                self._cmd.toggle_red_led(False)
            if self._green_state:
                self._green_state = False
                self._cmd.toggle_green_led(False)