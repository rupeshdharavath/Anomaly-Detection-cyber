import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './layout/Sidebar';
import Dashboard from './pages/Dashboard';
import AlertsPage from './pages/AlertsPage';
import AlertDetailPage from './pages/AlertDetailPage';
import SimulatePage from './pages/SimulatePage';
import ModelComparisonPage from './pages/ModelComparisonPage';
import EntityHistoryPage from './pages/EntityHistoryPage';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
        <div className="min-h-screen px-6 lg:pl-72">
          <div className="min-h-screen mx-auto max-w-7xl">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/alerts/:alertId" element={<AlertDetailPage />} />
              <Route path="/simulate" element={<SimulatePage />} />
              <Route path="/models" element={<ModelComparisonPage />} />
              <Route path="/entity/:entityId" element={<EntityHistoryPage />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
