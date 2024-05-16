# YouTube Comments Extractor and Query System

This project allows users to extract comments from YouTube videos, upload PDFs and query their contents, and interact with these data sources using a chatbot-like interface powered by an LLM (Language Model) from LM Studio.

## Features

1. **Fetch YouTube Comments**
   - Extract comments from YouTube videos using the YouTube Data API.
   - Save comments with a reference name.
   - Load and display saved comments.
   - Download comments as a text file.
   - Manage API keys for the YouTube Data API.

2. **Chat Interface**
   - Load saved comments and interact with them using an LLM.
   - Save chat sessions with a reference name.
   - Load and continue from previous chat sessions.
   - Download chat history as a PDF.
   - Delete chat sessions.

3. **PDF Upload and Query**
   - Upload PDFs and extract text from them.
   - Save extracted text with a reference name.
   - Load and display saved PDF text.
   - Interact with the PDF text using an LLM.
   - Save chat sessions with a reference name.
   - Load and continue from previous chat sessions.
   - Download chat history as a PDF.
   - Delete chat sessions.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
2. Install dependencies:
   ```pip install streamlit google-api-python-client openai faiss-cpu scikit-learn PyMuPDF fpdf```
   
# Usage
Run the Streamlit application:
```streamlit run main.py```
Open your web browser and navigate to http://localhost:8501.

Use the sidebar to navigate between the features:

1. ***Fetch YouTube Comments***
2. ***Chat Interface***
3. ***PDF Upload***
## Fetch YouTube Comments
- Select an API key or add a new one.
- Enter the YouTube video link and a reference name.
- Click on "Get Comments" to fetch and save comments.
- Load saved comments to view and download them.
## Chat Interface
- Select an API key and a model from LM Studio.
- Load saved comments using a reference name.
- Enter your query and interact with the comments.
- Save and load chat sessions.
- Download chat history as a PDF.
- Delete chat sessions.
## PDF Upload
- Select an API key from LM Studio.
- Upload a PDF and provide a reference name to save it.
- Load saved PDF text using a reference name.
- Enter your query and interact with the PDF text.
- Save and load chat sessions.
- Download chat history as a PDF.
- Delete chat sessions.

# File Structure
```.
├── main.py
├── youtube_comments.py
├── chat_interface.py
├── pdf_upload.py
├── api_keys.json
├── history.json
├── comments.json
├── pdf_data.json
├── chat_history.json
├── pdf_chat_history.json
└── README.md
```

- main.py: The main script to run the Streamlit application.
- youtube_comments.py: Module for fetching and managing YouTube comments.
- chat_interface.py: Module for interacting with comments using the chatbot interface.
- pdf_upload.py: Module for uploading PDFs, extracting text, and interacting with it using the chatbot interface.
- api_keys.json: JSON file to store YouTube API keys.
- history.json: JSON file to store the history of fetched comments.
- comments.json: JSON file to store comments data.
- pdf_data.json: JSON file to store PDF text data.
- chat_history.json: JSON file to store chat history for comments.
- pdf_chat_history.json: JSON file to store chat history for PDFs.
- README.md: This README file.

# Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or new features.

# License
This project is licensed under the MIT License.
