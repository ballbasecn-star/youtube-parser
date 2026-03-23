# 个人网站动画素材生成方案

## 生成原则

视频素材优先采用：

1. 先生成首帧图片
2. 再生成尾帧图片
3. 最后用首尾帧 + 统一 prompt 生成视频

这样做的原因：

- 风格更稳定
- 构图更可控
- 更接近当前目录两份文档里的工作方式
- 后续更容易把视频转成滚动帧序列

---

## 总体视觉约束

- 风格：高端、前卫、克制、精密
- 背景：暖白、浅灰、柔和中性色
- 避免：赛博朋克、紫蓝霓虹、夸张 HUD、廉价粒子特效
- 物体语言：模块化系统体、薄屏幕、金属框、玻璃板、数据轨道
- 镜头语言：慢推、平移、定轴旋转、受控分解
- 禁止：人物、文字、Logo、水印、过满构图、脏背景

---

## Act 1 / Hero

目标：生成一个可循环的高质感主视觉视频，用于首页第一屏。

### 首帧图 prompt

```text
A premium futuristic digital workspace for an independent developer and AI product builder, highly refined modular workstation, floating interface slabs, metallic rails, translucent panels, precise geometry, clean editorial composition, warm white studio background, soft graphite and ivory palette, restrained luxury, no people, no text, no logo, ultra clean, website hero visual, cinematic, 16:9
```

### 尾帧图 prompt

```text
The same premium futuristic digital workspace, slightly closer camera position, subtle rearrangement of floating interface slabs, a few modules gently shifted forward, refined parallax depth, precise geometry, warm white studio background, soft graphite and ivory palette, restrained luxury, no people, no text, no logo, ultra clean, website hero ending frame, cinematic, 16:9
```

### 视频生成 prompt

```text
Create a slow, elegant transition between the start frame and the end frame. The camera should gently dolly forward while the modular interface elements drift with controlled precision. Motion must feel premium, minimal, and architectural. No chaotic movement, no particles, no aggressive lighting changes, no text. The result should feel like a high-end digital product sculpture for a luxury portfolio website hero.
```

### 负面约束

```text
cyberpunk, neon purple, blue glow, hacker screen, characters, human hands, text overlays, logos, cluttered UI, busy background, particle storm, dramatic lens flare, low-detail render, cartoon style
```

### 建议生成数量

- 首帧：4 张
- 尾帧：4 张
- 视频：从最佳首尾帧组合里做 2 到 3 条

### 选择标准

- 构图是否适合网页右侧或整屏背景
- 物体是否足够“像一个系统”，而不是散乱装饰
- 画面是否干净，能承载左侧文字
- 运动是否克制，可循环

---

## Act 2 / System Exploded Scroll

目标：生成“完整服务系统 -> 分层拆解”的滚动主动画。

这一幕不是硬件产品渲染，不是显卡、电脑、主板、服务器，也不是家具、家居陈设、室内设计展品，而是一个被空间化表达的信息服务系统。

推荐理解方式：

- 更像“信息架构图被做成立体分层”
- 更像“界面系统拓扑图”
- 更像“数字工作流的空间示意图”
- 不是消费电子产品
- 不是家具或室内物件

四层语义建议：

1. Strategy / Product
2. Brand / Website
3. Build / Delivery
4. Automation / Workflow

### 首帧图 prompt

```text
A diagrammatic volumetric information-system composition for an independent developer and AI product builder, fully assembled as one coherent isometric structure, made of floating UI cards, translucent interface panes, routing lines, nodes, grids, stacked information layers, and connection paths, representing product strategy, website experience, software delivery, and automation workflows, schematic and digital rather than physical object design, clean orthographic or isometric composition, warm neutral background, calm, precise, high-end, no people, no readable text, no logo, not a computer, not a device, not furniture, not interior design, 16:9. Treat the composition as an isometric information architecture diagram made of interface panes, nodes, and routing layers, not as a physical machine, computer, motherboard, furniture object, or interior product render. Avoid any resemblance to chairs, tables, shelves, cabinets, lamps, home decor, interior staging, or architectural models. The scene should read as abstract interface topology, not as a physical object for a room.
```

### 尾帧图 prompt

```text
The same diagrammatic volumetric information-system composition in a controlled exploded view, separated into four distinct conceptual layers with elegant spacing, each layer still aligned as one coherent isometric system, made of floating UI cards, translucent interface panes, routing lines, nodes, grids, stacked information layers, and connection paths, representing strategy, website experience, software build, and automation workflows, schematic and digital rather than physical object design, clean orthographic or isometric composition, warm neutral background, calm, precise, high-end, no people, no readable text, no logo, not a computer, not a device, not furniture, not interior design, 16:9. Treat the composition as an isometric information architecture diagram made of interface panes, nodes, and routing layers, not as a physical machine, computer, motherboard, furniture object, or interior product render. Avoid any resemblance to chairs, tables, shelves, cabinets, lamps, home decor, interior staging, or architectural models. The scene should read as abstract interface topology, not as a physical object for a room.
```

### 视频生成 prompt

```text
Animate the assembled information-system composition into a controlled exploded view. The composition should separate into four clear conceptual layers with measured, elegant motion, while remaining visually coherent as one system. The movement must feel schematic, precise, and premium, like an interface topology diagram becoming spatial. No chaotic explosion, no debris, no sparks, no aggressive rotation, no hardware transformation, no furniture-like object behavior, no text. The result should feel like information architecture in motion, not a consumer electronic product and not an interior object. Treat the composition as an isometric information architecture diagram made of interface panes, nodes, and routing layers, not as a physical machine, computer, motherboard, furniture object, or interior product render. Avoid any resemblance to chairs, tables, shelves, cabinets, lamps, home decor, interior staging, or architectural models. The scene should read as abstract interface topology, not as a physical object for a room.
```

### 负面约束

```text
gpu, graphics card, motherboard, desktop computer, laptop, keyboard, server rack, circuit board, consumer electronics, device render, phone mockup, sci-fi weapon, furniture, chair, table, shelf, cabinet, lamp, sofa, interior design, room render, architectural interior, home decor, chaotic explosion, debris, broken parts, sparks, smoke, fire, blue neon glow, purple lighting, text labels, logo marks, low-detail CAD look, messy background
```

### 建议生成数量

- 首帧：4 张
- 尾帧：6 张
- 视频：从最佳首尾帧组合里做 3 条

### 选择标准

- 是否明显是“同一个服务系统”的前后状态
- 是否更像空间化的信息结构，而不是硬件设备
- 四层是否足够清晰，方便后面绑定 4 项服务
- 是否没有元素飞出画面
- 中心构图是否稳定，适合转帧序列

### 后续处理

- 将最终视频拆成 96 到 120 帧
- 输出为 `webp` 或优化后的 `jpg`
- 用于 sticky scroll 帧序列动画

---

## Act 3 / Signal Archive

目标：这一幕不依赖重视频，优先生成静帧素材和档案碎片。

### 主视觉静帧 prompt

```text
Editorial archive-style interface fragments for an AI product builder portfolio, layered screens, typography-like blocks without readable text, blueprint lines, cropped panels, premium monochrome palette, sharp composition, minimal but futuristic, warm neutral background, refined and quiet, suitable for a high-end article section
```

### 信号条静帧 prompt

```text
A premium signal-strip style composition for a digital archive wall, horizontal data fragments, modular UI slices, blueprint linework, restrained monochrome palette, soft contrast, clean editorial layout, no readable text, no logo, high-end portfolio website asset
```

### 建议生成数量

- 主视觉：3 到 4 张
- 信号条：3 到 4 张
- 局部碎片：6 张

### 选择标准

- 是否像“档案”而不是普通博客封面
- 是否适合做 hover 放大和横向滑动
- 色调是否与前两幕一致

---

## Act 4 / Contact Chamber

目标：生成非常轻的环境背景，作为结尾收束。

### 首帧图 prompt

```text
A quiet premium ambient chamber for a high-end digital portfolio ending scene, soft halo light, minimal linear structures, warm neutral background, large negative space, calm and elegant atmosphere, extremely clean, no text, no logo, cinematic 16:9
```

### 尾帧图 prompt

```text
The same quiet premium ambient chamber, with a subtle shift in halo light and delicate linear motion, warm neutral background, large negative space, calm and elegant atmosphere, extremely clean, no text, no logo, cinematic 16:9
```

### 视频生成 prompt

```text
Create an extremely subtle ambient transition between the start frame and the end frame. The motion should be almost imperceptible: a soft halo drift and delicate linear field movement. The scene must feel calm, spacious, and conclusive, suitable for the final contact section of a premium personal website.
```

### 负面约束

```text
busy scene, particles, strong glow, neon purple, abstract chaos, dramatic contrast, sci-fi tunnel, text overlays, logos, people
```

### 建议生成数量

- 首帧：2 张
- 尾帧：2 张
- 视频：1 到 2 条

### 选择标准

- 是否足够安静，适合收尾
- 是否不会抢走 CTA 的注意力

---

## 推荐生成顺序

1. Hero 首帧与尾帧
2. Hero 视频
3. System 首帧与尾帧
4. System 视频
5. Archive 静帧
6. Contact 首帧与尾帧
7. Contact 视频

---

## 推荐文件结构

```text
public/media/hero/
public/media/system/
public/media/system/frames/
public/media/archive/
public/media/contact/
```

---

## 下一步

当首批素材出来后，优先完成两件事：

1. 挑选 Hero 最终版本
2. 挑选 System 爆炸动画最终版本

这两组素材一旦定下来，首页的整体气质和技术实现方式也就基本定了。
