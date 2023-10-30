// App.js
import React, { useState } from 'react';
import Login from './components/login/login';
import Dashboard from './components/Dashboard/Dashboard';
import Registration from './components/Registration/Registration'; // New component
import './App.css';

function App() {
  const [username, setUsername] = useState(null);

  const handleLogin = (newUsername) => {
    setUsername(newUsername);
  };

  return (
    <div className="app-container">
      {username ? (
        <Dashboard username={username} />
      ) : (
        <>
          <Login onLogin={handleLogin} />
          <Registration onRegister={handleLogin} /> {/* New component */}
        </>
      )}
    </div>
  );
}

export default App;
