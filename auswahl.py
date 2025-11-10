import csv
from animation import run_animation

CSV_FILENAME = "Uebung_2_Pro_Person_2025-11-04.csv"
AUFGABEN_SPALTEN = [
    "Aufgabe 1 [1]",
    "Aufgabe 2 [2]",
    "Aufgabe 3 [3]",
    "Aufgabe 4 [4]",
    "Aufgabe 5 [5]"
]

def read_candidates():
    """Liest die Kandidaten aus der CSV-Datei."""
    candidates_per_task = {task: [] for task in AUFGABEN_SPALTEN}

    try:
        with open(CSV_FILENAME, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile, delimiter=";")
            for row in reader:
                full_name = f"{row['Vorname']} {row['Nachname']}"
                for task_column in AUFGABEN_SPALTEN:
                    if row.get(task_column, "").strip():
                        candidates_per_task[task_column].append(full_name)
    except FileNotFoundError:
        print(f"Fehler: Die Datei '{CSV_FILENAME}' wurde nicht gefunden.")
        return None
    except Exception as exc:
        print(f"Ein Fehler ist aufgetreten: {exc}")
        return None

    return candidates_per_task

def main():
    print("Starte die zufällige Auswahl für das Vorrechnen...")

    candidates_per_task = read_candidates()
    if candidates_per_task is None:
        return

    print("\nFür welche Aufgabe soll eine Person ausgewählt werden?")
    for index, task_name in enumerate(AUFGABEN_SPALTEN, start=1):
        print(f"  {index}) {task_name}")

    while True:
        try:
            choice = int(input(f"\nBitte wähle eine Aufgabe (1-{len(AUFGABEN_SPALTEN)}): "))
            if 1 <= choice <= len(AUFGABEN_SPALTEN):
                selected_task = AUFGABEN_SPALTEN[choice - 1]
                break
            print("Ungültige Auswahl. Bitte gib eine Zahl zwischen 1 und 5 ein.")
        except ValueError:
            print("Ungültige Eingabe. Bitte gib eine Zahl ein.")

    candidates_for_task = candidates_per_task[selected_task]
    winner = run_animation(candidates_for_task, selected_task)

    if winner:
        print(f"\nDie für '{selected_task}' ausgewählte Person ist: {winner}")
    else:
        print(f"\nFür '{selected_task}' konnte niemand ausgewählt werden, oder die Animation wurde abgebrochen.")

if __name__ == "__main__":
    main()
