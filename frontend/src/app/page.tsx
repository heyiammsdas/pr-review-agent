"use client";

import React, { useState, useEffect } from 'react';
import { submitReview, getReviewStatus, ReviewResult } from '@/lib/api';
import ReviewSummary from '@/components/ReviewSummary';

export default function Dashboard() {
  const [repository, setRepository] = useState('');
  const [prNumber, setPrNumber] = useState('');
  
  const [status, setStatus] = useState<'idle' | 'submitting' | 'queued' | 'processing' | 'completed' | 'failed'>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Polling effect
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const pollStatus = async () => {
      if (!jobId) return;
      try {
        const data = await getReviewStatus(jobId);
        
        if (data.status === 'completed') {
          setStatus('completed');
          setResult(data.result);
        } else if (data.status === 'failed') {
          setStatus('failed');
          setError(data.error || 'The review job failed internally.');
        } else {
          setStatus(data.status as 'queued' | 'processing');
          timeoutId = setTimeout(pollStatus, 3000);
        }
      } catch (err: any) {
        setStatus('failed');
        setError(err.message || 'Failed to poll status.');
      }
    };

    if (jobId && (status === 'queued' || status === 'processing')) {
      timeoutId = setTimeout(pollStatus, 2000);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [jobId, status]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repository.trim() || !prNumber.trim()) return;

    setError(null);
    setResult(null);
    setJobId(null);
    setStatus('submitting');

    try {
      const data = await submitReview(repository.trim(), parseInt(prNumber.trim(), 10));
      setJobId(data.job_id);
      setStatus('queued');
    } catch (err: any) {
      setStatus('failed');
      setError(err.message || 'Error communicating with backend.');
    }
  };

  const isWorking = status === 'submitting' || status === 'queued' || status === 'processing';

  return (
    <main className="relative min-h-screen w-full flex flex-col items-center justify-center p-4 sm:p-6 overflow-x-hidden bg-[#07080e]">
      {/* Ambient background glow matching the screenshot */}
      <div 
        className="pointer-events-none absolute inset-0 flex items-center justify-center"
        aria-hidden="true"
      >
        <div 
          className="w-[700px] h-[550px] sm:w-[900px] sm:h-[650px] rounded-full blur-[110px] opacity-40"
          style={{
            background: 'radial-gradient(circle, rgba(67, 56, 170, 0.7) 0%, rgba(30, 27, 75, 0.4) 45%, rgba(7, 8, 14, 0) 75%)'
          }}
        />
      </div>

      <div className="relative z-10 w-full max-w-xl flex flex-col items-center my-auto py-12">
        {/* Title */}
        <h1 className="text-3xl sm:text-4xl font-normal tracking-tight text-white/95 mb-8 text-center select-none">
          PR Review Agent
        </h1>

        {/* Input Card Container */}
        <div className="w-full max-w-[460px] bg-[#17181e]/90 backdrop-blur-md border border-[#2b2e39] rounded-[22px] p-5 sm:p-6 shadow-[0_20px_50px_rgba(0,0,0,0.65)]">
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <div>
              <input
                id="repo"
                type="text"
                required
                placeholder="github_username/repo"
                disabled={isWorking}
                className="w-full bg-[#1e2028] text-white placeholder-[#5a6072] text-[15px] px-4 py-3 rounded-xl border border-[#2f3340] focus:border-[#6355d8] focus:ring-1 focus:ring-[#6355d8]/50 outline-none transition-all disabled:opacity-50"
                value={repository}
                onChange={(e) => setRepository(e.target.value)}
              />
            </div>

            <div>
              <input
                id="pr"
                type="number"
                required
                min="1"
                placeholder="PR number"
                disabled={isWorking}
                className="w-full bg-[#1e2028] text-white placeholder-[#5a6072] text-[15px] px-4 py-3 rounded-xl border border-[#2f3340] focus:border-[#6355d8] focus:ring-1 focus:ring-[#6355d8]/50 outline-none transition-all disabled:opacity-50"
                value={prNumber}
                onChange={(e) => setPrNumber(e.target.value)}
              />
            </div>

            {/* Action Button - bottom right */}
            <div className="flex justify-end pt-1">
              <button
                type="submit"
                disabled={isWorking || !repository.trim() || !prNumber.trim()}
                className="bg-[#5e3be4] hover:bg-[#6c48f2] active:bg-[#5233c9] text-white text-[15px] font-medium px-6 py-2 rounded-full shadow-[0_4px_14px_rgba(94,59,228,0.4)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 flex items-center gap-2 cursor-pointer"
              >
                {isWorking && (
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                )}
                {status === 'submitting' ? 'Starting...' : isWorking ? 'Reviewing...' : 'Start'}
              </button>
            </div>
          </form>
        </div>

        {/* Status / In Progress Indicator */}
        {isWorking && (
          <div className="w-full max-w-[460px] mt-6 bg-[#17181e]/80 border border-[#2b2e39] rounded-2xl p-4 text-center flex flex-col items-center justify-center animate-fadeIn backdrop-blur-sm">
            <div className="flex items-center gap-2.5 text-[#a5b4fc] text-sm font-medium mb-1">
              <div className="w-2 h-2 rounded-full bg-[#6366f1] animate-ping" />
              <span>{status === 'queued' ? 'Review Queued in Redis' : 'AI Multi-Agent Review in Progress'}</span>
            </div>
            <p className="text-[#7c8397] text-xs max-w-sm">
              Analyzing pull request diffs, gathering RAG repository context, and running Security, Quality, and Testing agents.
            </p>
          </div>
        )}

        {/* Error Notification */}
        {error && (
          <div className="w-full max-w-[460px] mt-6 bg-red-950/40 border border-red-800/50 text-red-200 p-4 rounded-2xl text-sm backdrop-blur-sm">
            <div className="font-medium text-red-300 mb-0.5 flex items-center gap-1.5">
              <span>⚠️</span> Review Failed
            </div>
            <p className="text-red-300/80 text-xs">{error}</p>
          </div>
        )}

        {/* Review Results */}
        {status === 'completed' && result && (
          <div className="w-full max-w-4xl mt-10">
            <ReviewSummary result={result} />
          </div>
        )}
      </div>
    </main>
  );
}
