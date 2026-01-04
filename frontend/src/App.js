import './App.css';
import rvLogo from './rv-logo.jpg';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Function to start exporter
const startExporter = async (mode) => {
  try {
    await fetch(`http://localhost:5000/start_exporter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode })
    });
  } catch (err) {
    console.error("Exporter start failed:", err);
  }
};

// ------------ Real-Time Page Component ------------
function HomePage() {
  const [trafficStatus, setTrafficStatus] = useState('Loading...');

  useEffect(() => {
    startExporter('real');
  }, []);

  useEffect(() => {
    const fetchLatestPrediction = async () => {
  try {
    const res = await axios.get('http://localhost:5000/latest_prediction');
    if (res.data.traffic_type) {
      setTrafficStatus(res.data.traffic_type);
    }
  } catch (err) {
    console.error("Failed to fetch real-time prediction:", err);
    // Do not update trafficStatus on error
  }
};


    fetchLatestPrediction();
    const interval = setInterval(fetchLatestPrediction, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <div className="header">
        <div className="inst-name">
          <img src={rvLogo} className="rvLogo" alt="RV College of Engineering" />
          <p className='instName'>RV COLLEGE OF ENGINEERING</p>
        </div>

        <div className="userOptions" style={{ display: 'flex', gap: '50px', fontSize: '15px', fontWeight: '900', marginTop: '20px' }}>
          <Link to="/simulated" className="linkTop">SIMULATED</Link>
          <Link to="/" className="linkTop" style={{ backgroundColor: 'white', color: 'rgba(44,38,56,255)', borderStyle: 'solid', borderRadius: '10px' }}>REAL TIME</Link>
        </div>
      </div>

      <div style={{
        border: '2px solid #444',
        borderRadius: '8px',
        padding: '20px',
        width: '450px',
        margin: '20px auto',
        textAlign: 'center',
        backgroundColor: trafficStatus === 'Normal Traffic' ? 'lightgreen' : 'lightcoral',
        color: 'rgba(44,38,56,255)',
        fontSize: '20px',
        fontWeight: 'bold',
        marginBottom: '40px'
      }}>
        🚦 Traffic Status: {trafficStatus}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '20px',
        padding: '0 20px'
      }}>
        <iframe src="http://localhost:3000/d-solo/d4d04ff3-7b93-4a86-a5d0-cdc08900fc5d/nps-realtime?orgId=1&from=now-5m&to=now&refresh=1m&theme=light&panelId=3"
          width="100%" height="300" frameBorder="0" title="Panel 3" />
        <iframe src="http://localhost:3000/d-solo/d4d04ff3-7b93-4a86-a5d0-cdc08900fc5d/nps-realtime?orgId=1&from=now-5m&to=now&refresh=1m&theme=light&panelId=8"
          width="100%" height="300" frameBorder="0" title="Panel 8" />
        <iframe src="http://localhost:3000/d-solo/d4d04ff3-7b93-4a86-a5d0-cdc08900fc5d/nps-realtime?orgId=1&from=now-5m&to=now&refresh=1m&theme=light&panelId=6"
          width="100%" height="300" frameBorder="0" title="Panel 6" />
        <iframe src="http://localhost:3000/d-solo/d4d04ff3-7b93-4a86-a5d0-cdc08900fc5d/nps-realtime?orgId=1&from=now-5m&to=now&refresh=1m&theme=light&panelId=7"
          width="100%" height="300" frameBorder="0" title="Panel 7" />
      </div>
    </div>
  );
}

// ------------ Simulated Page Component ------------
function SimulatedPage() {
  const [trafficStatus, setTrafficStatus] = useState('Loading...');

  useEffect(() => {
    startExporter('simulated');
  }, []);

  useEffect(() => {
    const fetchLatestPrediction = async () => {
  try {
    const res = await axios.get('http://localhost:5000/latest_prediction-simulated');
    if (res.data.traffic_type) {
      setTrafficStatus(res.data.traffic_type);
    }
  } catch (err) {
    console.error("Failed to fetch simulated prediction:", err);
    // Do not update trafficStatus on error
  }
};

    fetchLatestPrediction();
    const interval = setInterval(fetchLatestPrediction, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <div className="header">
        <div className="inst-name">
          <img src={rvLogo} className="rvLogo" alt="RV College of Engineering" />
          <p className='instName'>RV COLLEGE OF ENGINEERING</p>
        </div>

        <div className="userOptions" style={{ display: 'flex', gap: '50px', fontSize: '15px', fontWeight: '900', marginTop: '20px' }}>
          <Link to="/simulated" className="linkTop" style={{ backgroundColor: 'white', color: 'rgba(44,38,56,255)', borderStyle: 'solid', borderRadius: '10px' }}>SIMULATED</Link>
          <Link to="/" className="linkTop">REAL TIME</Link>
        </div>
      </div>

      <div style={{
        border: '2px solid #444',
        borderRadius: '8px',
        padding: '20px',
        width: '450px',
        margin: '20px auto',
        textAlign: 'center',
        backgroundColor: trafficStatus === 'Normal Traffic' ? 'lightgreen' : 'lightcoral',
        color: 'rgba(44,38,56,255)',
        fontSize: '20px',
        fontWeight: 'bold',
        marginBottom: '40px'
      }}>
        🚦 Traffic Status: {trafficStatus}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '20px',
        padding: '0 20px'
      }}>
        <iframe src="http://localhost:3000/d-solo/e6339caf-a0b1-4614-9d5d-1e1d10d91369/new-dashboard?orgId=1&from=now-5m&to=now&refresh=30s&theme=light&panelId=4" width="100%" height="300" frameBorder="0"></iframe>
        <iframe src="http://localhost:3000/d-solo/e6339caf-a0b1-4614-9d5d-1e1d10d91369/new-dashboard?orgId=1&from=now-5m&to=now&refresh=30s&theme=light&panelId=1" width="100%" height="300" frameBorder="0"></iframe>
        <iframe src="http://localhost:3000/d-solo/e6339caf-a0b1-4614-9d5d-1e1d10d91369/new-dashboard?orgId=1&from=now-5m&to=now&refresh=30s&theme=light&panelId=2" width="100%" height="300" frameBorder="0"></iframe>
        <iframe src="http://localhost:3000/d-solo/e6339caf-a0b1-4614-9d5d-1e1d10d91369/new-dashboard?orgId=1&from=now-5m&to=now&refresh=30s&theme=light&panelId=3" width="100%" height="300" frameBorder="0"></iframe>
      </div>
    </div>
  );
}

// ------------ App Router ------------
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/simulated" element={<SimulatedPage />} />
      </Routes>
    </Router>
  );
}

export default App;
