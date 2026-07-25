import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BarChart3,
  AlertTriangle,
  Activity,
  Settings,
  LogOut,
  Menu,
  X,
  Shield,
} from 'lucide-react';

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();

  const navItems = [
    { name: 'Overview', path: '/', icon: BarChart3 },
    { name: 'Alerts', path: '/alerts', icon: AlertTriangle },
    { name: 'Simulate', path: '/simulate', icon: Activity },
    { name: 'Models', path: '/models', icon: Shield },
  ];

  return (
    <>
      {/* Mobile Toggle */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed top-4 left-4 z-50 lg:hidden text-white"
      >
        {open ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-screen w-72 bg-slate-900/95 border-r border-slate-800 shadow-soc z-40 transform transition-transform lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6 border-b border-slate-800 bg-slate-950/95 backdrop-blur-xl flex items-center gap-3">
          <Shield size={32} className="text-blue-400" />
          <div>
            <h1 className="text-xl font-bold text-white">SOC</h1>
            <p className="text-xs text-slate-400">Anomaly Detection</p>
          </div>
        </div>

        <nav className="p-6 space-y-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-2xl transition ${
                  isActive
                    ? 'bg-blue-500/15 text-blue-300 border border-blue-500/30'
                    : 'text-slate-300 hover:bg-slate-800/80'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <button className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-slate-800/80 text-slate-300 hover:bg-slate-700 transition w-full">
            <LogOut size={20} />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </div>

      {/* Mobile Overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
