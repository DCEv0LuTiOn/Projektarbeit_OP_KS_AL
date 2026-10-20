import os
from dynamixel_sdk import *

DEVICENAME       = 'COM12'    # Anpassen!
BAUDRATE         = 1000000
PROTOCOL_VERSION = 1.0

def main():
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
        print(f"FEHLER: Konnte Port {DEVICENAME} nicht öffnen/Baudrate setzen.")
        return

    print("Suche nach Servo...")
    found_id = None
    for test_id in range(254):
        _, dxl_comm_result, _ = packetHandler.ping(portHandler, test_id)
        if dxl_comm_result == COMM_SUCCESS:
            found_id = test_id
            break

    if found_id is None:
        print("FEHLER: Kein Servo gefunden.")
        portHandler.closePort()
        return

    # Hilfsfunktionen zum reinen Auslesen
    def r1(addr):
        val, res, _ = packetHandler.read1ByteTxRx(portHandler, found_id, addr)
        return val if res == COMM_SUCCESS else "ERR"

    def r2(addr):
        val, res, _ = packetHandler.read2ByteTxRx(portHandler, found_id, addr)
        return val if res == COMM_SUCCESS else "ERR"

    print("\n" + "="*50)
    print(f" SERVO INFO (Gefunden auf ID {found_id})")
    print("="*50)

    print("\n--- EEPROM (Dauerhafte Grundeinstellungen) ---")
    print(f"{'Model Number':<25}: {r2(0)}")
    print(f"{'Firmware Version':<25}: {r1(2)}")
    print(f"{'ID':<25}: {r1(3)}")
    print(f"{'Baud Rate (Index)':<25}: {r1(4)} (1 = 1 Mbps)")
    print(f"{'Return Delay Time':<25}: {r1(5)} (* 2 Mikrosekunden)")
    print(f"{'CW Angle Limit':<25}: {r2(6)}")
    print(f"{'CCW Angle Limit':<25}: {r2(8)}")
    print(f"{'High Temp Limit':<25}: {r1(11)} °C")
    print(f"{'Low Voltage Limit':<25}: {r1(12)} (* 0.1 V)")
    print(f"{'High Voltage Limit':<25}: {r1(13)} (* 0.1 V)")
    print(f"{'Max Torque':<25}: {r2(14)}")
    print(f"{'Status Return Level':<25}: {r1(16)}")
    print(f"{'Alarm LED':<25}: {r1(17)}")
    print(f"{'Shutdown':<25}: {r1(18)}")

    print("\n--- RAM (Flüchtige Laufzeitdaten) ---")
    print(f"{'Torque Enable':<25}: {r1(24)} (0=Aus, 1=Ein)")
    print(f"{'LED':<25}: {r1(25)} (0=Aus, 1=Ein)")
    print(f"{'CW Compliance Margin':<25}: {r1(26)}")
    print(f"{'CCW Compliance Margin':<25}: {r1(27)}")
    print(f"{'CW Compliance Slope':<25}: {r1(28)}")
    print(f"{'CCW Compliance Slope':<25}: {r1(29)}")
    print(f"{'Goal Position':<25}: {r2(30)}")
    print(f"{'Moving Speed':<25}: {r2(32)}")
    print(f"{'Torque Limit':<25}: {r2(34)}")
    print(f"{'Present Position':<25}: {r2(36)}")
    print(f"{'Present Speed':<25}: {r2(38)}")
    print(f"{'Present Load':<25}: {r2(40)}")
    print(f"{'Present Voltage':<25}: {r1(42)} (* 0.1 V)")
    print(f"{'Present Temperature':<25}: {r1(43)} °C")
    print(f"{'Moving Status':<25}: {r1(46)} (0=Steht, 1=Fährt)")
    
    print("\n" + "="*50)
    
    portHandler.closePort()

if __name__ == '__main__':
    main()