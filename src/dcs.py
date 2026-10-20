from dataclasses import dataclass, field
from typing import Optional
from server import _jetzt


# ---------------------------------------------------------------------------
# Dataclasses (eine pro Tabelle)
# Felder mit PK stehen am Ende und sind None, solange der Datensatz noch
# nicht in der Datenbank gespeichert wurde.
# ---------------------------------------------------------------------------

@dataclass
class ServoDC:
    name: str
    min_position: int = 0
    max_position: int = 1023  # AX-Serie: 0-1023
    servo_id: Optional[int] = None  # Dynamixel-ID des Servos, wird selbst vergeben | Primary Key, wird von der Datenbank vergeben

@dataclass
class ProgrammschrittDC:
    programm_id: int
    servo_id: int
    reihenfolge: int
    zielposition: int
    geschwindigkeit: int = 0  # AX-Serie: 0 = maximale Geschwindigkeit
    dauer_ms: int = 0
    schritt_id: Optional[int] = None #Primary Key, wird von der Datenbank vergeben
    

@dataclass
class ProgrammDC:
    name: str
    beschreibung: str = ""
    erstellt_am: str = field(default_factory=_jetzt)
    programm_id: Optional[int] = None #Primary Key, wird von der Datenbank vergeben

    
@dataclass
class ProgrammdurchlaufDC:
    programm_id: int
    status: str #= "laufend"
    endlosschleife: bool = False
    anzahl_zyklen_geplant: int = 1
    anzahl_zyklen_abgeschlossen: int = 0
    start_zeit: str = field(default_factory=_jetzt)
    end_zeit: Optional[str] = None
    durchlauf_id: Optional[int] = None #Primary Key, wird von der Datenbank vergeben


@dataclass
class LogeintragDC:
    typ: str  # INFO, WARNUNG, FEHLER oder MECHANISCH
    nachricht: str
    zeitstempel: str = field(default_factory=_jetzt)
    durchlauf_id: Optional[int] = None  # None = Ereignis außerhalb eines Durchlaufs (z. B. Not-Aus)
    log_id: Optional[int] = None #Primary Key, wird von der Datenbank vergeben
    
