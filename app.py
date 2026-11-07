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
