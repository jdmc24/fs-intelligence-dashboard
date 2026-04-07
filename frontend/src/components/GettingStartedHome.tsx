"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { API_BASE } from "@/lib/api";

/** Onboarding strip for Home: two workflows (earnings vs regulations), API context, and pointers to Compare. */
export function GettingStartedHome() {
  const [open, setOpen] = useState(true);
  const isLocalApi = useMemo(
    () => API_BASE.includes("127.0.0.1") || API_BASE.includes("localhost"),
    [],
  );

  return (
    <section
      className="surface-card border border-teal-200/80 bg-teal-50/50 dark:border-teal-900/50 dark:bg-teal-950/25"
      aria-label="Getting started"
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left sm:px-5"
      >
        <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Start here</span>
        <span className="text-xs font-medium text-teal-700 dark:text-teal-400">{open ? "Hide" : "Show"}</span>
      </button>
      {open ? (
        <div className="space-y-5 border-t border-teal-200/60 px-4 pb-4 pt-3 text-sm leading-relaxed text-zinc-700 dark:border-teal-900/40 dark:text-zinc-300 sm:px-5 sm:pb-5">
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            This app has two separate flows: <strong className="font-medium text-zinc-700 dark:text-zinc-200">earnings</strong>{" "}
            (calls + AI) and <strong className="font-medium text-zinc-700 dark:text-zinc-200">regulations</strong> (Federal
            Register + profiles). Pick one to begin; you can use both later.
          </p>

          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">API connection</p>
            <p className="mt-1 text-sm">
              Requests go to{" "}
              <code className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-xs dark:bg-zinc-900">{API_BASE}</code>
              {isLocalApi ? (
                <>
                  {" "}
                  (local). For production, set <code className="font-mono text-xs">NEXT_PUBLIC_BACKEND_URL</code> to your
                  Railway URL in Vercel (and in <code className="font-mono text-xs">frontend/.env.local</code> for local dev),
                  then redeploy / restart <code className="font-mono text-xs">npm run dev</code>.
                </>
              ) : (
                <> — deployed backend.</>
              )}
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-zinc-200/90 bg-white/80 p-4 dark:border-zinc-800 dark:bg-zinc-950/40">
              <p className="text-xs font-semibold uppercase tracking-wide text-teal-800 dark:text-teal-300">
                Earnings (this page)
              </p>
              <ol className="mt-2 list-decimal space-y-1.5 pl-4 text-sm">
                <li>
                  <strong className="font-medium text-zinc-800 dark:text-zinc-100">Fetch</strong> a ticker/quarter below (
                  or <span className="whitespace-nowrap">Load sample transcript</span>).
                </li>
                <li>
                  Open the transcript → <strong className="font-medium text-zinc-800 dark:text-zinc-100">Analyze with Claude</strong>{" "}
                  until status is <span className="font-mono text-xs">analyzed</span>.
                </li>
                <li>
                  <Link href="/compare" className="font-medium text-teal-700 underline decoration-teal-500/40 underline-offset-2 hover:text-teal-600 dark:text-teal-400">
                    Compare
                  </Link>
                  : timeline + quarter-over-quarter diff need <strong className="font-medium">two or more analyzed</strong>{" "}
                  quarters for the same ticker.
                </li>
              </ol>
            </div>

            <div className="rounded-xl border border-zinc-200/90 bg-white/80 p-4 dark:border-zinc-800 dark:bg-zinc-950/40">
              <p className="text-xs font-semibold uppercase tracking-wide text-teal-800 dark:text-teal-300">
                Regulations
              </p>
              <ol className="mt-2 list-decimal space-y-1.5 pl-4 text-sm">
                <li>
                  <Link href="/regulations" className="font-medium text-teal-700 underline decoration-teal-500/40 underline-offset-2 hover:text-teal-600 dark:text-teal-400">
                    Regulations
                  </Link>
                  : <strong className="font-medium text-zinc-800 dark:text-zinc-100">Fetch FR</strong> (ingest recent Federal
                  Register docs).
                </li>
                <li>
                  <strong className="font-medium text-zinc-800 dark:text-zinc-100">Run AI enrich</strong> (summaries /
                  severity / tags; needs Anthropic on the server).
                </li>
                <li>
                  Add a <strong className="font-medium text-zinc-800 dark:text-zinc-100">company profile</strong> so ticker
                  matching can surface relevant rules.
                </li>
              </ol>
            </div>
          </div>

          <div className="rounded-lg border border-amber-200/80 bg-amber-50/90 px-3 py-2 text-xs text-amber-950 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-100/95">
            <strong className="font-medium">First time on Home?</strong> Use the form below in order: choose ticker &amp;
            quarter → <span className="font-medium">Fetch from EarningsCall</span> → open the row from Recent earnings → run
            analysis. Regulatory cards on this page fill in after the Regulations flow.
          </div>
        </div>
      ) : null}
    </section>
  );
}
