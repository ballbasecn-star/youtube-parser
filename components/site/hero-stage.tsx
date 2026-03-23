"use client";

import { useMemo } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

type HeroStageProps = {
  name: string;
};

export function HeroStage({ name }: HeroStageProps) {
  const pointerX = useMotionValue(0);
  const pointerY = useMotionValue(0);

  const springX = useSpring(pointerX, { stiffness: 120, damping: 18, mass: 0.6 });
  const springY = useSpring(pointerY, { stiffness: 120, damping: 18, mass: 0.6 });

  const rotateY = useTransform(springX, [-0.5, 0.5], [-4, 4]);
  const rotateX = useTransform(springY, [-0.5, 0.5], [3.5, -3.5]);
  const translateX = useTransform(springX, [-0.5, 0.5], [-8, 8]);
  const translateY = useTransform(springY, [-0.5, 0.5], [-6, 6]);

  const badges = useMemo(
    () => [
      { label: "LIVE SYSTEM", className: "left-5 top-5 md:left-7 md:top-7", delay: 0 },
      { label: "SITE / MVP", className: "right-5 top-7 md:right-7 md:top-10", delay: 0.4 },
      { label: "AI PRODUCT PROTOTYPE", className: "left-5 bottom-7 md:left-7 md:bottom-8", delay: 0.8 }
    ],
    []
  );

  return (
    <div className="relative min-h-[60dvh] md:min-h-[82dvh] [perspective:1600px]">
      <motion.div
        className="absolute inset-0"
        style={{ rotateX, rotateY, x: translateX, y: translateY, transformStyle: "preserve-3d" }}
        onPointerMove={(event) => {
          const bounds = event.currentTarget.getBoundingClientRect();
          const nextX = (event.clientX - bounds.left) / bounds.width - 0.5;
          const nextY = (event.clientY - bounds.top) / bounds.height - 0.5;

          pointerX.set(nextX);
          pointerY.set(nextY);
        }}
        onPointerLeave={() => {
          pointerX.set(0);
          pointerY.set(0);
        }}
      >
        <div className="absolute inset-0 rounded-[2.7rem] border border-white/70 bg-[linear-gradient(150deg,rgba(255,255,255,0.82),rgba(244,238,228,0.14))] shadow-[0_60px_160px_-60px_rgba(18,16,13,0.35)]" />
        <div className="absolute inset-4 rounded-[2.25rem] border border-white/55 bg-[rgba(255,255,255,0.08)] shadow-[inset_0_1px_0_rgba(255,255,255,0.45)]" />
        <div className="absolute inset-[1.45rem] rounded-[2rem] border border-[rgba(43,37,30,0.12)] bg-[radial-gradient(circle_at_top_right,rgba(198,155,87,0.16),transparent_28%),rgba(233,226,216,0.94)]" />

        <div className="absolute inset-7 overflow-hidden rounded-[1.8rem] border border-[rgba(61,54,46,0.14)] bg-[var(--color-stage)] md:inset-8">
          <video
            className="absolute inset-0 h-full w-full scale-[1.03] object-cover object-[68%_50%]"
            autoPlay
            loop
            muted
            playsInline
            poster="/media/act1/%E9%A6%96%E5%B8%A7.png"
          >
            <source src="/media/act1/act1.mp4" type="video/mp4" />
          </video>

          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(20,18,14,0.74),rgba(20,18,14,0.2)_38%,rgba(20,18,14,0.12)_58%,rgba(20,18,14,0.42)_100%)]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_72%_36%,rgba(255,255,255,0.22),transparent_20%),radial-gradient(circle_at_80%_76%,rgba(198,155,87,0.14),transparent_24%)]" />
          <div className="absolute inset-y-0 left-[14%] w-px bg-[linear-gradient(180deg,transparent,rgba(255,255,255,0.45),transparent)]" />

          {badges.map((badge) => (
            <motion.div
              key={badge.label}
              className={`absolute ${badge.className} rounded-full border border-white/16 bg-[rgba(16,14,12,0.34)] px-3 py-2 text-[10px] tracking-[0.28em] text-white/78 uppercase backdrop-blur-md md:px-4`}
              animate={{ y: [0, -6, 0], opacity: [0.82, 1, 0.82] }}
              transition={{ duration: 4.8, repeat: Infinity, ease: "easeInOut", delay: badge.delay }}
            >
              {badge.label}
            </motion.div>
          ))}

          <div className="absolute right-6 bottom-6 rounded-[1.2rem] border border-white/14 bg-[rgba(18,16,13,0.32)] px-4 py-3 text-right text-[11px] tracking-[0.24em] text-white/64 uppercase backdrop-blur-md md:right-7 md:bottom-7">
            <div>{name}</div>
            <div className="mt-2 text-white/44">Official System Entry</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
