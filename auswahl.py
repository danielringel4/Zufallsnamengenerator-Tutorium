import csv
import json
from animation import run_animation

CSV_FILENAME = ".csv"


def read_candidates():
    """Liest die Kandidaten aus der CSV-Datei.

    Ermittelt automatisch alle Spalten, die mit 'Aufgabe' beginnen und
    gibt ein Dict zurück: {aufgabename: [voller_name, ...], ...}.
    """
    try:
        with open(CSV_FILENAME, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile, delimiter=";")
            if reader.fieldnames is None:
                print(f"Fehler: Keine Kopfzeile in '{CSV_FILENAME}' gefunden.")
                return None

            # Bestimme dynamisch die Aufgabenspalten (alles, was mit 'Aufgabe' beginnt)
            aufgaben_spalten = [c for c in reader.fieldnames if c and c.strip().startswith("Aufgabe")]
            candidates_per_task = {task: [] for task in aufgaben_spalten}

            for row in reader:
                vorname = (row.get('Vorname') or '').strip()
                nachname = (row.get('Nachname') or '').strip()
                full_name = f"{vorname} {nachname}".strip()
                if not full_name:
                    continue
                for task_column in aufgaben_spalten:
                    if row.get(task_column, "").strip():
                        candidates_per_task[task_column].append(full_name)
    except FileNotFoundError:
        print(f"Fehler: Die Datei '{CSV_FILENAME}' wurde nicht gefunden.")
        return None
    except Exception as exc:
        print(f"Ein Fehler ist aufgetreten: {exc}")
        return None
    for task, names in candidates_per_task.items():
        candidates_per_task[task] = list(dict.fromkeys(names))

    return candidates_per_task


def compute_vote_counts(candidates_per_task: dict) -> dict:
    """Gibt für jede Person zurück, für wie viele unterschiedliche Aufgaben sie gevotet hat.

    Zählt pro Aufgabe nur einmal (set), also entspricht der Wert der Anzahl der
    verschiedenen Aufgaben, für die die Person eine Lösung eingereicht hat.
    """
    counts = {}
    for lst in candidates_per_task.values():
        for name in set(lst):
            counts[name] = counts.get(name, 0) + 1
    return counts

def main():
    print("Starte die zufällige Auswahl für das Vorrechnen...")

    candidates_per_task = read_candidates()
    if candidates_per_task is None:
        return

    # Filter: nur Aufgaben anzeigen, für die es mindestens eine Spalte (auch wenn aktuell 0 Einträge)
    available_tasks = [t for t in candidates_per_task.keys()]
    if not available_tasks:
        print("Keine Aufgaben-Spalten in der CSV gefunden.")
        return

    # Ermittele, wie viele Aufgaben jede Person gevotet hat (n)
    vote_counts = compute_vote_counts(candidates_per_task)

    print("\nFür welche Aufgabe soll eine Person ausgewählt werden?")
    for index, task_name in enumerate(available_tasks, start=1):
        # Zeige Anzahl der Kandidaten in Klammern, falls gewünscht
        count = len(candidates_per_task.get(task_name, []))
        print(f"  {index}) {task_name} [{count}]")

    # Zusätzliche Option: Alle Namen
    all_index = len(available_tasks) + 1
    print(f"  {all_index}) Alle Namen (alle Kandidat:innen)")

    while True:
        try:
            choice = int(input(f"\nBitte wähle eine Aufgabe (1-{all_index}): "))
            if 1 <= choice <= all_index:
                if choice == all_index:
                    # Alle Namen aus allen Aufgaben (einmalig eindeutige Namen)
                    all_names = []
                    seen = set()
                    for lst in candidates_per_task.values():
                        for n in lst:
                            if n not in seen:
                                seen.add(n)
                                all_names.append(n)
                    selected_task = "Alle Aufgaben"
                    candidates_for_task = all_names
                else:
                    selected_task = available_tasks[choice - 1]
                    candidates_for_task = candidates_per_task.get(selected_task, [])
                break
            print(f"Ungültige Auswahl. Bitte gib eine Zahl zwischen 1 und {all_index} ein.")
        except ValueError:
            print("Ungültige Eingabe. Bitte gib eine Zahl ein.")

    # Berechne Gewichte gemäß Vorgabe: pro Person 100 Stimmen verteilt als 100 / n^2
    weights = {}
    for name in set(candidates_for_task):
        n = vote_counts.get(name, 1)
        try:
            n_val = int(n) if n else 1
        except Exception:
            n_val = 1
        if n_val <= 0:
            n_val = 1
        weights[name] = 100.0 / (n_val * n_val)

    with open("names.json", "r", encoding="utf-8") as f:
        json_names = json.load(f)

    avail_names = [p["name"] for p in json_names]
    intersec = set(candidates_for_task).intersection(avail_names)

    if not intersec:
        print(f"Alle Personen, die {selected_task} votiert haben, haben schon zweimal vorgerechnet.")
    else:
        # winner = run_animation(candidates_for_task, selected_task, weights=weights)
        winner = run_animation(list(intersec), selected_task)
        person_in_list = None
        for person in json_names:
            if person["name"] == winner:
                person_in_list = person
                break
        if person_in_list:
            json_names.remove(person_in_list)

            with open("names.json", "w", encoding="utf-8") as f:
                json.dump(json_names, f, ensure_ascii=False, indent=4)

    if winner:
        print(f"\nDie für '{selected_task}' ausgewählte Person ist: {winner}")
    else:
        print(f"\nFür '{selected_task}' konnte niemand ausgewählt werden, oder die Animation wurde abgebrochen.")

if __name__ == "__main__":
    main()