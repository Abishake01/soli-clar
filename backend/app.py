from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import requests
import json
import logging
from dotenv import load_dotenv
import uuid
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Helper function to add CORS headers
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Get Groq API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment variables")

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/api/convert', methods=['POST', 'OPTIONS'])
def convert_code():
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response())
        
    if not GROQ_API_KEY:
        response = make_response(jsonify({"error": "Groq API key is not configured"}), 500)
        return add_cors_headers(response)
    
    data = request.get_json()
    solidity_code = data.get('solidityCode')
    
    if not solidity_code:
        response = make_response(jsonify({"error": "No Solidity code provided"}), 400)
        return add_cors_headers(response)
    
    try:
        # Prepare prompt for Groq API
        prompt = f"""
Convert the following Solidity NFT smart contract code to Clarity language.
Focus on preserving functionality while utilizing Clarity's features and patterns.
Ensure all NFT-related functionality is properly implemented in Clarity.

IMPORTANT: Return ONLY the raw Clarity code without any markdown formatting, explanations, or introductory text.
Do not include ```clarity markers, do not start with "Here is the code:", and do not add any explanations.
Just return the Clarity code directly.

Solidity code:
```solidity
{solidity_code}
```
"""
        
        # Call Groq API
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",  # Using Llama 3 8B model which is available on Groq
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert smart contract developer who specializes in converting Solidity code to Clarity language. Your responses should contain ONLY the raw Clarity code without any markdown formatting, explanations, or introductory text. Do not use ```clarity markers, do not start with 'Here is the code:', and do not add any explanations. Just return the Clarity code directly."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        # Log the request details for debugging
        logger.info(f"Sending request to Groq API with model: {payload['model']}")
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        
        # Log response status for debugging
        logger.info(f"Groq API response status code: {response.status_code}")
        
        # Log error response if any
        if response.status_code != 200:
            logger.error(f"Groq API error response: {response.text}")
            
        response.raise_for_status()
        
        result = response.json()
        clarity_code = result['choices'][0]['message']['content'].strip()
        
        # Log the original response for debugging
        logger.info(f"Original AI response: {clarity_code[:100]}...")
        
        # Process the clarity code to remove markdown formatting
        # Remove "Here is the converted Clarity code:" and similar introductory text
        common_intros = [
            "Here is the converted Clarity code:",
            "Here's the converted Clarity code:",
            "The converted Clarity code is:",
            "Converted Clarity code:",
            "Here is the Clarity code:",
            "Here's the Clarity code:"
        ]
        
        for intro in common_intros:
            if intro.lower() in clarity_code.lower():
                # Split by the intro and take everything after it
                parts = clarity_code.split(intro, 1)
                if len(parts) > 1:
                    clarity_code = parts[1].strip()
        
        # Remove markdown code block formatting
        if "```" in clarity_code:
            # Extract content between code blocks or remove code block markers
            lines = clarity_code.split("\n")
            filtered_lines = []
            inside_code_block = False
            
            for line in lines:
                line_lower = line.lower()
                if line_lower.startswith("```clarity") or line_lower.startswith("```lisp") or line_lower == "```":
                    if not inside_code_block:
                        inside_code_block = True
                    else:
                        inside_code_block = False
                    continue
                
                # Only include lines if they're inside a code block or if we haven't found any code blocks yet
                if inside_code_block or "```" not in clarity_code:
                    filtered_lines.append(line)
            
            clarity_code = "\n".join(filtered_lines)
        
        logger.info(f"Processed clarity code: {clarity_code[:100]}...")
        
        response = make_response(jsonify({"clarityCode": clarity_code}))
        return add_cors_headers(response)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        error_message = f"Failed to communicate with Groq API: {str(e)}"
        response = make_response(jsonify({"error": error_message}), 500)
        return add_cors_headers(response)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        response = make_response(jsonify({"error": "Failed to parse response from Groq API"}), 500)
        return add_cors_headers(response)
    except KeyError as e:
        logger.error(f"KeyError in API response: {str(e)}")
        response = make_response(jsonify({"error": "Unexpected response format from Groq API"}), 500)
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        response = make_response(jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500)
        return add_cors_headers(response)

@app.route('/api/explain', methods=['POST', 'OPTIONS'])
def explain_code():
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response())

    if not GROQ_API_KEY:
        response = make_response(jsonify({"error": "Groq API key is not configured"}), 500)
        return add_cors_headers(response)

    data = request.get_json()
    clarity_code = data.get('clarityCode')

    if not clarity_code:
        response = make_response(jsonify({"error": "No Clarity code provided"}), 400)
        return add_cors_headers(response)

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""
You are an expert Clarity developer and teacher. Explain the following Clarity smart contract to a developer who knows Solidity. Cover:
- What the contract does at a high level
- Key differences versus a typical Solidity approach
- Any important security or clarity-specific concerns
- How to deploy and interact using Stacks CLI

Return a concise explanation with short sections and bullet points where helpful.

Clarity code:
```
{clarity_code}
```
"""

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a senior Clarity engineer and educator."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1200
        }

        logger.info("Sending explain request to Groq API")
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        logger.info(f"Groq API response status code (explain): {response.status_code}")
        response.raise_for_status()

        result = response.json()
        explanation = result['choices'][0]['message']['content'].strip()

        res = make_response(jsonify({"explanation": explanation}))
        return add_cors_headers(res)
    except Exception as e:
        logger.error(f"Explain endpoint error: {str(e)}")
        res = make_response(jsonify({"error": f"Failed to generate explanation: {str(e)}"}), 500)
        return add_cors_headers(res)

@app.route('/api/deploy', methods=['POST', 'OPTIONS'])
def deploy_contract():
    """Mock deployment endpoint. In a real implementation, integrate with Stacks transactions.
    Accepts: { clarityCode: string, contractName?: string, network?: 'testnet'|'mainnet' }
    Returns: { txId, contractAddress, contractId }
    """
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response())

    data = request.get_json() or {}
    clarity_code = data.get('clarityCode')
    contract_name = (data.get('contractName') or 'converted-contract').strip()
    network = (data.get('network') or 'testnet').lower()

    if not clarity_code:
        response = make_response(jsonify({"error": "No Clarity code provided"}), 400)
        return add_cors_headers(response)

    # Simulate processing time
    time.sleep(0.3)

    # Create deterministic-ish mock identifiers
    tx_id = str(uuid.uuid4()).replace('-', '')
    mock_address = 'ST' + tx_id[:38]  # Stacks addresses start with ST on testnet/mainnet
    contract_id = f"{mock_address}.{contract_name}"

    logger.info(f"Mock deployed contract {contract_id} on {network}")

    res = make_response(jsonify({
        "txId": tx_id,
        "contractAddress": mock_address,
        "contractId": contract_id,
        "network": network
    }))
    return add_cors_headers(res)

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response())
    
    response = make_response(jsonify({"status": "healthy"}))
    return add_cors_headers(response)

@app.route('/api/test-groq', methods=['GET', 'OPTIONS'])
def test_groq():
    """Test the connection to the Groq API."""
    if not GROQ_API_KEY:
        return jsonify({"error": "Groq API key is not configured"}), 500
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Simple test request
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Please respond with 'Groq API connection successful!'"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return jsonify({
            "status": "success",
            "message": "Groq API connection successful",
            "model": payload["model"],
            "response": result
        })
    except Exception as e:
        logger.error(f"Groq API test error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
