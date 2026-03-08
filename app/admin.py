import json
import os
import shutil
from datetime import datetime
from functools import wraps

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for, Response)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.forms import AdminUserForm, EditProfileForm
from app.models import MedicalAnalysis, User

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Профиль ─────────────────────────────────────────────────────────────────

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        # Проверка уникальности username
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('Это имя пользователя уже занято.', 'danger')
                return render_template('admin/profile.html', form=form)

        # Проверка уникальности email
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('Этот email уже зарегистрирован.', 'danger')
                return render_template('admin/profile.html', form=form)

        # Смена пароля
        if form.new_password.data:
            if not form.current_password.data:
                flash('Введите текущий пароль для его смены.', 'danger')
                return render_template('admin/profile.html', form=form)
            if not current_user.check_password(form.current_password.data):
                flash('Текущий пароль неверен.', 'danger')
                return render_template('admin/profile.html', form=form)
            current_user.set_password(form.new_password.data)

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Профиль успешно обновлён.', 'success')
        return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html', form=form)


# ── Управление пользователями (только для администратора) ───────────────────

@admin_bp.route('/admin/users')
@login_required
@admin_required
def user_list():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_new():
    form = AdminUserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Новый пользователь')
        if User.query.filter_by(email=form.email.data).first():
            flash('Email уже зарегистрирован.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Новый пользователь')
        if not form.password.data:
            flash('Пароль обязателен при создании пользователя.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Новый пользователь')

        user = User(username=form.username.data, email=form.email.data,
                    is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Пользователь «{user.username}» создан.', 'success')
        return redirect(url_for('admin.user_list'))

    return render_template('admin/user_form.html', form=form, title='Новый пользователь')


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm()

    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin

    if form.validate_on_submit():
        if form.username.data != user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('Имя пользователя уже занято.', 'danger')
                return render_template('admin/user_form.html', form=form,
                                       title=f'Редактирование: {user.username}', user=user)
        if form.email.data != user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email уже зарегистрирован.', 'danger')
                return render_template('admin/user_form.html', form=form,
                                       title=f'Редактирование: {user.username}', user=user)

        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash(f'Пользователь «{user.username}» обновлён.', 'success')
        return redirect(url_for('admin.user_list'))

    return render_template('admin/user_form.html', form=form,
                           title=f'Редактирование: {user.username}', user=user)


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Нельзя удалить собственную учётную запись.', 'danger')
        return redirect(url_for('admin.user_list'))

    username = user.username
    MedicalAnalysis.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь «{username}» и все его анализы удалены.', 'success')
    return redirect(url_for('admin.user_list'))


# ── Импорт / Экспорт БД ─────────────────────────────────────────────────────

_ANALYSIS_FIELDS = [
    'date', 'diet', 'glucose', 'triglycerides', 'hdl', 'total_cholesterol',
    'vldl', 'ldl', 'alt', 'creatinine', 'ast', 'de_ritis_ratio', 'ldl_hdl_ratio',
    'esr', 'hemoglobin', 'rbc', 'hematocrit', 'mcv', 'mch', 'mchc', 'rdw',
    'platelets', 'mpv', 'pdw', 'pct', 'wbc',
    'neutrophils_abs', 'neutrophils_pct', 'lymphocytes_abs', 'lymphocytes_pct',
    'monocytes_abs', 'monocytes_pct', 'eosinophils_abs', 'eosinophils_pct',
    'basophils_abs', 'basophils_pct',
    'bilirubin_total', 'bilirubin_direct', 'bilirubin_indirect',
    'alkaline_phosphatase', 'urea', 'gfr', 'ckf_total', 'psa', 'microalbumin',
    'urine_specific_gravity', 'urine_ph', 'urine_protein', 'urine_urobilinogen',
    'urine_glucose', 'urine_bilirubin', 'urine_ketones', 'urine_blood',
    'urine_leukocytes_semi', 'urine_leukocytes_micro',
    'urine_erythrocytes_changed', 'urine_erythrocytes_unchanged',
    'urine_nitrites', 'urine_cylinders_hyaline', 'urine_cylinders_granular',
    'urine_cylinders_waxy', 'urine_cylinders_epithelial', 'urine_cylinders_leukocyte',
    'urine_trichomonas', 'urine_yeast', 'urine_bacteria', 'urine_mucus',
    'urine_phosphates_amorphous', 'urine_urates', 'urine_crystals_triplephosphate',
    'urine_crystals_uric_acid', 'urine_crystals_oxalate',
    'urine_epithelium_renal', 'urine_epithelium_transitional', 'urine_spermatozoa',
    'urine_epithelium_flat', 'urine_color', 'urine_transparency',
    'hbs_ag', 'hiv_ab', 'hepatitis_c_ab', 'treponema_ab',
]


def _analysis_to_dict(a):
    d = {'id': a.id}
    for f in _ANALYSIS_FIELDS:
        v = getattr(a, f, None)
        if isinstance(v, datetime):
            v = v.strftime('%d.%m.%Y')
        d[f] = v
    return d


@admin_bp.route('/admin/db')
@login_required
def db_page():
    return render_template('admin/db.html')


@admin_bp.route('/admin/db/export')
@login_required
def db_export():
    if current_user.is_admin:
        # Полный экспорт SQLite-файла
        db_path = os.path.join(current_app.instance_path, 'medical_analyses.db')
        return send_file(db_path, as_attachment=True,
                         download_name='medical_analyses_backup.db',
                         mimetype='application/octet-stream')
    else:
        # Экспорт своих анализов в JSON
        analyses = current_user.analyses.order_by(MedicalAnalysis.date.asc()).all()
        data = [_analysis_to_dict(a) for a in analyses]
        payload = json.dumps({
            'exported_at': datetime.utcnow().isoformat(),
            'username': current_user.username,
            'analyses': data,
        }, ensure_ascii=False, indent=2)
        return Response(
            payload,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=my_analyses.json'},
        )


@admin_bp.route('/admin/db/import', methods=['POST'])
@login_required
def db_import():
    f = request.files.get('import_file')
    if not f or f.filename == '':
        flash('Файл не выбран.', 'danger')
        return redirect(url_for('admin.db_page'))

    filename = secure_filename(f.filename)

    if current_user.is_admin and filename.lower().endswith('.db'):
        db_path = os.path.join(current_app.instance_path, 'medical_analyses.db')
        backup_path = db_path + '.bak'
        shutil.copy2(db_path, backup_path)
        f.save(db_path)
        db.engine.dispose()
        flash('База данных импортирована. Предыдущая сохранена как .bak.', 'success')
        return redirect(url_for('admin.db_page'))

    if filename.lower().endswith('.json'):
        try:
            raw = json.loads(f.read().decode('utf-8'))
            entries = raw.get('analyses', raw) if isinstance(raw, dict) else raw
            count = 0
            for entry in entries:
                kwargs = {}
                for field in _ANALYSIS_FIELDS:
                    if field not in entry:
                        continue
                    val = entry[field]
                    if field == 'date' and val:
                        try:
                            val = datetime.strptime(val, '%d.%m.%Y')
                        except ValueError:
                            val = datetime.fromisoformat(val)
                    kwargs[field] = val
                db.session.add(MedicalAnalysis(user_id=current_user.id, **kwargs))
                count += 1
            db.session.commit()
            flash(f'Импортировано {count} анализов.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка импорта: {e}', 'danger')
        return redirect(url_for('admin.db_page'))

    flash('Поддерживаются файлы .json или .db (только для администратора).', 'danger')
    return redirect(url_for('admin.db_page'))
