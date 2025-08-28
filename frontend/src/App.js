import React from 'react';
import './App.css';
import CodeConverter from './components/CodeConverter';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Solidity to Clarity Code Converter</h1>
        <p>Convert your Solidity smart contracts to Clarity language</p>
      </header>
      <main>
        <CodeConverter />
      </main>
      
    </div>
  );
}

export default App;
