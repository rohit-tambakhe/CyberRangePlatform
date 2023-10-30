import React, { useState } from 'react';
import './Login.css';

function Login({ onLogin }) {
  const [tambakhe, settambakhe] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    // Assume authenticateUser is a function that sends a request to your backend
    const isAuthenticated = await authenticateUser(tambakhe, password);
    if (isAuthenticated) {
      onLogin(tambakhe);
    } else {
      alert('Authentication failed. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="tambakhe"
          value={tambakhe}
          onChange={(e) => settambakhe(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
