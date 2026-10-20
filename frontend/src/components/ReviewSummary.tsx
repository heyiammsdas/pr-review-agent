import React from 'react';
import { ReviewResult } from '@/lib/api';
import ReviewStats from './ReviewStats';
import FindingCard from './FindingCard';

export default function ReviewSummary({ result }: { result: ReviewResult }) {
  if (!result) return null;

  const security = result.issues.filter(i => i.category.toLowerCase() === 'security');
  const quality = result.issues.filter(i => i.category.toLowerCase() === 'code_quality');
  const testing = result.issues.filter(i => i.category.toLowerCase() === 'testing');
  
  // Any others
  const others = result.issues.filter(i => !['security', 'code_quality', 'testing'].includes(i.category.toLowerCase()));

  return (
    <div className="flex flex-col gap-6">
      <div className="bg-[#17181e]/90 border border-[#2b2e39] rounded-2xl p-6 backdrop-blur-md shadow-xl">
        <h2 className="text-xl font-semibold mb-2 text-white">Review Summary</h2>
        <p className="text-[#a0a6b8] whitespace-pre-wrap leading-relaxed text-sm">{result.summary}</p>
      </div>

      <ReviewStats stats={result.statistics} />

      {result.issues.length === 0 ? (
        <div className="bg-emerald-950/40 text-emerald-300 p-6 rounded-2xl text-center border border-emerald-800/40">
          <span className="text-2xl block mb-2">🎉</span>
          No issues found! The PR looks great.
        </div>
      ) : (
        <div className="flex flex-col gap-8">
          {security.length > 0 && (
            <section>
              <h3 className="text-base font-semibold text-rose-400 mb-3 border-b border-[#2b2e39] pb-2 flex items-center gap-2">
                <span>🛡️</span> Security Issues ({security.length})
              </h3>
              <div className="grid gap-3">
                {security.map((issue, idx) => <FindingCard key={idx} issue={issue} />)}
              </div>
            </section>
          )}

          {quality.length > 0 && (
            <section>
              <h3 className="text-base font-semibold text-amber-400 mb-3 border-b border-[#2b2e39] pb-2 flex items-center gap-2">
                <span>✨</span> Code Quality Issues ({quality.length})
              </h3>
              <div className="grid gap-3">
                {quality.map((issue, idx) => <FindingCard key={idx} issue={issue} />)}
              </div>
            </section>
          )}

          {testing.length > 0 && (
            <section>
              <h3 className="text-base font-semibold text-emerald-400 mb-3 border-b border-[#2b2e39] pb-2 flex items-center gap-2">
                <span>🧪</span> Testing Issues ({testing.length})
              </h3>
              <div className="grid gap-3">
                {testing.map((issue, idx) => <FindingCard key={idx} issue={issue} />)}
              </div>
            </section>
          )}

          {others.length > 0 && (
            <section>
              <h3 className="text-base font-semibold text-violet-400 mb-3 border-b border-[#2b2e39] pb-2 flex items-center gap-2">
                <span>📌</span> Other Findings ({others.length})
              </h3>
              <div className="grid gap-3">
                {others.map((issue, idx) => <FindingCard key={idx} issue={issue} />)}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
