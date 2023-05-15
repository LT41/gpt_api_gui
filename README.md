# gpt_api_gui

GPT-4 Conversation and PDF Reader is a desktop application that allows you to chat with a GPT-4 AI model while reading PDF files. The program saves tagged messages in a text file for future reference.

## Features

- Chat with GPT-4 AI model
- Select between different AI models (gpt-4 or gpt-3.5-turbo)
- Tag specific messages for future retrieval
- Save tagged messages along with the AI response to a file
- Open PDF files and read them while chatting
- Navigate between pages in the PDF
- Zoom in and out of the PDF

## Prerequisites

To use this application, you need to have Python 3 installed and set up on your computer. You also need to have a valid API Key for OpenAI.

## Dependencies

This application uses the following libraries:
- openai
- PyMuPDF (fitz)
- python-dotenv
- PyQt5

You can install these packages using the following command:

```bash
pip install openai PyMuPDF python-dotenv PyQt5
```

## How to Use

1. Set up your OpenAI API key in a `.env` file within the project directory like this:

```
OPENAI_API_KEY=your_api_key_here
```

2. Run the script using Python:

```bash
python gpt_4_conversation.py
```

3. Interact with the application. You can:
    - Type a message and press Enter or click the Send button to chat with the AI model.
    - Click on the "Open PDF" button to open a PDF file and read it alongside the chat.
    - Navigate between pages in the PDF using the "Next Page" and "Previous Page" buttons.
    - Zoom in and out of the PDF using the "Zoom In" and "Zoom Out" buttons.
    - Tag specific messages by clicking the "Tag Message" button, entering a tag, and choosing whether you want the AI to clarify the message.
    - Reset the chat by clicking the "Reset" button. Note that this will clear the chat history in the application.
    - To exit, type `exit` in the message input and press Enter or click the Send button.

4. The application saves tagged messages along with their corresponding AI response in a file named  `tags_YYYY-MM-DD.txt` in the current directory, where `YYYY-MM-DD` is the date when the message was tagged. You can access this file for future reference.
