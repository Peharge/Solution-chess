import chess
import chess.engine
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout
from PyQt6.QtGui import QFont, QMouseEvent
from PyQt6.QtCore import Qt, QPoint

# Initialisiere das Schachbrett
board = chess.Board()

# Definiere den Pfad zur Stockfish-Engine. Ersetze den Pfad durch den richtigen Pfad zu deiner Stockfish-Binärdatei.
# Stockfish kann kostenlos von https://stockfishchess.org/download/ heruntergeladen werden.
ENGINE_PATH = "C:\\Users\\julia\\PycharmProjects\\chess-bot\\stockfish\\stockfish-windows-x86-64-bmi2.exe"
  # Ersetze dies durch den tatsächlichen Pfad zur Stockfish-Binärdatei

# Erstelle eine Instanz der Schach-Engine
engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

class ChessChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schach-Chatbot")
        self.setGeometry(100, 100, 600, 500)

        # Haupt-Widget und Layouts erstellen
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Schachbrett-Anzeige
        self.board_display = QWidget()
        self.board_display.setFont(QFont('Courier', 14))
        self.board_layout = QGridLayout()
        self.board_display.setLayout(self.board_layout)

        self.piece_labels = {}
        self.source_square = None
        self.update_board_display()
        main_layout.addWidget(self.board_display)

        # Zug-Eingabefeld und Button
        move_layout = QHBoxLayout()
        self.move_entry = QLineEdit()
        self.move_entry.setPlaceholderText("Gib einen Zug ein (z.B. 'e2e4' oder 'e2-e4')")
        move_button = QPushButton("Zug machen")
        move_button.clicked.connect(self.make_move)
        move_layout.addWidget(self.move_entry)
        move_layout.addWidget(move_button)
        main_layout.addLayout(move_layout)

        # Ausgabe des Zugs
        self.move_output = QLabel("")
        self.move_output.setFont(QFont('Courier', 12))
        main_layout.addWidget(self.move_output)

        # Hilfetext
        help_text = "Gib einen Zug im Format 'e2-e4' oder 'e2e4' ein und drücke 'Zug machen'."
        help_label = QLabel(help_text)
        help_label.setFont(QFont('Courier', 10))
        main_layout.addWidget(help_label)

        # Chat-Funktion für Schachfragen
        query_layout = QHBoxLayout()
        self.query_entry = QLineEdit()
        self.query_entry.setPlaceholderText("Stelle eine Frage zu Schach")
        query_button = QPushButton("Frage stellen")
        query_button.clicked.connect(self.handle_query)
        query_layout.addWidget(self.query_entry)
        query_layout.addWidget(query_button)
        main_layout.addLayout(query_layout)

        # Ausgabe der Antwort auf Schachfragen
        self.query_response = QLabel("")
        self.query_response.setFont(QFont('Courier', 12))
        main_layout.addWidget(self.query_response)

    def get_best_move(self):
        """
        Ruft den besten Zug von der Stockfish-Engine ab.

        Returns:
            str: Der beste Zug in UCI-Notation.
        """
        try:
            result = engine.play(board, chess.engine.Limit(time=2.0))  # Zeit für den besten Zug auf 2 Sekunden begrenzen
            return result.move.uci()
        except Exception as e:
            self.show_error("Fehler", f"Fehler beim Abrufen des besten Zugs: {e}")
            return None

    def make_move(self):
        """
        Führt einen Zug durch und lässt die Engine den besten Zug für die nächste Stellung finden.
        """
        global board
        move = self.move_entry.text()
        try:
            if len(move) == 4:  # UCI-Zugformat erkennen, z.B. 'e2e4'
                move = chess.Move.from_uci(move)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    raise ValueError("Der Zug ist nicht legal.")
            else:  # SAN-Zugformat erkennen, z.B. 'e2-e4'
                move = chess.Move.from_san(move)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    raise ValueError("Der Zug ist nicht legal.")

            # Lass die Engine den besten Zug für die aktuelle Stellung finden
            best_move = self.get_best_move()
            if best_move:
                board.push_uci(best_move)
                self.update_board_display()
                self.move_entry.clear()
                move_response = f"Du ziehst: {move}\nStockfish schlägt vor: {chess.Move.from_uci(best_move)}"
                self.move_output.setText(move_response)
        except ValueError as ve:
            self.show_error("Ungültiger Zug", str(ve))
        except Exception as e:
            self.show_error("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    def update_board_display(self):
        """
        Aktualisiert die Anzeige des Schachbretts in der GUI.
        """
        # Leere das Layout des Schachbretts
        for i in reversed(range(self.board_layout.count())):
            widget = self.board_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Erstelle die Zeilen und Spalten des Schachbretts mit Koordinaten
        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)
                piece = board.piece_at(square)
                piece_text = piece.symbol() if piece else ""
                piece_label = QLabel(piece_text)
                piece_label.setFont(QFont('Courier', 16))
                piece_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                piece_label.setStyleSheet("border: 1px solid black; padding: 10px;")
                piece_label.setFixedSize(50, 50)
                piece_label.setProperty('square', chess.square_name(square))
                piece_label.setProperty('square_coord', (i, j))  # Speichert die Koordinaten des Schachfeldes
                piece_label.installEventFilter(self)  # Fügt einen Event-Filter hinzu
                self.board_layout.addWidget(piece_label, i, j)
                self.piece_labels[(i, j)] = piece_label

        # Füge die Koordinaten-Beschriftungen hinzu
        for i in range(8):
            file_label = QLabel(chr(97 + i))  # a, b, c, d, e, f, g, h
            file_label.setFont(QFont('Courier', 12))
            file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.board_layout.addWidget(file_label, 8, i)

        for i in range(8):
            rank_label = QLabel(str(8 - i))  # 8, 7, 6, 5, 4, 3, 2, 1
            rank_label.setFont(QFont('Courier', 12))
            rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.board_layout.addWidget(rank_label, i, 8)

    def eventFilter(self, obj, event):
        """
        Filtert Maus-Ereignisse, um das Drag-and-Drop-Verhalten zu ermöglichen.

        Args:
            obj (QWidget): Das Widget, auf dem das Ereignis stattfindet.
            event (QEvent): Das Ereignis.

        Returns:
            bool: Gibt True zurück, wenn das Ereignis verarbeitet wurde, sonst False.
        """
        if event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                source_coord = obj.property('square_coord')
                if source_coord:
                    self.source_square = source_coord
                    piece_label = self.piece_labels[self.source_square]
                    piece_label.setStyleSheet("border: 2px solid red; padding: 10px;")
        elif event.type() == event.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                target_coord = obj.property('square_coord')
                if self.source_square and target_coord:
                    move = chess.Move.from_uci(self.get_move_from_squares(self.source_square, target_coord))
                    if move in board.legal_moves:
                        board.push(move)
                        best_move = self.get_best_move()
                        if best_move:
                            board.push_uci(best_move)
                            self.update_board_display()
                            move_response = f"Du ziehst: {move}\nStockfish schlägt vor: {chess.Move.from_uci(best_move)}"
                            self.move_output.setText(move_response)
                    else:
                        self.show_error("Ungültiger Zug", "Der Zug ist nicht legal.")
                    piece_label = self.piece_labels[self.source_square]
                    piece_label.setStyleSheet("border: 1px solid black; padding: 10px;")
                    self.source_square = None
        return super().eventFilter(obj, event)

    def get_square_from_widget(self, widget):
        """
        Ermittelt die Schachfeld-Koordinaten basierend auf dem Widget.

        Args:
            widget (QWidget): Das Widget, das das Schachfeld darstellt.

        Returns:
            tuple: Die Koordinaten des Schachfeldes als (i, j)-Tupel.
        """
        return widget.property('square_coord')

    def get_move_from_squares(self, source_square, target_square):
        """
        Erzeugt eine UCI-Notation für den Zug basierend auf dem Quell- und Ziel-Square.

        Args:
            source_square (tuple): Die Koordinaten des Quell-Squares.
            target_square (tuple): Die Koordinaten des Ziel-Squares.

        Returns:
            str: Der Zug in UCI-Notation.
        """
        source_square_name = chess.square_name(chess.square(source_square[1], 7 - source_square[0]))
        target_square_name = chess.square_name(chess.square(target_square[1], 7 - target_square[0]))
        return source_square_name + target_square_name

    def generate_response(self, query):
        """
        Generiert eine Antwort basierend auf der Schachfrage des Benutzers.

        Args:
            query (str): Die Schachfrage des Benutzers.

        Returns:
            str: Die Antwort des Chatbots auf die Schachfrage.
        """
        query = query.lower()
        if "beste eröffnung" in query:
            return "Die beste Eröffnung hängt von deinem Spielstil ab. Beliebte Eröffnungen sind die Spanische Partie, das Königsgambit und die Sizilianische Verteidigung."
        elif "schach" in query:
            return "Schach ist ein Strategiespiel, bei dem zwei Spieler versuchen, den gegnerischen König schachmatt zu setzen."
        elif "schachmatt" in query:
            return "Schachmatt tritt ein, wenn der König des Gegners bedroht ist und es keinen legalen Zug gibt, um das Schach zu vermeiden."
        elif "pat" in query:
            return "Ein Patt tritt ein, wenn der Spieler am Zug ist, aber keinen legalen Zug machen kann und sein König nicht im Schach steht."
        elif "remis" in query:
            return "Remis ist ein Unentschieden im Schach. Es kann durch ein Patt, dreifache Stellungswiederholung oder durch ein Einvernehmen der Spieler erreicht werden."
        else:
            return "Ich kann dir bei Schachregeln und Eröffnungen helfen. Stelle mir eine Frage zum Schach!"

    def handle_query(self):
        """
        Behandelt die Schachfrage des Benutzers und zeigt die Antwort in der GUI an.
        """
        query = self.query_entry.text()
        response = self.generate_response(query)
        self.query_response.setText(response)

    def show_error(self, title, message):
        """
        Zeigt eine Fehlermeldung an.

        Args:
            title (str): Der Titel der Fehlermeldung.
            message (str): Die Fehlermeldung.
        """
        QMessageBox.critical(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessChatBot()
    window.show()
    sys.exit(app.exec())

    # Schließe die Engine beim Beenden des Programms
    engine.quit()
