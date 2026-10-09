import threading
from typing import Callable, Optional
import serial

class SerialComm:
    def __init__(
            self,
            port: str,
            on_data: Callable[[str], None],
            baudrate: int = 115200,
            timeout: float = 1.0
    ):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

        self._on_data: Callable[[str], None] = on_data
        self._stop_event = threading.Event()
        self._write_lock = threading.Lock()

        self._worker_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._worker_thread.start()

    def _reader_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                if self.ser.in_waiting > 0 or self.ser.timeout:
                    raw_data = self.ser.readline()
                    if raw_data:
                        line = raw_data.decode("utf-8", errors="replace").strip("\n")
                        self._on_data(line)
            except (serial.SerialException, TypeError):
                break

    def write(self, data: str) -> None:
        encoded = data.encode("utf-8")
        with self._write_lock:
            self.ser.write(encoded)