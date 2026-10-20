import sqlite3
from dcs import *
from contextlib import closing


"""
database.py - Allgemeine Funktionen für den Zugriff auf die SQLite-Datenbank.

Idee: Jede Tabelle hat eine passende Dataclass (dc). Die Funktionen lesen die
Felder einer Dataclass aus und bauen daraus automatisch die SQL-Befehle.
Dadurch braucht man nicht für jede Tabelle eigenen SQL-Code zu schreiben.

Voraussetzung: Die Namen der Dataclass-Felder müssen exakt den Spaltennamen
in der Tabelle entsprechen.
"""

# Pfad zur SQLite-Datei. Muss vor der ersten Nutzung gesetzt sein.
__db_path = "src/robotis.db"


# ---------------------------------------------------------------------------
# Benutzerdefinierte Abfragen (Selects, Inserts, Updates, Deletes) mit Dataclasses
# ---------------------------------------------------------------------------
def create_programm(programm: ProgrammDC | list[ProgrammDC] = None ) -> int:
    """
    Fügt ein neues Programm in die Datenbank ein und gibt die automatisch
    vergebene Programm-ID zurück.
    """
    try:
        if programm is not None:
            # Beispielprogramm anlegen, falls kein Programm übergeben wurde.
            execute_insert_dcs(programm)
    except: 
        create_Log_message(LogeintragDC(typ="FEHLER", nachricht="Fehler beim Anlegen des Programms."))

def create_Log_message(log: LogeintragDC | list[LogeintragDC] = None ) -> int:
    """
    Fügt eine neue Lognachricht in die Datenbank ein und gibt die automatisch
    vergebene Log-ID zurück.
    """
    try:
        if log is not None:
            # Beispielprogramm anlegen, falls kein Programm übergeben wurde.
            execute_insert_dcs(log)
    except: 
        create_Log_message(LogeintragDC(typ="FEHLER", nachricht="Fehler beim Anlegen des Logeintrags."))

def create_Servo(servo: ServoDC | list[ServoDC] = None ) -> int:
    """
    Fügt einen neuen Servo in die Datenbank ein und gibt die automatisch
    vergebene Servo-ID zurück.
    """
    try:
        if servo is not None:
            # Beispielprogramm anlegen, falls kein Programm übergeben wurde.
            execute_insert_dcs(servo)
    except: 
        create_Log_message(LogeintragDC(typ="FEHLER", nachricht="Fehler beim Anlegen des Servos."))

def create_Programmschritt(schritt: ProgrammschrittDC | list[ProgrammschrittDC] = None ) -> int:
    """
    Fügt einen neuen Programmschritt in die Datenbank ein und gibt die automatisch
    vergebene Schritt-ID zurück.
    """
    try:
        if schritt is not None:
            # Beispielprogramm anlegen, falls kein Programm übergeben wurde.
            execute_insert_dcs(schritt)
    except: 
        create_Log_message(LogeintragDC(typ="FEHLER", nachricht="Fehler beim Anlegen des Programmschritts."))




# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def get_dc_data(dc: object):
    """
    Liest aus einer Dataclass alle Informationen, die für SQL-Befehle nötig sind.

    Rückgabe:
        table_name       - Name der Tabelle (abgeleitet aus dem Klassennamen)
        fields_to_insert - Liste aller Feldnamen, z. B. ["name", "beschreibung"]
        values           - Dictionary {Feldname: Wert}, z. B. {"name": "P1", ...}
    """
    # Der Tabellenname ist der Klassenname ohne die Endung "DC".
    # Beispiel: Klasse "ServoDC" -> Tabelle "Servo"
    class_name = dc.__class__.__name__
    table_name = class_name[:class_name.find("DC")]

    fields_to_insert = []
    values = {}  # enthält die Werte, Schlüssel = Feldname

    # __dict__ enthält alle Instanzvariablen der Dataclass als Name -> Wert
    for key, value in dc.__dict__.items():
        fields_to_insert.append(key)
        values[key] = value

    return table_name, fields_to_insert, values


def get_table_primary_keys(connection, table_name) -> list[str]:
    """
    Fragt bei SQLite ab, welche Spalten einer Tabelle zum Primärschlüssel gehören.
    Rückgabe ist eine Liste, weil ein Primärschlüssel aus mehreren Spalten
    bestehen kann (zusammengesetzter Schlüssel).
    """
    # PRAGMA table_info liefert pro Spalte eine Zeile mit den Spalteninfos
    table_info = connection.execute(f"PRAGMA table_info({table_name})")

    pk_names = []
    for column in table_info:
        # column[1] = Spaltenname
        # column[5] = Position im Primärschlüssel:
        #   0 = kein Teil des PK, 1 = erster Teil, 2 = zweiter Teil, usw.
        if column[5] > 0:
            pk_names.append(column[1])
    return pk_names


# ---------------------------------------------------------------------------
# Lesen (SELECT)
# ---------------------------------------------------------------------------
def execute_select_dc_list(sql: str, dc_class, wheres: dict) -> list[object]:
    """
    Führt ein SELECT aus und gibt das Ergebnis als Liste von Dataclass-Objekten
    zurück (eine Dataclass pro Ergebniszeile).

    sql      - SELECT-Befehl mit benannten Platzhaltern, z. B. "... WHERE id = :id"
    dc_class - Dataclass-Klasse, in die die Zeilen umgewandelt werden
    wheres   - Dictionary mit den Werten für die Platzhalter, z. B. {"id": 5}
    """
    with sqlite3.connect(__db_path) as connection:
        # Ohne diese Zeile ignoriert SQLite Fremdschlüssel (Standard: aus).
        connection.execute("PRAGMA foreign_keys = ON;")
        # Mit Row-Objekten kann man auf Spalten über ihren Namen zugreifen.
        connection.row_factory = sqlite3.Row

        # closing() sorgt dafür, dass der Cursor am Ende wieder geschlossen wird.
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql, wheres)

            # Spaltennamen des SELECTs aus der Cursor-Beschreibung holen
            column_names = [col[0] for col in cursor.description]

            results = []
            for row in cursor.fetchall():  # alle Ergebniszeilen holen
                # Spaltennamen und Spaltenwerte zu einem Dictionary verbinden
                row_dict = dict(zip(column_names, row))
                # Dictionary entpacken und als Dataclass anlegen. Das klappt nur,
                # wenn Spaltennamen und Dataclass-Feldnamen gleich sind.
                results.append(dc_class(**row_dict))
            return results


def execute_select_dc(sql: str, dc_class, wheres: dict) -> object:
    """
    Wie execute_select_dc_list, liefert aber nur die erste Zeile als einzelnes
    Dataclass-Objekt zurück, oder None, wenn nichts gefunden wurde.
    """
    executed_list = execute_select_dc_list(sql, dc_class, wheres)
    if len(executed_list) > 0:
        return executed_list[0]
    else:
        return None


def execute_select_value(sql: str, wheres: dict) -> str | int | float:
    """
    Führt ein SELECT aus und gibt nur den ersten Wert der ersten Zeile zurück.
    Gedacht für Abfragen mit einem einzelnen Ergebnis, z. B. COUNT(*) oder MAX(...).
    """
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql, wheres)
            row = cursor.fetchone()  # nur die erste Zeile holen
            return row[0]            # und davon die erste Spalte


# ---------------------------------------------------------------------------
# Schreiben (INSERT, UPDATE, DELETE)
# Alle drei Funktionen akzeptieren ein einzelnes Objekt oder eine Liste und
# laufen in einer Transaktion: Entweder gelingt alles, oder nichts wird gespeichert.
# ---------------------------------------------------------------------------
def execute_insert_dcs(dcs: object | list[object]):
    """Fügt eine oder mehrere Dataclasses als neue Zeilen in ihre Tabelle ein."""
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")

        # Einzelnes Objekt in eine Liste mit einem Element umwandeln,
        # damit unten immer über eine Liste iteriert werden kann.
        if not isinstance(dcs, list):
            dcs = [dcs]

        try:
            for dc in dcs:
                # Tabellenname, Feldnamen und Werte aus der Dataclass lesen
                table_name, fields_to_insert, values = get_dc_data(dc)

                # Das Feld "ID" wird nicht eingefügt, da die Datenbank es
                # selbst hochzählt (Autoincrement).
                if "ID" in fields_to_insert:
                    fields_to_insert.remove("ID")
                    del values["ID"]

                # SQL mit benannten Parametern zusammenbauen, z. B.:
                # INSERT INTO Tabelle (name, email) VALUES (:name, :email)
                columns = ", ".join(fields_to_insert)
                placeholders = ", ".join(f":{p}" for p in fields_to_insert)
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                connection.execute(sql, values)

            # Erst hier werden alle Einfügungen endgültig gespeichert.
            connection.commit()
        except sqlite3.DatabaseError as e:
            # Bei einem Fehler alle bisherigen Änderungen dieses Aufrufs verwerfen.
            connection.rollback()
            print("DB Fehler:", e)
            raise  # Fehler weitergeben, damit der Aufrufer ihn behandeln kann


def execute_update_dcs(dcs: object | list[object]):
    """
    Aktualisiert eine oder mehrere bestehende Zeilen. Welche Zeile geändert wird,
    bestimmt der Primärschlüssel der Dataclass.
    """
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        if not isinstance(dcs, list):
            dcs = [dcs]

        try:
            for dc in dcs:
                table_name, fields_to_insert, values = get_dc_data(dc)

                # SET-Teil bauen: pro Feld "spalte=:spalte"
                update_values = []
                for column in fields_to_insert:
                    update_values.append(column + "=:" + column)

                # WHERE-Teil bauen: pro Primärschlüssel-Spalte "spalte=:spalte"
                primary_keys = get_table_primary_keys(connection, table_name)
                where_values = []
                for column in primary_keys:
                    where_values.append(column + "=:" + column)

                # Ergebnis z. B.: UPDATE Tabelle SET name=:name WHERE id=:id
                sql = (
                    f"UPDATE {table_name} SET {', '.join(update_values)} "
                    f"WHERE {' AND '.join(where_values)}"
                )
                connection.execute(sql, values)
            connection.commit()
        except sqlite3.DatabaseError as e:
            connection.rollback()
            print("DB Fehler:", e)
            raise


def execute_delete_dcs(dcs: object | list[object]):
    """
    Löscht eine oder mehrere Zeilen. Welche Zeile gelöscht wird, bestimmt der
    Primärschlüssel der Dataclass.
    """
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        if not isinstance(dcs, list):
            dcs = [dcs]

        try:
            for dc in dcs:
                table_name, fields, values = get_dc_data(dc)
                primary_keys = get_table_primary_keys(connection, table_name)

                # Sicherheitsabfrage: Ohne Primärschlüssel wäre die WHERE-Bedingung
                # leer und ein DELETE würde alle Zeilen der Tabelle löschen.
                if not primary_keys:
                    raise ValueError(
                        f"Tabelle {table_name} hat keine Primärschlüssel. "
                        "Löschen nicht sicher möglich."
                    )

                # WHERE-Bedingung aus den Primärschlüsseln bauen.
                # Ergebnis: ["ID=:ID"] oder ["ID1=:ID1", "ID2=:ID2"] bei
                # zusammengesetzten Schlüsseln.
                where_clauses = [f"{column}=:{column}" for column in primary_keys]

                sql = f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}"
                connection.execute(sql, values)
            connection.commit()

        except sqlite3.DatabaseError as e:
            connection.rollback()
            print("DB Fehler beim Löschen:", e)
            raise

# ---------------------------------------------------------------------------
# Tabellen erstellen
# ---------------------------------------------------------------------------
def create_tables(db_path: str = "src/robotis.db") -> None:
    """Legt alle Tabellen in der SQLite-Datei an (falls noch nicht vorhanden)."""
    #status_werte = ", ".join(f"'{s}'" for s in DURCHLAUF_STATUS)
    #log_werte = ", ".join(f"'{t}'" for t in LOG_TYPEN)

    schema = f"""
    CREATE TABLE IF NOT EXISTS servo (
        servo_id     INTEGER PRIMARY KEY,
        name         TEXT    NOT NULL,
        min_position INTEGER NOT NULL,
        max_position INTEGER NOT NULL,
        CHECK (min_position < max_position)
    );

    CREATE TABLE IF NOT EXISTS programm (
        programm_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT NOT NULL UNIQUE,
        beschreibung TEXT NOT NULL DEFAULT '',
        erstellt_am  TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS programmschritt (
        schritt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        programm_id     INTEGER NOT NULL,
        servo_id        INTEGER NOT NULL,
        reihenfolge     INTEGER NOT NULL,
        zielposition    INTEGER NOT NULL,
        geschwindigkeit INTEGER NOT NULL DEFAULT 0,
        dauer_ms        INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (programm_id) REFERENCES programm (programm_id) ON DELETE CASCADE,
        FOREIGN KEY (servo_id)    REFERENCES servo (servo_id)
    );

    CREATE TABLE IF NOT EXISTS programmdurchlauf (
        durchlauf_id                INTEGER PRIMARY KEY AUTOINCREMENT,
        programm_id                 INTEGER NOT NULL,
        start_zeit                  TEXT    NOT NULL,
        end_zeit                    TEXT,
        status                      TEXT,
        endlosschleife              INTEGER NOT NULL DEFAULT 0
                                    CHECK (endlosschleife IN (0, 1)),
        anzahl_zyklen_geplant       INTEGER NOT NULL DEFAULT 1,
        anzahl_zyklen_abgeschlossen INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (programm_id) REFERENCES programm (programm_id)
    );

    CREATE TABLE IF NOT EXISTS logeintrag (
        log_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        durchlauf_id INTEGER,
        zeitstempel  TEXT NOT NULL,
        typ          TEXT NOT NULL,
        nachricht    TEXT NOT NULL,
        FOREIGN KEY (durchlauf_id) REFERENCES programmdurchlauf (durchlauf_id)
    );

    CREATE INDEX IF NOT EXISTS idx_schritt_programm
        ON programmschritt (programm_id, reihenfolge);
    CREATE INDEX IF NOT EXISTS idx_durchlauf_programm
        ON programmdurchlauf (programm_id);
    CREATE INDEX IF NOT EXISTS idx_log_zeit
        ON logeintrag (zeitstempel);
    """

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema)
    
# ---------------------------------------------------------------------------
# Datenbank zurücksetzen (alle Tabellen löschen)
# ---------------------------------------------------------------------------
def reset_database(db_path: str = "src/robotis.db") -> None:
    """Löscht alle Tabellen in der SQLite-Datei (falls vorhanden)."""
    schema = """
    DROP TABLE IF EXISTS logeintrag;
    DROP TABLE IF EXISTS programmdurchlauf;
    DROP TABLE IF EXISTS programmschritt;
    DROP TABLE IF EXISTS programm;
    DROP TABLE IF EXISTS servo;
    """

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema)
    create_tables()
    

if __name__ == "__main__":
    #create_tables()
    #print("Tabellen wurden in robotis.db angelegt.")
    #reset_database()
    #create_programm()
    pass
