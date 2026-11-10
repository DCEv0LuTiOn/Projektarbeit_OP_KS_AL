from servo.dynamixelBus import DynamixelBus
from servo.ax12_servo import AX12AServo

def main():
    # Beispiel für die Verwendung der DynamixelBus-Klasse
    bus = DynamixelBus(device_name='/dev/ttyUSB0', baudrate=1000000)
    
    if not bus.connect():
        return

    # Füge ein Servo mit ID 1 hinzu
    for i in range(1,18):
        servo = bus.add_servo(dxl_id=i)
        servo.enable_torque()  # Aktiviere das Drehmoment für das Servo

    # Setze das Zielposition des Servos
    bus.get_servo(1).move(position=512, speed=100)  # Mittelstellung
    bus.get_servo(3).move(position=512, speed=100)  # Mittelstellung
    bus.get_servo(5).move(position=512, speed=100)  # Mittelstellung

    # Warte, bis das Servo seine Bewegung abgeschlossen hat
    # servo1.wait_until_stopped(timeout=5.0)

    # Trenne die Verbindung und schalte das Drehmoment ab
    bus.disconnect(wait_for_servos=True)

if __name__ == "__main__":
    main()