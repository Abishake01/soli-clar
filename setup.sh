#!/bin/bash
echo "Setting up Solidity to Clarity Converter..."

echo "Creating Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "Python setup complete!"
echo ""
echo "Note: You need to create a .env file with your Groq API key."
echo "Copy the .env.example file to .env and add your key."
echo ""
deactivate
cd ..

echo "Setting up React frontend..."
cd frontend
echo "Installing npm dependencies..."
npm install
echo "Frontend setup complete!"
cd ..

echo ""
echo "Setup completed successfully!"
echo ""
echo "To start the backend: run ./start-backend.sh"
echo "To start the frontend: run ./start-frontend.sh"
echo ""
echo "Remember to add your Groq API key to backend/.env"
