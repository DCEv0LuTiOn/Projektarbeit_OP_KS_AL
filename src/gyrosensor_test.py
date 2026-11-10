"""
mpu6050_test.py - Liest den MPU-6050 (Beschleunigung, Gyro, Temperatur)
per I2C am Raspberry Pi aus und gibt die Werte in der Konsole aus.

Voraussetzungen:
    1. I2C aktivieren:   sudo raspi-config -> Interface Options -> I2C
    2. Bibliothek:       pip install smbus2
    3. Sensor prüfen:    i2cdetect -y 1   (es sollte die Adresse 68 erscheinen)

Start:
    python mpu6050_test.py        (mit Strg+C beenden)
"""

import time
from smbus2 import SMBus

I2C_BUS = 1          # Auf dem Raspberry Pi ist es der Bus 1 (GPIO2 = SDA, GPIO3 = SCL)
MPU_ADDR = 0x68      # Standardadresse (0x69, wenn der Pin AD0 auf 3,3 V liegt)

# Register des MPU-6050
REG_PWR_MGMT_1 = 0x6B   # Energieverwaltung, der Sensor startet im Schlafmodus
REG_WHO_AM_I = 0x75     # Kennung des Chips
REG_DATA_START = 0x3B   # Ab hier folgen 14 Bytes: Beschleunigung, Temperatur, Gyro

# Umrechnungsfaktoren für die Standardbereiche (+-2 g und +-250 Grad/s)
ACCEL_SCALE = 16384.0   # Rohwert pro g
GYRO_SCALE = 131.0      # Rohwert pro Grad/s


def to_signed(high: int, low: int) -> int:
    """Setzt zwei Bytes zu einer vorzeichenbehafteten 16-Bit-Zahl zusammen."""
    value = (high << 8) | low
    return value - 65536 if value >= 32768 else value


def read_raw(bus: SMBus) -> dict:
    """Liest alle 14 Datenbytes in einem Zug und gibt die Rohwerte zurück."""
    d = bus.read_i2c_block_data(MPU_ADDR, REG_DATA_START, 14)
    return {
        "ax": to_signed(d[0], d[1]),
        "ay": to_signed(d[2], d[3]),
        "az": to_signed(d[4], d[5]),
        "temp": to_signed(d[6], d[7]),
        "gx": to_signed(d[8], d[9]),
        "gy": to_signed(d[10], d[11]),
        "gz": to_signed(d[12], d[13]),
    }


def calibrate_gyro(bus: SMBus, samples: int = 200) -> dict:
    """
    Misst den Gyro im Stillstand und gibt den Mittelwert als Offset zurück.
    Der Sensor muss dabei ruhig liegen.
    """
    sums = {"gx": 0, "gy": 0, "gz": 0}
    for _ in range(samples):
        raw = read_raw(bus)
        for axis in sums:
            sums[axis] += raw[axis]
        time.sleep(0.005)
    return {axis: sums[axis] / samples for axis in sums}


def main():
    try:
        with SMBus(I2C_BUS) as bus:
            # Sensor aus dem Schlafmodus holen (sonst liefert er nur Nullen)
            bus.write_byte_data(MPU_ADDR, REG_PWR_MGMT_1, 0)
            time.sleep(0.1)

            who = bus.read_byte_data(MPU_ADDR, REG_WHO_AM_I)
            print(f"WHO_AM_I: 0x{who:02X} (beim echten MPU-6050 ist es 0x68)")

            print("Kalibriere den Gyro, bitte Sensor nicht bewegen ...")
            offset = calibrate_gyro(bus)
            print("Fertig. Strg+C zum Beenden.\n")

            while True:
                raw = read_raw(bus)

                # Rohwerte in physikalische Einheiten umrechnen
                ax = raw["ax"] / ACCEL_SCALE
                ay = raw["ay"] / ACCEL_SCALE
                az = raw["az"] / ACCEL_SCALE
                gx = (raw["gx"] - offset["gx"]) / GYRO_SCALE
                gy = (raw["gy"] - offset["gy"]) / GYRO_SCALE
                gz = (raw["gz"] - offset["gz"]) / GYRO_SCALE
                temp = raw["temp"] / 340.0 + 36.53  # Formel aus dem Datenblatt

                print(
                    f"Accel [g]: X={ax:+6.2f} Y={ay:+6.2f} Z={az:+6.2f} | "
                    f"Gyro [°/s]: X={gx:+7.2f} Y={gy:+7.2f} Z={gz:+7.2f} | "
                    f"Temp: {temp:.1f} °C"
                )
                time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nBeendet.")
    except OSError as e:
        print(f"I2C-Fehler: {e}")
        print("Prüfen: Ist I2C aktiviert? Zeigt 'i2cdetect -y 1' die Adresse 68? Verkabelung korrekt?")


if __name__ == "__main__":
    main()
