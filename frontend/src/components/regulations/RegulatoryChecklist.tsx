import type { RegulatoryPipelineStatus } from "@/lib/api";

type Props = {
  pipeline: RegulatoryPipelineStatus;
};

function Row({ done, label, hint }: { done: boolean; label: string; hint?: string }) {
  return (
    <li className="flex gap-2">
      <span className="mt-0.5 font-mono text-sm" aria-hidden>
        {done ? "✓" : "○"}
      </span>
      <span>
        <span className={done ? "text-zinc-800 dark:text-zinc-100" : "text-zinc-600 dark:text-zinc-400"}>{label}</span>
        {hint ? (
          <span className="mt-0.5 block text-xs text-zinc-500 dark:text-zinc-500">{hint}</span>
        ) : null}
      </span>
    </li>
  );
}

/** Three-step checklist: ingest → enrich queue → company profiles (drives ticker matching). */
export function RegulatoryChecklist({ pipeline }: Props) {
  const hasDocs = pipeline.reg_documents_count > 0;
  const ingestDone = hasDocs;

  const rawLeft = pipeline.raw_pending_count;
  const enrichDone = hasDocs && rawLeft === 0 && pipeline.enriched_count > 0;
  const enrichHint =
    !hasDocs
      ? "Use Fetch FR first."
      : rawLeft > 0
        ? `${rawLeft} document(s) still raw — click Run AI enrich (repeat until the queue is clear).`
        : pipeline.enriched_count === 0 && hasDocs
          ? "Queue is clear but nothing enriched yet — run Run AI enrich, or check error counts in the stats above."
          : undefined;

  const profileDone = pipeline.company_profiles_count > 0;
  const profileHint = profileDone ? undefined : "Save at least one profile below so tickers can match rules.";

  return (
    <div className="surface-card mt-6 border border-zinc-200/90 p-4 dark:border-zinc-800 sm:p-5">
      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">Regulations checklist</h2>
      <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
        Do these in order. Ticker matching stays &ldquo;not ready&rdquo; until you have enriched docs and saved profiles.
      </p>
      <ol className="mt-3 list-none space-y-2.5 text-sm">
        <Row done={ingestDone} label="Ingest Federal Register documents" hint={!ingestDone ? "Fetch FR (e.g. last 3 days)." : undefined} />
        <Row
          done={enrichDone}
          label="Clear the raw queue (AI enrichment)"
          hint={enrichHint}
        />
        <Row done={profileDone} label="Save a company profile" hint={profileHint} />
      </ol>
    </div>
  );
}
