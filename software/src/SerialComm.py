import threading
import queue
import time
import serial

class SerialComm:
    def __init__(
            self,
            port: str,
            baudrate: int = 115200,
            timeout: float = 1.0
    ):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.rx_queue: queue.Queue[str] = queue.Queue()
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
                        self.rx_queue.put(line)
            except (serial.SerialException, TypeError):
                break

    def write(self, data: str) -> None:
        encoded = data.encode("utf-8")
        with self._write_lock:
            self.ser.write(encoded)

    def read(self, block: bool = True, timeout: float | None = None) -> str | None:
        try:
            return self.rx_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None