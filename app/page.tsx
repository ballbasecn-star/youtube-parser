import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight, GithubLogo, LinkedinLogo, XLogo } from "@phosphor-icons/react/dist/ssr";
import { ActTwoSequence } from "@/components/site/act-two-sequence";
import { HeroStage } from "@/components/site/hero-stage";
import { SignalTicker } from "@/components/site/signal-ticker";

const profile = {
  name: "林克",
  email: "linkerai123@gmail.com",
  github: "https://github.com/ballbasecn-star",
  x: "",
  linkedin: ""
};

const mobileNavItems = [
  { href: "#hero", label: "About" },
  { href: "#services", label: "Services" },
  { href: "#writing", label: "Writing" },
  { href: "#contact", label: "Contact" }
];

const writingItems = [
  {
    title: "为什么大多数 AI 产品的问题，不在模型，而在交互",
    summary: "好的 AI 体验首先解决路径，而不是参数。"
  },
  {
    title: "独立开发最稀缺的能力，不是速度，而是取舍",
    summary: "速度决定启动，取舍决定结果。"
  },
  {
    title: "当网站开始会动，表达才真正成立",
    summary: "动画不是装饰，它是叙事与转化的一部分。"
  }
];

const signalItems = [
  "正在构建：AI 工作流、表达型网站、产品原型",
  "已提供：官网、AI 产品原型、自动化、MVP",
  "长期关注：交互、性能、视觉表达"
];

const socialItems = [
  profile.github
    ? { href: profile.github, label: "GitHub", icon: GithubLogo }
    : null,
  profile.x ? { href: profile.x, label: "X", icon: XLogo } : null,
  profile.linkedin
    ? { href: profile.linkedin, label: "LinkedIn", icon: LinkedinLogo }
    : null
].filter(Boolean) as Array<{
  href: string;
  label: string;
  icon: typeof GithubLogo;
}>;

export default function HomePage() {
  return (
    <main className="relative overflow-hidden">
      <div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_top_left,_rgba(198,155,87,0.12),_transparent_28%),radial-gradient(circle_at_85%_18%,_rgba(34,34,34,0.08),_transparent_24%)]" />
      <div className="pointer-events-none fixed inset-x-0 top-0 z-0 h-40 bg-[linear-gradient(180deg,rgba(245,241,234,0.95),rgba(245,241,234,0))]" />

      <header className="fixed inset-x-0 top-0 z-40 px-4 py-4 md:px-8">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between rounded-full border border-[var(--color-border)] bg-[rgba(247,244,239,0.78)] px-4 py-3 backdrop-blur-xl md:px-6">
          <Link href="#hero" className="text-sm font-medium tracking-[0.18em] text-[var(--color-muted)] uppercase">
            {profile.name}
          </Link>
          <nav className="hidden items-center gap-6 text-sm text-[var(--color-muted)] md:flex">
            <Link href="#hero" className="transition-colors hover:text-[var(--color-ink)]">
              About
            </Link>
            <Link href="#services" className="transition-colors hover:text-[var(--color-ink)]">
              Services
            </Link>
            <Link href="#writing" className="transition-colors hover:text-[var(--color-ink)]">
              Writing
            </Link>
            <Link href="#contact" className="transition-colors hover:text-[var(--color-ink)]">
              Contact
            </Link>
          </nav>
        </div>
      </header>

      <nav className="fixed inset-x-4 bottom-4 z-40 md:hidden">
        <div className="mx-auto flex max-w-md items-center justify-between rounded-full border border-[var(--color-border)] bg-[rgba(247,244,239,0.84)] px-3 py-2 shadow-[0_25px_60px_-35px_rgba(19,17,14,0.35)] backdrop-blur-xl">
          {mobileNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-full px-3 py-2 text-[11px] tracking-[0.22em] text-[var(--color-muted)] uppercase transition-colors hover:text-[var(--color-ink)]"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </nav>

      <section id="hero" className="relative z-10 px-4 pb-20 pt-28 md:px-8 md:pb-24 md:pt-36">
        <div className="mx-auto grid max-w-[1400px] gap-10 md:grid-cols-[minmax(0,0.76fr)_minmax(0,1.24fr)] md:items-end">
          <div className="flex min-h-[64dvh] flex-col justify-between gap-10 pb-2 md:min-h-[74dvh] md:gap-12 md:pb-8">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-3 rounded-full border border-[var(--color-border)] bg-white/70 px-4 py-2 text-xs tracking-[0.2em] text-[var(--color-muted)] uppercase shadow-[0_20px_60px_-30px_rgba(25,22,19,0.25)]">
                <span className="h-2 w-2 rounded-full bg-[var(--color-accent)]" />
                Independent Developer / AI Product Builder
              </div>
              <div className="space-y-6">
                <p className="max-w-24 text-xs tracking-[0.32em] text-[var(--color-faint)] uppercase md:text-sm">
                  Act 1 / Hero
                </p>
                <h1 className="max-w-4xl text-[2.85rem] font-medium tracking-[-0.08em] text-[var(--color-ink)] md:text-[6.8rem] md:leading-[0.88]">
                  独立开发者，
                  <br />
                  AI 产品人。
                  <br />
                  把概念推进成可上线、可使用、可交易的数字体验。
                </h1>
              </div>
              <p className="max-w-[34rem] text-base leading-8 text-[var(--color-muted)] md:text-lg">
                我与品牌、团队和创作者合作，提供官网、AI 产品原型、自动化与 MVP 开发。产品判断、体验设计与工程落地，在这里同时发生。
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex flex-wrap items-center gap-3">
                <Link
                  href="#contact"
                  className="inline-flex items-center gap-2 rounded-full bg-[var(--color-ink)] px-5 py-3 text-sm text-[var(--color-page)] transition-transform duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
                >
                  发起合作
                  <ArrowUpRight size={16} />
                </Link>
                <Link
                  href="#services"
                  className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border-strong)] bg-white/70 px-5 py-3 text-sm text-[var(--color-ink)] transition-transform duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
                >
                  查看服务
                </Link>
                <Link
                  href="#writing"
                  className="inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm text-[var(--color-muted)] transition-colors hover:text-[var(--color-ink)]"
                >
                  阅读文章
                </Link>
              </div>

              <div className="grid gap-4 border-t border-[var(--color-border)] pt-6 md:grid-cols-2">
                {[
                  { label: "Services", value: "官网 / AI 产品原型" },
                  { label: "Systems", value: "自动化 / MVP" }
                ].map((item) => (
                  <div key={item.label} className="space-y-2">
                    <div className="font-mono text-[11px] tracking-[0.28em] text-[var(--color-faint)] uppercase">
                      {item.label}
                    </div>
                    <div className="text-sm leading-7 text-[var(--color-muted)] md:text-[15px]">
                      {item.value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <HeroStage name={profile.name} />
        </div>
      </section>

      <ActTwoSequence />

      <section id="writing" className="relative z-10 px-4 py-20 md:px-8 md:py-28">
        <div className="mx-auto max-w-[1400px] space-y-10">
          <SignalTicker items={signalItems} />
          <div className="grid gap-8 md:grid-cols-[minmax(0,0.74fr)_minmax(0,1.26fr)] md:items-end">
            <div className="space-y-4">
              <p className="text-xs tracking-[0.32em] text-[var(--color-faint)] uppercase">Act 3 / Signal Archive</p>
              <h2 className="max-w-3xl text-4xl font-medium tracking-[-0.07em] md:text-[5.3rem] md:leading-[0.92]">
                写作，也是产品的一部分。
              </h2>
            </div>
            <p className="max-w-[34rem] text-base leading-8 text-[var(--color-muted)] md:justify-self-end md:text-lg">
              我持续记录关于 AI 产品、独立开发与数字体验的判断。文章、实验与项目片段，共同构成我的方法档案。
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
            <div className="group relative overflow-hidden rounded-[2.4rem] border border-[var(--color-border)] bg-[var(--color-panel)] p-4 shadow-[0_30px_90px_-50px_rgba(23,20,18,0.28)]">
              <div className="relative overflow-hidden rounded-[2rem] border border-white/50 bg-[var(--color-stage)]">
                <Image
                  src="/media/act3/%E4%B8%BB%E8%A7%86%E8%A7%89%E9%9D%99%E5%B8%A7.png"
                  alt="Archive featured visual"
                  width={2816}
                  height={1536}
                  priority
                  className="h-full w-full object-cover transition-transform duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-[1.02]"
                />
                <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_14%,rgba(13,12,11,0.08)_40%,rgba(13,12,11,0.74)_100%)]" />
                <div className="absolute bottom-0 left-0 right-0 space-y-3 p-6 md:p-8">
                  <div className="text-xs tracking-[0.24em] text-white/62 uppercase">Featured Essay</div>
                  <h3 className="max-w-3xl text-2xl font-medium tracking-[-0.05em] text-white md:text-4xl">
                    {writingItems[0].title}
                  </h3>
                  <p className="max-w-2xl text-sm leading-7 text-white/72 md:text-base">
                    {writingItems[0].summary}
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-6">
              <div className="overflow-hidden rounded-[2.2rem] border border-[var(--color-border)] bg-[var(--color-panel)] p-4 shadow-[0_30px_90px_-50px_rgba(23,20,18,0.28)]">
                <div className="relative overflow-hidden rounded-[1.8rem] border border-white/55 bg-[var(--color-stage)]">
                  <Image
                    src="/media/act3/%E4%BF%A1%E5%8F%B7%E6%9D%A1%E9%9D%99%E5%B8%A7.png"
                    alt="Signal strip visual"
                    width={2752}
                    height={1536}
                    className="h-64 w-full object-cover md:h-80"
                  />
                  <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_0%,rgba(16,15,13,0.12)_56%,rgba(16,15,13,0.78)_100%)]" />
                  <div className="absolute bottom-0 left-0 right-0 grid gap-3 p-6">
                    {signalItems.map((item) => (
                      <div
                        key={item}
                        className="rounded-full border border-white/18 bg-white/9 px-4 py-3 text-sm text-white/82 backdrop-blur-sm"
                      >
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-[2.2rem] border border-[var(--color-border)] bg-[rgba(255,255,255,0.72)] p-5 shadow-[0_30px_90px_-50px_rgba(23,20,18,0.28)] md:p-6">
                {writingItems.slice(1).map((item, index) => (
                  <article
                    key={item.title}
                    className="group grid gap-3 border-t border-[var(--color-border)] py-5 first:border-t-0 first:pt-0 last:pb-0 md:grid-cols-[84px_minmax(0,1fr)]"
                  >
                    <div className="font-mono text-xs tracking-[0.28em] text-[var(--color-faint)] uppercase">
                      0{index + 2}
                    </div>
                    <div className="space-y-3">
                      <h3 className="text-2xl font-medium tracking-[-0.05em] transition-transform duration-300 group-hover:translate-x-1">
                        {item.title}
                      </h3>
                      <p className="max-w-[35rem] text-sm leading-7 text-[var(--color-muted)] md:text-base">
                        {item.summary}
                      </p>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="contact" className="relative z-10 px-4 pb-32 pt-8 md:px-8 md:pb-32">
        <div className="mx-auto max-w-[1400px]">
          <div className="relative overflow-hidden rounded-[3rem] border border-[var(--color-border)] bg-[var(--color-stage)] px-8 py-16 shadow-[0_40px_120px_-60px_rgba(19,18,16,0.25)] md:px-12 md:py-20">
            <div className="absolute inset-0">
              <video
                className="absolute inset-0 h-full w-full object-cover opacity-58"
                autoPlay
                loop
                muted
                playsInline
                poster="/media/act4/%E9%A6%96%E5%B8%A7.png"
              >
                <source src="/media/act4/act4.mp4" type="video/mp4" />
              </video>
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_26%,rgba(255,255,255,0.14),transparent_22%),radial-gradient(circle_at_78%_72%,rgba(198,155,87,0.14),transparent_28%),linear-gradient(180deg,rgba(18,17,15,0.08),rgba(18,17,15,0.74))]" />
            </div>
            <div className="relative z-10 grid gap-10 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] lg:items-end">
              <div className="space-y-4">
                <p className="text-xs tracking-[0.32em] text-white/52 uppercase">Act 4 / Contact Chamber</p>
                <h2 className="max-w-4xl text-4xl font-medium tracking-[-0.06em] text-white md:text-6xl">
                  如果你在做一个值得认真完成的项目，我们可以聊聊。
                </h2>
                <p className="max-w-[38rem] text-base leading-8 text-white/72 md:text-lg">
                  适合官网、AI 产品原型、自动化与 MVP 项目。欢迎联系我，讨论合作、共创或定制服务。
                </p>
              </div>

              <div className="space-y-6 rounded-[2rem] border border-white/18 bg-[rgba(255,255,255,0.08)] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] backdrop-blur-xl">
                <div className="text-[11px] tracking-[0.24em] text-white/48 uppercase">Direct Contact</div>
                <div className="flex flex-wrap gap-3">
                  <Link
                    href={`mailto:${profile.email}`}
                    className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm text-[var(--color-ink)] transition-transform duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
                  >
                    发起合作
                    <ArrowUpRight size={16} />
                  </Link>
                  <Link
                    href={`mailto:${profile.email}`}
                    className="inline-flex items-center gap-2 rounded-full border border-white/24 px-5 py-3 text-sm text-white transition-colors duration-300 hover:bg-white/10 active:scale-[0.98]"
                  >
                    发送邮件
                  </Link>
                </div>
                <div className="space-y-3 text-sm text-white/72">
                  <p>{profile.email}</p>
                  <div className="flex items-center gap-4 text-white/72">
                    {socialItems.map((item) => {
                      const Icon = item.icon;

                      return (
                        <Link
                          key={item.label}
                          href={item.href}
                          aria-label={item.label}
                          className="transition-colors hover:text-white"
                          target="_blank"
                          rel="noreferrer"
                        >
                          <Icon size={20} />
                        </Link>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
