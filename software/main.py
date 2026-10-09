from src.SerialComm import SerialComm

def handle_data(message: str) -> None:
    print(f"[RX]: {message}")

def main():
    serial_port = SerialComm(port="/dev/ttyUSB0", on_data=handle_data)
    serial_port.write("READANDGET")

    while True:
        pass


if __name__ == "__main__":
    main()