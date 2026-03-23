const capabilities = [
  "YouTube 链接解析骨架",
  "统一 parser 契约占位页",
  "后续将补齐 parse / transcript / metadata 输出"
];

export default function HomePage() {
  return (
    <main className="shell">
      <section className="card hero">
        <div className="eyebrow">youtube-parser</div>
        <h1>YouTube parser 服务骨架已经收敛完成。</h1>
        <p>
          当前仓库已经移除了与 parser 项目无关的个人展示站素材，保留为一个面向
          `linker-platform` 的 YouTube 能力服务最小骨架。
        </p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>当前保留内容</h2>
          <ul>
            <li>Next.js 运行骨架</li>
            <li>健康检查接口 `/api/v1/health`</li>
            <li>能力声明接口 `/api/v1/capabilities`</li>
            <li>Docker / compose / scripts 基础文件</li>
          </ul>
        </article>

        <article className="card">
          <h2>下一步建议</h2>
          <ul>
            {capabilities.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
