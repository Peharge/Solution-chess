import chess
import tkinter as tk
from tkinter import messagebox
import random

# Initialisiere das Schachbrett
board = chess.Board()

# Funktion zur Generierung von Antworten durch den Chatbot für Schachfragen
def generate_response(query):
    if "beste Eröffnung" in query.lower():
        return "Die beste Eröffnung hängt von deinem Spielstil ab, aber die Spanische Partie (1.e4 e5 2.Nf3 Nc6 3.Bb5) ist eine populäre und starke Eröffnung."
    elif "schach" in query.lower():
        return "Schach ist ein Strategiespiel für zwei Spieler, bei dem das Ziel ist, den gegnerischen König schachmatt zu setzen."
    elif "wie viele züge bis schachmatt" in query.lower():
        return f"Es ist schwierig, genau zu sagen, wie viele Züge bis zum Schachmatt benötigt werden, da es von der Stellung und den Zügen des Gegners abhängt."
    elif "erkläre" in query.lower():
        return "Ich kann dir die Regeln und Strategien für Schach erklären. Stelle mir eine spezifische Frage!"
    else:
        return "Ich kann dir bei Schachregeln und Eröffnungen helfen. Stelle mir eine Frage zum Schach!"

# Funktion zur Durchführung eines Schachzugs durch den Benutzer
def make_move():
    global board
    move = move_entry.get()
    try:
        board.push_san(move)
        # Einfache Zufallsgenerierung für den gegnerischen Zug (nicht sehr intelligent, aber einfach)
        if not board.is_game_over():
            possible_moves = list(board.legal_moves)
            random_move = random.choice(possible_moves)
            board.push(random_move)
            update_board_display()
            move_entry.delete(0, tk.END)
            move_response = f"Du ziehst: {move}\nGegner zieht: {board.san(random_move)}"
            move_output.set(move_response)
        else:
            move_output.set("Das Spiel ist beendet. Bitte starte eine neue Partie.")
    except ValueError:
        messagebox.showerror("Ungültiger Zug", "Der Zug ist ungültig. Bitte versuche es erneut.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Funktion zur Aktualisierung der Schachbrett-Anzeige
def update_board_display():
    board_display.set(str(board))

# GUI-Teil
def create_tkinter_gui():
    global root, move_entry, move_output, board_display, query_entry, query_response

    root = tk.Tk()
    root.title("Schach-Chatbot")

    # Schachbrett-Anzeige
    board_display = tk.StringVar()
    board_display.set(str(board))
    board_label = tk.Label(root, textvariable=board_display, font=('Courier', 14))
    board_label.pack()

    # Zug-Eingabefeld
    move_entry = tk.Entry(root)
    move_entry.pack()

    # Zug-Button
    move_button = tk.Button(root, text="Zug machen", command=make_move)
    move_button.pack()

    # Ausgabe des Zugs
    move_output = tk.StringVar()
    move_output.set("")
    move_output_label = tk.Label(root, textvariable=move_output, font=('Courier', 12))
    move_output_label.pack()

    # Hilfetext
    help_text = "Gib einen Zug im Format 'e2-e4' ein und drücke 'Zug machen'."
    help_label = tk.Label(root, text=help_text, font=('Courier', 10))
    help_label.pack()

    # Chat-Funktion für Schachfragen
    def handle_query():
        query = query_entry.get()
        response = generate_response(query)
        query_response.set(response)

    # Schachfragen-Eingabefeld und Button
    query_entry = tk.Entry(root)
    query_entry.pack()
    query_button = tk.Button(root, text="Frage stellen", command=handle_query)
    query_button.pack()

    # Ausgabe der Antwort auf Schachfragen
    query_response = tk.StringVar()
    query_response.set("")
    query_response_label = tk.Label(root, textvariable=query_response, font=('Courier', 12))
    query_response_label.pack()

    root.mainloop()

# Hauptprogramm
if __name__ == "__main__":
    create_tkinter_gui()
