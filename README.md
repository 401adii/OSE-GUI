# Opis
Repozytorium zawiera kod źródłowy projektu powstałego w ramach przedmiotu "Oprogramowanie Systemów Elektronicznych - Projekt" prowadzonego na kierunku Elektronika i Telekomunikacja (2 stopień) na wydziale ETI Politechniki Gdańskiej.
# Uruchamianie
## Firmware
W celu wgrania i uruchomienia firmware na mikrokontroler ESP-32 należy zainstalować środowisko [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html) (wersja 6.1)

Następnie należy wgrać oprogramowanie znajdujące się w katalogu [firmware](firmware/) za pomocą EIM GUI lub wpisując w terminalu:
```bash
idf.py build flash monitor
```

## Software
Aby uruchomić aplikację należy w katalogu [software](software/) wproadzić:
```bash
./scripts/setup.sh
source ./.venv/bin/activate
./scripts/start.sh <port>
```

# Autorzy
* Hubert Mucha     193152
* Adrian Czekański 193216