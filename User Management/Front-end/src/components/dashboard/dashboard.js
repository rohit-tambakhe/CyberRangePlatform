import React, { useState, useEffect } from 'react';
import './Dashboard.css';

function Dashboard({ username }) {
  const [scenarios, setScenarios] = useState([]);

  useEffect(() => {
    // Assume fetchScenarios is a function that sends a request to your backend
    const data = fetchScenarios(username);
    setScenarios(data);
  }, [username]);

  return (
    <div className="dashboard-container">
      <h1>Welcome, {username}</h1>
      <ul className="scenario-list">
        {scenarios.map((scenario) => (
          <li key={scenario.id}>
            {scenario.name} - {scenario.description}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard;
