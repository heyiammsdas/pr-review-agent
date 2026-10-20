import React from 'react';

interface StatsProps {
  stats: {
    total: number;
    security: number;
    code_quality: number;
    testing: number;
  };
}

export default function ReviewStats({ stats }: StatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="bg-[#17181e]/90 border border-[#2b2e39] rounded-2xl p-4 text-center">
        <div className="text-[#7c8397] text-xs font-semibold uppercase tracking-wider">Total</div>
        <div className="text-2xl sm:text-3xl font-bold text-white mt-1">{stats.total}</div>
      </div>
      <div className="bg-rose-950/20 border border-rose-900/30 rounded-2xl p-4 text-center">
        <div className="text-rose-400 text-xs font-semibold uppercase tracking-wider">Security</div>
        <div className="text-2xl sm:text-3xl font-bold text-rose-300 mt-1">{stats.security}</div>
      </div>
      <div className="bg-amber-950/20 border border-amber-900/30 rounded-2xl p-4 text-center">
        <div className="text-amber-400 text-xs font-semibold uppercase tracking-wider">Quality</div>
        <div className="text-2xl sm:text-3xl font-bold text-amber-300 mt-1">{stats.code_quality}</div>
      </div>
      <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-2xl p-4 text-center">
        <div className="text-emerald-400 text-xs font-semibold uppercase tracking-wider">Testing</div>
        <div className="text-2xl sm:text-3xl font-bold text-emerald-300 mt-1">{stats.testing}</div>
      </div>
    </div>
  );
}
