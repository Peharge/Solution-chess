import chess
import chess.engine

# Initialisiere das Schachbrett
board = chess.Board()

# Definiere den Pfad zur Stockfish-Engine. Ersetze den Pfad durch den richtigen Pfad zu deiner Stockfish-Binärdatei.
# Stockfish kann kostenlos von https://stockfishchess.org/download/ heruntergeladen werden.
ENGINE_PATH = "C:\\Users\\julia\\PycharmProjects\\chess-bot\\stockfish\\stockfish-windows-x86-64-bmi2.exe"  # Ersetze dies durch den tatsächlichen Pfad zur Stockfish-Binärdatei

# Erstelle eine Instanz der Schach-Engine
try:
    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
except Exception as e:
    print(f"Fehler beim Laden der Stockfish-Engine: {e}")
    exit(1)

def get_best_move():
    """
    Ruft den besten Zug von der Stockfish-Engine ab.

    Returns:
        str: Der beste Zug in UCI-Notation.
    """
    result = engine.play(board, chess.engine.Limit(time=2.0))  # Zeit für den besten Zug auf 2 Sekunden begrenzen
    return result.move.uci()

def make_move(move):
    """
    Führt einen Zug durch und lässt die Engine den besten Zug für die nächste Stellung finden.

    Args:
        move (str): Der Zug im SAN- oder UCI-Format.
    """
    global board
    try:
        if len(move) == 4:  # UCI-Zugformat erkennen, z.B. 'e2e4'
            move = chess.Move.from_uci(move)
            board.push(move)
        else:  # SAN-Zugformat erkennen, z.B. 'e2-e4'
            board.push_san(move)

        # Lass die Engine den besten Zug für die aktuelle Stellung finden
        best_move = get_best_move()
        board.push_uci(best_move)
        print(f"Du ziehst: {move}\nStockfish schlägt vor: {chess.Move.from_uci(best_move)}")
    except ValueError:
        print("Der Zug ist ungültig. Bitte versuche es erneut.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# Beispiel für die Verwendung der Engine und eines Zuges
make_move("e2e4")
print(board)

# Schließe die Engine beim Beenden des Programms
engine.quit()
