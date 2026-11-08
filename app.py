import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

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
            created_at TEXT NOT NULL,
            creator_id INTEGER,
            FOREIGN KEY (creator_id) REFERENCES users(id)
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
            user_id INTEGER NOT NULL,
            voted_at TEXT NOT NULL,
            UNIQUE(poll_id, user_id),
            FOREIGN KEY (poll_id) REFERENCES polls(id),
            FOREIGN KEY (option_id) REFERENCES options(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    # [NEW] users 表：存用户名和密码哈希
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
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


# [NEW] 登录验证装饰器：没登录就跳转到登录页
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


# [NEW] 获取当前登录用户
def get_current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    return db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()


# [NEW] 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('register'))

        if len(username) < 2:
            flash('用户名至少2个字符', 'danger')
            return redirect(url_for('register'))

        if len(password) < 4:
            flash('密码至少4个字符', 'danger')
            return redirect(url_for('register'))

        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('用户名已存在，请换一个', 'danger')
            return redirect(url_for('register'))

        db.execute(
            'INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        db.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# [NEW] 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# [NEW] 登出路由
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录', 'info')
    return redirect(url_for('index'))


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


# [CHANGED] 创建投票需要登录
@app.route('/create', methods=['GET', 'POST'])
@login_required
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
        # [CHANGED] 存入创建者ID
        cursor = db.execute(
            'INSERT INTO polls (title, description, deadline, created_at, creator_id) VALUES (?, ?, ?, ?, ?)',
            (title, description, deadline, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session['user_id'])
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

    # [CHANGED] 用 user_id 查是否已投票，而不是 IP
    voted = None
    if 'user_id' in session:
        voted = db.execute(
            'SELECT option_id FROM votes WHERE poll_id = ? AND user_id = ?',
            (poll_id, session['user_id'])
        ).fetchone()

    expired = is_poll_expired(poll)

    return render_template(
        'detail.html', poll=poll, option_stats=option_stats,
        total_votes=total_votes, voted=voted, is_expired=expired
    )


# [CHANGED] 投票需要登录，用 user_id 去重
@app.route('/vote/<int:poll_id>', methods=['POST'])
@login_required
def vote(poll_id):
    db = get_db()
    poll = db.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    if not poll:
        flash('投票不存在', 'danger')
        return redirect(url_for('index'))

    if is_poll_expired(poll):
        flash('投票已截止', 'warning')
        return redirect(url_for('detail', poll_id=poll_id))

    # [CHANGED] 用 user_id 检查是否已投票
    existing = db.execute(
        'SELECT * FROM votes WHERE poll_id = ? AND user_id = ?',
        (poll_id, session['user_id'])
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

    # [CHANGED] 存入 user_id 而不是 IP
    db.execute(
        'INSERT INTO votes (poll_id, option_id, user_id, voted_at) VALUES (?, ?, ?, ?)',
        (poll_id, option_id, session['user_id'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
