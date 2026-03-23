"use client";

import { motion } from "framer-motion";

type SignalTickerProps = {
  items: string[];
};

export function SignalTicker({ items }: SignalTickerProps) {
  const loopItems = [...items, ...items];

  return (
    <div className="overflow-hidden rounded-full border border-[var(--color-border)] bg-[rgba(255,255,255,0.62)] py-3 shadow-[0_20px_70px_-45px_rgba(22,20,18,0.28)]">
      <motion.div
        className="flex min-w-max items-center gap-4 px-4"
        animate={{ x: ["0%", "-50%"] }}
        transition={{ duration: 22, repeat: Infinity, ease: "linear" }}
      >
        {loopItems.map((item, index) => (
          <div
            key={`${item}-${index}`}
            className="flex items-center gap-4 rounded-full border border-[rgba(73,66,58,0.1)] bg-[rgba(245,241,234,0.8)] px-4 py-2"
          >
            <span className="h-2 w-2 rounded-full bg-[var(--color-accent)]" />
            <span className="text-xs tracking-[0.18em] text-[var(--color-muted)] uppercase md:text-sm">
              {item}
            </span>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
