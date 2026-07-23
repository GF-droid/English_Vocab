# 📚 记单词 — 智能英语词汇学习系统

一个功能完整、界面美观的英语词汇学习 Web 应用。基于 **SM-2 间隔重复算法** 科学记忆单词，集成 **AI 大模型** 提供智能学习助手和翻译评分，是你学习英语的全能工具箱。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.x-green" alt="Flask">
  <img src="https://img.shields.io/badge/AI-DeepSeek%20|%20Kimi%20|%20千问%20|%20豆包-purple" alt="AI">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## ✨ 核心功能

### 🧠 科学记忆
- **SM-2 间隔重复** — 实现 SuperMemo-2 算法，根据每次复习评分自动调整下次复习时间
- **每日学习队列** — 自动推送到期单词，每次 20 个，零规划负担
- **掌握状态追踪** — `学习中 → 复习中 → 已掌握` 三级递进，可视化进度

### 📝 多维测验
- **选择题** — 看释义选单词，支持按单词书/错题/形近词范围出题
- **拼写题** — 看释义默写单词，Levenshtein 编辑距离精确判定
- **自动纠错** — 错题自动收录，支持按类型筛选和批量复习

### 📚 单词管理
- **单词书分组** — 自由创建单词书（如"四级核心"、"考研词汇"），拖拽式管理
- **智能搜索** — 按单词/释义/词性/掌握状态多维度筛选
- **CSV/JSON 导入导出** — 一键备份或迁移词库
- **在线查词** — 集成 Free Dictionary API，英文释义 + MyMemory 中文翻译，一键导入

### 🤖 AI 智能助手 *(新)*
- **英语学习助手** — 右下角浮动气泡窗，可拖动、可缩放，随时提问
- **多模型支持** — DeepSeek / Kimi / 通义千问 / 豆包 / 智谱 GLM 一键切换
- **翻译练习评分** — 导入英文文章，自行翻译后 AI 自动评分，错误标红
- **快捷查词** — 阅读中点击单词即可弹出释义，支持一键加入单词书
- **API 连接测试** — 设置页面内置诊断工具，直观排查连接问题

### 📊 数据看板
- 30 天学习热力图 + 每日复习/新词趋势图
- 单词书维度掌握率统计
- 错题类型分布
- 连续打卡天数追踪

### 🎤 其他
- **gTTS 语音合成** — 自动生成单词发音 mp3
- **形近词识别** — 基于编辑距离自动发现易混淆单词，支持对比学习
- **明暗主题** — 一键切换，自动记忆偏好

---

## 🚀 快速开始

### 环境要求

- Python **3.10+**
- pip

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/GF-droid/English_Vocab.git
cd English_Vocab

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 导入预置词汇数据（可选）
python seed_data.py

# 5. 启动
python app.py
```

浏览器访问 **http://localhost:5000**。

---

## 📖 使用教程

### 1. 初始设置

首次使用建议先导入词汇数据：

```bash
python seed_data.py
```

然后访问 http://localhost:5000/settings/ 配置 AI 大模型：

1. 选择服务商（如 DeepSeek）
2. 填入 API Key
3. 点击「🔌 测试连接」验证配置
4. 保存

> 各平台均有免费额度：DeepSeek 注册送、Kimi 注册送、千问百万 Token 免费。

### 2. 每日学习流程

```
📅 每天打开 → 首页查看待复习数量 → 进入「每日学习」
→ 逐词翻卡片 → 诚实评分(0-5) → 系统自动安排下次复习
→ 每日学习量达到后自动停止
```

评分参考：
| 分数 | 含义 | 效果 |
|------|------|------|
| 0-2 | 忘记/不确定 | 间隔重置为 1 天 |
| 3 | 努力后想起 | 间隔正常递增 |
| 4-5 | 轻松想起 | 间隔加速递增 |

### 3. 单词管理

**添加单词：**
- 搜索页 → 输入单词 → 搜索
- 本地未找到时会自动查询在线词典，点击「导入」即可

**创建单词书：**
- 导航栏「单词书」→ 创建 → 命名选色
- 在单词详情页或搜索结果中点击「加入单词书」

**批量导入：**
- 导航栏「导入导出」→ 上传 CSV/JSON 文件
- CSV 格式：`word,phonetic,definition,example_sentence,example_translation,part_of_speech,tags`

### 4. 测验模式

- **选择题**：适合日常自测，支持限定范围（单词书/错题/形近词组）
- **拼写题**：适合强化输出能力
- 错题自动收录到「错题本」，可在测验中选择「仅做错题」

### 5. AI 学习助手

点击右下角 **🤖 浮动按钮** 打开助手：

- **拖动按钮**可移动位置，弹窗会自动跟随
- **拖动弹窗右下角手柄**可调整大小，下次打开保持
- 可以问：单词用法、语法解析、句子翻译、作文润色等

### 6. 翻译练习

这是为进阶学习者设计的功能：

1. **导入文章** — 翻译练习 → 导入文章 → 粘贴英文原文
2. **开始翻译** — 左右分栏：左侧原文，右侧输入框
3. **查词** — 点击原文中任意单词，右侧弹出释义面板
4. **提交评分** — AI 逐句对比评分，错误部分标红并给出修改建议
5. **复习** — 历史评分记录长期保存，可回看对比

### 7. 形近词管理

- 导航栏「形近词」→ 自动发现
- 系统用编辑距离算法扫描词库，找出拼写相似的词对
- 可手动创建分组，进行对比学习和专项测验

---

## 🏗️ 项目结构

```
English_Vocab/
├── app.py                     # Flask 应用入口 & 工厂函数
├── config.py                  # 配置（数据库、学习参数等）
├── models.py                  # 数据模型（8 张表）
├── spaced_repetition.py       # SM-2 算法实现
├── seed_data.py               # 预置词汇数据
├── requirements.txt
├── routes/
│   ├── main.py                # 首页仪表盘、统计
│   ├── study.py               # 间隔重复学习
│   ├── quiz.py                # 选择题 + 拼写题
│   ├── words.py               # 单词 CRUD + 搜索
│   ├── word_books.py          # 单词书管理
│   ├── wrong_book.py          # 错题本
│   ├── similar.py             # 形近词管理
│   ├── translation.py         # 翻译练习（AI 评分）
│   ├── settings.py            # AI 配置设置
│   ├── api.py                 # JSON API + 在线查词 + AI 对话
│   └── ai_helper.py           # AI 大模型调用封装
├── templates/                 # Jinja2 模板（20 个页面）
└── static/
    ├── css/style.css          # 全局样式
    └── audio/                 # TTS 生成音频
```

---

## ⚙️ 配置参考

| 配置项 | 位置 | 说明 |
|--------|------|------|
| AI API Key / 模型 | 设置页面 `/settings` | 存于 SQLite 数据库，不会上传 Git |
| `WORDS_PER_SESSION` | `config.py` | 每次学习的单词数，默认 20 |
| `NEW_WORDS_PER_DAY` | `config.py` | 每日新词上限，默认 10 |
| `SECRET_KEY` | `config.py` 或环境变量 | 生产环境请通过环境变量设置 |

---

## 🧩 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.x + SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 前端 | Bootstrap 5.3 + Chart.js 4 + Bootstrap Icons |
| AI 集成 | DeepSeek / Kimi / 千问 / 豆包 / 智谱（OpenAI 兼容） |
| 语音 | gTTS（Google Text-to-Speech） |
| 查词 | Free Dictionary API + MyMemory 翻译 |
| 算法 | SM-2 间隔重复 + Levenshtein 编辑距离 |

---

## 📄 License

MIT © 2024
