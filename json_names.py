import csv
import json

csv_file = ".csv"

def create_json(csv_file: str, json_file: str = "names.json"):
    """
    Liest eine csv-Datei und erstellt eine JSON, in welcher jede Person zweimal aufgelistet wird.
    """
    votierliste = []
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            vorname = (row.get('Vorname') or '').strip()
            nachname = (row.get('Nachname') or '').strip()
            full_name = f"{vorname} {nachname}".strip()
            person = {"anmeldename": row["Anmeldename"], "name": full_name}
            votierliste.extend([person]*2)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(votierliste, f, ensure_ascii=False, indent=4)

create_json(csv_file=csv_file)