import React from 'react';
import { ReviewIssue } from '@/lib/api';

const severityBadgeStyles: Record<string, string> = {
  critical: 'bg-rose-950/60 text-rose-300 border-rose-800/60',
  high: 'bg-red-950/50 text-red-300 border-red-800/50',
  medium: 'bg-amber-950/50 text-amber-300 border-amber-800/50',
  low: 'bg-sky-950/50 text-sky-300 border-sky-800/50',
};

export default function FindingCard({ issue }: { issue: ReviewIssue }) {
  const badgeClass = severityBadgeStyles[issue.severity.toLowerCase()] || 'bg-zinc-800 text-zinc-300 border-zinc-700';

  return (
    <div className="border border-[#2b2e39] rounded-2xl p-4 bg-[#17181e]/90 backdrop-blur-md shadow-sm flex flex-col gap-2.5">
      <div className="flex items-center justify-between">
        <span className="font-medium text-white/90 text-sm">
          {issue.category}
        </span>
        <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-semibold uppercase tracking-wider border ${badgeClass}`}>
          {issue.severity}
        </span>
      </div>
      
      <div className="text-xs font-mono text-[#a5b4fc] bg-[#1f212a] px-2.5 py-1 rounded-lg border border-[#2f3340] inline-block w-fit">
        {issue.file}{issue.line !== null ? `:${issue.line}` : ''} {issue.is_contextual && '(Contextual)'}
      </div>
      
      <h4 className="font-medium text-white text-sm mt-0.5">{issue.title}</h4>
      <p className="text-[#9ca3af] text-xs leading-relaxed">{issue.description}</p>
      
      <div className="mt-1 text-xs text-[#cbd5e1] bg-[#1e2029] border border-[#2b2e39] rounded-xl p-3">
        <strong className="text-[#a5b4fc]">Suggestion:</strong> {issue.suggestion}
      </div>
    </div>
  );
}
