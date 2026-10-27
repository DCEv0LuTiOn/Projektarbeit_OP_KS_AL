import sys
from dynamixel_sdk import PortHandler, PacketHandler
from ax12_servo import AX12AServo

class DynamixelBus:
    """
    Verwaltet die serielle Hardware-Schnittstelle (COM-Port) und alle daran 
    angeschlossenen Dynamixel-Servos.
    """

    def __init__(self, device_name: str, baudrate: int = AX12AServo._DEFAULT_BAUDRATE, protocol_version: float = AX12AServo._DEFAULT_PROTOCOL_VERSION):
        """
        Initialisiert die Bus-Schnittstelle.

        Args:
            device_name (str): Name der Schnittstelle ('COM12', '/dev/ttyUSB0').
            baudrate (int): Baudrate in bps.
            protocol_version (float): Protokollversion.
        """
        self._device_name = device_name
        self._baudrate = baudrate
        self._protocol_version = protocol_version
        
        self._port_handler = PortHandler(device_name)
        self._packet_handler = PacketHandler(protocol_version)
        self._servos = {}

    def connect(self) -> bool:
        """Öffnet den seriellen Port und stellt die Baudrate ein."""
        if not self._port_handler.openPort():
            print(f"Fehler: Konnte Port {self._device_name} nicht öffnen!")
            return False
        if not self._port_handler.setBaudRate(self._baudrate):
            print(f"Fehler: Konnte Baudrate {self._baudrate} nicht setzen!")
            return False
        print(f"Bus-Verbindung hergestellt an {self._device_name} ({self._baudrate} bps).")
        return True

    def add_servo(self, dxl_id: int) -> AX12AServo:
        """Erstellt ein AX12AServo-Objekt auf diesem Bus und registriert es."""
        servo = AX12AServo(dxl_id, self._port_handler, self._packet_handler)
        self._servos[dxl_id] = servo
        return servo

    def get_servo(self, dxl_id: int) -> AX12AServo:
        """Gibt ein bereits registriertes Servo-Objekt anhand seiner ID zurück."""
        return self._servos.get(dxl_id)

    def wait_until_all_stopped(self, timeout: float = 10.0):
        """Wartet, bis alle registrierten Servos am Bus ihre Bewegung beendet haben."""
        for servo in self._servos.values():
            servo.wait_until_stopped(timeout=timeout)

    def disconnect(self, wait_for_servos: bool = True):
        """Trennt die Bus-Verbindung sauber und schaltet das Drehmoment ab."""
        if wait_for_servos:
            print("Warte auf Abschluss aller Servo-Bewegungen...")
            self.wait_until_all_stopped()

        for servo in self._servos.values():
            servo.disable_torque()
            
        self._port_handler.closePort()
        print("Bus-Verbindung getrennt.")


# ==============================================================================
# DIREKTER TEST DER BUS-KLASSE (`python dynamixel_bus.py`)
# ==============================================================================
if __name__ == '__main__':
    _DEVICENAME    = '/dev/ttyUSB0'   # 'COM12' (Windows) oder '/dev/ttyUSB0' (Linux/Pi)

    bus = DynamixelBus(device_name=_DEVICENAME)
    
    if not bus.connect():
        sys.exit(1)

    try:
        # Servo registrieren & steuern
        servo_1 = bus.add_servo(dxl_id=9)
        servo_2 = bus.add_servo(dxl_id=10)

        servo_1.enable_torque()
        servo_2.enable_torque()

        # möglichkeit 1: Servo auf Position fahren
        # servo_1.move(position=512, speed=100)  # Mitte
        # servo_2.move(position=512, speed=100)  # Mitte

        # möglichkeit 2: Servo auf Position fahren (Bus-Objekt)
        bus.get_servo(9).move(position=1000, speed=200)
        bus.get_servo(10).move(position=100, speed=200)

        # Telemetrie abfragen
        print(f"Aktuelle Spannung : {servo_1.get_voltage()} V")
        print(f"Aktuelle Temp     : {servo_1.get_temperature()} °C")

        print(f"Aktuelle Spannung : {servo_2.get_voltage()} V")
        print(f"Aktuelle Temp     : {servo_2.get_temperature()} °C")

    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer.")

    finally:
        # Schließt den Port und schaltet Torque erst ab, wenn die Bewegung fertig ist
        bus.disconnect(wait_for_servos=True)