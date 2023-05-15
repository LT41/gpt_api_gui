import os
import openai
import datetime
import fitz
from dotenv import load_dotenv
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QPlainTextEdit, QScrollBar, QWidget, QSplitter, QLabel, QListWidget, QListWidgetItem, QInputDialog, QComboBox, QFileDialog
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor, QIcon, QPixmap, QFont, QImage


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_history = []

def chatting(input_message, chat_history, model):
    system_message = f"you are now chatting with model {model}"
    print(system_message)
    chat_history.append({"role": "system", "content": "You are now chatting with an AI."})
    chat_history.append({"role": "user", "content": input_message})
    print(f"Making api call with model {model}")
    response = openai.ChatCompletion.create(
        model=model,
        messages=chat_history,
        max_tokens=1000
    )

    chat_history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})

    return response['choices'][0]['message']['content'], chat_history

class ChatThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, user_input, parent=None):
        QThread.__init__(self, parent)
        self.user_input = user_input

    def run(self):
        global chat_history
        model = self.parent().model_selection.currentText()  # Get the selected model from the dropdown
        response, chat_history = chatting(self.user_input, chat_history, model)
        self.signal.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("GPT-4 Conversation")
        self.setWindowIcon(QIcon("too_cool.png"))
        self.model_selection = QComboBox(self)
        self.model_selection.addItem("gpt-4")
        self.model_selection.addItem("gpt-3.5-turbo")

        # Create and configure the widgets
        self.tag_list = QListWidget(self)
        self.tag_list.setMinimumWidth(200)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        
        self.delete_tag_button = QPushButton("Delete Tag", self)
        self.delete_tag_button.clicked.connect(self.delete_tag)
        
        tag_list_layout = QVBoxLayout()
        tag_list_layout.addWidget(self.tag_list)
        tag_list_layout.addWidget(self.delete_tag_button)
        
        self.tag_button = QPushButton("Tag Message", self)
        self.tag_button.clicked.connect(self.tag_message)
        
        self.display_text = QTextEdit(self)
        self.display_text.setReadOnly(True)

        self.entry = QPlainTextEdit(self)
        self.entry.keyPressEvent = self.entry_keyPressEvent

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.process_input)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_chat)
        
        # Create and set-up the splitters
        splitter_vertical = QSplitter(Qt.Vertical)
        splitter_vertical.addWidget(self.display_text)
        splitter_vertical.addWidget(self.entry)

        splitter_horizontal = QSplitter(Qt.Horizontal)
        splitter_horizontal.addWidget(splitter_vertical)
        tag_list_widget = QWidget()
        tag_list_widget.setLayout(tag_list_layout)
        splitter_horizontal.addWidget(tag_list_widget)
        self.pdf_display = QPlainTextEdit(self)  # Add QLabel for the PDF display
        splitter_horizontal.addWidget(self.pdf_display)
        splitter_horizontal.setStretchFactor(0, 3)
        splitter_horizontal.setStretchFactor(1, 1)

        # Organize the main layout
        main_widget = QVBoxLayout()
        main_widget.addWidget(splitter_horizontal)
        main_widget.addWidget(self.model_selection)  # Add the model selection dropdown to the layout
        main_widget.addWidget(self.tag_button)
        main_widget.addWidget(self.send_button)
        main_widget.addWidget(self.reset_button)
        self.open_pdf_button = QPushButton("Open PDF", self)
        self.open_pdf_button.clicked.connect(self.open_pdf)  # Connect the button to the open_pdf function
        main_widget.addWidget(self.open_pdf_button)
        self.next_page_button = QPushButton("Next Page", self)
        self.next_page_button.clicked.connect(self.next_page)
        main_widget.addWidget(self.next_page_button)
        self.prev_page_button = QPushButton("Previous Page", self)
        self.prev_page_button.clicked.connect(self.previous_page)
        main_widget.addWidget(self.prev_page_button)
        
        self.zoom_in_button = QPushButton("Zoom In", self)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        main_widget.addWidget(self.zoom_in_button)
        self.zoom_out_button = QPushButton("Zoom Out", self)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        main_widget.addWidget(self.zoom_out_button)


        # Set the central widget and layout
        central_widget = QWidget(self)
        central_widget.setLayout(main_widget)
        self.setCentralWidget(central_widget)
        
        # Create the model selection dropdown

        # Aesthetic color scheme
        self.setStyleSheet("""
        * {
            font-size: 16px; 
            }
            QMainWindow {
                background-color: #282a36;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #44475a;
                color: #f8f8f2;
                font-family: "Consolas";
            }
            QPushButton {
                background-color: #6272a4;
                color: #f8f8f2;
            }
            QPushButton:hover {
                background-color: #7797b9;
            }
            QPushButton:pressed {
                background-color: #5e6b8c;
            }
            QListWidget {
                background-color: #44475a;
                color: #f8f8f2;
            }
        """)

        
    def _append_display_text(self, text:str, color:QColor, is_bold=False):
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        if is_bold:
            char_format.setFontWeight(QFont.Bold)
        cursor = QTextCursor(self.display_text.document())
        cursor.movePosition(QTextCursor.End)  # Move cursor to end of document
        cursor.insertText(text, char_format)
        self.display_text.setTextCursor(cursor)

    def process_input(self):
        user_input = self.entry.toPlainText().strip()

        if not user_input:
            return

        if user_input.lower() == "exit":
            self._append_display_text(f"User: {user_input}\n", QColor("#50fa7b"))
            self._append_display_text("Goodbye!\n", QColor("#50fa7b"))
            self.entry.setPlainText("")
            self.entry.setDisabled(True)
            self.send_button.setDisabled(True)
        else:
            self._append_display_text(f"User: ", QColor("#50fa7b"), is_bold=True)
            self._append_display_text(f"{user_input}\n", QColor("#50fa7b"))
            self.entry.setPlainText("")
            self.chat_thread = ChatThread(user_input, self)
            self.chat_thread.signal.connect(self.display_response)
            self.chat_thread.start()

    def display_response(self, response):
            model_name = self.model_selection.currentText()  # Get the selected model name
            if model_name == "gpt-4":
                self._append_display_text(f"{model_name.upper()}: ", QColor("#bd93f9"), is_bold=True)
                self._append_display_text(response + "\n", QColor("#bd93f9"))
            elif model_name == "gpt-3.5-turbo":
                self._append_display_text(f"{model_name.upper()}: ", QColor("#ffa500"), is_bold=True)  # Use orange color for gpt-3.5-turbo
                self._append_display_text(response + "\n", QColor("#ffa500"))


    def reset_chat(self):
        global chat_history
        chat_history = []
        self.display_text.clear()
        
    def delete_tag(self):
        current_item = self.tag_list.currentItem()
        if current_item:
            row = self.tag_list.row(current_item)
            self.tag_list.takeItem(row)

    # New method to handle "Enter" key press event in the entry
    def entry_keyPressEvent(self, e):
        if e.key() == Qt.Key_Return and not (e.modifiers() & Qt.ShiftModifier):
            self.process_input()
        else:
            QPlainTextEdit.keyPressEvent(self.entry, e)
            
    def send_clarification(self, clarification_type):
        message_to_clarify = chat_history[-1]['content']
        clarification_msg = f"{clarification_type}: {message_to_clarify}"
        self.chat_thread = ChatThread(clarification_msg, self)  # Set self as parent
        self.chat_thread.signal.connect(self.display_response)
        self.chat_thread.start()

        
    def tag_message(self):
        tag, ok = QInputDialog.getText(self, "Tag Message", "Enter tag:")
        if ok and tag:
            item = QListWidgetItem(f"{len(chat_history) - 1}: {tag}")
            item.setForeground(QColor("#f1fa8c"))  # Change color to yellow
            self.tag_list.addItem(item)
            
            model_name = self.model_selection.currentText()

            # Ask user if they want the chatbot to clarify the message
            clarify, ok = QInputDialog.getItem(self, "Clarify Message", f"Would you like {model_name.upper()}to clarify this message?", ["Yes", "No"], 0, False)
            if ok and clarify == "Yes":
                # Ask the user to select the clarification type
                clarification_type, ok = QInputDialog.getItem(self, "Clarification Type", "How would you like GPT-4 to clarify this message?", ["Explain like I'm five", "Explain like I'm smart"], 0, False)
                if ok and clarification_type:
                    item.setBackground(QColor("#ff0000"))  # Highlight the item in the list
                    self.send_clarification(clarification_type)

            # Save the tagged message and GPT-4 response to a file
            file_name = "tags_" + datetime.datetime.now().strftime("%Y-%m-%d") + ".txt"

            # Check if the file already exists
            if os.path.exists(file_name):
                mode = "a"  # Append to existing file
            else:
                mode = "w"  # Create new file

            with open(file_name, mode, encoding="utf-8") as file:
                # Write the tagged message to the file
                file.write(f"Tag: {tag}\n")

                # Access chat_history and GPT-4's response
                _, user_message, gpt4_response = chat_history[-3:]

                # Write the messages to the file
                file.write(f"User: {user_message}\n")
                file.write(f"GPT-4: {gpt4_response}\n\n")
                
    def open_pdf(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF files (*.pdf)")
        if not filepath:
            return

        self.pdf_doc = fitz.open(filepath)
        self.current_page = 0
        self.show_page(self.current_page)

    def show_page(self, page_number):
        page = self.pdf_doc.load_page(page_number)
        text = page.get_text("text")
        self.pdf_display.setPlainText(text)
        
    def next_page(self):
        if hasattr(self, "pdf_doc") and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def previous_page(self):
        if hasattr(self, "pdf_doc") and self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)
            
    def zoom_in(self):
        font = self.pdf_display.font()
        font_size = font.pointSize()
        if font_size < 30:
            font.setPointSize(font_size + 1)
            self.pdf_display.setFont(font)

    def zoom_out(self):
        font = self.pdf_display.font()
        font_size = font.pointSize()
        if font_size > 5:
            font.setPointSize(font_size - 1)
            self.pdf_display.setFont(font)


app = QApplication([])

window = MainWindow()
window.show()

app.exec_()