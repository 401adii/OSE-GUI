from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QDoubleSpinBox
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from src.CmdInterface import CmdInterface

TEMPERATURE_POLLING_MS = 1000

class Ui(QMainWindow):
    def __init__(self, cmd: CmdInterface):
        super().__init__()
        
        self._cmd = cmd
        self.setWindowTitle("Temperature Alert System")

        # State variables
        self._temperature = -1
        self._red_state = False
        self._green_state = False
        self._lower_threshold = 23.0
        self._upper_threshold = 30.0
        self._time_counter = 0

        # UI Widgets
        self.temperature_label = QLabel(f"Temperature: {self._temperature}°C")
        self.temperature_label.setStyleSheet("font-size: 14pt; font-weight: bold;")

        self._lower_spinbox = QDoubleSpinBox()
        self._lower_spinbox.setRange(-50.0, 150.0)
        self._lower_spinbox.setValue(self._lower_threshold)
        self._lower_spinbox.setSingleStep(0.5)
        self._lower_spinbox.setMaximum(self._upper_threshold - 0.5)

        self._upper_spinbox = QDoubleSpinBox()
        self._upper_spinbox.setRange(-50.0, 150.0)
        self._upper_spinbox.setValue(self._upper_threshold)
        self._upper_spinbox.setSingleStep(0.5)
        self._upper_spinbox.setMinimum(self._lower_threshold + 0.5)

        self._red_led_widget = QLabel()
        self._red_led_widget.setFixedSize(24, 24)

        self._green_led_widget = QLabel()
        self._green_led_widget.setFixedSize(24, 24)

        self._update_led_styles()

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

        red_led_layout = QHBoxLayout()
        red_led_layout.addWidget(QLabel("Red LED Alarm:"))
        red_led_layout.addWidget(self._red_led_widget)
        red_led_layout.addStretch()

        green_led_layout = QHBoxLayout()
        green_led_layout.addWidget(QLabel("Green LED Alarm:"))
        green_led_layout.addWidget(self._green_led_widget)
        green_led_layout.addStretch()

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.temperature_label)
        right_layout.addSpacing(10)
        right_layout.addLayout(lower_layout)
        right_layout.addLayout(upper_layout)
        right_layout.addSpacing(15)
        right_layout.addLayout(red_led_layout)
        right_layout.addLayout(green_led_layout)
        right_layout.addStretch()

        # Chart Setup
        self._series = QLineSeries()
        self._chart = QChart()
        self._chart.addSeries(self._series)
        self._chart.setTitle("Temperature over Time")
        self._chart.legend().hide()

        self._axis_x = QValueAxis()
        self._axis_x.setTitleText("Time (s)")
        self._axis_x.setRange(0, 60)
        self._chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._series.attachAxis(self._axis_x)

        self._axis_y = QValueAxis()
        self._axis_y.setTitleText("Temperature (°C)")
        self._axis_y.setRange(-10, 50)
        self._chart.addAxis(self._axis_y, Qt.AlignLeft)
        self._series.attachAxis(self._axis_y)

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self._chart_view.setMinimumSize(500, 350)

        # Main Layout (Graph Left, Controls Right)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._chart_view, stretch=3)
        main_layout.addLayout(right_layout, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Init hardware state
        try:
            self._cmd.toggle_red_led(False)
            self._cmd.toggle_green_led(False)
        except Exception:
            pass

        # Timer setup
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._read_temperature)
        self._timer.start(TEMPERATURE_POLLING_MS)
    
    def _read_temperature(self):
        try:
            temp = self._cmd.read_temperature()
            if temp is not None:
                self._temperature = temp
                self.temperature_label.setText(f"Temperature: {self._temperature}°C")
                self._evaluate_thresholds()

                if self._temperature != -1:
                    self._series.append(self._time_counter, self._temperature)
                    if self._time_counter > 60:
                        self._axis_x.setRange(self._time_counter - 60, self._time_counter)
                    else:
                        self._axis_x.setRange(0, max(60, self._time_counter))
                    self._time_counter += 1
        except Exception as e:
            print(f"Warning: Failed to read temperature ({e})")

    def _update_lower_threshold(self, value):
        self._lower_threshold = value
        self._upper_spinbox.setMinimum(value + 0.5)
        self._evaluate_thresholds()

    def _update_upper_threshold(self, value):
        self._upper_threshold = value
        self._lower_spinbox.setMaximum(value - 0.5)
        self._evaluate_thresholds()

    def _update_led_styles(self):
        if self._red_state:
            red_style = "background-color: #ff3333; border-radius: 12px; border: 2px solid #cc0000;"
        else:
            red_style = "background-color: #442222; border-radius: 12px; border: 2px solid #221111;"
        self._red_led_widget.setStyleSheet(red_style)

        if self._green_state:
            green_style = "background-color: #33cc33; border-radius: 12px; border: 2px solid #009900;"
        else:
            green_style = "background-color: #224422; border-radius: 12px; border: 2px solid #112211;"
        self._green_led_widget.setStyleSheet(green_style)

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

        # Update the visual LED colors on the UI
        self._update_led_styles()

    def closeEvent(self, event):
        try:
            self._cmd.toggle_red_led(False)
            self._cmd.toggle_green_led(False)
        except Exception:
            pass
            
        if hasattr(self, '_timer'):
            self._timer.stop()
            
        event.accept()