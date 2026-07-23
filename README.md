# English Vocab 📚

一个基于 Flask 的全功能英语词汇学习应用，内置 SM-2 间隔重复算法，帮助你科学高效地记忆单词。

## ✨ 功能特性

### 📖 单词管理
- **单词 CRUD** — 添加、编辑、删除单词，支持音标、释义、例句、词性、标签
- **多维度搜索** — 按单词、释义、词性、掌握状态筛选，支持分页
- **在线查词** — 集成 [Free Dictionary API](https://dictionaryapi.dev/)，一键导入单词释义
- **导入/导出** — 支持 CSV 和 JSON 格式的批量导入导出

### 📚 单词书
- 创建多个单词书分类管理词汇（如"四级核心"、"考研词汇"）
- 可视化学习进度（已学 / 已掌握百分比）
- 支持按单词/添加时间/掌握状态排序

### 🧠 间隔重复学习（SM-2）
- 实现 [SuperMemo-2](https://en.wikipedia.org/wiki/SuperMemo) 算法
- 根据每次复习评分（0-5）自动调整复习间隔
- 三级掌握状态：`learning` → `reviewing` → `mastered`
- 每日待复习单词自动排队

### 📝 测验模式
- **选择题（MC）** — 看释义选单词，支持错题重做和形近词专项
- **拼写题（Spell）** — 看释义拼写单词
- 自动记录错题并入错题本

### 📕 错题本
- 按单词聚合错误记录，显示错误次数和类型
- 支持标记已复习、批量标记、删除
- 与测验和学习模块联动

### 🔍 形近词识别
- 基于 **Levenshtein 编辑距离** 自动发现拼写相似的单词
- 手动创建形近词组，支持对比学习
- 可在测验中进行形近词组专项训练

### 📊 学习统计
- 仪表盘概览：待复习数、已掌握数、错题数、连续打卡天数
- 30 天学习热力图
- 单词书维度的学习进度
- 错题类型分布

### 🎤 语音朗读
- 使用 **gTTS**（Google Text-to-Speech）自动生成单词发音
- 按需生成并缓存 mp3 文件

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/GF-droid/English_Vocab.git
cd English_Vocab

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. （可选）导入预置词汇数据
python seed_data.py

# 5. 启动应用
python app.py
```

浏览器访问 **http://localhost:5000** 即可使用。

---

## 🏗️ 项目结构

```
English_Vocab/
├── app.py                    # 应用入口，Flask 工厂函数
├── config.py                 # 配置文件（数据库、密钥、学习参数）
├── models.py                 # 数据模型（6 张表）
├── spaced_repetition.py      # SM-2 间隔重复算法
├── seed_data.py              # 预置词汇数据
├── requirements.txt          # Python 依赖
├── vocab.db                  # SQLite 数据库（运行时生成）
├── routes/
│   ├── __init__.py
│   ├── main.py               # 首页仪表盘、统计、导入导出页
│   ├── study.py              # 间隔重复学习
│   ├── quiz.py               # 选择题 + 拼写测验
│   ├── words.py              # 单词 CRUD + 搜索
│   ├── word_books.py         # 单词书管理
│   ├── wrong_book.py         # 错题本
│   ├── similar.py            # 形近词识别 & 管理
│   └── api.py                # JSON API（语音、查词、导入导出）
├── templates/                # Jinja2 模板（18 个页面）
├── static/
│   ├── css/style.css         # 样式
│   └── audio/                # gTTS 生成的语音文件
└── venv/                     # 虚拟环境（不纳入版本控制）
```

## 🗃️ 数据模型

| 表名 | 说明 |
|------|------|
| `words` | 单词（拼写、音标、释义、例句、词性、标签） |
| `word_books` | 单词书（名称、封面颜色） |
| `word_book_items` | 单词书 ↔ 单词（多对多关联） |
| `learning_records` | 学习记录（ease factor、间隔、掌握状态） |
| `wrong_answers` | 错题记录（题目类型、错误答案、复习状态） |
| `similar_word_groups` | 形近词组（名称、描述） |
| `similar_word_items` | 形近词组 ↔ 单词 |
| `daily_checkins` | 每日打卡（复习数、新词数） |

## ⚙️ 配置说明

在 [config.py](config.py) 中可调整：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SECRET_KEY` | 环境变量或默认值 | Flask 密钥（生产环境请务必修改） |
| `DATABASE_URL` | `sqlite:///vocab.db` | 数据库地址 |
| `WORDS_PER_SESSION` | 20 | 每次学习会话的单词数 |
| `NEW_WORDS_PER_DAY` | 10 | 每日新词引入上限 |

## 🧩 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | Flask 3.x |
| ORM | SQLAlchemy（Flask-SQLAlchemy） |
| 数据库 | SQLite |
| 语音合成 | gTTS（Google Text-to-Speech） |
| 编辑距离 | python-Levenshtein |
| 在线词典 | Free Dictionary API |

## 📄 License

MIT
