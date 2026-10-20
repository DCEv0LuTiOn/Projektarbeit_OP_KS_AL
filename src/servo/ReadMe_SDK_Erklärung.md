### Die Konstanten (Das Setup)
Die Konstanten definieren die grundlegenden Spielregeln für die 
Kommunikation zwischen deinem PC/Pi und dem Servo.

- **`PROTOCOL_VERSION = 1.0`:** 
  Die "Sprache". Die älteren AX-12A Servos aus deinem Bioloid-System 
  verstehen nur Protokoll 1.0. Neuere Serien (wie die X-Serie) nutzen 2.0.

- **`BAUDRATE = 1000000`:** 
  Die Kommunikationsgeschwindigkeit in Bits pro Sekunde (1 Megabit/s). 
  Wenn Sender und Empfänger nicht exakt auf dieselbe Geschwindigkeit 
  eingestellt sind, erkennen sie nur Datensalat.

- **`DEVICENAME = 'COM3'`:** 
  Der physische Pfad zum U2D2-Adapter. Unter Windows ist das ein COM-Port, 
  auf deinem Raspberry Pi wird das später ein Pfad wie `'/dev/ttyUSB0'`.

- **`DXL_ID = 1`:** 
  Die eindeutige Adresse (Hausnummer) des Servos. Da bei deinem Aufbau 
  später mehrere Arme und Beine an derselben Datenleitung hängen 
  (Bussystem), lauschen alle Servos gleichzeitig. Die ID (1 bis 253) sagt 
  dem Datenpaket, für welchen konkreten Motor der Befehl bestimmt ist.

- **`ADDR_AX_TORQUE_ENABLE = 24` & `ADDR_AX_GOAL_POSITION = 30`:** 
  Jeder Dynamixel-Servo hat einen internen Speicher, die sogenannte 
  "Control Table". Das ist wie eine Excel-Tabelle direkt im Motor. 
  Diese Tabelle hat zwei Bereiche: Den flüchtigen Speicher (RAM, für aktive 
  Bewegungen) und den dauerhaften Speicher (EEPROM, behält Werte wie die ID 
  auch ohne Strom).

  **Wichtige Adressen im EEPROM (Dauerhafte Grundeinstellungen):**
  *(Achtung: EEPROM-Werte können oft nur überschrieben werden, wenn 
  Torque Enable auf 0 steht!)*
  - **Adresse 0 & 2 (`Model Number & Firmware Version`):** Hardware- und 
    Softwarekennung des Servos (Modell 12 steht z.B. für AX-12A). Nur lesbar.
  - **Adresse 3 (`ID`):** Speichert die ID (1-253) dauerhaft.
  - **Adresse 4 (`Baud Rate`):** Speichert die Kommunikationsgeschwindigkeit 
    als Index-Wert. Index 1 steht für 1.000.000 bps.
  - **Adresse 5 (`Return Delay Time`):** Die Pause (in Mikrosekunden), 
    die der Servo wartet, bevor er eine Antwort zurückschickt.
  - **Adresse 6 & 8 (`CW / CCW Angle Limit`):** Definiert die mechanischen 
    Grenzen. Setzt du beide Limits auf 0, wechselt der AX-12A in den 
    "Wheel Mode" (Rad-Modus) und dreht endlos weiter wie ein Rad.
  - **Adresse 11 (`High Temp Limit`):** Sicherheitsgrenze (meist 70°C).
  - **Adresse 12 & 13 (`Low / High Voltage Limit`):** Die Spannungsgrenzen 
    (Wert * 0.1V). Unter- oder überschreitet der Akku diese Werte, löst der 
    Servo Alarm aus.
  - **Adresse 14 (`Max Torque`):** Die absolute Hardware-Obergrenze für 
    die Kraft. RAM-Werte können diesen Wert nie überschreiten.
  - **Adresse 16 (`Status Return Level`):** Legt fest, wie gesprächig der 
    Servo ist. Standard ist 2 (antwortet auf jeden gesendeten Befehl).
  - **Adresse 17 (`Alarm LED`):** Definiert durch ein Bit-Muster, bei 
    welchen Fehlern (z.B. Überlastung) die rote LED zu blinken beginnt.
  - **Adresse 18 (`Shutdown`):** Der "Not-Aus". Definiert, bei welchen 
    Fehlern der Servo sofort abschaltet (Torque=0), um nicht kaputtzugehen.

  **Wichtige Adressen im RAM (Flüchtige Laufzeitdaten / Aktive Steuerung):**
  - **Adresse 24 (`Torque Enable`):** Der "Motorschalter". Die Steuerplatine 
    ist immer wach, aber dieser Schalter verbindet sie mit dem Elektromotor. 
    Bei 0 ist der Motor abgekoppelt (Freilauf), bei 1 bekommt er Strom, 
    spannt an und hält die Position eisern fest.
  - **Adresse 25 (`LED`):** Steuert die rote LED am Servo (0=Aus, 1=Ein).
  - **Adresse 26 & 27 (`CW / CCW Compliance Margin`):** Der Toleranzbereich. 
    Definiert mechanisches Spiel um die Zielposition, bei dem der Motor nicht 
    aktiv nachkorrigiert. Das verhindert ständiges, nervöses Zittern.
  - **Adresse 28 & 29 (`CW / CCW Compliance Slope`):** Die "Federung". 
    Bestimmt, wie weich der Motor abbremst, wenn er sich dem Ziel nähert.
  - **Adresse 30 (`Goal Position`):** Die Zielposition für Bewegungen.
  - **Adresse 32 (`Moving Speed`):** Legt die Bewegungsgeschwindigkeit 
    fest (0 bis 1023). 0 = maximale Geschwindigkeit, 1023 = extrem langsam.
  - **Adresse 34 (`Torque Limit`):** Begrenzt die maximale Kraft für die 
    aktuelle Aufgabe. Sehr nützlich für greifende Roboterhände.
  - **Adresse 36 (`Present Position`):** Ein reiner Lese-Wert. Hieraus 
    kann dein Code abfragen, wo der Motor gerade physisch steht.
  - **Adresse 38 (`Present Speed`):** Liest die aktuelle, tatsächliche 
    Drehgeschwindigkeit im Moment der Abfrage aus.
  - **Adresse 40 (`Present Load`):** Liest aus, wie stark der Motor gerade 
    mechanisch belastet wird (z. B. wenn der Arm gegen etwas stößt).
  - **Adresse 42 (`Present Voltage`):** Zeigt die aktuelle Spannung an 
    (z. B. "111" für 11,1 V). Perfekt für eine Akku-Warnung im Code!
  - **Adresse 43 (`Present Temperature`):** Liest die interne Temperatur 
    in Celsius aus, wichtig um Überhitzungsschäden zu vermeiden.
  - **Adresse 46 (`Moving`):** Status-Wert (0 oder 1). Dein Code kann hier 
    auslesen, ob der Servo noch fährt (1) oder am Ziel angekommen ist (0).

- **`TORQUE_ENABLE = 1` & `GOAL_POSITION = 512`:** 
  Das sind die tatsächlichen Werte, die wir in die oben genannten Adressen 
  schreiben.
  
  - **Werte für `TORQUE_ENABLE`:**
    `1` = Motor an. Das Drehmoment ist aktiv, der Servo spannt an.
    `0` = Motor aus. Der Servo ist im Freilauf/schlaff und lässt sich 
    von Hand bewegen.
  
  - **Werte für `GOAL_POSITION`:**
    Der AX-12A hat im Standard-Modus ("Joint Mode") einen Bewegungsradius 
    von 300 Grad.
    `512` = Exakte Mittelstellung (150°).
    `0`   = Maximaler linker Anschlag (0°).
    `1023`= Maximaler rechter Anschlag (300°).
    *(Hinweis: Im "Wheel Mode" werden 0-1023 nicht als Position, sondern 
    als Drehgeschwindigkeit interpretiert).*


### Die Handler (Die Übersetzer)
Die DYNAMIXEL SDK teilt die Arbeit in zwei Software-Werkzeuge auf:

- **`PortHandler` (Hardware-Ebene):** 
  Er kümmert sich um das physische Kabel. Er greift sich den USB-Port 
  (`COM3`), öffnet die Verbindung zum Betriebssystem, blockiert den Port 
  für andere Programme und stellt die Taktrate (`BAUDRATE`) ein.

- **`PacketHandler` (Software-Ebene):** 
  Er ist der Protokoll-Übersetzer. Ein Servo versteht kein Python. Wenn 
  du sagst "Gehe zu Position 512", baut der PacketHandler daraus ein 
  exaktes, maschinenlesbares Paket aus Nullen und Einsen, das dem 
  Protokoll 1.0 entspricht (inklusive Prüfsummen, um Datenfehler zu 
  erkennen). Er entpackt auch die Antworten vom Servo.


### Das Drehmoment (Torque)
Das Drehmoment ("Torque") beschreibt die Kraft, die der Motor aufbringt. 
Wenn der Servo Strom hat, `Torque Enable` aber auf `0` steht, ist der Motor 
im Leerlauf. Du kannst das Servohorn mit den Fingern frei drehen. Die 
Elektronik ist zwar wach und antwortet auf Datenpakete, aber der Motor 
greift mechanisch nicht ein.

Sobald du `Torque Enable = 1` sendest, spannt der Servo seine Muskeln an. 
Er hält nun starr seine aktuelle Position und wehrt sich mit voller Kraft 
gegen jede Bewegung von außen. 
WICHTIG: Ein Servo akzeptiert und fährt erst dann neue Zielpositionen an, 
wenn das Drehmoment vorher aktiviert wurde.


### Tx und Rx (Transmit & Receive)
Diese Abkürzungen stehen für die Richtung des Datenflusses:

- **Tx (Transmit / Senden):** 
  Der PC schickt einen Befehl über das Kabel an den Servo.
- **Rx (Receive / Empfangen):** 
  Der PC lauscht auf eine Antwort oder Statusmeldung vom Servo.

In Funktionen wie `write1ByteTxRx` oder `write2ByteTxRx` passieren beide 
Schritte direkt hintereinander:
1. Der PC schreibt Daten an den Servo (Tx).
2. Der PC blockiert für den Bruchteil einer Millisekunde und wartet, bis 
   der Servo eine Bestätigung zurücksendet (Rx), dass der Befehl fehlerfrei 
   angekommen und ausgeführt wurde.

Der Unterschied zwischen `1Byte` und `2Byte` liegt nur in der Größe der 
Zahl: Ein Schalter wie "Torque On/Off" (0 oder 1) passt in ein winziges 
1-Byte-Paket. Eine Zielposition wie 512 ist mathematisch zu groß für 
1 Byte (welches maximal bis 255 zählen kann) und muss daher aufgeteilt 
als 2-Byte-Paket gesendet werden.