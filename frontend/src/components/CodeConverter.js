import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeConverter.css';

// Base URL for API requests
const API_BASE_URL = 'http://localhost:5000';

const CodeConverter = () => {
  const [solidityCode, setSolidityCode] = useState('');
  const [clarityCode, setClarityCode] = useState('');
  const [versions, setVersions] = useState([]);
  const [selectedVersionIndex, setSelectedVersionIndex] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [copied, setCopied] = useState(false);
  const [deployResult, setDeployResult] = useState(null);
  const clarityCodeRef = useRef(null);

  // Check backend status on component mount
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/health`);
        if (response.status === 200) {
          setBackendStatus('connected');
        } else {
          setBackendStatus('error');
        }
      } catch (err) {
        console.error('Backend connection error:', err);
        setBackendStatus('error');
      }
    };

    checkBackendStatus();
  }, []);

  const handleCopyClick = () => {
    if (clarityCode) {
      navigator.clipboard.writeText(clarityCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!solidityCode.trim()) {
      setError('Please enter Solidity code to convert');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setClarityCode('');
    
    try {
      // Make direct API call to backend
      const response = await axios.post(`${API_BASE_URL}/api/convert`, { solidityCode });
      const output = response.data.clarityCode || '';
      setClarityCode(output);
      if (output) {
        const newVersion = { timestamp: Date.now(), clarityCode: output };
        setVersions((prev) => [newVersion, ...prev].slice(0, 10));
        setSelectedVersionIndex(0);
      }
    } catch (err) {
      console.error('Conversion error:', err);
      
      if (err.code === 'ERR_NETWORK') {
        setError('Network error: Unable to connect to the server. Please check if the backend server is running.');
      } else if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(`Server error: ${err.response.data.error || 'Unknown server error'}`);
      } else if (err.request) {
        // The request was made but no response was received
        setError('No response from server. Please check if the backend server is running.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(`Error: ${err.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestoreVersion = (index) => {
    setSelectedVersionIndex(index);
    setClarityCode(versions[index]?.clarityCode || '');
  };

  const handleDeploy = async () => {
    if (!clarityCode.trim()) return;
    setIsDeploying(true);
    setDeployResult(null);
    setError('');
    try {
      const response = await axios.post(`${API_BASE_URL}/api/deploy`, {
        clarityCode,
        contractName: 'converted-contract',
        network: 'testnet'
      });
      setDeployResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Deploy failed');
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <div className="converter-container">
      <div className="status-bar">
        <div className={`status-indicator ${
          backendStatus === 'checking' ? 'loading' : 
          backendStatus === 'connected' ? '' : 
          'error'
        }`}>
          {backendStatus === 'checking' ? 'Checking Backend...' : 
           backendStatus === 'connected' ? 'Backend Connected' : 
           'Backend Not Connected'}
        </div>
        <div className={`status-indicator ${isLoading ? 'loading' : error ? 'error' : ''}`}>
          {isLoading ? 'Processing...' : error ? 'Error' : 'Ready'}
        </div>
      </div>
      
      <div className="code-panels">
        <div className="code-panel">
          <h3>Solidity Code</h3>
          <textarea
            className="code-input"
            value={solidityCode}
            onChange={(e) => setSolidityCode(e.target.value)}
            placeholder="Paste your Solidity NFT smart contract code here..."
            disabled={isLoading}
          />
        </div>
        
        <div className="code-panel">
          <h3>Clarity Code</h3>
          {clarityCode ? (
            <>
              <div className="code-header">
                <button 
                  className="copy-button" 
                  onClick={handleCopyClick}
                  title="Copy to clipboard"
                >
                  {copied ? 'Copied!' : 'Copy'}
                </button>
                <button 
                  className="copy-button" 
                  onClick={handleDeploy}
                  disabled={isDeploying}
                  title="Deploy to Stacks (mock)"
                  style={{ marginLeft: '8px', backgroundColor: '#10b981' }}
                >
                  {isDeploying ? 'Deploying...' : 'Deploy'}
                </button>
              </div>
              <div className="code-container" ref={clarityCodeRef}>
                <SyntaxHighlighter
                  language="lisp" // Clarity is Lisp-like
                  style={vscDarkPlus}
                  className="code-output"
                  wrapLines={true}
                  showLineNumbers={true}
                  lineNumberStyle={{ minWidth: '2.25em', paddingRight: '1em' }}
                >
                  {clarityCode}
                </SyntaxHighlighter>
              </div>
              {deployResult && (
                <div className="status-bar" style={{ justifyContent: 'flex-start', marginTop: '8px' }}>
                  <div className="status-indicator">Deployed: {deployResult.contractId}</div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-output">
              Converted Clarity code will appear here
            </div>
          )}
        </div>
      </div>

      {versions.length > 0 && (
        <div>
          <h4 style={{ textAlign: 'left' }}>Versions</h4>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {versions.map((v, idx) => (
              <button
                key={v.timestamp}
                className="copy-button"
                onClick={() => handleRestoreVersion(idx)}
                style={{ backgroundColor: selectedVersionIndex === idx ? '#6366f1' : '#4b5563' }}
              >
                {new Date(v.timestamp).toLocaleTimeString()}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {error && <div className="error-message">{error}</div>}
      
      <button
        className="convert-button"
        onClick={handleSubmit}
        disabled={isLoading || !solidityCode.trim()}
      >
        {isLoading ? 'Converting...' : 'Convert to Clarity'}
      </button>
    </div>
  );
};

export default CodeConverter;
