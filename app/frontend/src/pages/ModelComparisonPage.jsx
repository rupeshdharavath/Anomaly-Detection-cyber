import React from 'react';
import StatCard from '../components/StatCard';

const ModelComparisonPage = () => {
  const models = [
    { name: 'Baseline', precision: 0.92, recall: 0.88, f1: 0.90, auc: 0.95 },
    { name: 'LSTM', precision: 0.88, recall: 0.93, f1: 0.90, auc: 0.94 },
    { name: 'Ensemble', precision: 0.94, recall: 0.91, f1: 0.92, auc: 0.96 },
  ];

  return (
    <div className="min-h-screen bg-transparent text-slate-100 p-6">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Model Comparison</h1>
          <p className="text-slate-300 mt-2">Performance metrics for the baseline, LSTM, and ensemble models.</p>
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
