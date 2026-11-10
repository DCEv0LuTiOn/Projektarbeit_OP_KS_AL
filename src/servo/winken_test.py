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
            # Beide Servos starten in derselben Schleifenrunde ihre Bewegung.
            bus.get_servo(5).move(position=200, speed=200)
            bus.get_servo(3).move(position=300, speed=200)

            # Gemeinsam warten, bis beide ihre Bewegung abgeschlossen haben.
            bus.wait_until_all_stopped(timeout=10.0)

            # Nächste gemeinsame Bewegung für beide Servos.
            bus.get_servo(5).move(position=500, speed=200)
            bus.get_servo(3).move(position=500, speed=200)
            bus.wait_until_all_stopped(timeout=10.0)
    except KeyboardInterrupt:
        print("Beende das Programm...")
    finally:
        bus.disconnect(wait_for_servos=True)
        # Trenne die Verbindung und schalte das Drehmoment ab


if __name__ == "__main__":
    main()
