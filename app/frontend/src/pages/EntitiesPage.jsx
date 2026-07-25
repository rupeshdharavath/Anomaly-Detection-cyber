import React, { useEffect, useState } from 'react';
import { Users, Smartphone, Search } from 'lucide-react';
import { useStore } from '../store/store';

const EntitiesPage = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [searchTerm, setSearchTerm] = useState('');
  const { fetchUsers, fetchDevices, searchEntities, entities, loading } = useStore();

  useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers(1);
    } else {
      fetchDevices(1);
    }
  }, [activeTab]);

  const handleSearch = async (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (term.length > 1) {
      try {
        await searchEntities(term, activeTab === 'users' ? 'user' : 'device');
      } catch (err) {
        console.error('Error searching:', err);
      }
    }
  };

  const displayData = activeTab === 'users' ? entities.users : entities.devices;

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <div className="p-6 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-white">Entities</h1>
            <p className="text-slate-300 mt-1">Users and devices in your network</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 border-b border-slate-700">
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-3 font-medium border-b-2 transition flex items-center gap-2 ${
                activeTab === 'users'
                  ? 'text-blue-400 border-blue-500'
                  : 'text-slate-400 border-transparent hover:text-slate-300'
              }`}
            >
              <Users size={20} />
              Users ({entities.users.length})
            </button>
            <button
              onClick={() => setActiveTab('devices')}
              className={`px-4 py-3 font-medium border-b-2 transition flex items-center gap-2 ${
                activeTab === 'devices'
                  ? 'text-blue-400 border-blue-500'
                  : 'text-slate-400 border-transparent hover:text-slate-300'
              }`}
            >
              <Smartphone size={20} />
              Devices ({entities.devices.length})
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 text-slate-400" size={20} />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchTerm}
              onChange={handleSearch}
              className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Entities Table */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg overflow-hidden">
            {loading ? (
              <div className="p-12 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-2"></div>
                <p className="text-slate-400">Loading {activeTab}...</p>
              </div>
            ) : displayData.length === 0 ? (
              <div className="p-12 text-center text-slate-400">
                No {activeTab} found
              </div>
            ) : (
              <div className="overflow-x-auto scrollbar-thin scrollbar-track-slate-800 scrollbar-thumb-slate-600">
                <table className="w-full text-sm">
                  <thead className="bg-slate-900/50 border-b border-slate-700/50">
                    <tr>
                      {activeTab === 'users' ? (
                        <>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Name</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">User ID</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Department</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Office</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Email</th>
                        </>
                      ) : (
                        <>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Device ID</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Type</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">OS</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">Browser</th>
                          <th className="px-4 py-3 text-left font-semibold text-slate-300">MAC Address</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {displayData.map((entity, idx) => (
                      <tr key={idx} className="hover:bg-slate-700/30 transition cursor-pointer">
                        {activeTab === 'users' ? (
                          <>
                            <td className="px-4 py-3 text-white">{entity.name || entity.user_id}</td>
                            <td className="px-4 py-3 text-slate-300">{entity.user_id}</td>
                            <td className="px-4 py-3 text-slate-300">{entity.department || '-'}</td>
                            <td className="px-4 py-3 text-slate-300">{entity.office || '-'}</td>
                            <td className="px-4 py-3 text-slate-300 text-xs">{entity.email || '-'}</td>
                          </>
                        ) : (
                          <>
                            <td className="px-4 py-3 text-white">{entity.device_id}</td>
                            <td className="px-4 py-3 text-slate-300">{entity.device_type}</td>
                            <td className="px-4 py-3 text-slate-300">{entity.operating_system}</td>
                            <td className="px-4 py-3 text-slate-300">{entity.browser}</td>
                            <td className="px-4 py-3 text-slate-300 text-xs font-mono">{entity.mac_address}</td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EntitiesPage;
