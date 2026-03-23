"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  motion,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
  useSpring,
  useTransform
} from "framer-motion";

const phaseCopy = [
  {
    number: "01",
    label: "官网",
    body: "把品牌气质、信息结构与互动叙事压进同一个入口，让第一印象直接服务转化。"
  },
  {
    number: "02",
    label: "AI 产品原型",
    body: "先定义问题，再定义功能。让 AI 真正进入场景，而不是停留在展示层。"
  },
  {
    number: "03",
    label: "自动化",
    body: "把重复劳动收进流程，把注意力留给更重要的事。"
  },
  {
    number: "04",
    label: "MVP",
    body: "用可运行的产品推进判断，而不是用文档拖延决策。"
  }
];

const frameCount = 101;

export function ActTwoSequence() {
  const sectionRef = useRef<HTMLElement | null>(null);
  const prefersReducedMotion = useReducedMotion();
  const [frameIndex, setFrameIndex] = useState(0);
  const [activePhase, setActivePhase] = useState(0);
  const [phaseProgress, setPhaseProgress] = useState(0);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });
  const visualY = useSpring(useTransform(scrollYProgress, [0, 1], [18, -18]), {
    stiffness: 120,
    damping: 26,
    mass: 0.8
  });
  const visualScale = useSpring(useTransform(scrollYProgress, [0, 1], [0.985, 1.02]), {
    stiffness: 120,
    damping: 24,
    mass: 0.78
  });

  const frameSources = useMemo(
    () =>
      Array.from({ length: frameCount }, (_, index) => {
        const frameNumber = String(index + 1).padStart(3, "0");
        return `/media/act2/frames/frame_${frameNumber}.jpg`;
      }),
    []
  );

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      frameSources.forEach((source) => {
        const image = new window.Image();
        image.src = source;
      });
    }, 400);

    return () => window.clearTimeout(timeout);
  }, [frameSources]);

  useMotionValueEvent(scrollYProgress, "change", (value) => {
    const clamped = Math.min(0.9999, Math.max(0, value));
    const nextFrame = Math.min(frameCount - 1, Math.floor(clamped * frameCount));
    const scaledPhase = clamped * phaseCopy.length;
    const nextPhase = Math.min(phaseCopy.length - 1, Math.floor(scaledPhase));
    const nextPhaseProgress = Math.min(1, Math.max(0, scaledPhase - nextPhase));

    setFrameIndex((current) => (current === nextFrame ? current : nextFrame));
    setActivePhase((current) => (current === nextPhase ? current : nextPhase));
    setPhaseProgress((current) =>
      Math.abs(current - nextPhaseProgress) < 0.01 ? current : nextPhaseProgress
    );
  });

  return (
    <section
      id="services"
      ref={sectionRef}
      className="relative z-10 min-h-[280dvh] px-4 py-6 md:min-h-[320dvh] md:px-8"
    >
      <div className="sticky top-0 flex min-h-[100dvh] items-center py-16 md:py-20">
        <div className="mx-auto grid max-w-[1400px] gap-10 md:grid-cols-[minmax(0,0.62fr)_minmax(0,1.38fr)] md:items-center">
          <div className="space-y-10 pr-0 md:pr-10">
            <div className="space-y-4">
              <p className="text-xs tracking-[0.32em] text-[var(--color-faint)] uppercase">
                Act 2 / System Exploded Scroll
              </p>
              <h2 className="text-4xl font-medium tracking-[-0.06em] md:text-5xl">
                一套从方向到交付的工作系统。
              </h2>
              <p className="max-w-[34rem] text-sm leading-7 text-[var(--color-muted)] md:text-base">
                围绕官网、AI 产品原型、自动化与 MVP，我把产品方向、体验设计和开发交付连接成同一个系统。
              </p>
            </div>

            <div className="relative overflow-hidden rounded-[2.3rem] border border-[var(--color-border)] bg-[rgba(255,255,255,0.64)] p-6 shadow-[0_30px_90px_-60px_rgba(23,20,18,0.24)] md:p-7">
              <div className="absolute inset-y-7 left-6 w-px bg-[rgba(67,59,51,0.12)] md:left-7" />
              <motion.div
                className="absolute inset-y-7 left-6 w-px origin-top bg-[var(--color-accent)] md:left-7"
                style={{ scaleY: scrollYProgress }}
              />

              <div className="border-b border-[var(--color-border)] pb-7 pl-8">
                <div className="font-mono text-[3.6rem] leading-none tracking-[-0.08em] text-[rgba(33,29,25,0.18)] md:text-[5.5rem]">
                  {phaseCopy[activePhase].number}
                </div>
                <div className="mt-3 text-[11px] tracking-[0.26em] text-[var(--color-faint)] uppercase">
                  Current Service Layer
                </div>
                <div className="mt-4 h-px w-full overflow-hidden rounded-full bg-[rgba(67,59,51,0.08)]">
                  <motion.div
                    className="h-full origin-left bg-[var(--color-accent)]"
                    animate={{ scaleX: Math.max(0.08, phaseProgress) }}
                    transition={{ type: "spring", stiffness: 140, damping: 26 }}
                  />
                </div>
                <h3 className="mt-3 text-3xl font-medium tracking-[-0.06em] md:text-[2.7rem]">
                  {phaseCopy[activePhase].label}
                </h3>
                <p className="mt-4 max-w-[28rem] text-sm leading-7 text-[var(--color-muted)] md:text-base">
                  {phaseCopy[activePhase].body}
                </p>
              </div>

              <div className="pt-5 pl-8">
                <div className="mb-4 text-[11px] tracking-[0.24em] text-[var(--color-faint)] uppercase">
                  Scroll Through The Stack
                </div>
              </div>

              <div className="relative pl-8">
              {phaseCopy.map((phase, index) => {
                const isActive = index === activePhase;
                const itemProgress =
                  index < activePhase ? 1 : index === activePhase ? phaseProgress : 0;
                return (
                  <motion.div
                    key={phase.number}
                    layout
                    className={`relative py-4 transition-all duration-300 ${
                      isActive ? "translate-x-2 opacity-100" : "opacity-62"
                    }`}
                  >
                    <div
                      className={`absolute -left-[2.15rem] top-6 h-3 w-3 rounded-full border ${
                        isActive
                          ? "border-[var(--color-accent)] bg-[var(--color-accent)]"
                          : "border-[rgba(67,59,51,0.2)] bg-[var(--color-page)]"
                      }`}
                    />
                    <div className="grid gap-2 rounded-[1.6rem] border border-transparent px-3 py-2 transition-all duration-300 md:px-4">
                      <div className="flex items-center gap-3">
                        <div className="font-mono text-xs tracking-[0.24em] text-[var(--color-faint)] uppercase">
                          {phase.number}
                        </div>
                        <h4 className="text-xl font-medium tracking-[-0.05em]">{phase.label}</h4>
                      </div>
                      <p
                        className={`max-w-[28rem] overflow-hidden text-sm leading-7 text-[var(--color-muted)] transition-all duration-300 ${
                          isActive ? "max-h-28 opacity-100" : "max-h-0 opacity-0"
                        }`}
                      >
                        {phase.body}
                      </p>
                      <div className="mt-1 h-px overflow-hidden rounded-full bg-[rgba(67,59,51,0.08)]">
                        <motion.div
                          className="h-full origin-left bg-[var(--color-accent)]"
                          animate={{ scaleX: itemProgress }}
                          transition={{ type: "spring", stiffness: 160, damping: 24 }}
                        />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
              </div>
            </div>
          </div>

          <motion.div
            className="relative min-h-[60dvh] md:min-h-[72dvh]"
            style={{ y: prefersReducedMotion ? 0 : visualY, scale: prefersReducedMotion ? 1 : visualScale }}
          >
            <div className="absolute inset-0 rounded-[2.7rem] border border-white/55 bg-[linear-gradient(155deg,rgba(255,255,255,0.86),rgba(239,233,222,0.48))] shadow-[0_50px_140px_-70px_rgba(15,14,12,0.34)]" />
            <div className="absolute inset-4 rounded-[2.2rem] border border-[rgba(57,49,42,0.12)] bg-[var(--color-stage)]" />
            <div className="absolute inset-6 overflow-hidden rounded-[1.95rem] border border-white/40">
              {prefersReducedMotion ? (
                <video
                  className="h-full w-full object-cover"
                  autoPlay
                  loop
                  muted
                  playsInline
                  poster="/media/act2/%E9%A6%96%E5%B8%A7.png"
                >
                  <source src="/media/act2/act2.mp4" type="video/mp4" />
                </video>
              ) : (
                <img
                  src={frameSources[frameIndex]}
                  alt="Exploded system animation frame"
                  className="h-full w-full object-cover"
                />
              )}
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_65%_34%,rgba(198,155,87,0.14),transparent_28%),linear-gradient(180deg,rgba(16,14,12,0.04),rgba(16,14,12,0.22))]" />
              <div className="absolute left-6 top-6 rounded-full border border-[rgba(57,49,42,0.12)] bg-white/72 px-4 py-2 text-[10px] tracking-[0.28em] text-[var(--color-muted)] uppercase backdrop-blur-md md:left-7 md:top-7">
                Service Architecture
              </div>
              <div className="absolute left-6 bottom-7 max-w-[16rem] rounded-[1.4rem] border border-white/16 bg-[rgba(16,14,12,0.26)] px-4 py-4 text-white/78 backdrop-blur-md md:left-7">
                <div className="font-mono text-[10px] tracking-[0.24em] text-white/52 uppercase">
                  {phaseCopy[activePhase].number} / 04
                </div>
                <div className="mt-2 text-base font-medium tracking-[-0.04em] text-white">
                  {phaseCopy[activePhase].label}
                </div>
              </div>
            </div>

            <div className="absolute bottom-8 left-8 right-8 flex items-center gap-3">
              {phaseCopy.map((phase, index) => {
                const itemProgress =
                  index < activePhase ? 1 : index === activePhase ? phaseProgress : 0;

                return (
                  <div key={phase.number} className="flex min-w-0 flex-1 flex-col gap-2">
                    <div className="text-[10px] tracking-[0.24em] text-[var(--color-faint)] uppercase">
                      {phase.number}
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-[rgba(64,58,51,0.12)]">
                      <motion.div
                        className="h-full rounded-full bg-[var(--color-accent)]"
                        animate={{ scaleX: itemProgress }}
                        transition={{ type: "spring", stiffness: 140, damping: 24 }}
                        style={{ transformOrigin: "left center" }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
