# 网络投票系统 - 完整项目解析文档

## 一、项目概述

**项目名称：** 网络投票系统（Online Voting System）

**功能简介：** 本系统是一个基于 Python Flask 框架开发的轻量级网络投票平台。用户可以创建包含多个选项的投票主题，每个选项支持文字描述和图片展示（本地上传或 URL 链接）。系统通过 IP 地址实现一人一票的去重机制，并实时统计和展示各选项的得票数与百分比。投票可设置截止时间，过期后自动关闭投票通道。整个系统开箱即用，无需复杂配置，适合班级活动、团队团建、意见征集等场景。

**技术栈一览表：**

| 层次       | 技术/工具          | 版本/说明                  | 作用                         |
| ---------- | ------------------ | -------------------------- | ---------------------------- |
| 后端框架   | Flask              | 轻件轻量级 Web 框架        | 路由分发、请求处理、模板渲染 |
| 数据库     | SQLite             | Python 内置，无需安装      | 存储投票、选项、投票记录     |
| 模板引擎   | Jinja2             | Flask 内置                 | HTML 模板继承与动态渲染      |
| 前端框架   | Bootstrap 5        | 5.3.0（CDN 引入）          | 响应式布局与 UI 组件         |
| 自定义样式 | CSS3               | 手写样式文件               | 卡片动效、进度条渐变等       |
| 前端交互   | 原生 JavaScript    | 无第三方库                | 动态添加/删除投票选项        |
| 图片处理   | Werkzeug           | Flask 依赖                | 安全文件名处理               |
| 运行环境   | Python             | 3.x                        | 解释器                       |

---

## 二、设计思路

### 2.1 需求分析：为什么做这个系统

在日常生活和学习中，经常需要进行集体决策，例如：

- **班级活动：** 班级聚餐选餐厅、选团建活动
- **团队协作：** 项目方案投票、会议时间确定
- **意见征集：** 对某个话题收集群体偏好

传统的举手投票方式存在以下问题：
1. 无法匿名，参与者可能受从众心理影响
2. 统计繁琐，容易出错
3. 参与者不在同一地点时无法进行
4. 结果不够直观，缺乏可视化展示

基于以上痛点，本系统旨在提供一个**简单易用、开箱即用、结果直观**的在线投票工具。

### 2.2 核心功能设计

本系统围绕"创建—投票—查看"三个核心环节设计了以下功能模块：

| 功能模块       | 具体功能                                                     |
| -------------- | ------------------------------------------------------------ |
| 投票创建       | 设置标题、描述、截止时间；动态添加多个选项；选项支持图片     |
| 选项图片展示   | 支持本地图片上传（png/jpg/gif 等）和外部图片 URL 两种方式    |
| 投票参与       | 单选投票；通过 IP 地址限制一人一票；过期投票自动阻止         |
| 结果展示       | 实时计算各选项票数和百分比；进度条可视化；高亮用户所选选项   |
| 投票管理       | 列表页展示所有投票；状态标签（进行中/已截止）；票数预览       |
| 消息提示       | 使用 Flash 消息机制，操作成功/失败均有即时反馈               |

### 2.3 用户交互流程（从创建投票到查看结果）

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  访问首页    │ ──> │  点击"创建   │ ──> │  填写投票    │ ──> │  添加选项    │
│  查看列表    │     │  新投票"     │     │  基本信息    │     │  (可加图片)  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                        │
                                                                        ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  返回首页    │ <── │  查看投票    │ <── │  提交投票    │ <── │  创建成功    │
│  或继续操作  │     │  结果统计    │     │  (单选)      │     │  跳转详情页  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

**详细流程说明：**

1. **访问首页：** 用户打开网站，看到所有投票列表（卡片式展示），每个卡片显示标题、描述摘要、创建日期、总票数和状态标签。
2. **创建投票：** 点击"创建新投票"按钮，进入创建页面。填写投票标题（必填）、描述（可选）、截止时间（可选）。
3. **添加选项：** 点击"+ 添加选项"按钮动态添加选项卡片，每个选项可填写文字（必填）、描述（可选）、上传图片或填写图片 URL（可选）。页面初始默认显示两个选项。
4. **提交创建：** 点击"创建投票"按钮，前端先校验至少两个有效选项，后端再次校验并写入数据库，成功后跳转到投票详情页。
5. **参与投票：** 其他用户访问详情页，若未投过票且投票未截止，可单选一个选项并提交。系统通过 IP 地址判断是否已投票。
6. **查看结果：** 投票后（或投票已截止时），页面展示所有选项的得票数和百分比进度条，用户自己投的选项会以绿色高亮显示。

---

## 三、框架选型理由

### 3.1 为什么选 Flask（对比 Django、FastAPI）

| 对比维度     | Flask（本项目）           | Django                  | FastAPI                  |
| ------------ | ------------------------- | ----------------------- | ------------------------ |
| 学习曲线     | 平缓，概念少，上手快     | 陡峭，需理解 MTV 全套   | 中等，需懂异步编程       |
| 代码量       | 少，单文件即可运行       | 多，项目结构固定        | 中等                     |
| 灵活性       | 高，自由组织代码         | 低，"约定优于配置"      | 高                       |
| 内置功能     | 精简，按需扩展           | 丰富（Admin/ORM/Auth等）| 精简                     |
| 模板引擎     | Jinja2（内置）           | Django Templates        | 需第三方（如 Jinja2）    |
| 适合场景     | 小型项目、原型开发       | 中大型项目              | API 服务、高性能场景     |

**选 Flask 的理由：**
1. 本项目是一个小型应用，功能明确，不需要 Django 那套庞大的生态。
2. Flask 的路由用装饰器定义，代码简洁直观，适合教学演示。
3. SQLite 数据库操作直接使用 Python 标准库 `sqlite3`，无需引入 ORM，降低复杂度。
4. Flask 与 Jinja2 模板引擎天然集成，方便服务端渲染 HTML 页面。

### 3.2 为什么选 SQLite（对比 MySQL、PostgreSQL）

| 对比维度     | SQLite（本项目）          | MySQL                   | PostgreSQL               |
| ------------ | ------------------------- | ----------------------- | ------------------------ |
| 安装配置     | 无需安装，Python 内置     | 需安装配置服务          | 需安装配置服务           |
| 运行方式     | 单文件嵌入式              | 独立服务进程            | 独立服务进程             |
| 并发性能     | 适合低并发（读写锁）      | 高并发                  | 高并发                   |
| 数据迁移     | 复制文件即可              | 需导出导入              | 需导出导入               |
| 适合场景     | 小型应用、开发测试        | 中大型 Web 应用         | 大型复杂应用             |

**选 SQLite 的理由：**
1. **零配置：** Python 标准库自带 `sqlite3` 模块，无需额外安装数据库服务器。
2. **便携性：** 整个数据库就是一个 `voting.db` 文件，拷贝即迁移。
3. **够用：** 投票系统并发量不高，SQLite 的性能完全满足需求。
4. **教学友好：** 降低环境搭建门槛，老师或同学拿到代码即可运行。

### 3.3 为什么选 Bootstrap 5

1. **响应式开箱即用：** 通过 `col-md-6`、`col-lg-4` 等栅格类，自动适配手机/平板/桌面。
2. **组件丰富：** 卡片（card）、进度条（progress）、导航栏（navbar）、警告框（alert）等组件直接可用，无需手写大量 CSS。
3. **CDN 引入：** 不需要本地安装 npm 包，一个 `<link>` 标签即可引入。
4. **中文友好：** 社区文档丰富，中文资料多，适合学习。
5. **版本 5 不依赖 jQuery：** 相比 Bootstrap 4，去掉了 jQuery 依赖，更轻量。

### 3.4 为什么选 Jinja2

1. **Flask 原生支持：** Flask 默认使用 Jinja2，无需额外配置。
2. **模板继承：** 通过 `{% extends 'base.html' %}` 实现布局复用，避免重复代码。
3. **语法直观：** `{{ variable }}` 输出变量，`{% if %}` / `{% for %}` 控制逻辑，学习成本低。
4. **安全自动转义：** 默认对输出内容进行 HTML 转义，防止 XSS 攻击。

### 3.5 选型总结表

| 技术        | 选择原因一句话总结                           |
| ----------- | -------------------------------------------- |
| Flask       | 轻量、灵活、学习成本低，完美匹配小型项目     |
| SQLite      | 零配置、零安装、单文件便携，降低环境门槛     |
| Bootstrap 5 | 响应式 + 丰富组件，快速构建美观界面           |
| Jinja2      | Flask 原生集成，模板继承减少重复代码           |

---

## 四、系统架构

### 4.1 三层架构描述（表现层-业务层-数据层）

本系统采用经典的三层架构模式，各层职责清晰分离：

```
┌─────────────────────────────────────────────────────────┐
│                    表现层（Presentation）                │
│  templates/*.html + static/css/style.css                │
│  职责：页面渲染、用户交互、表单展示                       │
│  技术：Jinja2 模板 + Bootstrap 5 + 原生 JS              │
├─────────────────────────────────────────────────────────┤
│                    业务层（Business）                    │
│  app.py 中的路由函数与辅助函数                           │
│  职责：请求处理、业务逻辑、数据校验、权限控制             │
│  技术：Flask 路由装饰器、Werkzeug 工具库                 │
├─────────────────────────────────────────────────────────┤
│                    数据层（Data）                        │
│  SQLite 数据库 (voting.db) + sqlite3 驱动               │
│  职责：数据持久化存储、查询、事务管理                     │
│  技术：Python 标准库 sqlite3                            │
└─────────────────────────────────────────────────────────┘
```

**各层交互说明：**
- **表现层 → 业务层：** 用户在浏览器操作，HTTP 请求发送到 Flask 路由。
- **业务层 → 数据层：** 路由函数通过 `get_db()` 获取连接，执行 SQL。
- **数据层 → 业务层：** 查询结果以 `sqlite3.Row` 对象返回。
- **业务层 → 表现层：** 调用 `render_template()` 将数据注入模板，返回 HTML。

### 4.2 目录结构说明

```
voting-system/
├── app.py                      # 后端核心：Flask 应用、路由、数据库操作
├── voting.db                   # SQLite 数据库文件（运行后自动生成）
├── PROJECT_ANALYSIS.md         # 本项目解析文档
├── static/                     # 静态资源目录
│   ├── css/
│   │   └── style.css           # 自定义样式表
│   └── uploads/                # 用户上传的图片存放目录（运行后自动生成）
└── templates/                  # Jinja2 模板目录
    ├── base.html               # 基础模板（导航栏、页脚、消息提示）
    ├── index.html              # 首页模板（投票列表）
    ├── create.html             # 创建投票页面模板
    └── detail.html             # 投票详情与结果页面模板
```

**目录设计说明：**
- `static/` 是 Flask 约定的静态文件目录，存放 CSS 和用户上传的图片。
- `templates/` 是 Flask 约定的模板目录，`render_template()` 默认从此目录查找。
- `voting.db` 和 `static/uploads/` 在程序首次运行时由 `init_db()` 自动创建。

### 4.3 请求处理流程

以"用户提交投票"为例，一次完整的请求处理流程如下：

```
用户点击"提交投票"
      │
      ▼
浏览器发送 POST /vote/<poll_id>  (携带 option_id)
      │
      ▼
Flask 路由匹配 → vote(poll_id) 函数
      │
      ▼
get_db() 获取数据库连接
      │
      ▼
查询 polls 表，验证投票是否存在 ──(不存在)──> 重定向首页 + 错误提示
      │(存在)
      ▼
is_poll_expired() 检查是否过期 ──(已过期)──> 重定向详情页 + 提示已截止
      │(未过期)
      ▼
查询 votes 表，检查该 IP 是否已投票 ──(已投)──> 重定向详情页 + 提示已投过
      │(未投)
      ▼
验证 option_id 是否合法 ──(不合法)──> 重定向详情页 + 错误提示
      │(合法)
      ▼
INSERT INTO votes 写入投票记录
      │
      ▼
db.commit() 提交事务
      │
      ▼
flash('投票成功！') 设置成功消息
      │
      ▼
redirect(url_for('detail')) 重定向到详情页
      │
      ▼
用户看到投票结果（含自己刚投的一票）
```

---

## 五、数据库设计

### 5.1 数据库总览

本系统使用 SQLite 数据库，数据库名为 `voting.db`，共设计 **3 张表**：`polls`（投票主题表）、`options`（选项表）、`votes`（投票记录表）。

### 5.2 表结构详细说明

#### 5.2.1 polls 表（投票主题表）

存储每次投票的基本信息。

| 字段名      | 类型    | 约束                        | 作用                     |
| ----------- | ------- | --------------------------- | ------------------------ |
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT   | 投票唯一标识，自增主键   |
| title       | TEXT    | NOT NULL                    | 投票标题（必填）         |
| description | TEXT    | （可为空）                  | 投票描述（可选）         |
| deadline    | TEXT    | （可为空）                  | 截止时间，格式 YYYY-MM-DDTHH:MM |
| created_at  | TEXT    | NOT NULL                    | 创建时间，格式 YYYY-MM-DD HH:MM:SS |

#### 5.2.2 options 表（选项表）

存储每个投票下的具体选项。

| 字段名      | 类型    | 约束                        | 作用                     |
| ----------- | ------- | --------------------------- | ------------------------ |
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT   | 选项唯一标识，自增主键   |
| poll_id     | INTEGER | NOT NULL, FOREIGN KEY       | 所属投票 ID，关联 polls.id |
| text        | TEXT    | NOT NULL                    | 选项文字（必填）         |
| description | TEXT    | （可为空）                  | 选项描述（可选）         |
| image_url   | TEXT    | （可为空）                  | 选项图片 URL（上传路径或外部链接） |

#### 5.2.3 votes 表（投票记录表）

存储每次投票行为的记录，通过唯一约束实现一人一票。

| 字段名      | 类型    | 约束                        | 作用                     |
| ----------- | ------- | --------------------------- | ------------------------ |
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT   | 记录唯一标识，自增主键   |
| poll_id     | INTEGER | NOT NULL, FOREIGN KEY       | 所属投票 ID，关联 polls.id |
| option_id   | INTEGER | NOT NULL, FOREIGN KEY       | 所选选项 ID，关联 options.id |
| ip_address  | TEXT    | NOT NULL                    | 投票者 IP 地址           |
| voted_at    | TEXT    | NOT NULL                    | 投票时间                 |
| —           | —       | UNIQUE(poll_id, ip_address) | 联合唯一约束：同一投票同一IP只能投一次 |

### 5.3 表之间关系

```
polls (投票主题)           options (选项)           votes (投票记录)
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│ id (PK)      │◄────────┤ poll_id (FK) │          │ poll_id (FK) │──► polls.id
│ title        │    1:N   │ id (PK)      │◄────────┤ option_id(FK)│──► options.id
│ description  │          │ text         │    1:N   │ id (PK)      │
│ deadline     │          │ description  │          │ ip_address   │
│ created_at   │          │ image_url    │          │ voted_at     │
└──────────────┘          └──────────────┘          └──────────────┘
```

**关系说明：**
- **polls → options：一对多**。一个投票主题包含多个选项，通过 `options.poll_id` 外键关联。
- **polls → votes：一对多**。一个投票主题可以有多条投票记录，通过 `votes.poll_id` 外键关联。
- **options → votes：一对多**。一个选项可以被多人投票，通过 `votes.option_id` 外键关联。
- **votes 表的 UNIQUE(poll_id, ip_address) 约束**：确保同一个 IP 在同一个投票中只能有一条记录，这是实现"一人一票"的核心约束。

### 5.4 建表 SQL 及解析

```sql
-- 投票主题表
CREATE TABLE IF NOT EXISTS polls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    deadline TEXT,
    created_at TEXT NOT NULL
);
```
**解析：** `IF NOT EXISTS` 保证重复调用 `init_db()` 不会报错。`AUTOINCREMENT` 确保主键自增，即使删除记录也不会复用 ID。

```sql
-- 选项表
CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    FOREIGN KEY (poll_id) REFERENCES polls(id)
);
```
**解析：** 外键 `poll_id` 引用 `polls(id)`，保证选项不会指向不存在的投票。`text` 为 NOT NULL，因为选项文字是必填项。`image_url` 可为空，表示选项可以没有图片。

```sql
-- 投票记录表
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    ip_address TEXT NOT NULL,
    voted_at TEXT NOT NULL,
    UNIQUE(poll_id, ip_address),
    FOREIGN KEY (poll_id) REFERENCES polls(id),
    FOREIGN KEY (option_id) REFERENCES options(id)
);
```
**解析：** `UNIQUE(poll_id, ip_address)` 是本表最关键的约束——它是一个联合唯一约束，确保"同一个投票 + 同一个 IP"的组合在表中唯一。如果同一 IP 尝试对同一投票再次插入记录，SQLite 会抛出 `IntegrityError`。不过本系统在应用层就做了检查（先查询再插入），所以正常流程不会触发这个约束。这个约束是数据库层面的最后一道防线。

---

## 六、完整源代码与逐行解析

### 6.1 app.py - 后端核心代码与逐行解析

#### 完整源代码

```python
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'voting-system-secret-key-2024'

DATABASE = 'voting.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            FOREIGN KEY (poll_id) REFERENCES polls(id)
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            voted_at TEXT NOT NULL,
            UNIQUE(poll_id, ip_address),
            FOREIGN KEY (poll_id) REFERENCES polls(id),
            FOREIGN KEY (option_id) REFERENCES options(id)
        )
    ''')
    db.commit()
    db.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_poll_expired(poll):
    if not poll['deadline']:
        return False
    try:
        deadline_dt = datetime.strptime(poll['deadline'], '%Y-%m-%dT%H:%M')
        return deadline_dt < datetime.now()
    except (ValueError, TypeError):
        return False


@app.route('/')
def index():
    db = get_db()
    polls = db.execute('''
        SELECT p.*,
               (SELECT COUNT(*) FROM votes v WHERE v.poll_id = p.id) as total_votes
        FROM polls p
        ORDER BY p.created_at DESC
    ''').fetchall()
    return render_template('index.html', polls=polls, is_poll_expired=is_poll_expired)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deadline = request.form.get('deadline', '').strip() or None

        if not title:
            flash('请填写投票标题', 'danger')
            return redirect(url_for('create'))

        option_texts = request.form.getlist('option_text[]')
        option_descs = request.form.getlist('option_desc[]')
        option_urls = request.form.getlist('option_url[]')
        option_files = request.files.getlist('option_file[]')

        options = []
        for i, text in enumerate(option_texts):
            text = text.strip()
            if not text:
                continue
            desc = option_descs[i].strip() if i < len(option_descs) else ''
            url = option_urls[i].strip() if i < len(option_urls) else ''
            file = option_files[i] if i < len(option_files) else None

            image_url = ''
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename) or 'image.png'
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = url_for('static', filename=f'uploads/{filename}')
            elif url:
                image_url = url

            options.append((text, desc, image_url))

        if len(options) < 2:
            flash('至少需要两个有效选项', 'danger')
            return redirect(url_for('create'))

        db = get_db()
        cursor = db.execute(
            'INSERT INTO polls (title, description, deadline, created_at) VALUES (?, ?, ?, ?)',
            (title, description, deadline, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        poll_id = cursor.lastrowid
        for text, desc, img_url in options:
            db.execute(
                'INSERT INTO options (poll_id, text, description, image_url) VALUES (?, ?, ?, ?)',
                (poll_id, text, desc, img_url)
            )
        db.commit()
        flash('投票创建成功！', 'success')
        return redirect(url_for('detail', poll_id=poll_id))

    return render_template('create.html')


@app.route('/poll/<int:poll_id>')
def detail(poll_id):
    db = get_db()
    poll = db.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    if not poll:
        flash('投票不存在', 'danger')
        return redirect(url_for('index'))

    options = db.execute('SELECT * FROM options WHERE poll_id = ?', (poll_id,)).fetchall()

    total_votes = 0
    option_stats = []
    for opt in options:
        count = db.execute(
            'SELECT COUNT(*) as c FROM votes WHERE option_id = ?', (opt['id'],)
        ).fetchone()['c']
        total_votes += count
        option_stats.append({'option': opt, 'count': count})

    for stat in option_stats:
        stat['percent'] = round(stat['count'] / total_votes * 100, 1) if total_votes > 0 else 0

    ip = request.remote_addr
    voted = db.execute(
        'SELECT option_id FROM votes WHERE poll_id = ? AND ip_address = ?',
        (poll_id, ip)
    ).fetchone()

    expired = is_poll_expired(poll)

    return render_template(
        'detail.html', poll=poll, option_stats=option_stats,
        total_votes=total_votes, voted=voted, is_expired=expired
    )


@app.route('/vote/<int:poll_id>', methods=['POST'])
def vote(poll_id):
    db = get_db()
    poll = db.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    if not poll:
        flash('投票不存在', 'danger')
        return redirect(url_for('index'))

    if is_poll_expired(poll):
        flash('投票已截止', 'warning')
        return redirect(url_for('detail', poll_id=poll_id))

    ip = request.remote_addr
    existing = db.execute(
        'SELECT * FROM votes WHERE poll_id = ? AND ip_address = ?',
        (poll_id, ip)
    ).fetchone()
    if existing:
        flash('您已经投过票了', 'warning')
        return redirect(url_for('detail', poll_id=poll_id))

    option_id = request.form.get('option_id')
    if not option_id:
        flash('请选择一个选项', 'danger')
        return redirect(url_for('detail', poll_id=poll_id))

    opt = db.execute(
        'SELECT * FROM options WHERE id = ? AND poll_id = ?',
        (option_id, poll_id)
    ).fetchone()
    if not opt:
        flash('无效的选项', 'danger')
        return redirect(url_for('detail', poll_id=poll_id))

    db.execute(
        'INSERT INTO votes (poll_id, option_id, ip_address, voted_at) VALUES (?, ?, ?, ?)',
        (poll_id, option_id, ip, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    db.commit()
    flash('投票成功！', 'success')
    return redirect(url_for('detail', poll_id=poll_id))


@app.template_filter('format_deadline')
def format_deadline(deadline):
    if not deadline:
        return ''
    try:
        dt = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return deadline


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

#### 逐行/逐函数解析

**① 导入模块（第1-5行）**

```python
import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g
from werkzeug.utils import secure_filename
```

- `os`：用于创建目录（`os.makedirs`）和拼接路径（`os.path.join`）。
- `sqlite3`：Python 内置的 SQLite 数据库驱动，无需 pip 安装。
- `datetime`：用于处理截止时间的解析和当前时间获取。
- `Flask` 等：从 Flask 框架导入核心功能：
  - `Flask`：创建应用实例
  - `render_template`：渲染模板
  - `request`：访问请求数据（表单、文件、IP等）
  - `redirect` / `url_for`：重定向和 URL 反转
  - `flash`：闪现消息（一次性提示）
  - `g`：请求级全局对象，用于存储数据库连接
- `secure_filename`：Werkzeug 提供的安全文件名处理函数，防止上传文件名包含恶意路径。

**② 应用初始化（第7-13行）**

```python
app = Flask(__name__)
app.secret_key = 'voting-system-secret-key-2024'

DATABASE = 'voting.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
```

- `Flask(__name__)`：创建 Flask 应用实例，`__name__` 帮助 Flask 定位静态文件和模板目录。
- `secret_key`：Flask session 和 flash 消息加密所需的密钥。生产环境应使用环境变量。
- `DATABASE`：数据库文件名常量。
- `UPLOAD_FOLDER`：上传图片的保存目录。
- `ALLOWED_EXTENSIONS`：允许上传的图片扩展名集合，使用集合（set）便于快速查找。

**③ get_db() - 获取数据库连接（第16-20行）**

```python
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db
```

- **设计模式：** 请求级单例模式。利用 Flask 的 `g` 对象（每个请求独立），确保同一请求内复用同一个数据库连接，避免重复创建。
- `row_factory = sqlite3.Row`：将查询结果的行设置为可通过字段名访问（如 `poll['title']`），而不仅仅是索引访问。
- 首次调用时创建连接并存入 `g.db`，后续调用直接返回已存在的连接。

**④ close_db() - 关闭数据库连接（第23-26行）**

```python
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

- `@app.teardown_appcontext`：Flask 装饰器，注册的函数会在每次应用上下文销毁时（即请求结束时）自动调用。
- `g.pop('db', None)`：取出并移除 `g.db`，如果不存在返回 `None`。
- 确保每个请求结束后数据库连接被正确关闭，防止连接泄漏。

**⑤ init_db() - 初始化数据库（第29-56行）**

```python
def init_db():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS polls (...)''')
    db.execute('''CREATE TABLE IF NOT EXISTS options (...)''')
    db.execute('''CREATE TABLE IF NOT EXISTS votes (...)''')
    db.commit()
    db.close()
```

- `os.makedirs(UPLOAD_FOLDER, exist_ok=True)`：创建上传目录，`exist_ok=True` 表示目录已存在时不报错。
- 直接使用 `sqlite3.connect()` 而非 `get_db()`，因为此函数在应用上下文之外调用（程序启动时）。
- 三条 `CREATE TABLE IF NOT EXISTS` 语句创建三张表（详见第五章数据库设计）。
- `db.commit()` 提交建表事务，`db.close()` 关闭连接。

**⑥ allowed_file() - 检查文件扩展名（第59-60行）**

```python
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

- 逻辑：文件名中必须包含 `.`，且最后一个 `.` 后的扩展名（转小写）在允许集合中。
- 例如 `photo.JPG` → 扩展名 `jpg` → 在集合中 → 返回 `True`。
- 例如 `noext` → 不含 `.` → 返回 `False`。

**⑦ is_poll_expired() - 检查投票是否过期（第63-70行）**

```python
def is_poll_expired(poll):
    if not poll['deadline']:
        return False
    try:
        deadline_dt = datetime.strptime(poll['deadline'], '%Y-%m-%dT%H:%M')
        return deadline_dt < datetime.now()
    except (ValueError, TypeError):
        return False
```

- 如果没有设置截止时间（`deadline` 为空），返回 `False`（永不过期）。
- 使用 `strptime` 将截止时间字符串解析为 `datetime` 对象，格式 `%Y-%m-%dT%H:%M` 对应 HTML `<input type="datetime-local">` 的值格式（如 `2024-12-31T23:59`）。
- 比较截止时间与当前时间，截止时间更早则已过期。
- `try/except` 捕获格式错误，异常时返回 `False`（容错处理，不因脏数据阻断流程）。

**⑧ index() - 首页路由（第73-80行）**

```python
@app.route('/')
def index():
    db = get_db()
    polls = db.execute('''
        SELECT p.*,
               (SELECT COUNT(*) FROM votes v WHERE v.poll_id = p.id) as total_votes
        FROM polls p
        ORDER BY p.created_at DESC
    ''').fetchall()
    return render_template('index.html', polls=polls, is_poll_expired=is_poll_expired)
```

- `@app.route('/')`：注册根路径路由，支持 GET 请求。
- SQL 使用**子查询**计算每个投票的总票数：`(SELECT COUNT(*) FROM votes v WHERE v.poll_id = p.id)`。
- `ORDER BY p.created_at DESC`：按创建时间降序排列，最新的投票排在最前。
- `fetchall()` 获取所有行。
- 将 `polls` 列表和 `is_poll_expired` 函数传递给模板，模板中可直接调用该函数判断每个投票的状态。

**⑨ create() - 创建投票路由（第83-141行）**

```python
@app.route('/create', methods=['GET', 'POST'])
def create():
```

- 同时处理 GET（显示表单）和 POST（提交表单）请求。

**POST 分支解析：**

```python
title = request.form.get('title', '').strip()
description = request.form.get('description', '').strip()
deadline = request.form.get('deadline', '').strip() or None
```
- 从表单获取数据并去除首尾空格。`deadline` 为空字符串时转为 `None`（数据库存储 NULL）。

```python
if not title:
    flash('请填写投票标题', 'danger')
    return redirect(url_for('create'))
```
- 标题为空时，设置错误闪现消息并重定向回创建页面。

```python
option_texts = request.form.getlist('option_text[]')
option_descs = request.form.getlist('option_desc[]')
option_urls = request.form.getlist('option_url[]')
option_files = request.files.getlist('option_file[]')
```
- 使用 `getlist()` 获取同名的多个表单值（前端用 `option_text[]` 等数组命名）。
- 文件使用 `request.files.getlist()` 获取。

```python
options = []
for i, text in enumerate(option_texts):
    text = text.strip()
    if not text:
        continue
    ...
```
- 遍历所有选项文字，跳过空文字的选项。

```python
if file and file.filename and allowed_file(file.filename):
    filename = secure_filename(file.filename) or 'image.png'
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_url = url_for('static', filename=f'uploads/{filename}')
elif url:
    image_url = url
```
- **图片处理逻辑（优先级：上传文件 > URL）：**
  1. 如果有上传文件且扩展名合法：
     - `secure_filename()` 处理文件名（去除特殊字符，防止路径穿越攻击）
     - 如果处理后的文件名为空（如纯中文文件名），使用默认名 `image.png`
     - 在文件名前加时间戳前缀，防止重名覆盖
     - 保存到 `static/uploads/` 目录
     - 生成可通过 Flask 访问的 URL
  2. 否则如果有 URL，直接使用该 URL

```python
if len(options) < 2:
    flash('至少需要两个有效选项', 'danger')
    return redirect(url_for('create'))
```
- 后端再次校验选项数量（前端也做了校验，这是双重保险）。

```python
db = get_db()
cursor = db.execute(
    'INSERT INTO polls (title, description, deadline, created_at) VALUES (?, ?, ?, ?)',
    (title, description, deadline, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
)
poll_id = cursor.lastrowid
for text, desc, img_url in options:
    db.execute(
        'INSERT INTO options (poll_id, text, description, image_url) VALUES (?, ?, ?, ?)',
        (poll_id, text, desc, img_url)
    )
db.commit()
```
- 先插入 `polls` 记录，获取自增主键 `poll_id`。
- 再循环插入所有 `options` 记录，关联该 `poll_id`。
- `db.commit()` 一次性提交所有插入操作（事务保证原子性）。
- 使用 `?` 参数化查询，防止 SQL 注入。

**GET 分支：** `return render_template('create.html')` 直接渲染创建表单。

**⑩ detail() - 投票详情路由（第144-172行）**

```python
@app.route('/poll/<int:poll_id>')
def detail(poll_id):
```
- `<int:poll_id>` 是 Flask 的动态路由转换器，自动将 URL 中的 ID 转为整数。

```python
poll = db.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
if not poll:
    flash('投票不存在', 'danger')
    return redirect(url_for('index'))
```
- 查询投票主题，不存在则提示并重定向首页。

```python
options = db.execute('SELECT * FROM options WHERE poll_id = ?', (poll_id,)).fetchall()

total_votes = 0
option_stats = []
for opt in options:
    count = db.execute(
        'SELECT COUNT(*) as c FROM votes WHERE option_id = ?', (opt['id'],)
    ).fetchone()['c']
    total_votes += count
    option_stats.append({'option': opt, 'count': count})
```
- 查询该投票的所有选项。
- 逐个选项查询其得票数，累加总票数。
- 构建 `option_stats` 列表，每项包含选项对象和票数。

```python
for stat in option_stats:
    stat['percent'] = round(stat['count'] / total_votes * 100, 1) if total_votes > 0 else 0
```
- 计算每个选项的百分比，保留一位小数。总票数为 0 时百分比为 0（避免除零错误）。

```python
ip = request.remote_addr
voted = db.execute(
    'SELECT option_id FROM votes WHERE poll_id = ? AND ip_address = ?',
    (poll_id, ip)
).fetchone()
```
- 获取访问者 IP，查询是否已投票。如果已投，`voted` 包含所投的 `option_id`。

```python
expired = is_poll_expired(poll)

return render_template(
    'detail.html', poll=poll, option_stats=option_stats,
    total_votes=total_votes, voted=voted, is_expired=expired
)
```
- 判断是否过期，将所有数据传递给详情模板。

**⑪ vote() - 投票提交路由（第175-213行）**

```python
@app.route('/vote/<int:poll_id>', methods=['POST'])
def vote(poll_id):
```
- 仅处理 POST 请求（表单提交）。

**投票校验流程（层层把关）：**

```python
# 1. 投票是否存在
poll = db.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
if not poll:
    flash('投票不存在', 'danger')
    return redirect(url_for('index'))

# 2. 投票是否已截止
if is_poll_expired(poll):
    flash('投票已截止', 'warning')
    return redirect(url_for('detail', poll_id=poll_id))

# 3. 是否已经投过票（IP去重）
ip = request.remote_addr
existing = db.execute(
    'SELECT * FROM votes WHERE poll_id = ? AND ip_address = ?',
    (poll_id, ip)
).fetchone()
if existing:
    flash('您已经投过票了', 'warning')
    return redirect(url_for('detail', poll_id=poll_id))

# 4. 是否选择了选项
option_id = request.form.get('option_id')
if not option_id:
    flash('请选择一个选项', 'danger')
    return redirect(url_for('detail', poll_id=poll_id))

# 5. 选项是否合法（属于该投票）
opt = db.execute(
    'SELECT * FROM options WHERE id = ? AND poll_id = ?',
    (option_id, poll_id)
).fetchone()
if not opt:
    flash('无效的选项', 'danger')
    return redirect(url_for('detail', poll_id=poll_id))
```

- 五重校验确保投票的合法性和安全性。注意第 5 步同时检查 `id` 和 `poll_id`，防止跨投票提交选项。

```python
db.execute(
    'INSERT INTO votes (poll_id, option_id, ip_address, voted_at) VALUES (?, ?, ?, ?)',
    (poll_id, option_id, ip, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
)
db.commit()
flash('投票成功！', 'success')
return redirect(url_for('detail', poll_id=poll_id))
```
- 校验全部通过后，插入投票记录并提交事务。
- 设置成功消息，重定向回详情页查看结果。

**⑫ format_deadline() - 自定义模板过滤器（第216-223行）**

```python
@app.template_filter('format_deadline')
def format_deadline(deadline):
    if not deadline:
        return ''
    try:
        dt = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return deadline
```

- `@app.template_filter('format_deadline')`：注册为 Jinja2 模板过滤器，可在模板中用 `{{ poll.deadline | format_deadline }}` 调用。
- 功能：将 `2024-12-31T23:59` 格式转为更友好的 `2024-12-31 23:59` 显示格式。
- 异常时原样返回，保证容错。

**⑬ 程序入口（第226-228行）**

```python
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

- `init_db()`：启动时初始化数据库和上传目录。
- `host='0.0.0.0'`：监听所有网络接口，允许局域网内其他设备访问。
- `port=5000`：使用 5000 端口。
- `debug=True`：开启调试模式，代码修改后自动重载，出错时显示详细调试信息。**生产环境应关闭。**

---

### 6.2 style.css - 自定义样式与解析

#### 完整源代码

```css
body {
    background-color: #f5f7fa;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}
.container {
    flex-grow: 1;
}
.poll-card {
    transition: transform 0.2s, box-shadow 0.2s;
}
.poll-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.12) !important;
}
.option-image {
    max-width: 100%;
    max-height: 200px;
    border-radius: 8px;
    object-fit: cover;
    display: block;
}
.option-label {
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s, background-color 0.2s;
}
.option-label:hover {
    border-color: #0d6efd;
    box-shadow: 0 0 0 .2rem rgba(13, 110, 253, .15);
}
.option-label:has(input:checked) {
    border-color: #0d6efd;
    border-width: 2px;
    background-color: #e7f1ff;
}
.option-card {
    transition: opacity 0.2s;
}
.progress {
    height: 26px;
    border-radius: 13px;
    background-color: #e9ecef;
}
.progress-bar {
    background: linear-gradient(90deg, #0d6efd, #6610f2);
    transition: width 0.6s ease;
    font-size: .8rem;
    font-weight: 600;
    color: #fff;
    min-width: 0;
}
.progress-bar-voted {
    background: linear-gradient(90deg, #198754, #20c997);
}
.empty-state {
    padding: 4rem 1rem;
}
.result-item {
    padding: .5rem;
    border-radius: .5rem;
}
.result-item:hover {
    background-color: #f8f9fa;
}
footer {
    margin-top: auto;
}
```

#### 样式解析

| CSS 选择器/类名               | 作用解析                                                   |
| ----------------------------- | ---------------------------------------------------------- |
| `body`                        | 设置浅灰背景 `#f5f7fa`，使用 flex 布局让页脚始终贴底       |
| `.container`                  | `flex-grow: 1` 让主内容区撑满，页脚自然下沉                |
| `.poll-card` / `:hover`       | 投票卡片悬停时上移 4px 并加深阴影，产生"浮起"交互效果      |
| `.option-image`               | 选项图片限制最大高度 200px，圆角 8px，`object-fit: cover` 保持比例裁剪 |
| `.option-label` / `:hover`    | 选项卡片可点击（cursor: pointer），悬停时蓝色边框高亮      |
| `.option-label:has(input:checked)` | 使用 CSS `:has()` 伪类，当选中的 radio 在卡片内时，卡片显示蓝色高亮背景。这是较新的 CSS 特性，实现"选中即高亮" |
| `.option-card`                | 选项卡片的透明度过渡动画                                   |
| `.progress`                   | 自定义进度条高度 26px，圆角 13px                            |
| `.progress-bar`               | 进度条使用蓝紫渐变 `linear-gradient(90deg, #0d6efd, #6610f2)`，宽度变化有 0.6s 动画 |
| `.progress-bar-voted`         | 用户已投的选项使用绿青渐变 `#198754 → #20c997`，视觉区分    |
| `.empty-state`                | 空状态（暂无投票）的内边距，让空页面不显得太空              |
| `.result-item` / `:hover`     | 结果项悬停时浅灰背景，增强交互感                            |
| `footer`                      | `margin-top: auto` 配合 body 的 flex 布局，页脚自动贴底    |

---

### 6.3 base.html - 基础模板与解析

#### 完整源代码

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}投票系统{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">📊 投票系统</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navContent">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navContent">
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="{{ url_for('index') }}">首页</a>
                    <a class="nav-link" href="{{ url_for('create') }}">创建投票</a>
                </div>
            </div>
        </div>
    </nav>
    <div class="container mt-4 mb-5">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
    <footer class="text-center text-muted py-3 border-top">
        <small>Python Flask + SQLite 投票系统</small>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

#### 模板继承解析

**模板继承机制：** `base.html` 是所有页面的基础骨架，子模板通过 `{% extends 'base.html' %}` 继承它，并填充三个可覆盖的块（block）：

| 块名       | 作用                           | 覆盖的子模板              |
| ---------- | ------------------------------ | ------------------------- |
| `title`    | 页面 `<title>` 标签内容        | index.html、create.html、detail.html |
| `content`  | 页面主体内容                   | 所有子模板                |
| `scripts`  | 页面底部额外的 JavaScript      | create.html（动态选项 JS）|

**逐段解析：**

- **`<head>` 部分：** 设置字符集 UTF-8、移动端视口、Bootstrap CSS（CDN）、自定义 CSS。
- **导航栏 `<nav>`：** Bootstrap 响应式导航栏，包含品牌名"📊 投票系统"和两个链接（首页、创建投票）。在小屏幕上自动折叠为汉堡菜单。
- **闪现消息区域：** `{% with messages = get_flashed_messages(with_categories=true) %}` 获取所有 flash 消息（带分类），循环渲染为 Bootstrap alert 警告框。`with_categories=true` 使消息包含类别（success/danger/warning），对应 Bootstrap 的 `alert-success`/`alert-danger`/`alert-warning` 样式。`alert-dismissible` 让消息框可关闭。
- **内容区 `{% block content %}`：** 子模板填充的占位符。
- **页脚 `<footer>`：** 显示技术栈信息。
- **脚本：** 引入 Bootstrap JS（提供折叠、警告框关闭等交互功能），`{% block scripts %}` 供子模板追加脚本。

---

### 6.4 index.html - 首页投票列表与解析

#### 完整源代码

```html
{% extends 'base.html' %}
{% block title %}投票列表 - 投票系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="mb-0">📋 投票列表</h2>
    <a href="{{ url_for('create') }}" class="btn btn-primary">+ 创建新投票</a>
</div>
{% if polls %}
<div class="row">
    {% for poll in polls %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm poll-card">
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">{{ poll.title }}</h5>
                {% if poll.description %}
                <p class="card-text text-muted flex-grow-1">{{ poll.description[:80] }}{% if poll.description|length > 80 %}...{% endif %}</p>
                {% else %}
                <p class="card-text text-muted flex-grow-1">&nbsp;</p>
                {% endif %}
                <div class="d-flex justify-content-between text-muted small mb-2">
                    <span>📅 {{ poll.created_at[:10] }}</span>
                    <span>🗳️ {{ poll.total_votes }} 票</span>
                </div>
                <div>
                    {% if is_poll_expired(poll) %}
                    <span class="badge bg-secondary">已截止</span>
                    {% else %}
                    <span class="badge bg-success">进行中</span>
                    {% endif %}
                    {% if poll.deadline %}
                    <span class="badge bg-info text-dark">截止: {{ poll.deadline | format_deadline }}</span>
                    {% endif %}
                </div>
            </div>
            <div class="card-footer bg-transparent border-0">
                <a href="{{ url_for('detail', poll_id=poll.id) }}" class="btn btn-outline-primary btn-sm w-100">查看详情</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="text-center py-5 empty-state">
    <div class="display-4 text-muted mb-3">🗳️</div>
    <h4 class="text-muted">暂无投票</h4>
    <p class="text-muted">点击右上角"创建新投票"开始吧</p>
    <a href="{{ url_for('create') }}" class="btn btn-primary mt-2">创建第一个投票</a>
</div>
{% endif %}
{% endblock %}
```

#### 列表展示解析

- **继承基础模板：** `{% extends 'base.html' %}`，覆盖 `title` 和 `content` 块。
- **页面头部：** 左侧标题"📋 投票列表"，右侧"创建新投票"按钮，使用 flex 布局两端对齐。
- **投票列表渲染：**
  - `{% if polls %}` 判断是否有投票数据。
  - `{% for poll in polls %}` 循环渲染每个投票卡片。
  - `col-md-6 col-lg-4`：响应式栅格——大屏一行 3 个（4/12），中屏一行 2 个（6/12），小屏一行 1 个。
  - `card h-100`：卡片等高排列，`poll-card` 类添加悬停动效。
  - **标题：** `{{ poll.title }}` 直接输出。
  - **描述：** `{{ poll.description[:80] }}` 截取前 80 个字符，超过则显示 `...`（Jinja2 的切片语法）。
  - **元信息：** 创建日期（取前 10 位即日期部分）和总票数。
  - **状态标签：** 调用 `is_poll_expired(poll)` 判断，已截止显示灰色"已截止"，否则显示绿色"进行中"。有截止时间时额外显示蓝色标签。
  - **查看详情按钮：** 链接到 `detail` 路由，传递 `poll_id`。
- **空状态：** 无投票时显示居中的空状态提示，引导用户创建第一个投票。

---

### 6.5 create.html - 创建投票页面与解析

#### 完整源代码

```html
{% extends 'base.html' %}
{% block title %}创建投票 - 投票系统{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <h2 class="mb-4">✏️ 创建新投票</h2>
        <form method="POST" enctype="multipart/form-data" id="createForm">
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title mb-3">基本信息</h5>
                    <div class="mb-3">
                        <label class="form-label">投票标题 <span class="text-danger">*</span></label>
                        <input type="text" name="title" class="form-control" required placeholder="例如：本周团建吃什么？">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">投票描述（可选）</label>
                        <textarea name="description" class="form-control" rows="2" placeholder="对本次投票的补充说明"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">截止时间（可选）</label>
                        <input type="datetime-local" name="deadline" class="form-control">
                    </div>
                </div>
            </div>

            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="card-title mb-0">投票选项</h5>
                        <button type="button" class="btn btn-success btn-sm" onclick="addOption()">+ 添加选项</button>
                    </div>
                    <div id="optionsContainer"></div>
                    <small class="text-muted">至少需要两个选项，每个选项可上传图片或填写图片URL</small>
                </div>
            </div>

            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary btn-lg">✓ 创建投票</button>
                <a href="{{ url_for('index') }}" class="btn btn-outline-secondary btn-lg">取消</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
let optionIndex = 0;
function addOption() {
    const container = document.getElementById('optionsContainer');
    const div = document.createElement('div');
    div.className = 'card mb-3 option-card border-success';
    div.id = 'option-' + optionIndex;
    div.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0 text-success">选项 ${optionIndex + 1}</h6>
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeOption(${optionIndex})">🗑 删除</button>
            </div>
            <div class="mb-2">
                <input type="text" name="option_text[]" class="form-control" placeholder="选项文字（必填，如：牛、羊、张三）" required>
            </div>
            <div class="mb-2">
                <textarea name="option_desc[]" class="form-control" rows="1" placeholder="选项描述（可选）"></textarea>
            </div>
            <div class="row g-2">
                <div class="col-md-6">
                    <label class="form-label small text-muted">上传图片（可选）</label>
                    <input type="file" name="option_file[]" class="form-control form-control-sm" accept="image/*">
                </div>
                <div class="col-md-6">
                    <label class="form-label small text-muted">或填写图片URL（可选）</label>
                    <input type="url" name="option_url[]" class="form-control form-control-sm" placeholder="https://...">
                </div>
            </div>
        </div>
    `;
    container.appendChild(div);
    optionIndex++;
}
function removeOption(index) {
    const div = document.getElementById('option-' + index);
    if (div) div.remove();
}
addOption();
addOption();
document.getElementById('createForm').addEventListener('submit', function(e) {
    const options = document.querySelectorAll('.option-card input[name="option_text[]"]');
    let validCount = 0;
    options.forEach(opt => {
        if (opt.value.trim()) validCount++;
    });
    if (validCount < 2) {
        e.preventDefault();
        alert('至少需要两个有效的选项');
    }
});
</script>
{% endblock %}
```

#### 动态选项和图片上传解析

**HTML 表单部分：**

- `enctype="multipart/form-data"`：表单包含文件上传，必须设置此编码类型。
- **基本信息卡片：** 标题（必填，`required` 属性）、描述（可选）、截止时间（`type="datetime-local"` 提供日期时间选择器）。
- **投票选项卡片：** 包含一个"+ 添加选项"按钮和一个空容器 `#optionsContainer`，选项卡片由 JavaScript 动态生成。
- **提交按钮：** 创建投票和取消按钮。

**JavaScript 部分（动态选项管理）：**

- `let optionIndex = 0`：全局计数器，为每个选项分配唯一 ID。
- `addOption()` 函数：
  - 创建一个 `div` 元素，设置类名和 ID。
  - 使用模板字符串（反引号）生成 HTML 内容，包含：
    - 选项序号标题和删除按钮
    - 选项文字输入框（`name="option_text[]"`，数组命名便于后端 `getlist()` 接收）
    - 选项描述文本域（`name="option_desc[]"`）
    - 图片上传输入框（`name="option_file[]"`，`accept="image/*"` 限制只能选图片）
    - 图片 URL 输入框（`name="option_url[]"`）
  - 将 `div` 追加到容器，`optionIndex` 递增。
- `removeOption(index)` 函数：根据 ID 找到选项卡片并移除。
- `addOption(); addOption();`：页面加载时默认创建两个选项。
- **表单提交校验：** 监听表单 `submit` 事件，统计有效选项（文字非空）数量，少于 2 个时 `e.preventDefault()` 阻止提交并弹出提示。这是前端校验，与后端校验形成双重保险。

---

### 6.6 detail.html - 投票详情与结果展示与解析

#### 完整源代码

```html
{% extends 'base.html' %}
{% block title %}{{ poll.title }} - 投票系统{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <div class="mb-4">
            <h2>{{ poll.title }}</h2>
            {% if poll.description %}
            <p class="text-muted lead fs-6">{{ poll.description }}</p>
            {% endif %}
            <div class="d-flex flex-wrap gap-3 text-muted small">
                <span>📅 创建于 {{ poll.created_at }}</span>
                <span>🗳️ 总票数: {{ total_votes }}</span>
                {% if poll.deadline %}
                <span>⏰ 截止: {{ poll.deadline | format_deadline }}</span>
                {% endif %}
            </div>
        </div>

        {% if is_expired %}
        <div class="alert alert-warning">⚠️ 此投票已截止</div>
        {% endif %}

        {% if voted and not is_expired %}
        <div class="alert alert-info">✅ 您已投过票，以下是当前结果</div>
        {% endif %}

        {% if not voted and not is_expired %}
        <form method="POST" action="{{ url_for('vote', poll_id=poll.id) }}" id="voteForm">
            <h4 class="mb-3">请选择一个选项：</h4>
            <div class="row">
                {% for stat in option_stats %}
                <div class="col-md-6 mb-3">
                    <label class="card option-label h-100">
                        <div class="card-body">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="option_id" value="{{ stat.option.id }}" id="opt-{{ stat.option.id }}" required>
                                <label class="form-check-label fw-bold fs-5" for="opt-{{ stat.option.id }}">{{ stat.option.text }}</label>
                            </div>
                            {% if stat.option.description %}
                            <p class="text-muted small mt-1 mb-0">{{ stat.option.description }}</p>
                            {% endif %}
                            {% if stat.option.image_url %}
                            <img src="{{ stat.option.image_url }}" class="option-image mt-2" alt="{{ stat.option.text }}">
                            {% endif %}
                        </div>
                    </label>
                </div>
                {% endfor %}
            </div>
            <button type="submit" class="btn btn-primary btn-lg">🗳️ 提交投票</button>
        </form>
        <hr class="my-4">
        {% endif %}

        <h4 class="mb-3">📊 投票结果</h4>
        {% if total_votes > 0 %}
        <div class="results">
            {% for stat in option_stats %}
            <div class="mb-3 result-item">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-bold">{{ stat.option.text }}</span>
                    <span class="text-muted">{{ stat.count }} 票 · {{ stat.percent }}%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar {% if voted and voted.option_id == stat.option.id %}progress-bar-voted{% endif %}" role="progressbar" style="width: {{ stat.percent }}%;" aria-valuenow="{{ stat.percent }}" aria-valuemin="0" aria-valuemax="100">{{ stat.percent }}%</div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="text-muted">暂无投票数据，快来成为第一个投票的人吧！</p>
        {% endif %}

        <hr class="my-4">
        <a href="{{ url_for('index') }}" class="btn btn-outline-secondary">← 返回首页</a>
    </div>
</div>
{% endblock %}
```

#### 投票和结果展示解析

**页面结构分为四个区域：**

**① 投票信息头部：**
- 显示投票标题、描述、创建时间、总票数、截止时间。
- 使用 `format_deadline` 过滤器格式化截止时间。

**② 状态提示区域：**
- `{% if is_expired %}`：投票已截止时显示黄色警告框。
- `{% if voted and not is_expired %}`：已投票且未截止时显示蓝色提示框。

**③ 投票表单区域（条件渲染）：**
- `{% if not voted and not is_expired %}`：**只有未投票且未截止时才显示投票表单**。这是核心的条件判断。
- 表单提交到 `vote` 路由，方法 POST。
- `{% for stat in option_stats %}` 循环渲染每个选项卡片：
  - 使用 `<label>` 包裹 `<input type="radio">`，实现点击整个卡片即可选中。
  - `option-label` 类提供悬停和选中高亮样式。
  - 显示选项文字、描述和图片（如果有）。
  - `required` 确保必须选择一个选项。

**④ 投票结果区域：**
- `{% if total_votes > 0 %}`：有投票数据时显示结果。
- `{% for stat in option_stats %}` 循环渲染每个选项的结果：
  - 上方显示选项名称和"X 票 · Y%"。
  - 下方是 Bootstrap 进度条，`style="width: {{ stat.percent }}%;"` 设置宽度。
  - `{% if voted and voted.option_id == stat.option.id %}progress-bar-voted{% endif %}`：如果用户投了这个选项，进度条使用绿色渐变样式（`progress-bar-voted`），其他选项使用蓝紫渐变。这让用户一眼看到自己的选择。
- 无投票数据时显示提示文案。
- 底部"返回首页"按钮。

---

## 七、关键功能实现详解

### 7.1 投票去重机制（IP限制）

**实现目标：** 防止同一用户对同一投票重复投票。

**技术方案：** 基于 IP 地址 + 数据库唯一约束双重保障。

**实现细节：**

1. **应用层检查（前置校验）：**

```python
# vote() 路由中
ip = request.remote_addr  # 获取访问者 IP
existing = db.execute(
    'SELECT * FROM votes WHERE poll_id = ? AND ip_address = ?',
    (poll_id, ip)
).fetchone()
if existing:
    flash('您已经投过票了', 'warning')
    return redirect(url_for('detail', poll_id=poll_id))
```

在写入投票记录前，先查询 `votes` 表中是否已存在"该投票 + 该 IP"的记录。如果存在，直接返回提示，不执行插入。

2. **数据库层约束（后置保障）：**

```sql
UNIQUE(poll_id, ip_address)
```

`votes` 表上的联合唯一约束是最后一道防线。即使应用层检查被绕过（如并发请求），数据库也会拒绝重复插入并抛出 `IntegrityError`。

3. **详情页状态判断：**

```python
# detail() 路由中
ip = request.remote_addr
voted = db.execute(
    'SELECT option_id FROM votes WHERE poll_id = ? AND ip_address = ?',
    (poll_id, ip)
).fetchone()
```

详情页也查询当前 IP 是否已投票，将结果传给模板，模板据此决定显示投票表单还是只显示结果。

**局限性说明：**
- 同一局域网内多台设备可能共享同一个公网 IP，会被误判为同一用户。
- 使用代理或 VPN 的用户可能 IP 不固定。
- 这是教学项目的简化方案，生产环境应结合 Cookie/Session + 用户登录实现更精确的去重。

### 7.2 图片上传处理

**实现目标：** 允许用户为投票选项上传本地图片或提供图片 URL。

**技术方案：** Flask 文件上传 + Werkzeug 安全文件名 + 时间戳防重名。

**完整处理流程：**

```
前端 <input type="file" name="option_file[]">
                    │
                    ▼
表单以 multipart/form-data 提交
                    │
                    ▼
后端 request.files.getlist('option_file[]') 获取文件列表
                    │
                    ▼
遍历每个文件，检查 allowed_file(filename)
                    │(合法)
                    ▼
secure_filename(file.filename) 处理安全文件名
                    │
                    ▼
添加时间戳前缀: 20241207143012345678_photo.jpg
                    │
                    ▼
file.save() 保存到 static/uploads/ 目录
                    │
                    ▼
url_for('static', filename='uploads/...') 生成访问 URL
                    │
                    ▼
URL 存入 options.image_url 字段
```

**关键代码解析：**

```python
if file and file.filename and allowed_file(file.filename):
    filename = secure_filename(file.filename) or 'image.png'
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_url = url_for('static', filename=f'uploads/{filename}')
elif url:
    image_url = url
```

- `secure_filename()` 的作用：将 `../../../etc/passwd` 这样的恶意文件名转为安全的形式，防止目录穿越攻击。对于纯中文文件名（如 `图片.png`），处理结果可能为空，此时用 `or 'image.png'` 提供默认名。
- 时间戳前缀 `%Y%m%d%H%M%S%f` 精确到微秒，确保文件名唯一，避免不同用户上传同名文件互相覆盖。
- **优先级逻辑：** 如果同时提供了上传文件和 URL，优先使用上传文件（`if ... elif url`）。

**前端配合：**

```html
<input type="file" name="option_file[]" class="form-control form-control-sm" accept="image/*">
```

- `accept="image/*"` 限制文件选择器只显示图片文件。
- `name="option_file[]"` 数组命名，配合 `getlist()` 接收多文件。

### 7.3 实时结果计算

**实现目标：** 投票后立即看到最新的统计结果，包括各选项票数和百分比。

**技术方案：** 每次访问详情页时实时查询和计算，无缓存。

**计算流程：**

```python
# detail() 路由中

# 第一步：查询所有选项
options = db.execute('SELECT * FROM options WHERE poll_id = ?', (poll_id,)).fetchall()

# 第二步：逐个选项统计票数
total_votes = 0
option_stats = []
for opt in options:
    count = db.execute(
        'SELECT COUNT(*) as c FROM votes WHERE option_id = ?', (opt['id'],)
    ).fetchone()['c']
    total_votes += count
    option_stats.append({'option': opt, 'count': count})

# 第三步：计算百分比
for stat in option_stats:
    stat['percent'] = round(stat['count'] / total_votes * 100, 1) if total_votes > 0 else 0
```

**解析：**
1. 查询该投票的所有选项。
2. 对每个选项执行 `COUNT(*)` 查询其得票数，累加得到总票数。
3. 计算每个选项的百分比：`count / total_votes * 100`，`round(..., 1)` 保留一位小数。
4. **除零保护：** `if total_votes > 0 else 0`，当还没有人投票时百分比为 0，避免 `ZeroDivisionError`。

**前端展示：**

```html
<div class="progress">
    <div class="progress-bar" style="width: {{ stat.percent }}%;">
        {{ stat.percent }}%
    </div>
</div>
```

- Bootstrap 进度条通过 `width` 样式控制宽度，CSS 添加了 `transition: width 0.6s ease` 动画，票数变化时进度条平滑过渡。
- 用户自己投的选项使用绿色渐变（`progress-bar-voted`），其他选项使用蓝紫渐变，视觉区分明显。

**"实时"的含义：** 本系统不需要 WebSocket 或 AJAX 轮询。因为投票后通过 `redirect` 跳回详情页，服务端重新查询并渲染最新数据，用户看到的就是实时结果。这种"PRG 模式"（Post-Redirect-Get）既实现了实时更新，又避免了重复提交问题。

### 7.4 数据库连接管理

**实现目标：** 高效管理数据库连接，避免频繁创建/关闭的开销和连接泄漏。

**技术方案：** 基于 Flask `g` 对象的请求级单例模式 + `teardown_appcontext` 自动清理。

**设计模式图解：**

```
请求开始
    │
    ▼
路由函数调用 get_db()
    │
    ├── g 中没有 'db' → 创建新连接 → 存入 g.db → 返回连接
    │
    └── g 中已有 'db' → 直接返回 g.db（复用）
    │
    ▼
路由函数执行完毕，可能多次调用 get_db() 都复用同一连接
    │
    ▼
请求结束，触发 teardown_appcontext
    │
    ▼
close_db() 执行：g.pop('db') → db.close() 关闭连接
```

**关键代码：**

```python
def get_db():
    if 'db' not in g:           # 检查是否已存在连接
        g.db = sqlite3.connect(DATABASE)  # 创建新连接
        g.db.row_factory = sqlite3.Row    # 设置行工厂
    return g.db                 # 返回连接（新建或复用）

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)      # 取出并移除连接
    if db is not None:
        db.close()              # 关闭连接
```

**为什么这样设计？**

1. **`g` 对象的特性：** Flask 的 `g`（global）对象在**每个请求**中是独立的，请求结束后自动清理。将数据库连接存入 `g`，可以确保：
   - 同一请求内复用连接（避免多次 `sqlite3.connect()` 的开销）
   - 不同请求之间隔离（避免多线程共享连接的并发问题）

2. **`row_factory = sqlite3.Row`：** 让查询结果可以通过字段名访问（`poll['title']`），而非默认的索引访问（`poll[1]`），代码更可读。

3. **`teardown_appcontext` 的可靠性：** 无论请求成功还是抛出异常，`teardown_appcontext` 注册的函数都会执行，确保连接一定被关闭，防止泄漏。

4. **`g.pop('db', None)` 的安全性：** 使用 `pop` 而非 `get`，取出后即从 `g` 中移除。`None` 默认值防止 `g` 中没有 `db` 时抛出 `AttributeError`。

---

## 八、项目运行说明

### 8.1 环境要求

| 软件     | 版本要求       | 说明                         |
| -------- | -------------- | ---------------------------- |
| Python   | 3.7 及以上     | 需要支持 f-string 等特性     |
| pip      | 随 Python 安装 | 用于安装 Flask               |
| Flask    | 2.x 及以上     | Web 框架                     |
| 浏览器   | 现代浏览器     | Chrome/Firefox/Edge/Safari   |

**操作系统：** Windows / macOS / Linux 均可。

### 8.2 安装步骤

**第一步：获取项目代码**

```bash
# 方式一：从 GitHub 克隆
git clone https://github.com/520maodizhang/online-voting-system.git
cd online-voting-system

# 方式二：直接下载源码压缩包并解压
```

**第二步：创建虚拟环境（推荐）**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**第三步：安装依赖**

```bash
pip install flask
```

> Flask 安装时会自动安装 Werkzeug、Jinja2 等依赖。SQLite 驱动 `sqlite3` 是 Python 标准库，无需安装。

### 8.3 启动命令

```bash
python app.py
```

启动成功后会显示类似输出：

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

打开浏览器访问 **http://127.0.0.1:5000** 即可使用。

> 如果在局域网内其他设备访问，使用本机 IP 替换 127.0.0.1，如 http://192.168.1.100:5000。

### 8.4 使用流程

1. **访问首页：** 打开 http://127.0.0.1:5000，看到投票列表（首次使用为空）。
2. **创建投票：** 点击"+ 创建新投票"，填写标题、描述、截止时间，添加至少两个选项（可上传图片），点击"创建投票"。
3. **参与投票：** 在首页点击"查看详情"进入投票页面，选择一个选项，点击"提交投票"。
4. **查看结果：** 投票后自动显示结果，各选项的票数和百分比以进度条展示。
5. **分享投票：** 将详情页的 URL 分享给他人，他人打开即可投票（需在同一局域网或部署到公网）。

---

## 九、项目亮点与不足

### 9.1 项目亮点

| 亮点               | 说明                                                                 |
| ------------------ | -------------------------------------------------------------------- |
| **零配置启动**     | 只需 `pip install flask` + `python app.py`，数据库和目录自动创建      |
| **代码结构清晰**   | 单文件后端 + 模板继承，逻辑分层明确，适合教学                        |
| **双重校验机制**   | 前端 JS + 后端 Python 双重校验，保证数据合法性                       |
| **IP 去重 + DB 约束** | 应用层检查 + 数据库唯一约束，双重防止重复投票                        |
| **图片安全处理**   | `secure_filename` 防目录穿越 + 时间戳防重名 + 扩展名白名单           |
| **响应式设计**     | Bootstrap 5 栅格系统，手机/平板/桌面自适应                           |
| **交互体验好**     | 卡片悬停动效、选项选中高亮、进度条动画、闪现消息提示                 |
| **PRG 模式**       | Post-Redirect-Get 模式，避免重复提交，投票后实时看到结果             |
| **容错处理**       | 时间解析 try/except、除零保护、空值处理，代码健壮                    |
| **参数化查询**     | 所有 SQL 使用 `?` 占位符，防止 SQL 注入攻击                          |

### 9.2 局限性

| 局限性                 | 说明                                                         |
| ---------------------- | ------------------------------------------------------------ |
| **IP 去重精度有限**    | 局域网共享 IP 会误判，代理/VPN 导致 IP 不固定                |
| **无用户认证**         | 没有登录注册功能，无法精确识别用户身份                       |
| **无后台管理**         | 无法编辑/删除已创建的投票，无法管理选项                       |
| **单选投票**           | 目前只支持单选，不支持多选、排序投票等复杂场景               |
| **无防刷票机制**       | 除了 IP 限制外，没有验证码、频率限制等防刷手段               |
| **secret_key 硬编码**  | 密钥直接写在代码中，生产环境应使用环境变量                   |
| **debug 模式**         | 默认开启 debug 模式，生产环境需关闭                          |
| **无分页功能**         | 投票数量多时首页一次性加载全部，无分页                       |
| **图片无压缩**         | 上传图片原样保存，大图片会占用较多存储和带宽                 |
| **无数据备份**         | SQLite 单文件，无自动备份机制                                |

### 9.3 改进方向

| 改进方向               | 具体方案                                                     |
| ---------------------- | ------------------------------------------------------------ |
| **用户系统**           | 添加注册/登录功能，基于用户 ID 去重更精确                     |
| **多选投票**           | 支持多选、限制选择数量、排序投票等模式                        |
| **后台管理**           | 添加管理页面，支持编辑/删除投票、查看统计图表                 |
| **防刷票**             | 添加验证码、投票频率限制、Cookie + IP 双重去重               |
| **部署优化**           | 使用 Gunicorn/uWSGI 部署，关闭 debug，secret_key 用环境变量   |
| **数据库升级**         | 迁移到 MySQL/PostgreSQL，使用 SQLAlchemy ORM                  |
| **分页与搜索**         | 首页添加分页和搜索功能，支持按状态/时间筛选                   |
| **图片优化**           | 上传时自动压缩/裁剪，生成缩略图，支持对象存储（如 OSS/S3）    |
| **实时通知**           | 使用 WebSocket 实时推送投票结果更新                           |
| **数据可视化**         | 添加饼图/柱状图展示结果（如使用 Chart.js）                    |
| **API 接口**           | 提供 RESTful API，支持第三方调用和移动端接入                  |

---

> 本文档由项目开发者编写，用于向指导老师汇报讲解网络投票系统的设计与实现。文档涵盖项目概述、设计思路、技术选型、系统架构、数据库设计、完整源代码逐行解析、关键功能详解、运行说明及项目评估，力求全面且通俗易懂。
