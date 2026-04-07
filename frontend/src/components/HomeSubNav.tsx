"use client";

/** Sticky in-page nav on Home: jump to earnings vs regulations bands. */
export function HomeSubNav() {
  return (
    <nav
      className="sticky top-14 z-40 -mx-4 mb-6 flex gap-1 rounded-xl border border-zinc-200/90 bg-white/95 p-1 shadow-sm backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/95 sm:-mx-0 sm:mb-8"
      aria-label="On this page"
    >
      <a
        href="#section-earnings"
        className="min-h-11 flex-1 rounded-lg px-4 py-3 text-center text-sm font-medium text-zinc-700 transition hover:bg-zinc-100 hover:text-zinc-900 active:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white dark:active:bg-zinc-700"
      >
        Earnings
      </a>
      <a
        href="#section-regulations"
        className="min-h-11 flex-1 rounded-lg px-4 py-3 text-center text-sm font-medium text-zinc-700 transition hover:bg-zinc-100 hover:text-zinc-900 active:bg-zinc-200 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white dark:active:bg-zinc-700"
      >
        Regulations
      </a>
    </nav>
  );
}
