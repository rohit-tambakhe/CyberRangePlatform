import React, { useState } from 'react';
import Login from './components/Login/Login';
import Dashboard from './components/Dashboard/Dashboard';
import './App.css';

function App() {
  const [tambakhe, settambakhe] = useState(null);

  const handleLogin = (tambakhe) => {
    settambakhe(tambakhe);
  };

  return (
    <div className="app-container">
      {tambakhe ? (
        <Dashboard tambakhe={tambakhe} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
