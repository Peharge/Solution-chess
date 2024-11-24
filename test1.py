import chess
import chess.engine
import tkinter as tk
from tkinter import messagebox

# Initialisiere das Schachbrett
board = chess.Board()

# Definiere den Pfad zur Stockfish-Engine. Ersetze den Pfad durch den richtigen Pfad zu deiner Stockfish-Binärdatei.
# Stockfish kann kostenlos von https://stockfishchess.org/download/ heruntergeladen werden.
ENGINE_PATH = "C:\\Users\\julia\\PycharmProjects\\chess-bot\\stockfish\\stockfish-windows-x86-64-vnni512.exe"  # Ersetze dies durch den tatsächlichen Pfad zur Stockfish-Binärdatei

# Erstelle eine Instanz der Schach-Engine
engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

def get_best_move():
    """
    Ruft den besten Zug von der Stockfish-Engine ab.

    Returns:
        str: Der beste Zug in UCI-Notation.
    """
    result = engine.play(board, chess.engine.Limit(time=2.0))  # Zeit für den besten Zug auf 2 Sekunden begrenzen
    return result.move.uci()

def make_move():
    """
    Führt einen Zug durch und lässt die Engine den besten Zug für die nächste Stellung finden.
    """
    global board
    move = move_entry.get()
    try:
        if len(move) == 4:  # UCI-Zugformat erkennen, z.B. 'e2e4'
            move = chess.Move.from_uci(move)
            board.push(move)
        else:  # SAN-Zugformat erkennen, z.B. 'e2-e4'
            board.push_san(move)

        # Lass die Engine den besten Zug für die aktuelle Stellung finden
        best_move = get_best_move()
        board.push_uci(best_move)
        update_board_display()
        move_entry.delete(0, tk.END)
        move_response = f"Du ziehst: {move}\nStockfish schlägt vor: {chess.Move.from_uci(best_move)}"
        move_output.set(move_response)
    except ValueError:
        messagebox.showerror("Ungültiger Zug", "Der Zug ist ungültig. Bitte versuche es erneut.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

def update_board_display():
    """
    Aktualisiert die Anzeige des Schachbretts in der GUI.
    """
    board_display.set(str(board))

def generate_response(query):
    """
    Generiert eine Antwort basierend auf der Schachfrage des Benutzers.

    Args:
        query (str): Die Schachfrage des Benutzers.

    Returns:
        str: Die Antwort des Chatbots auf die Schachfrage.
    """
    if "beste Eröffnung" in query.lower():
        return "Die beste Eröffnung hängt von deinem Spielstil ab. Beliebte Eröffnungen sind die Spanische Partie und das Königsgambit."
    elif "schach" in query.lower():
        return "Schach ist ein Strategiespiel, bei dem zwei Spieler versuchen, den gegnerischen König schachmatt zu setzen."
    elif "schachmatt" in query.lower():
        return "Schachmatt tritt ein, wenn der König des Gegners bedroht ist und es keinen legalen Zug gibt, um das Schach zu vermeiden."
    else:
        return "Ich kann dir bei Schachregeln und Eröffnungen helfen. Stelle mir eine Frage zum Schach!"

def handle_query():
    """
    Behandelt die Schachfrage des Benutzers und zeigt die Antwort in der GUI an.
    """
    query = query_entry.get()
    response = generate_response(query)
    query_response.set(response)

def create_tkinter_gui():
    """
    Erstellt die GUI für das Schachspiel und den Schach-Chatbot.
    """
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
    help_text = "Gib einen Zug im Format 'e2-e4' oder 'e2e4' ein und drücke 'Zug machen'."
    help_label = tk.Label(root, text=help_text, font=('Courier', 10))
    help_label.pack()

    # Chat-Funktion für Schachfragen
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

if __name__ == "__main__":
    create_tkinter_gui()

    # Schließe die Engine beim Beenden des Programms
    engine.quit()
