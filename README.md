# Solidity to Clarity Code Converter

A web application that converts Solidity NFT smart contracts to Clarity language using AI powered by Groq API.

## Project Structure

```
solidity-to-clarity-converter/
├── frontend/               # React frontend
│   ├── public/             # Public assets
│   └── src/                # React source code
│       ├── components/     # React components
│       └── ...
└── backend/                # Python Flask backend
    ├── app.py              # Main Flask application
    ├── requirements.txt    # Python dependencies
    └── .env.example        # Environment variables example
```

## Features

- Convert Solidity NFT smart contracts to Clarity language
- Interactive web interface with code syntax highlighting
- Powered by Groq AI for accurate code conversion

## Prerequisites

- Node.js and npm for frontend
- Python 3.8+ for backend
- Groq API key

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file and add your Groq API key:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to include your actual Groq API key.

6. Start the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Paste your Solidity NFT smart contract code in the left panel.
2. Click the "Convert to Clarity" button.
3. View the converted Clarity code in the right panel.

## License

MIT
