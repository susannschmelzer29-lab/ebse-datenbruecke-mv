"""Rohdaten abrufen, unverändert ablegen, Prüfsummen festhalten.

Regeln: Vorhandene Rohdateien werden nie überschrieben. Weicht eine Datei von der
festgehaltenen Prüfsumme ab, stoppt der Lauf mit einer Meldung.
"""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone

from src.config import QUELLEN, RAW

MANIFEST = RAW / "manifest.json"


class RohdatenFehler(RuntimeError):
    pass


def sha256(pfad) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def lade_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}


def pruefe_datei(pfad, erwartet: str) -> None:
    ist = sha256(pfad)
    if ist != erwartet:
        raise RohdatenFehler(
            f"{pfad.name}: Prüfsumme weicht ab (erwartet {erwartet[:12]}…, gefunden {ist[:12]}…). "
            "Die Datei wurde verändert oder der Herausgeber hat eine neue Fassung veröffentlicht. "
            "Bitte prüfen, bevor das Manifest angepasst wird.")


def _download(url: str) -> bytes:
    letzter = None
    for versuch in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except OSError as e:
            letzter = e
            time.sleep(3 * (versuch + 1))
    raise RohdatenFehler(f"Abruf gescheitert: {url} ({letzter})")


def fetch_all(log=print) -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = lade_manifest()
    for qid, q in QUELLEN.items():
        pfad = RAW / q["datei"]
        if pfad.exists() and qid not in manifest:
            # Nie stillschweigend eine Datei unbekannter Herkunft zur Referenz machen
            raise RohdatenFehler(f"{pfad.name} liegt vor, fehlt aber im Manifest. Herkunft klären.")
        if not pfad.exists():
            log(f"  {qid}: lade {q['titel']}")
            inhalt = _download(q["url"])
            magic = b"PK" if pfad.suffix == ".xlsx" else b"%PDF"
            if not inhalt.startswith(magic):
                raise RohdatenFehler(f"{qid}: Server lieferte keine {pfad.suffix}-Datei.")
            digest = hashlib.sha256(inhalt).hexdigest()
            if qid in manifest and manifest[qid]["sha256"] != digest:
                raise RohdatenFehler(
                    f"{qid}: Der Herausgeber liefert eine andere Fassung als im Manifest festgehalten.")
            pfad.write_bytes(inhalt)
            manifest.setdefault(qid, {
                "datei": q["datei"], "url": q["url"], "sha256": digest, "bytes": len(inhalt),
                "abgerufen_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        pruefe_datei(pfad, manifest[qid]["sha256"])
        log(f"  {qid}: Prüfsumme stimmt ({manifest[qid]['bytes']:,} Bytes)".replace(",", "."))
    return manifest


if __name__ == "__main__":
    fetch_all()
