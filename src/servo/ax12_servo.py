import time
from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS

class AX12AServo:
    """
    Repräsentiert einen einzelnen ROBOTIS Dynamixel AX-12A Servo.
    Ermöglicht Bewegungssteuerung und Telemetrie über Protocol 1.0.
    """

    # Private Standard-Kommunikationseinstellungen
    _DEFAULT_BAUDRATE         = 1000000  # 1 Mbps
    _DEFAULT_PROTOCOL_VERSION = 1.0      # Protocol 1.0

    # Private Control Table Adressen (AX-12A)
    _ADDR_TORQUE_ENABLE       = 24
    _ADDR_GOAL_POSITION       = 30
    _ADDR_MOVING_SPEED        = 32
    _ADDR_PRESENT_POSITION    = 36
    _ADDR_PRESENT_SPEED       = 38
    _ADDR_PRESENT_LOAD        = 40
    _ADDR_PRESENT_VOLTAGE     = 42
    _ADDR_PRESENT_TEMPERATURE = 43
    _ADDR_MOVING              = 46

    def __init__(self, dxl_id: int, port_handler: PortHandler, packet_handler: PacketHandler = None):
        """
        Initialisiert das Servo-Objekt.

        Args:
            dxl_id (int): Die Bus-ID des Servos (1 - 252).
            port_handler (PortHandler): Die gemeinsam genutzte PortHandler-Instanz.
            packet_handler (PacketHandler, optional): Die PacketHandler-Instanz.
        """
        self._id = dxl_id
        self._port_handler = port_handler
        
        if packet_handler is None:
            self._packet_handler = PacketHandler(self._DEFAULT_PROTOCOL_VERSION)
        else:
            self._packet_handler = packet_handler

    @property
    def id(self) -> int:
        """Gibt die ID des Servos zurück."""
        return self._id

    # --------------------------------------------------------------------------
    # STEUERUNGSFUNKTIONEN
    # --------------------------------------------------------------------------

    def enable_torque(self) -> bool:
        """Aktiviert das Drehmoment des Servos."""
        result, error = self._packet_handler.write1ByteTxRx(
            self._port_handler, self._id, self._ADDR_TORQUE_ENABLE, 1
        )
        if result != COMM_SUCCESS or error != 0:
            print(f"[Servo {self._id}] Fehler beim Aktivieren des Drehmoments.")
            return False
        return True

    def disable_torque(self) -> bool:
        """Deaktiviert das Drehmoment des Servos (Freilauf)."""
        result, error = self._packet_handler.write1ByteTxRx(
            self._port_handler, self._id, self._ADDR_TORQUE_ENABLE, 0
        )
        return result == COMM_SUCCESS and error == 0

    def set_speed(self, speed: int) -> bool:
        """Setzt die Bewegungsgeschwindigkeit (0 - 1023)."""
        speed = max(0, min(1023, speed))
        result, error = self._packet_handler.write2ByteTxRx(
            self._port_handler, self._id, self._ADDR_MOVING_SPEED, speed
        )
        return result == COMM_SUCCESS and error == 0

    def move(self, position: int, speed: int = 0) -> bool:
        """
        Fährt den Servo auf die Zielposition (0 - 1023).
        Standard-Geschwindigkeit ist 0 (Vollgas / Maximale Motorleistung).
        """
        position = max(0, min(1023, position))

        # Geschwindigkeit vor der Fahrt setzen (0 = Vollgas)
        self.set_speed(speed)

        result, error = self._packet_handler.write2ByteTxRx(
            self._port_handler, self._id, self._ADDR_GOAL_POSITION, position
        )
        if result != COMM_SUCCESS or error != 0:
            print(f"[Servo {self._id}] Fehler beim Anfahren von Position {position}.")
            return False

        print(f"==> Servo {self._id} -> Position {position} (Speed: {speed})")
        return True

    def wait_until_stopped(self, poll_delay: float = 0.05, timeout: float = 10.0) -> bool:
        """Blockiert die Ausführung, bis der Servo seine Zielposition erreicht hat."""
        time.sleep(0.05)
        start_time = time.time()
        
        while self.is_moving():
            time.sleep(poll_delay)
            if time.time() - start_time > timeout:
                print(f"[Servo {self._id}] Timeout beim Warten auf Bewegungsende.")
                return False
        return True

    # --------------------------------------------------------------------------
    # DIAGNOSE & TELEMETRIE
    # --------------------------------------------------------------------------

    def get_speed(self) -> int:
        """Liest die aktuell gesetzte Ziel-Geschwindigkeit aus (0 - 1023)."""
        speed, result, error = self._packet_handler.read2ByteTxRx(
            self._port_handler, self._id, self._ADDR_MOVING_SPEED
        )
        if result == COMM_SUCCESS and error == 0:
            return speed
        return -1

    def get_temperature(self) -> int:
        """Liest die aktuelle Innentemperatur in °C aus."""
        temperature, result, error = self._packet_handler.read1ByteTxRx(
            self._port_handler, self._id, self._ADDR_PRESENT_TEMPERATURE
        )
        if result == COMM_SUCCESS and error == 0:
            return temperature
        return -1

    def get_voltage(self) -> float:
        """Liest die aktuelle Betriebsspannung in Volt aus."""
        voltage_raw, result, error = self._packet_handler.read1ByteTxRx(
            self._port_handler, self._id, self._ADDR_PRESENT_VOLTAGE
        )
        if result == COMM_SUCCESS and error == 0:
            return voltage_raw / 10.0
        return -1.0

    def get_position(self) -> int:
        """Liest die aktuelle Ist-Position aus (0 - 1023)."""
        position, result, error = self._packet_handler.read2ByteTxRx(
            self._port_handler, self._id, self._ADDR_PRESENT_POSITION
        )
        if result == COMM_SUCCESS and error == 0:
            return position
        return -1

    def get_load(self) -> int:
        """Liest die aktuelle Motorauslastung aus (0 - 1023)."""
        load, result, error = self._packet_handler.read2ByteTxRx(
            self._port_handler, self._id, self._ADDR_PRESENT_LOAD
        )
        if result == COMM_SUCCESS and error == 0:
            return load & 0x3FF
        return -1

    def is_moving(self) -> bool:
        """Prüft, ob der Servo momentan in Bewegung ist."""
        moving, result, error = self._packet_handler.read1ByteTxRx(
            self._port_handler, self._id, self._ADDR_MOVING
        )
        if result == COMM_SUCCESS and error == 0:
            return bool(moving)
        return False

    def get_status(self) -> dict:
        """Erfasst alle wesentlichen Telemetriewerte in einem Dictionary."""
        return {
            "id": self._id,
            "position": self.get_position(),
            "target_speed": self.get_speed(),
            "temperature_c": self.get_temperature(),
            "voltage_v": self.get_voltage(),
            "load_raw": self.get_load(),
            "is_moving": self.is_moving()
        }