"use client";

import type { Transcript } from "@/lib/api";

function StepRow({
  label,
  description,
  done,
  active,
}: {
  label: string;
  description: string;
  done: boolean;
  active: boolean;
}) {
  return (
    <li className="flex gap-3">
      <span
        className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
          done
            ? "bg-teal-600 text-white dark:bg-teal-500"
            : active
              ? "border-2 border-teal-500 bg-teal-50 text-teal-800 dark:bg-teal-950/50 dark:text-teal-200"
              : "border border-zinc-300 bg-zinc-50 text-zinc-500 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-400"
        }`}
        aria-hidden
      >
        {done ? "✓" : ""}
      </span>
      <div>
        <p
          className={`text-sm font-medium ${active || done ? "text-zinc-900 dark:text-zinc-100" : "text-zinc-500 dark:text-zinc-400"}`}
        >
          {label}
        </p>
        <p className="text-xs text-zinc-500 dark:text-zinc-500">{description}</p>
      </div>
    </li>
  );
}

/** Linear progress for fetch → load → analyze on Home. */
export function FetchProgressSteps({
  busy,
  transcriptId,
  transcript,
}: {
  busy: boolean;
  transcriptId: string | null;
  transcript: Transcript | null;
}) {
  const step1Done = Boolean(transcriptId && transcript);
  const processing = transcript?.status === "processing";
  const hasReadable =
    Boolean(transcript?.sections?.length) ||
    Boolean(transcript?.raw_text && transcript.raw_text.length > 0);
  const step2Done = Boolean(transcript && !processing && hasReadable);
  const step3Done = transcript?.status === "analyzed";

  const step1Active =
    !step1Done && Boolean(busy || (transcriptId && !transcript));
  const step2Active = Boolean(transcript && processing);
  const step3Active = Boolean(transcript && !processing && hasReadable && !step3Done);

  return (
    <div
      className="rounded-xl border border-zinc-200/90 bg-zinc-50/80 px-3 py-3 dark:border-zinc-800 dark:bg-zinc-900/40 sm:px-4"
      aria-live="polite"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Progress</p>
      <ol className="mt-2 space-y-2.5">
        <StepRow
          label="1. Fetch transcript"
          description="Use Fetch from EarningsCall or load a sample."
          done={step1Done}
          active={step1Active}
        />
        <StepRow
          label="2. Transcript loaded"
          description={processing ? "Processing…" : "Text appears below when ready."}
          done={step2Done || step3Done}
          active={step2Active}
        />
        <StepRow
          label="3. Analyze with Claude"
          description="Run analysis, then use Compare with two analyzed quarters."
          done={step3Done}
          active={step3Active}
        />
      </ol>
    </div>
  );
}
