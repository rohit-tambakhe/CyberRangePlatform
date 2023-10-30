import React, { useState } from 'react';
import Login from './components/Login/Login';
import Dashboard from './components/Dashboard/Dashboard';
import './App.css';

function App() {
  const [username, setusername] = useState(null);

  const handleLogin = (username) => {
    setusername(username);
  };

  return (
    <div className="app-container">
      {username ? (
        <Dashboard username={username} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
