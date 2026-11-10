from dynamixelBus import DynamixelBus, AX12AServo


def main():
    # Beispiel für die Verwendung der DynamixelBus-Klasse
    bus = DynamixelBus(device_name="/dev/ttyUSB0", baudrate=1000000)

    if not bus.connect():
        return

    # Füge ein Servo mit ID 1 hinzu
    for i in range(1, 18):
        servo:AX12AServo = bus.add_servo(dxl_id=i)
        servo.enable_torque()  # Aktiviere das Drehmoment für das Servo

    # Setze das Zielposition des Servos
    bus.get_servo(1).move(position=512)  # Mittelstellung
    bus.get_servo(3).move(position=512)  # Mittelstellung
    bus.get_servo(5).move(position=512)  # Mittelstellung

    try:
        while True:
            # Hier können weitere Steuerbefehle oder Telemetrieabfragen erfolgen
            bus.get_servo(5).move(position=200, speed=50) 
            # bus.get_servo(5).wait_until_stopped(timeout=5.0)  # Warte, bis das Servo seine Bewegung abgeschlossen hat
            bus.get_servo(5).move(position=500, speed=50) 
            # bus.get_servo(5).wait_until_stopped(timeout=5.0)  # Warte, bis das Servo seine Bewegung abgeschlossen hat
            # Hier können weitere Steuerbefehle oder Telemetrieabfragen erfolgen
            bus.get_servo(3).move(position=300, speed=50) 
            # bus.get_servo(3).wait_until_stopped(timeout=5.0)  # Warte, bis das Servo seine Bewegung abgeschlossen hat
            bus.get_servo(3).move(position=500, speed=50) 
            # bus.get_servo(3).wait_until_stopped(timeout=5.0)  # Warte, bis das Servo seine Bewegung abgeschlossen hat
    except KeyboardInterrupt:
        print("Beende das Programm...")
    finally:
        bus.disconnect(wait_for_servos=True)
        # Trenne die Verbindung und schalte das Drehmoment ab


if __name__ == "__main__":
    main()
