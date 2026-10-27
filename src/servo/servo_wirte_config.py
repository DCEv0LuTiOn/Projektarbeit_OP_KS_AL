import os
import time
from dynamixel_sdk import *

# ==============================================================================
# KONFIGURATION
# ==============================================================================
DEVICENAME       = 'COM12'    # Windows: 'COM3' etc. | Linux/Pi: '/dev/ttyUSB0'
BAUDRATE         = 1000000   # Kommunikationsgeschwindigkeit (1 Mbps für AX-12A)
PROTOCOL_VERSION = 1.0       # AX-12A nutzt Protokoll 1.0

# ==============================================================================
# ZIEL-WERTE (Diese Werte werden in das EEPROM des Servos geschrieben)
# ==============================================================================

# Die neue ID, die der Servo erhalten soll (1 bis 252).
# Werkseinstellung: 1
CONF_NEW_ID          = 2 

# Antwort-Verzögerung in Mikrosekunden (Wert * 2 us). 
# 0 = schnellste Kommunikation (empfohlen für U2D2 Adapter).
# Werkseinstellung: 250 (entspricht 500 µs Verzögerung)
CONF_RETURN_DELAY    = 0

# Mechanische Winkel-Limits (0 bis 1023).
# Standard für 300° Bewegungsradius: CW = 0, CCW = 1023.
# Wenn BEIDE Werte auf 0 stehen, dreht der Servo endlos (Wheel Mode).
# Werkseinstellung: CW = 0, CCW = 1023
CONF_CW_ANGLE_LIMIT  = 0
CONF_CCW_ANGLE_LIMIT = 1023

# Maximale Betriebstemperatur in Grad Celsius (0 bis 99). 
# Schützt vor dem Durchbrennen.
# Werkseinstellung: 70 (°C)
CONF_MAX_TEMP        = 70

# Spannungslimits (Wert * 10 = Volt).
# Für 11,1V LiPo schützt Min 90 (9.0V) vor Tiefenentladung.
# Werkseinstellung Min: 60 (6.0V)
# Werkseinstellung Max: 140 (14.0V)
CONF_MIN_VOLTAGE     = 90
CONF_MAX_VOLTAGE     = 140

# Maximales Drehmoment (0 bis 1023). 
# 1023 ist die volle Kraft. Niedrigere Werte machen den Motor schwächer.
# Werkseinstellung: 1023 (100% Kraft)
CONF_MAX_TORQUE      = 1023

# Alarm-LED Konditionen (Fehler, bei denen die rote LED blinkt).
# 36 = Überhitzung (32) + Überlastung (4).
# Werkseinstellung: 36
CONF_ALARM_LED       = 36

# Shutdown Konditionen (Fehler, bei denen der Motor aus Sicherheitsgründen abschaltet).
# 36 = Überhitzung (32) + Überlastung (4).
# Werkseinstellung: 36
CONF_SHUTDOWN        = 36


# ==============================================================================
# ADRESSEN DER CONTROL TABLE (AX-12A)
# ==============================================================================
ADDR_ID = 3
ADDR_RETURN_DELAY = 5
ADDR_CW_LIMIT = 6
ADDR_CCW_LIMIT = 8
ADDR_MAX_TEMP = 11
ADDR_MIN_VOLT = 12
ADDR_MAX_VOLT = 13
ADDR_MAX_TORQUE = 14
ADDR_ALARM_LED = 17
ADDR_SHUTDOWN = 18

ADDR_TORQUE_ENABLE = 24


# ==============================================================================
# HAUPTPROGRAMM
# ==============================================================================
def main():
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
        print(f"FEHLER: Konnte Port {DEVICENAME} nicht öffnen oder Baudrate setzen.")
        return

    print("Suche nach Servo...")
    found_id = None
    for test_id in range(254):
        _, dxl_comm_result, _ = packetHandler.ping(portHandler, test_id)
        if dxl_comm_result == COMM_SUCCESS:
            found_id = test_id
            print(f"==> Servo mit ID {found_id} gefunden!")
            break

    if found_id is None:
        print("FEHLER: Kein Servo gefunden.")
        portHandler.closePort()
        return

    print("\n" + "="*50)
    print(" ACHTUNG: ÜBERSCHREIBEN DER SERVO-KONFIGURATION")
    print("="*50)
    print(f"Aktuelle Servo ID : {found_id}")
    print(f"NEUE Ziel-ID      : {CONF_NEW_ID}")
    print("Weitere Werte wie Limits und Sicherheitseinstellungen werden überschrieben.")
    
    # Sicherheitsabfrage
    bestaetigung = input("\nMöchtest du diese Werte wirklich schreiben? (j/n): ").strip().lower()
    
    if bestaetigung != 'j':
        print("\nVorgang durch Benutzer abgebrochen. Es wurde nichts geändert.")
        portHandler.closePort()
        return

    print("\nSchreibe Daten...")
    
    # Drehmoment aus, um EEPROM zu schreiben
    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_TORQUE_ENABLE, 0)
    time.sleep(0.1)

    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_RETURN_DELAY, CONF_RETURN_DELAY)
    packetHandler.write2ByteTxRx(portHandler, found_id, ADDR_CW_LIMIT, CONF_CW_ANGLE_LIMIT)
    packetHandler.write2ByteTxRx(portHandler, found_id, ADDR_CCW_LIMIT, CONF_CCW_ANGLE_LIMIT)
    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_MAX_TEMP, CONF_MAX_TEMP)
    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_MIN_VOLT, CONF_MIN_VOLTAGE)
    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_MAX_VOLT, CONF_MAX_VOLTAGE)
    packetHandler.write2ByteTxRx(portHandler, found_id, ADDR_MAX_TORQUE, CONF_MAX_TORQUE)
    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_ALARM_LED, CONF_ALARM_LED)
    packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_SHUTDOWN, CONF_SHUTDOWN)

    # ID zum Schluss ändern
    if found_id != CONF_NEW_ID:
        packetHandler.write1ByteTxRx(portHandler, found_id, ADDR_ID, CONF_NEW_ID)
        print(f"  [OK] ID auf {CONF_NEW_ID} geändert.")

    print("\nSchreibvorgang abgeschlossen!")
    portHandler.closePort()

if __name__ == '__main__':
    main()