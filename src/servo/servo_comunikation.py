import os
from dynamixel_sdk import *

# --- Konfiguration ---
PROTOCOL_VERSION = 1.0       # AX-12A nutzt Protokoll 1.0
BAUDRATE         = 1000000   # Standard-Baudrate für AX-12A
DEVICENAME       = 'COM12'   # WICHTIG: Im Windows-Geräte-Manager deinen COM-Port prüfen!
DXL_ID           = 9         # Die ID des Servos, den du testen willst

# Control Table Adressen für AX-12A Servos
ADDR_AX_TORQUE_ENABLE = 24
ADDR_AX_GOAL_POSITION = 30

TORQUE_ENABLE  = 1           # Wert für "Torque ON"
GOAL_POSITION  = 512         # Mittelposition (Wertebereich ca. 0 bis 1023)

# 1. Handler initialisieren
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# 2. Port öffnen & Baudrate setzen
if portHandler.openPort() and portHandler.setBaudRate(BAUDRATE):
    print("Port erfolgreich geöffnet.")
else:
    print("Fehler: Konnte Port nicht öffnen oder Baudrate nicht setzen!")
    quit()

# 3. Drehmoment aktivieren (Servo wird steif)
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_AX_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print(f"Kommunikationsfehler: {packetHandler.getTxRxResult(dxl_comm_result)}")
else:
    print(f"Drehmoment für Servo ID {DXL_ID} aktiviert.")

# 4. Servo auf Zielposition bewegen
print(f"Bewege Servo {DXL_ID} auf Position {GOAL_POSITION}...")
packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_AX_GOAL_POSITION, GOAL_POSITION)

# Port sauber schließen
portHandler.closePort()