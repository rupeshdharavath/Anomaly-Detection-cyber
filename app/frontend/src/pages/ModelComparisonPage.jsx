import React, { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import { modelsAPI } from '../api/client';

const fallbackModels = [
  { name: 'Baseline', precision: 0.92, recall: 0.88, f1: 0.90, auc: 0.95 },
  { name: 'LSTM', precision: 0.88, recall: 0.93, f1: 0.90, auc: 0.94 },
  { name: 'Ensemble', precision: 0.94, recall: 0.91, f1: 0.92, auc: 0.96 },
];

const ModelComparisonPage = () => {
  const [models, setModels] = useState(fallbackModels);
  const [dataSource, setDataSource] = useState('example');

  useEffect(() => {
    let mounted = true;
    const fetchPerformance = async () => {
      try {
        const res = await modelsAPI.getPerformance();
        const payload = res.data;
        // Expected shape: { data: { baseline: {...}, lstm: {...}, ensemble: {...} } }
        if (payload && payload.data && mounted) {
          const { baseline, lstm, ensemble } = payload.data;
          const normalize = (m) => ({
            precision: m?.precision ?? m?.Precision ?? 0,
            recall: m?.recall ?? m?.Recall ?? 0,
            f1: m?.f1 ?? m?.f1_score ?? m?.F1 ?? 0,
            auc: m?.auc ?? m?.auc_roc ?? m?.AUC ?? 0,
            accuracy: m?.accuracy ?? 0,
            samples_evaluated: m?.samples_evaluated ?? m?.samples ?? 0,
          });

          if (baseline && lstm && ensemble) {
            setModels([
              { name: 'Baseline', ...normalize(baseline) },
              { name: 'LSTM', ...normalize(lstm) },
              { name: 'Ensemble', ...normalize(ensemble) },
            ]);
            setDataSource('real');
            return;
          }
        }
        setDataSource('example');
      } catch (err) {
        console.warn('Model performance API unavailable, using example metrics', err);
        setDataSource('example');
      }
    };
    fetchPerformance();
    return () => { mounted = false; };
  }, []);

  return (
    <div className="min-h-screen bg-transparent text-slate-100 p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Model Comparison</h1>
          <p className="text-slate-300 mt-2">Performance metrics for the baseline, LSTM, and ensemble models.</p>
          <p className={`mt-2 text-sm ${dataSource === 'real' ? 'text-green-400' : 'text-yellow-400'}`}>
            {dataSource === 'real' ? '✓ Metrics from held-out test set' : '⚠ Example metrics (API unavailable)'}
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {models.map((model) => (
            <div key={model.name} className="rounded-3xl bg-slate-800/70 border border-slate-700 p-6">
              <h2 className="text-xl font-semibold text-white">{model.name}</h2>
              <div className="mt-5 space-y-4 text-slate-200">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-slate-400">Precision</span>
                  <span>{(model.precision * 100).toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span className="text-slate-400">Recall</span>
                  <span>{(model.recall * 100).toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span className="text-slate-400">F1 score</span>
                  <span>{(model.f1 * 100).toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span className="text-slate-400">AUC</span>
                  <span>{(model.auc * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ModelComparisonPage;
