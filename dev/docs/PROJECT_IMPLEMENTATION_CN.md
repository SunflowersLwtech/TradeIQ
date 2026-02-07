# TradeIQ 项目实际实现解读文档

> 本文档基于对项目全部源代码的逐文件分析，详细解读 TradeIQ 的**实际实现**（非设计目标），帮助开发者快速理解系统架构和代码逻辑。

---

## 目录

1. [项目总览](#1-项目总览)
2. [技术栈实况](#2-技术栈实况)
3. [后端架构详解](#3-后端架构详解)
4. [前端架构详解](#4-前端架构详解)
5. [AI Agent 系统](#5-ai-agent-系统)
6. [三大业务支柱](#6-三大业务支柱)
7. [实时通信系统](#7-实时通信系统)
8. [认证与安全](#8-认证与安全)
9. [演示系统](#9-演示系统)
10. [数据流全链路](#10-数据流全链路)
11. [目录结构速查](#11-目录结构速查)
12. [API 接口清单](#12-api-接口清单)
13. [环境变量清单](#13-环境变量清单)
14. [现有不足与改进方向](#14-现有不足与改进方向)

---

## 1. 项目总览

### 1.1 项目定位

TradeIQ 是 Deriv AI Hackathon 2026 参赛项目，主题为 **"Intelligent Trading Analyst"**（智能交易分析师）。

项目口号：**"散户的彭博终端、从未拥有过的交易教练、一直想要的内容团队"**。

### 1.2 三大核心支柱

| 支柱 | 功能 | 关键约束 |
|------|------|---------|
| **市场分析** (Market Analysis) | 实时行情、技术指标、情绪分析、AI 问答 | 不做预测/信号 |
| **行为教练** (Behavioral Coaching) | 交易模式检测、情绪识别、支持性提醒 | 支持而非限制 |
| **社交内容** (Content Engine) | AI 生成社交帖子、多人格、Bluesky 发布 | 品牌安全、合规 |

### 1.3 评判标准对齐

- **洞察力 (30%)**：多数据源融合分析 + 行为模式检测
- **实用性 (25%)**：每日简报、实时解释、温和提醒
- **工艺 (20%)**：Next.js 现代 UI、对话式 AI、WebSocket 实时更新
- **野心 (15%)**：三个 AI Agent 协同工作
- **演示 (10%)**：四幕式故事结构

---

## 2. 技术栈实况

> **注意**：实际技术栈与最初设计文档有差异（设计文档写的是 FastAPI + LangGraph，实际采用 Django + 原生函数调用）。

### 实际使用

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端框架** | Next.js 16 + React 19 | App Router 模式 |
| **UI 组件** | 纯 Tailwind CSS v4 手写组件 | 非 shadcn/ui（设计文档写了但未使用） |
| **图表** | Recharts + lightweight-charts | Recharts 为主，TradingView 已安装但未使用 |
| **动画** | Framer Motion | 页面过渡和交互动画 |
| **图标** | Lucide React | 全套线性图标 |
| **后端框架** | Django 5 + DRF + Channels | 非 FastAPI |
| **AI 引擎** | DeepSeek-V3.2 (通过 OpenRouter) | 非 Claude API（设计文档写了但未使用） |
| **AI 编排** | 原生函数调用 (Function Calling) | 非 LangGraph |
| **数据库** | Supabase PostgreSQL | 通过 dj-database-url 连接 |
| **实时通信** | Django Channels (WebSocket) | InMemory Channel Layer |
| **社交平台** | Bluesky (AT Protocol) | atproto 库 |
| **新闻数据** | NewsAPI + Finnhub | 双数据源聚合 |
| **行情数据** | Deriv WebSocket API | app_id=125489 |

---

## 3. 后端架构详解

### 3.1 Django 项目结构

```
backend/
├── tradeiq/                # Django 主配置
│   ├── settings.py         # 全局设置（DB、CORS、Auth、Channels）
│   ├── urls.py             # 根路由（6 个 API 模块）
│   ├── asgi.py             # WebSocket 入口（Channels）
│   ├── celery.py           # Celery 任务队列配置（已配置但未大量使用）
│   ├── auth_utils.py       # Supabase JWT → UserProfile 映射
│   ├── permissions.py      # 自定义 DRF 权限类
│   ├── exceptions.py       # 全局异常处理
│   └── middleware/
│       └── supabase_auth.py  # Supabase JWT 认证中间件
│
├── agents/                 # AI Agent 编排层
├── market/                 # 市场分析模块
├── behavior/               # 行为检测模块
├── content/                # 内容生成模块
├── chat/                   # WebSocket 聊天
├── demo/                   # 演示场景管理
└── manage.py
```

### 3.2 六大业务模块

每个模块遵循 Django 标准结构：`models.py` → `serializers.py` → `views.py` → `urls.py` → `tools.py`。

其中 `tools.py` 是本项目特色——每个模块提供可被 AI Agent 调用的工具函数。

---

## 4. 前端架构详解

### 4.1 页面结构 (App Router)

```
src/app/
├── page.tsx              # 仪表盘主页
├── market/page.tsx       # 市场分析页
├── behavior/page.tsx     # 行为教练页
├── content/page.tsx      # 内容引擎页
├── pipeline/page.tsx     # Agent 管道页（新增）
├── login/page.tsx        # 登录页
└── auth/callback/page.tsx  # OAuth 回调页
```

### 4.2 组件架构

```
src/components/
├── layout/
│   ├── AppShell.tsx       # 全局壳（Navbar + TickerBar + Sidebar）
│   ├── Navbar.tsx         # 顶部导航（Logo、5 个页面链接、登录按钮）
│   ├── Sidebar.tsx        # 右侧面板（AI Chat + Activity 两个 Tab）
│   └── TickerBar.tsx      # 行情滚动条（30s 循环滚动，10s 轮询更新）
│
├── market/
│   ├── PnLChart.tsx       # Recharts 面积图（PnL / 行情双用途）
│   └── MarketOverview.tsx # 市场总览表格（12 列网格）
│
├── behavior/
│   └── BehaviorCard.tsx   # 行为模式卡片（严重度指示 + AI 建议折叠）
│
├── content/
│   └── ContentWorkbench.tsx  # 内容工作台（生成 → 预览 → 发布全流程）
│
├── chat/
│   ├── ChatPanel.tsx      # 聊天面板（消息列表 + 输入框）
│   └── ChatMessage.tsx    # 消息气泡（区分用户/AI/提醒/免责）
│
└── ui/                    # 通用 UI 组件
    ├── DataCard.tsx       # 数据卡片（标题、数值、趋势箭头、发光效果）
    ├── StatusBadge.tsx    # 状态标签（5 种颜色 + 脉冲动画）
    ├── DisclaimerBadge.tsx  # 免责声明（3 种变体：内联/横幅/页脚）
    ├── DataSourceBadge.tsx  # 数据源标签（LIVE 绿 / FALLBACK 橙）
    ├── CollapsibleSection.tsx  # 可折叠区块
    └── LoadingDots.tsx    # 加载动画（3 个跳动圆点）
```

### 4.3 自定义 Hooks 体系

项目的核心设计模式是 **`useApiWithFallback`** —— 所有数据获取都经过这个 Hook，自动处理加载、错误、回退数据、轮询。

```
useApiWithFallback<T>
├── data: T              // 实际数据（真实或回退）
├── isLoading: boolean   // 加载状态
├── error: string | null // 错误信息
├── isUsingMock: boolean // 是否使用回退数据
├── refetch()            // 手动刷新
└── isBackendOnline      // 后端是否在线
```

**各页面 Hooks：**

| Hook | 功能 |
|------|------|
| `useTickerData()` | 行情滚动条数据，实时价格 + 涨跌幅 |
| `useMarketOverview()` | 市场简报 + 工具列表 |
| `useMarketInsights()` | AI 洞察动态流 |
| `useTrades()` | 交易记录格式化 |
| `useBehaviorPatterns()` | 行为模式批量分析 |
| `useSessionStats()` | 交易会话统计（胜率、风险等级） |
| `usePersonas()` | AI 人格列表 + 互动数据 |
| `usePosts()` | 社交帖子管理 |
| `useDashboardMetrics()` | 仪表盘指标（组合价值、日 PnL、风险分） |
| `useBackendHealth()` | 后端健康检测（3s 超时） |

### 4.4 API 客户端 (`src/lib/api.ts`)

统一的 `ApiClient` 类，封装了约 **25+ 个 API 方法**和 **60+ 个 TypeScript 接口**。

```typescript
class ApiClient {
  request<T>(path, options?)    // 通用请求，支持 Bearer Token

  // 市场分析
  getMarketBrief(instruments?)  // 市场简报
  askMarketAnalyst(question)    // AI 分析师问答
  getLivePrice(instrument)      // 实时行情
  getMarketHistory(...)         // K 线数据
  getMarketTechnicals(...)      // 技术指标
  getMarketSentiment(...)       // 情绪分析

  // 行为教练
  getTrades(userId?)            // 交易历史
  analyzeBatch(userId, hours)   // 批量行为分析

  // 内容引擎
  generateContent(data)         // 生成内容
  publishToBluesky(content)     // 发布到 Bluesky

  // Agent 管道
  runPipeline(params)           // 完整 4 阶段管道
  runMonitor / runAnalyst / runAdvisor / runContentGen  // 单步执行

  // 演示
  loadScenario(scenario)        // 加载演示场景
  analyzeScenario(scenario)     // 分析演示场景
}
```

### 4.5 视觉设计

**主题**：全暗色（#000000 背景），金融终端风格

**配色方案**：
- 盈利色：`#4ade80` (绿)，带绿色辉光
- 亏损色：`#f87171` (红)，带红色辉光
- 强调色：`#3b82f6` (蓝)
- 警告色：`#fbbf24` (黄)
- 辅助色：`#22d3ee` (青)

**字体**：
- 数据显示：JetBrains Mono（等宽字体）
- 正文：Inter

**特效**：
- 毛玻璃效果 (backdrop-blur)
- 渐变边框
- 脉冲动画（实时指示器）
- 行情滚动条（CSS 动画）
- 数据卡片悬停效果

---

## 5. AI Agent 系统

### 5.1 架构概述

系统不使用 LangGraph 或其他框架，而是基于 **DeepSeek 原生函数调用 (Function Calling)** 实现 Agent 路由。

```
用户输入 → Router（自动检测 Agent 类型）
         → 加载对应系统提示词 + 工具集
         → 发送给 DeepSeek (支持 Function Calling)
         → DeepSeek 决定调用哪些工具
         → 执行工具，将结果回传给 DeepSeek
         → DeepSeek 生成最终回复
         → 合规过滤（敏感词检测）
         → 添加免责声明
         → 返回给用户
```

### 5.2 核心文件

| 文件 | 职责 |
|------|------|
| `agents/router.py` | 查询路由器：接收用户输入 → 选择工具 → 调 LLM → 执行工具 → 合规过滤 |
| `agents/llm_client.py` | 统一 LLM 客户端：优先 OpenRouter，回退到直连 DeepSeek API |
| `agents/tools_registry.py` | 工具注册表：定义各 Agent 可用工具及其 JSON Schema |
| `agents/prompts.py` | 系统提示词：每个 Agent 的角色定义和合规规则 |
| `agents/compliance.py` | 合规过滤器：敏感词黑名单 + 预测词检测 + 免责声明注入 |
| `agents/agent_team.py` | 四阶段管道：Monitor → Analyst → Advisor → Creator |

### 5.3 四阶段管道 (Agent Team Pipeline)

```
阶段 1：市场监控 (Market Monitor)
  输入：instruments 列表, event 描述
  输出：MonitorOutput（events 列表、top_event、severity）
  工具：fetch_price_data, search_news

    ↓

阶段 2：分析师 (Analyst)
  输入：MonitorOutput
  输出：AnalysisReport（root_causes, impact_assessment, key_levels）
  工具：analyze_technicals, get_sentiment, search_news

    ↓

阶段 3：投资顾问 (Portfolio Advisor)
  输入：AnalysisReport + 用户投资组合
  输出：PersonalizedInsight（personalized_analysis, action_items, risk_assessment）
  工具：get_recent_trades, get_trading_statistics

    ↓

阶段 4：内容创作 (Content Creator)
  输入：AnalysisReport + PersonalizedInsight
  输出：MarketCommentary（bluesky_post, thread, hashtags）
  工具：generate_draft, generate_thread
```

每个阶段使用 Python `dataclass` 定义输入输出契约，阶段间通过数据传递连接。任一阶段失败不会中断整个管道，而是标记为 `partial`（部分成功）。

### 5.4 工具注册表

**市场分析工具**：
- `fetch_price_data(instrument)` — Deriv WebSocket 实时价格
- `fetch_price_history(instrument, timeframe, count)` — K 线数据
- `search_news(query, limit)` — NewsAPI + Finnhub 新闻
- `analyze_technicals(instrument, timeframe)` — SMA、RSI、趋势、波动率
- `get_sentiment(instrument)` — LLM 情绪分析
- `explain_market_move(instrument, move)` — 行情异动解释
- `generate_market_brief(instruments)` — 多品种简报

**行为分析工具**：
- `get_recent_trades(user_id, hours)` — 最近交易记录
- `analyze_trade_patterns(user_id, hours)` — 行为模式检测
- `generate_behavioral_nudge_with_ai(user_id, analysis)` — AI 生成提醒
- `get_trading_statistics(user_id, days)` — 交易统计
- `save_behavioral_metric(user_id, date, data)` — 保存日度指标

**内容生成工具**：
- `generate_draft(persona_id, topic, platform, max_length)` — 单条帖子
- `generate_thread(persona_id, topic, num_posts, platform)` — 帖子线程
- `format_for_platform(content, platform)` — 平台适配（字数限制）

### 5.5 合规系统

这是项目的关键特色——所有 AI 输出必须经过合规过滤：

**黑名单词汇**：`guaranteed`、`moon`、`easy money`、`get rich`、`sure thing`

**预测词检测**：`will hit`、`price will`、`going to`

**免责声明**：每条输出自动追加 `📊 Analysis by TradeIQ | Not financial advice`

---

## 6. 三大业务支柱

### 6.1 市场分析 (Market Module)

**数据模型**：
- `MarketInsight` — 存储 AI 生成的市场洞察（品种、情绪分数、数据源）

**数据源接入**：
```
Deriv WebSocket API (wss://ws.derivws.com/websockets/v3)
├── 实时报价（tick 数据）
├── 历史 K 线（OHLC candles）
└── 支持品种：外汇 (frxEURUSD)、加密货币 (cryBTCUSD)、波动率指数 (R_75, R_100)

NewsAPI + Finnhub
├── 关键词搜索新闻
├── 双源聚合去重
└── 用于情绪分析输入
```

**技术分析实现** (`market/tools.py: analyze_technicals`)：
- SMA(20) 和 SMA(50) — 简单移动平均线
- RSI(14) — 相对强弱指标
- 波动率 — 收益率标准差
- 支撑/阻力位 — 20 根 K 线的高低点
- 趋势判断 — 看涨/看跌/中性

**前端呈现**：
- 品种选择器（8+ 交易对）
- Recharts 面积图（实时行情）
- 技术指标面板（RSI、SMA、支撑阻力）
- 情绪仪表盘（多空评分 -1.0 到 1.0）
- AI 分析师问答（推荐问题列表）

### 6.2 行为教练 (Behavior Module)

**数据模型**：
- `UserProfile` — 用户画像（邮箱、偏好、关注列表）
- `Trade` — 单笔交易（品种、盈亏、持续时间、`is_mock` 标记）
- `BehavioralMetric` — 日度聚合指标（胜率、模式标记、情绪状态）

**四大检测算法** (`behavior/detection.py`)：

#### 1. 报复性交易 (Revenge Trading)
```
触发条件：亏损后 10 分钟内连续 ≥3 笔交易
严重度：
  - low: 3 笔
  - medium: 4 笔
  - high: ≥5 笔
输出：trade_count, time_window, trigger_loss
```

#### 2. 过度交易 (Overtrading)
```
触发条件：当日交易笔数 > 日均 × 2
严重度：
  - low: 2-2.5 倍
  - medium: 2.5-3 倍
  - high: >3 倍
输出：today_count, average, ratio
```

#### 3. 追损交易 (Loss Chasing)
```
触发条件：连续 ≥2 笔亏损 + 仓位增加 ≥20%
严重度：按连续亏损次数和加仓比例计算
输出：consecutive_losses, size_increase_pct
```

#### 4. 时段模式 (Time-Based Patterns)
```
触发条件：某时段胜率 < 35%（至少 3 笔交易）
严重度：根据胜率高低
输出：worst_hours, win_rate_by_hour
```

**实时提醒机制**：
```
创建交易 → TradeViewSet.create()
         → analyze_trade_patterns() （分析过去 24 小时）
         → 检测四种模式
         → if needs_nudge:
              generate_behavioral_nudge_with_ai()  // DeepSeek 生成提醒
              → WebSocket 推送到 chat_user_{user_id} 群组
         → 保存 BehavioralMetric
```

**提醒语气**：支持性而非惩罚性（"我注意到..."，而非"你在犯错..."）

### 6.3 社交内容引擎 (Content Module)

**数据模型**：
- `AIPersona` — AI 人格（冷静分析师、数据极客等），含性格描述和系统提示词
- `SocialPost` — 生成的帖子（平台、状态：草稿/已发布、互动数据）

**生成流程**：
```
用户输入洞察 → 选择平台（Bluesky 单帖 / 线程）
            → 选择 AI 人格
            → DeepSeek 生成内容（受人格风格约束）
            → 合规检查（敏感词过滤 + 免责声明）
            → 字数适配（Bluesky 限 300 字符）
            → 预览卡片
            → 发布到 Bluesky（可选）
```

**Bluesky 发布** (`content/bluesky.py`)：
- 使用 `atproto` 库实现 AT Protocol
- 支持单条发布和线程发布
- AT URI 转换为 Web URL
- 发布结果反馈（包含链接）

**ContentWorkbench 组件**（前端核心）：
- 输入区：市场洞察文本
- 选择区：平台 + 人格
- 预览区：Bluesky 卡片样式预览 + 字数计数器
- 操作区：复制 + 发布按钮

---

## 7. 实时通信系统

### 7.1 后端 WebSocket (Django Channels)

**ASGI 配置** (`tradeiq/asgi.py`)：
```python
ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # ws/chat/
    )
})
```

**ChatConsumer** (`chat/consumers.py`)：
- 连接路径：`ws://localhost:8000/ws/chat/?user_id=uuid`
- 加入频道组：`chat_user_{user_id}`
- 接收消息格式：`{"message": "...", "agent_type": "auto", "user_id": "..."}`
- 回复消息格式：`{"type": "reply", "message": "...", "agent_type": "...", "tools_used": [...]}`
- 自动检测 Agent 类型：
  - 包含 "pattern"/"behavior"/"revenge" → 行为分析 Agent
  - 包含 "post"/"bluesky"/"content" → 内容生成 Agent
  - 其他 → 市场分析 Agent
- 处理中发送 "thinking" 状态指示

### 7.2 前端 WebSocket (`src/lib/websocket.ts`)

**TradeIQWebSocket 类**：
```typescript
connect()          // 建立连接
disconnect()       // 断开连接
send(message)      // 发送 JSON 消息
sendMessage(content)  // 发送聊天消息
onMessage(handler)    // 订阅消息
onStatusChange(handler)  // 订阅状态变化
getStatus()        // 获取当前状态
```

**特性**：
- 指数退避重连（最多 5 次）
- 消息处理器模式（支持清理）
- 连接状态：`connecting` | `connected` | `disconnected` | `error`

### 7.3 行为提醒推送

当用户创建交易触发行为检测后，提醒消息通过 WebSocket Channel Group 异步推送到聊天面板，实现"交易时实时教练"效果。

---

## 8. 认证与安全

### 8.1 Supabase JWT 认证

**中间件** (`tradeiq/middleware/supabase_auth.py`)：
1. 从请求头提取 `Authorization: Bearer <token>`
2. 使用 `SUPABASE_JWT_SECRET` 验证 JWT 签名
3. 从 claims 中提取用户邮箱

**用户映射** (`tradeiq/auth_utils.py`)：
```python
get_or_create_user_from_jwt(jwt_claims)
# 原子事务操作，防竞态条件
# Supabase Auth → UserProfile (通过邮箱关联)
```

### 8.2 权限类

- `IsAuthenticated` — 需要认证
- `IsAuthenticatedOrReadOnly` — 读开放，写需认证
- `IsOwnerOrReadOnly` — 仅所有者可修改

### 8.3 CORS 配置

- 允许来源：`localhost:3000`（开发模式允许所有来源）
- 允许凭证：是
- 允许头：全部

---

## 9. 演示系统

### 9.1 设计理念

项目包含完整的演示场景管理系统，专为 Hackathon 现场演示设计。

### 9.2 演示场景

| 场景 | 触发模式 | 预期检测 |
|------|---------|---------|
| revenge_trading | 亏损后 10 分钟内 5 笔交易 | 报复性交易 |
| overtrading | 日内 25 笔（均值 8 笔） | 过度交易 |
| loss_chasing | 4 连亏 + 1.5x 加仓 | 追损交易 |
| healthy_session | 6 笔，60% 胜率 | 无异常（健康） |

### 9.3 演示端点

| 端点 | 功能 |
|------|------|
| `POST /api/demo/seed/` | 创建演示用户 + 加载默认场景 |
| `POST /api/demo/load-scenario/` | 加载指定场景的交易数据 |
| `POST /api/demo/analyze/` | 加载场景 + 行为分析 + AI 提醒（一步完成） |
| `GET /api/demo/scenarios/` | 列出可用场景 |
| `POST /api/demo/wow-moment/` | **三柱演示**：市场分析 + 行为洞察 + 内容预览 |

### 9.4 "WOW Moment" 演示流程

这是最核心的演示端点，一次调用展示三大支柱协同：

```
输入：instrument（如 frxEURUSD）+ user_id
 ↓
1. 市场分析：获取该品种实时行情 + 情绪分析
2. 行为洞察：分析用户最近交易模式，生成教练建议
3. 内容预览：基于分析结果，生成 Bluesky 帖子草稿
 ↓
输出：{market_analysis, behavioral_insight, content_preview}
```

**演示用户 ID**：`d1000000-0000-0000-0000-000000000001`

---

## 10. 数据流全链路

### 10.1 市场分析链路

```
Deriv WebSocket → fetch_price_data() → Router
                                         ↓
NewsAPI + Finnhub → search_news() → DeepSeek (Function Calling)
                                         ↓
                     analyze_technicals() → LLM 综合分析
                                         ↓
                     get_sentiment() → 合规过滤 → 用户
```

### 10.2 行为教练链路

```
用户创建交易 → POST /api/behavior/trades/
              ↓
         TradeViewSet.create()
              ↓
         analyze_trade_patterns() (24h 回溯)
              ↓
    ┌─ detect_revenge_trading()
    ├─ detect_overtrading()
    ├─ detect_loss_chasing()
    └─ detect_time_patterns()
              ↓
         if pattern_detected:
              ↓
         generate_behavioral_nudge_with_ai()
              ↓
    ┌─ WebSocket → 聊天面板实时推送
    └─ save_behavioral_metric() → 数据库存储
```

### 10.3 内容生成链路

```
用户输入洞察 + 选择人格/平台
         ↓
    POST /api/content/generate/
         ↓
    load_persona_prompt()
         ↓
    DeepSeek (人格化生成)
         ↓
    compliance_check() → 合规过滤
         ↓
    format_for_platform() → 字数适配
         ↓
    返回草稿 → 用户预览
         ↓
    POST /api/content/publish-bluesky/ (可选)
         ↓
    atproto → Bluesky 发布 → 返回帖子 URL
```

### 10.4 Agent 管道链路

```
POST /api/agents/pipeline/
         ↓
    Stage 1: Market Monitor
    - 检测波动事件（如 EUR/USD +2.5%）
         ↓
    Stage 2: Analyst
    - 分析根因（新闻 + 情绪 + 技术面）
         ↓
    Stage 3: Portfolio Advisor
    - 结合用户持仓，个性化建议
         ↓
    Stage 4: Content Creator
    - 生成 Bluesky 帖子（≤300 字符）
         ↓
    返回 PipelineResult（4 个阶段全部输出）
```

---

## 11. 目录结构速查

```
deriv hackathon/
├── .env                          # 环境变量（含真实密钥）
├── .gitignore                    # Git 忽略规则（349 行）
├── README.md                     # 项目说明
│
├── backend/                      # Django 后端
│   ├── tradeiq/                  # 主配置（settings, urls, asgi, auth）
│   ├── agents/                   # AI Agent（router, llm_client, tools, pipeline）
│   ├── market/                   # 市场（models, tools, views）
│   ├── behavior/                 # 行为（models, detection, tools, views）
│   ├── content/                  # 内容（models, tools, bluesky, views）
│   ├── chat/                     # WebSocket（consumers）
│   ├── demo/                     # 演示（views, scenarios）
│   ├── fixtures/                 # 测试数据
│   ├── requirements.txt          # Python 依赖
│   └── manage.py
│
├── frontend/                     # Next.js 前端
│   ├── src/app/                  # 页面路由（5 个主页面）
│   ├── src/components/           # 组件（25+ 个）
│   ├── src/hooks/                # 自定义 Hooks（10+ 个）
│   ├── src/lib/                  # API 客户端 + WebSocket
│   └── package.json              # Node 依赖
│
├── scripts/                      # 工具脚本
│   ├── setup_env.sh              # 环境安装
│   ├── start_backend.sh          # 启动后端
│   ├── start_frontend.sh         # 启动前端
│   ├── verify_env.py             # 环境检测
│   └── environment.yml           # Conda 环境定义
│
└── dev/                          # 开发资源
    ├── diagrams/                 # 10 张架构图（PNG）
    ├── docs/                     # 设计文档 + 实施计划
    └── tests/                    # 测试脚本
```

---

## 12. API 接口清单

### 市场分析 (`/api/market/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/market/ask/` | AI 分析师问答 |
| POST | `/api/market/brief/` | 市场简报 |
| POST | `/api/market/price/` | 实时行情 |
| POST | `/api/market/history/` | K 线历史 |
| POST | `/api/market/technicals/` | 技术指标 |
| POST | `/api/market/sentiment/` | 情绪分析 |

### 行为教练 (`/api/behavior/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/behavior/trades/` | 交易列表/创建 |
| POST | `/api/behavior/trades/analyze_batch/` | 批量分析 |
| POST | `/api/behavior/trades/load_demo_scenario/` | 加载演示场景 |
| GET | `/api/behavior/profiles/{id}/statistics/` | 用户统计 |
| GET | `/api/behavior/metrics/summary/` | 行为摘要 |
| POST | `/api/behavior/metrics/create_demo_user/` | 创建演示用户 |

### 内容引擎 (`/api/content/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/content/generate/` | 生成内容 |
| POST | `/api/content/publish-bluesky/` | 发布到 Bluesky |
| GET | `/api/content/personas/` | 人格列表 |
| GET/POST | `/api/content/posts/` | 帖子 CRUD |

### AI Agent (`/api/agents/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/agents/query/` | 单 Agent 查询 |
| POST | `/api/agents/chat/` | 自动路由聊天 |
| POST | `/api/agents/pipeline/` | 完整 4 阶段管道 |
| POST | `/api/agents/monitor/` | 市场监控（第 1 阶段） |
| POST | `/api/agents/analyst/` | 市场分析（第 2 阶段） |
| POST | `/api/agents/advisor/` | 投资顾问（第 3 阶段） |
| POST | `/api/agents/content-gen/` | 内容创作（第 4 阶段） |

### 演示 (`/api/demo/`)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/demo/seed/` | 初始化演示数据 |
| GET | `/api/demo/scenarios/` | 场景列表 |
| POST | `/api/demo/load-scenario/` | 加载场景 |
| POST | `/api/demo/analyze/` | 场景分析 |
| POST | `/api/demo/wow-moment/` | 三柱联合演示 |

### WebSocket

| 协议 | 路径 | 说明 |
|------|------|------|
| WS | `ws://localhost:8000/ws/chat/` | AI 聊天 + 行为提醒推送 |

---

## 13. 环境变量清单

```bash
# Django 核心
DJANGO_SECRET_KEY=...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库
DATABASE_URL=postgresql://postgres:password@host:5432/postgres

# Supabase
SUPABASE_JWT_SECRET=...
SUPABASE_URL=https://xxx.supabase.co

# LLM (二选一)
DEEPSEEK_API_KEY=...         # DeepSeek 直连
OPENROUTER_API_KEY=...       # OpenRouter（当前主用）

# 新闻数据
NEWS_API_KEY=...
FINNHUB_API_KEY=...

# Deriv
DERIV_APP_ID=125489

# Bluesky
BLUESKY_HANDLE=xxx.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Google OAuth（可选）
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
CALLBACK_URL=...

# 前端
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_AUTH_CALLBACK_URL=http://localhost:3000/auth/callback
```

### 13.1 Google 登录 `redirect_uri_mismatch` 修复要点

若出现 `Error 400: redirect_uri_mismatch`，需要在 Google Cloud Console 的 OAuth Client 中添加**精确**回调地址：

```text
https://<your-project-ref>.supabase.co/auth/v1/callback
```

其中 `<your-project-ref>` 必须与 `NEXT_PUBLIC_SUPABASE_URL` 对应（如 `https://abc.supabase.co` 则回调为 `https://abc.supabase.co/auth/v1/callback`）。

同时需在 Supabase Auth URL 配置中允许前端回跳地址（如 `http://localhost:3000/auth/callback`）。

---

## 14. 现有不足与改进方向

### 14.1 设计 vs 实现差异

| 项目 | 设计文档 | 实际实现 |
|------|---------|---------|
| 后端框架 | FastAPI + LangGraph | Django + 原生函数调用 |
| AI 引擎 | Claude API | DeepSeek (via OpenRouter) |
| UI 组件库 | shadcn/ui | 纯 Tailwind 手写组件 |
| 图表库 | TradingView Lightweight Charts | Recharts（lightweight-charts 已装未用） |
| 缓存 | Upstash Redis | InMemory Channel Layer |
| 部署 | Vercel + Railway | 本地开发（未部署） |

### 14.2 架构层面

- **无 Docker 配置**：缺少容器化部署方案
- **无 CI/CD**：缺少自动化测试和部署流水线
- **Channel Layer**：使用 InMemoryChannelLayer，不支持多进程
- **无状态管理**：前端无全局状态管理（React Context / Zustand）
- **无单元测试**：`tests/` 目录存在但测试用例不完善

### 14.3 安全层面

- `.env` 包含真实密钥，需确保不被提交到公开仓库
- JWT 认证流程已实现但前端集成不完整
- CORS 在调试模式允许所有来源

### 14.4 可优化方向

- **TradingView Charts**：已安装 `lightweight-charts`，可替换 Recharts 获得更专业的金融图表体验
- **Redis Channel Layer**：部署时应切换到 Redis，支持多进程 WebSocket
- **流式响应**：AI 回复可使用 SSE/Stream 实现打字机效果
- **离线缓存**：利用 `useApiWithFallback` 的回退机制，可扩展为 Service Worker 缓存
- **国际化**：当前仅英文，可增加多语言支持

---

> 📝 **文档生成时间**：2026-02-08
> 📦 **项目版本**：基于 commit `6e40c59` 分析
> 🔍 **分析范围**：全部后端 Python 源文件 + 全部前端 TypeScript 源文件 + 配置文件 + 脚本
