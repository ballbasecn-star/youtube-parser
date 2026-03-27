# 模块说明：解析流水线

## 目标

该模块负责把用户输入的 YouTube 链接或分享文本，转换为统一契约下的 `ParsedContentPayload`。

## 输入

支持以下输入：

- 单条 YouTube URL
- 包含 YouTube URL 的分享文本

当前第一版重点支持：

- `watch`
- `youtu.be`
- `shorts`
- `live`

## 主要职责

- 识别并验证 YouTube 链接
- 提取 `videoId`
- 生成 `canonicalUrl`
- 拉取元数据、字幕和基础指标
- 标准化为统一结构
- 输出 warning 和错误码

## 模块边界

该模块负责“解析”和“标准化输出”，不负责：

- 主库写入
- 内容状态管理
- 创作项目管理
- AI 分析和生成
- 页面 UI 展示

## 解析阶段

建议按以下阶段组织：

1. 输入解析
2. URL 规范化
3. 元数据获取
4. transcript 获取
5. metrics 获取
6. 标准化映射
7. envelope 输出

## 输出要求

至少应稳定输出：

- `platform`
- `sourceType`
- `externalId`
- `canonicalUrl`
- `title`
- `author`
- `content`
- `media.covers`
- `rawPayload`
- `warnings`

## 关键风险

- YouTube 页面结构变化
- transcript 可用性不稳定
- 指标字段可能因地区、权限或页面变更而缺失
- 不同链接形式若 canonical 规则不统一，会影响主系统去重

## 何时更新本文档

当以下内容变化时必须更新：

- 支持的输入范围变化
- 解析阶段变化
- transcript 或 metrics 处理规则变化
- 输出结构变化
