import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { useStore } from '../store/store';
import AlertDetail from '../components/AlertDetail';

const AlertDetailPage = () => {
  const { alertId } = useParams();
  const navigate = useNavigate();
  const { getAlertDetail, selectedAlert, loading, error } = useStore();
  const [hasLoaded, setHasLoaded] = useState(false);

  useEffect(() => {
    const loadAlert = async () => {
      if (!alertId) {
        return;
      }

      try {
        await getAlertDetail(alertId);
      } catch (err) {
        console.error('Error loading alert detail:', err);
      } finally {
        setHasLoaded(true);
      }
    };

    loadAlert();
  }, [alertId, getAlertDetail]);

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <div className="p-6 space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <button
              type="button"
              onClick={() => navigate('/alerts')}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-700 bg-slate-900/80 px-4 py-2 text-slate-200 transition hover:bg-slate-800"
            >
              <ArrowLeft size={18} />
              Back to alerts
            </button>
            <h1 className="mt-6 text-3xl font-bold text-white">Alert dashboard</h1>
            <p className="text-slate-400 mt-2 max-w-2xl">
              Full alert detail view with all available metadata, timelines, and investigation context.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-900/80 px-5 py-4 text-slate-300">
            <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Selected alert</p>
            <p className="mt-2 text-lg font-semibold text-white">{alertId || 'N/A'}</p>
          </div>
        </div>

        {!hasLoaded && (
          <div className="rounded-3xl border border-slate-700 bg-slate-900/80 p-12 text-center text-slate-400">
            <Loader2 className="mx-auto mb-4 h-8 w-8 animate-spin text-blue-400" />
            Loading alert details...
          </div>
        )}

        {hasLoaded && error && (
          <div className="rounded-3xl border border-rose-500/40 bg-rose-500/10 p-8 text-rose-200">
            <p className="text-lg font-semibold">Unable to load alert details.</p>
            <p className="mt-2 text-slate-300">{error}</p>
          </div>
        )}

        {hasLoaded && !error && selectedAlert && selectedAlert.alert && (
          <AlertDetail selectedAlert={selectedAlert} />
        )}

        {hasLoaded && !error && !selectedAlert && (
          <div className="rounded-3xl border border-slate-700 bg-slate-900/80 p-12 text-center text-slate-400">
            <p className="text-lg font-semibold text-white">Alert not found</p>
            <p className="mt-2">Please return to the alerts list and select a valid alert.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertDetailPage;
