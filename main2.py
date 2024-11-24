import sys
import chess
import chess.engine
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout, QTextEdit
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QEvent
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QLabel, QGridLayout, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsBlurEffect

import chess.engine

# Initialisiere das Schachbrett
board = chess.Board()

ENGINE_PATH = "C:\\Users\\julia\\PycharmProjects\\chess-bot\\stockfish\\stockfish-windows-x86-64-avx2.exe"

engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

engine.configure({
    "UCI_LimitStrength": False,  # Deaktiviere die Begrenzung der Spielstärke
    "UCI_Elo": 1320,             # Setze eine extrem hohe Elo-Zahl für maximale Stärke (Standard bei unbegrenzter Spielstärke)
    "Threads": 6,                # Anzahl der Threads, die Stockfish nutzen soll (anpassen an Ihr System)
    "Hash": 8192,                # Erhöhe den Hash-Speicher in MB (falls Ihr System genug RAM hat)
})


class ChessChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat++")
        self.setGeometry(100, 100, 700, 700)

        self.setWindowIcon(QtGui.QIcon(
            'C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.4'))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        main_widget.setLayout(main_layout)

        self.board_display = QWidget()
        self.board_display.setFont(QFont('Courier', 14))
        self.board_layout = QGridLayout()
        self.board_display.setLayout(self.board_layout)

        self.piece_labels = {}
        self.selected_piece = None
        self.update_board_display()
        main_layout.addWidget(self.board_display)

        help_text = "\nKlicke auf eine Figur und dann auf das Ziel-Feld, um den Zug auszuführen \noder gib einen Zug ein:"
        help_label = QLabel(help_text)
        help_label.setFont(QFont('Courier', 10))
        main_layout.addWidget(help_label)

        move_layout = QHBoxLayout()
        self.move_entry = QLineEdit()
        self.move_entry.setPlaceholderText("Gib einen Zug ein (z.B. 'e2e4')")
        self.move_entry.setFixedSize(600, 30)
        move_button = QPushButton("Zug machen")
        move_button.setFixedSize(85, 30)
        move_button.setStyleSheet("""
            QPushButton {
                background-color: #1c1c1c;
                color: #ffffff;
                border-radius: 5px;
                border: 2px solid #4a4a4a;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 3px solid #0078d7;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                border: 3px solid #004578;
            }
                """)
        move_button.clicked.connect(self.make_move)
        move_layout.addWidget(self.move_entry)
        move_layout.addWidget(move_button)
        main_layout.addLayout(move_layout)

        self.move_output = QLabel("")
        self.move_output.setFont(QFont('Courier', 12))
        main_layout.addWidget(self.move_output)

        help_text = "\nStelle eine Frage an Chat++:"
        help_label = QLabel(help_text)
        help_label.setFont(QFont('Courier', 10))
        main_layout.addWidget(help_label)

        query_layout = QHBoxLayout()
        self.query_entry = QLineEdit()
        self.query_entry.setPlaceholderText("Stelle eine Frage an Chat++")
        self.query_entry.setFixedSize(600, 30)
        query_button = QPushButton("Frage stellen")
        query_button.setFixedSize(85, 30)
        query_button.setStyleSheet("""
            QPushButton {
                background-color: #1c1c1c;
                color: #ffffff;
                border-radius: 5px;
                border: 2px solid #4a4a4a;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 3px solid #0078d7;
            }
            QPushButton:pressed {
                background-color: #0078d7;
                border: 3px solid #004578;
            }
        """)
        query_button.clicked.connect(self.handle_query)
        query_layout.addWidget(self.query_entry)
        query_layout.addWidget(query_button)

        wrapper_layout = QVBoxLayout()
        wrapper_layout.addLayout(query_layout)
        wrapper_layout.addStretch()

        main_layout.addLayout(wrapper_layout)
        self.setLayout(main_layout)

        self.query_response = QLabel("")
        self.query_response.setFont(QFont('Courier', 12))
        main_layout.addWidget(self.query_response)

        self.board_display.installEventFilter(self)

    def get_best_move(self):
        """
        Ruft den besten Zug von der Stockfish-Engine ab.

        Returns:
            str: Der beste Zug in UCI-Notation.
        """
        try:
            result = engine.play(board, chess.engine.Limit(time=10.0, depth=20))
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
            if len(move) == 4:
                move = chess.Move.from_uci(move)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    raise ValueError("Der Zug ist nicht legal.")
            elif len(move) >= 5:
                move = chess.Move.from_san(move)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    raise ValueError("Der Zug ist nicht legal.")
            else:
                raise ValueError("Ungültiges Zugformat.")

            best_move = self.get_best_move()
            if best_move:
                board.push_uci(best_move)
                self.update_board_display()
                move_response = f"Du ziehst: {move}\nChat++ zieht: {chess.Move.from_uci(best_move)}"
                self.move_output.setText(move_response)
            else:
                self.show_error("Fehler", "Chat++ konnte keinen Zug finden.")
        except ValueError as ve:
            self.show_error("Ungültiger Zug", str(ve))
        except Exception as e:
            self.show_error("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    def update_board_display(self):
        """
        Aktualisiert die Anzeige des Schachbretts in der GUI.
        """
        for i in reversed(range(self.board_layout.count())):
            widget = self.board_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        PIECE_IMAGE_PATHS = {
            'K': 'C:/Users/julia/PycharmProjects/chess-bot/img2/wK.svg',
            'Q': 'C:/Users/julia/PycharmProjects/chess-bot/img2/wQ.svg',
            'R': 'C:/Users/julia/PycharmProjects/chess-bot/img2/wR.svg',
            'B': 'C:/Users/julia/PycharmProjects/chess-bot/img2/wB.svg',
            'N': 'C:/Users/julia/PycharmProjects/chess-bot/img2/wN.svg',
            'P': 'C:/Users/julia/PycharmProjects/chess-bot/img2/wP.svg',
            'k': 'C:/Users/julia/PycharmProjects/chess-bot/img2/bK.svg',
            'q': 'C:/Users/julia/PycharmProjects/chess-bot/img2/bQ.svg',
            'r': 'C:/Users/julia/PycharmProjects/chess-bot/img2/bR.svg',
            'b': 'C:/Users/julia/PycharmProjects/chess-bot/img2/bB.svg',
            'n': 'C:/Users/julia/PycharmProjects/chess-bot/img2/bN.svg',
            'p': 'C:/Users/julia/PycharmProjects/chess-bot/img2/bP.svg',
        }

        for i in range(8):
            for j in range(8):
                square = chess.square(j, 7 - i)
                piece = board.piece_at(square)
                piece_label = QLabel()
                piece_label.setFont(QFont('Courier', 16))
                piece_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                piece_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid black; padding: 10px; border-radius: 10px; /* Abgerundete Ecken */
                    }
                    
                    QLabel:hover {
                        border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #0078d7, stop: 1 #008000);
                    }
                
                """)
                piece_label.setFixedSize(70, 70)
                piece_label.setProperty('square', chess.square_name(square))
                piece_label.setProperty('square_coord', (i, j))
                piece_label.installEventFilter(self)

                if piece:
                    piece_image_path = PIECE_IMAGE_PATHS.get(piece.symbol())
                    if piece_image_path:
                        piece_label.setPixmap(
                            QPixmap(piece_image_path).scaled(55, 55, Qt.AspectRatioMode.KeepAspectRatio))

                self.board_layout.addWidget(piece_label, i, j)
                self.piece_labels[(i, j)] = piece_label

        for i in range(8):
            file_label = QLabel(chr(97 + i))  # a, b, c, d, e, f, g, h
            file_label.setFont(QFont('Courier', 12))
            file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.board_layout.addWidget(file_label, 8, i)

        for i in range(8):
            rank_label = QLabel(str(8 - i))  # 8, 7, 6, 5, 4, 3, 2, 1
            rank_label.setFont(QFont('Courier', 12))
            rank_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
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
                coord = obj.property('square_coord')
                if coord:
                    if self.selected_piece:
                        target_coord = coord
                        move = self.get_move_from_squares(self.selected_piece, target_coord)
                        if move:
                            try:
                                chess_move = chess.Move.from_uci(move)
                                if chess_move in board.legal_moves:
                                    board.push(chess_move)
                                    self.update_board_display()
                                    move_response = f"Du ziehst: {move}"
                                    self.move_output.setText(move_response)

                                    best_move = self.get_best_move()
                                    if best_move:
                                        board.push_uci(best_move)
                                        self.update_board_display()
                                        move_response += f"\nChat++ schlägt vor: {chess.Move.from_uci(best_move)}"
                                        self.move_output.setText(move_response)
                                    else:
                                        self.show_error("Fehler", "Chat++ konnte keinen Zug finden.")
                                else:
                                    self.show_error("Ungültiger Zug", "Der Zug ist nicht legal.")
                            except Exception as e:
                                self.show_error("Fehler", f"Fehler beim Erzeugen des Zuges: {e}")

                            self.selected_piece = None
                            self.update_board_display()
                        else:
                            self.show_error("Fehler", "Ungültige Zug-Notation.")
                    else:
                        self.selected_piece = coord
                        piece_label = self.piece_labels[coord]
                        piece_label.setStyleSheet(""" 
                            QLabel {
                                border-radius: 10px; /* Abgerundete Ecken */
                                border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #ff0000, stop: 1 #008000);
                                padding: 10px;
                            }

                            QLabel:hover {
                                border: 4px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #ff0000, stop: 1 #008000);
                            }

                        """)

                        for (x, y), label in self.piece_labels.items():
                            if (x, y) != coord:
                                label.setStyleSheet("""
                                    QLabel {
                                        border-radius: 10px; /* Abgerundete Ecken */
                                        border: 1px solid black; padding: 10px;
                                    }

                                    QLabel:hover {
                                        border: 3px solid red;
                                    }
                                """)
                        for move in board.legal_moves:
                            if move.from_square == chess.square(coord[1], 7 - coord[0]):
                                target_coord = (
                                7 - chess.square_rank(move.to_square), chess.square_file(move.to_square))
                                if target_coord in self.piece_labels:
                                    target_label = self.piece_labels[target_coord]
                                    target_label.setStyleSheet("""
                                        QLabel {
                                            border-radius: 10px; /* Abgerundete Ecken */
                                            padding: 10px; /* Innenabstand */
                                            border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #00ff00, stop: 1 #008000); /* Linearer Farbverlauf für den Rand */
                                        }
                                        QLabel:hover {
                                            border: 4px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #00ff00, stop: 1 #008000); /* Rand beim Hover */
                                        }
                                        QLabel:pressed {
                                            border: 3px solid qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0, stop: 0 #ff0000, stop: 1 #008000); /* Rand beim Klicken */
                                        }
                                    """)
                else:
                    # Entfernen Sie den grünen Rand von den Ziel-Feldern, wenn außerhalb des Schachbretts
                    for (x, y), label in self.piece_labels.items():
                        if label.property('square_coord') in [coord for (x, y), label in self.piece_labels.items() if
                                                              label.styleSheet().startswith("border: 2px solid green")]:
                            label.setStyleSheet("border: 1px solid black; padding: 10px; background-color: rgba(0, 255, 0, 0.5);")

        return super().eventFilter(obj, event)

    def get_move_from_squares(self, source_square, target_square):
        """
        Erzeugt eine UCI-Notation für den Zug basierend auf dem Quell- und Ziel-Square.

        Args:
            source_square (tuple): Die Koordinaten des Quell-Squares.
            target_square (tuple): Die Koordinaten des Ziel-Squares.

        Returns:
            str: Der Zug in UCI-Notation oder None, wenn die Quelle und das Ziel dasselbe sind.
        """
        if source_square == target_square:
            return None  # Kein Zug, wenn Quelle und Ziel gleich sind
        source_square_name = chess.square_name(chess.square(source_square[1], 7 - source_square[0]))
        target_square_name = chess.square_name(chess.square(target_square[1], 7 - target_square[0]))
        return source_square_name + target_square_name

    def show_error(self, title, message):
        """
        Zeigt eine Fehlermeldung an.

        Args:
            title (str): Der Titel der Fehlermeldung.
            message (str): Die Fehlermeldung.
        """
        QMessageBox.critical(self, title, message)

    def handle_query(self):
        """
        Behandelt die Schach-Frage und gibt eine Antwort.
        """
        query = self.query_entry.text()
        if query:
            response = self.ask_stockfish(query)
            self.query_response.setText(response)
        else:
            self.query_response.setText("Bitte stelle eine Frage.")

    def ask_stockfish(self, query):
        """
        Fragt Stockfish nach einer Antwort auf eine Schachfrage.

        Args:
            query (str): Die Schachfrage.

        Returns:
            str: Die Antwort von Stockfish.
        """
        try:
            with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
                result = engine.play(board, chess.engine.Limit(time=2.0))
                best_move = result.move
                return f"Beste Zug: {best_move.uci()}"
        except Exception as e:
            return f"Fehler bei der Anfrage an Chat++: {e}"

# Hauptfunktion
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = ChessChatBot()
    main_win.show()
    sys.exit(app.exec())
