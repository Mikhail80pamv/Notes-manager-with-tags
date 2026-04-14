from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.models import User, Note
from app.forms import RegistrationForm, LoginForm, NoteForm

# Создаём Blueprint с именем 'main'
main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
@main.route('/index')
def index():
    if current_user.is_authenticated:
        notes = current_user.notes.order_by(Note.updated_at.desc()).all()
        tag_filter = request.args.get('tag')
        if tag_filter:
            notes = [note for note in notes if tag_filter in note.get_tags_list()]
        return render_template('index.html', title='Мои заметки', notes=notes, tag_filter=tag_filter)
    return render_template('index.html', title='Добро пожаловать')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались! Теперь можете войти.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Регистрация', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            flash('Вы успешно вошли!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Неверный email или пароль.', 'danger')
    return render_template('login.html', title='Вход', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/note/new', methods=['GET', 'POST'])
@login_required
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(title=form.title.data, body=form.body.data, tags=form.tags.data, author=current_user)
        db.session.add(note)
        db.session.commit()
        flash('Заметка создана!', 'success')
        return redirect(url_for('main.index'))
    return render_template('note_form.html', title='Новая заметка', form=form, legend='Новая заметка')

@main.route('/note/<int:note_id>')
@login_required
def note_detail(note_id):
    note = Note.query.get_or_404(note_id)
    if note.author != current_user:
        abort(403)
    return render_template('note_detail.html', title=note.title, note=note)

@main.route('/note/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.author != current_user:
        abort(403)
    form = NoteForm()
    if form.validate_on_submit():
        note.title = form.title.data
        note.body = form.body.data
        note.tags = form.tags.data
        db.session.commit()
        flash('Заметка обновлена!', 'success')
        return redirect(url_for('main.note_detail', note_id=note.id))
    elif request.method == 'GET':
        form.title.data = note.title
        form.body.data = note.body
        form.tags.data = note.tags
    return render_template('note_form.html', title='Редактирование', form=form, legend='Редактировать заметку')

@main.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.author != current_user:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Заметка удалена.', 'info')
    return redirect(url_for('main.index'))