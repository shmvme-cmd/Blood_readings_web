from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import MedicalAnalysis, BodyMeasurement
from app.forms import AnalysisForm, BodyMeasurementForm, HeightForm
from app.norms import MedicalNorms
from app.pdf_parser import parse_pdf

main_bp = Blueprint('main', __name__)
norms = MedicalNorms()


@main_bp.route('/')
def index():
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    analyses = current_user.analyses.order_by(MedicalAnalysis.date.desc()).all()
    return render_template('dashboard.html', analyses=analyses)


@main_bp.route('/analyses')
@login_required
def list_analyses():
    analyses = current_user.analyses.order_by(MedicalAnalysis.date.desc()).all()
    return render_template('analyses/list.html', analyses=analyses, norms=norms)


@main_bp.route('/analyses/add', methods=['GET', 'POST'])
@login_required
def add_analysis():
    form = AnalysisForm()
    if form.validate_on_submit():
        try:
            # Calculate derived values
            ast = form.ast.data
            alt = form.alt.data
            ldl = form.ldl.data
            hdl = form.hdl.data
            insulin = form.insulin.data
            glucose = form.glucose.data

            de_ritis_ratio = ast / alt if (ast is not None and alt) else None
            ldl_hdl_ratio = ldl / hdl if (ldl is not None and hdl) else None
            homa_ir = form.homa_ir.data
            if homa_ir is None and insulin is not None and glucose is not None:
                homa_ir = round(insulin * glucose / 22.5, 3)

            analysis = MedicalAnalysis(
                date=datetime.strptime(form.date.data, '%d.%m.%Y'),
                diet=form.diet.data,
                glucose=form.glucose.data,
                triglycerides=form.triglycerides.data,
                hdl=hdl,
                total_cholesterol=form.total_cholesterol.data,
                vldl=form.vldl.data,
                ldl=ldl,
                alt=alt,
                creatinine=form.creatinine.data,
                ast=ast,
                de_ritis_ratio=de_ritis_ratio,
                ldl_hdl_ratio=ldl_hdl_ratio,
                esr=form.esr.data,
                hemoglobin=form.hemoglobin.data,
                rbc=form.rbc.data,
                hematocrit=form.hematocrit.data,
                mcv=form.mcv.data,
                mch=form.mch.data,
                mchc=form.mchc.data,
                rdw=form.rdw.data,
                platelets=form.platelets.data,
                mpv=form.mpv.data,
                pdw=form.pdw.data,
                pct=form.pct.data,
                wbc=form.wbc.data,
                neutrophils_abs=form.neutrophils_abs.data,
                neutrophils_pct=form.neutrophils_pct.data,
                lymphocytes_abs=form.lymphocytes_abs.data,
                lymphocytes_pct=form.lymphocytes_pct.data,
                monocytes_abs=form.monocytes_abs.data,
                monocytes_pct=form.monocytes_pct.data,
                eosinophils_abs=form.eosinophils_abs.data,
                eosinophils_pct=form.eosinophils_pct.data,
                basophils_abs=form.basophils_abs.data,
                basophils_pct=form.basophils_pct.data,
                albumin=form.albumin.data,
                total_protein=form.total_protein.data,
                ggt=form.ggt.data,
                potassium=form.potassium.data,
                calcium=form.calcium.data,
                sodium=form.sodium.data,
                phosphorus=form.phosphorus.data,
                chloride=form.chloride.data,
                bilirubin_total=form.bilirubin_total.data,
                bilirubin_direct=form.bilirubin_direct.data,
                bilirubin_indirect=form.bilirubin_indirect.data,
                alkaline_phosphatase=form.alkaline_phosphatase.data,
                urea=form.urea.data,
                gfr=form.gfr.data,
                ckf_total=form.ckf_total.data,
                psa=form.psa.data,
                microalbumin=form.microalbumin.data,
                ferritin=form.ferritin.data,
                insulin=insulin,
                homa_ir=homa_ir,
                vitamin_d=form.vitamin_d.data,
                nechiporenko_leukocytes=form.nechiporenko_leukocytes.data,
                nechiporenko_erythrocytes=form.nechiporenko_erythrocytes.data,
                nechiporenko_cylinders=form.nechiporenko_cylinders.data,
                urine_specific_gravity=form.urine_specific_gravity.data,
                urine_ph=form.urine_ph.data,
                urine_protein=form.urine_protein.data,
                urine_urobilinogen=form.urine_urobilinogen.data,
                urine_glucose=form.urine_glucose.data,
                urine_bilirubin=form.urine_bilirubin.data,
                urine_ketones=form.urine_ketones.data,
                urine_blood=form.urine_blood.data,
                urine_leukocytes_semi=form.urine_leukocytes_semi.data,
                urine_leukocytes_micro=form.urine_leukocytes_micro.data,
                urine_erythrocytes_changed=form.urine_erythrocytes_changed.data,
                urine_erythrocytes_unchanged=form.urine_erythrocytes_unchanged.data,
                urine_nitrites=form.urine_nitrites.data,
                urine_cylinders_hyaline=form.urine_cylinders_hyaline.data,
                urine_cylinders_granular=form.urine_cylinders_granular.data,
                urine_cylinders_waxy=form.urine_cylinders_waxy.data,
                urine_cylinders_epithelial=form.urine_cylinders_epithelial.data,
                urine_cylinders_leukocyte=form.urine_cylinders_leukocyte.data,
                urine_trichomonas=form.urine_trichomonas.data,
                urine_yeast=form.urine_yeast.data,
                urine_bacteria=form.urine_bacteria.data,
                urine_mucus=form.urine_mucus.data,
                urine_phosphates_amorphous=form.urine_phosphates_amorphous.data,
                urine_urates=form.urine_urates.data,
                urine_crystals_triplephosphate=form.urine_crystals_triplephosphate.data,
                urine_crystals_uric_acid=form.urine_crystals_uric_acid.data,
                urine_crystals_oxalate=form.urine_crystals_oxalate.data,
                urine_epithelium_renal=form.urine_epithelium_renal.data,
                urine_epithelium_transitional=form.urine_epithelium_transitional.data,
                urine_spermatozoa=form.urine_spermatozoa.data,
                urine_epithelium_flat=form.urine_epithelium_flat.data,
                urine_color=form.urine_color.data or None,
                urine_transparency=form.urine_transparency.data or None,
                hbs_ag=form.hbs_ag.data or None,
                hiv_ab=form.hiv_ab.data or None,
                hepatitis_c_ab=form.hepatitis_c_ab.data or None,
                treponema_ab=form.treponema_ab.data or None,
                user_id=current_user.id
            )

            db.session.add(analysis)
            db.session.commit()
            flash('Анализ успешно добавлен!', 'success')
            return redirect(url_for('main.list_analyses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении анализа: {str(e)}', 'danger')

    return render_template('analyses/add.html', form=form, norms=norms)


@main_bp.route('/analyses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_analysis(id):
    analysis = MedicalAnalysis.query.get_or_404(id)
    if analysis.user_id != current_user.id:
        flash('У вас нет прав для редактирования этого анализа', 'danger')
        return redirect(url_for('main.list_analyses'))

    form = AnalysisForm(obj=analysis)
    form.date.data = analysis.date.strftime('%d.%m.%Y')
    if request.method == 'GET':
        form.diet.data = analysis.diet or 'none'

    if form.validate_on_submit():
        try:
            # Update analysis data
            analysis.date = datetime.strptime(form.date.data, '%d.%m.%Y')
            analysis.diet = form.diet.data
            analysis.glucose = form.glucose.data
            analysis.triglycerides = form.triglycerides.data
            analysis.hdl = form.hdl.data
            analysis.total_cholesterol = form.total_cholesterol.data
            analysis.vldl = form.vldl.data
            analysis.ldl = form.ldl.data
            analysis.alt = form.alt.data
            analysis.creatinine = form.creatinine.data
            analysis.ast = form.ast.data
            analysis.esr = form.esr.data
            analysis.hemoglobin = form.hemoglobin.data
            analysis.rbc = form.rbc.data
            analysis.hematocrit = form.hematocrit.data
            analysis.mcv = form.mcv.data
            analysis.mch = form.mch.data
            analysis.mchc = form.mchc.data
            analysis.rdw = form.rdw.data
            analysis.platelets = form.platelets.data
            analysis.mpv = form.mpv.data
            analysis.pdw = form.pdw.data
            analysis.pct = form.pct.data
            analysis.wbc = form.wbc.data
            analysis.neutrophils_abs = form.neutrophils_abs.data
            analysis.neutrophils_pct = form.neutrophils_pct.data
            analysis.lymphocytes_abs = form.lymphocytes_abs.data
            analysis.lymphocytes_pct = form.lymphocytes_pct.data
            analysis.monocytes_abs = form.monocytes_abs.data
            analysis.monocytes_pct = form.monocytes_pct.data
            analysis.eosinophils_abs = form.eosinophils_abs.data
            analysis.eosinophils_pct = form.eosinophils_pct.data
            analysis.basophils_abs = form.basophils_abs.data
            analysis.basophils_pct = form.basophils_pct.data
            analysis.albumin = form.albumin.data
            analysis.total_protein = form.total_protein.data
            analysis.ggt = form.ggt.data
            analysis.potassium = form.potassium.data
            analysis.calcium = form.calcium.data
            analysis.sodium = form.sodium.data
            analysis.phosphorus = form.phosphorus.data
            analysis.chloride = form.chloride.data
            analysis.bilirubin_total = form.bilirubin_total.data
            analysis.bilirubin_direct = form.bilirubin_direct.data
            analysis.bilirubin_indirect = form.bilirubin_indirect.data
            analysis.alkaline_phosphatase = form.alkaline_phosphatase.data
            analysis.urea = form.urea.data
            analysis.gfr = form.gfr.data
            analysis.ckf_total = form.ckf_total.data
            analysis.psa = form.psa.data
            analysis.microalbumin = form.microalbumin.data
            analysis.ferritin = form.ferritin.data
            analysis.insulin = form.insulin.data
            _homa = form.homa_ir.data
            if _homa is None and form.insulin.data is not None and form.glucose.data is not None:
                _homa = round(form.insulin.data * form.glucose.data / 22.5, 3)
            analysis.homa_ir = _homa
            analysis.vitamin_d = form.vitamin_d.data
            analysis.nechiporenko_leukocytes = form.nechiporenko_leukocytes.data
            analysis.nechiporenko_erythrocytes = form.nechiporenko_erythrocytes.data
            analysis.nechiporenko_cylinders = form.nechiporenko_cylinders.data
            analysis.urine_specific_gravity = form.urine_specific_gravity.data
            analysis.urine_ph = form.urine_ph.data
            analysis.urine_protein = form.urine_protein.data
            analysis.urine_urobilinogen = form.urine_urobilinogen.data
            analysis.urine_glucose = form.urine_glucose.data
            analysis.urine_bilirubin = form.urine_bilirubin.data
            analysis.urine_ketones = form.urine_ketones.data
            analysis.urine_blood = form.urine_blood.data
            analysis.urine_leukocytes_semi = form.urine_leukocytes_semi.data
            analysis.urine_leukocytes_micro = form.urine_leukocytes_micro.data
            analysis.urine_erythrocytes_changed = form.urine_erythrocytes_changed.data
            analysis.urine_erythrocytes_unchanged = form.urine_erythrocytes_unchanged.data
            analysis.urine_nitrites = form.urine_nitrites.data
            analysis.urine_cylinders_hyaline = form.urine_cylinders_hyaline.data
            analysis.urine_cylinders_granular = form.urine_cylinders_granular.data
            analysis.urine_cylinders_waxy = form.urine_cylinders_waxy.data
            analysis.urine_cylinders_epithelial = form.urine_cylinders_epithelial.data
            analysis.urine_cylinders_leukocyte = form.urine_cylinders_leukocyte.data
            analysis.urine_trichomonas = form.urine_trichomonas.data
            analysis.urine_yeast = form.urine_yeast.data
            analysis.urine_bacteria = form.urine_bacteria.data
            analysis.urine_mucus = form.urine_mucus.data
            analysis.urine_phosphates_amorphous = form.urine_phosphates_amorphous.data
            analysis.urine_urates = form.urine_urates.data
            analysis.urine_crystals_triplephosphate = form.urine_crystals_triplephosphate.data
            analysis.urine_crystals_uric_acid = form.urine_crystals_uric_acid.data
            analysis.urine_crystals_oxalate = form.urine_crystals_oxalate.data
            analysis.urine_epithelium_renal = form.urine_epithelium_renal.data
            analysis.urine_epithelium_transitional = form.urine_epithelium_transitional.data
            analysis.urine_spermatozoa = form.urine_spermatozoa.data
            analysis.urine_epithelium_flat = form.urine_epithelium_flat.data
            analysis.urine_color = form.urine_color.data or None
            analysis.urine_transparency = form.urine_transparency.data or None
            analysis.hbs_ag = form.hbs_ag.data or None
            analysis.hiv_ab = form.hiv_ab.data or None
            analysis.hepatitis_c_ab = form.hepatitis_c_ab.data or None
            analysis.treponema_ab = form.treponema_ab.data or None

            # Recalculate derived values
            analysis.de_ritis_ratio = analysis.ast / analysis.alt if (analysis.ast is not None and analysis.alt) else None
            analysis.ldl_hdl_ratio = analysis.ldl / analysis.hdl if (analysis.ldl is not None and analysis.hdl) else None

            db.session.commit()
            flash('Анализ успешно обновлён!', 'success')
            return redirect(url_for('main.list_analyses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении анализа: {str(e)}', 'danger')

    return render_template('analyses/edit.html', form=form, analysis=analysis, norms=norms)


@main_bp.route('/analyses/<int:id>/delete', methods=['POST'])
@login_required
def delete_analysis(id):
    analysis = MedicalAnalysis.query.get_or_404(id)
    if analysis.user_id != current_user.id:
        flash('У вас нет прав для удаления этого анализа', 'danger')
        return redirect(url_for('main.list_analyses'))

    try:
        db.session.delete(analysis)
        db.session.commit()
        flash('Анализ успешно удалён!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении анализа: {str(e)}', 'danger')

    return redirect(url_for('main.list_analyses'))


_NUMERIC_FIELDS = [
    'glucose', 'triglycerides', 'hdl', 'total_cholesterol', 'vldl', 'ldl',
    'alt', 'creatinine', 'ast', 'de_ritis_ratio', 'ldl_hdl_ratio',
    'esr', 'hemoglobin', 'rbc', 'hematocrit', 'mcv', 'mch', 'mchc', 'rdw',
    'platelets', 'mpv', 'pdw', 'pct', 'wbc',
    'neutrophils_abs', 'neutrophils_pct', 'lymphocytes_abs', 'lymphocytes_pct',
    'monocytes_abs', 'monocytes_pct', 'eosinophils_abs', 'eosinophils_pct',
    'basophils_abs', 'basophils_pct',
    'albumin', 'total_protein', 'ggt', 'potassium', 'calcium', 'sodium', 'phosphorus', 'chloride',
    'bilirubin_total', 'bilirubin_direct', 'bilirubin_indirect',
    'alkaline_phosphatase', 'urea', 'gfr', 'ckf_total', 'psa', 'microalbumin',
    'ferritin', 'insulin', 'homa_ir', 'vitamin_d',
    'nechiporenko_leukocytes', 'nechiporenko_erythrocytes', 'nechiporenko_cylinders',
    'urine_specific_gravity', 'urine_ph', 'urine_protein', 'urine_urobilinogen',
]


@main_bp.route('/analyses/merge', methods=['POST'])
@login_required
def merge_analyses():
    raw_ids = request.form.getlist('ids[]')
    date_str = request.form.get('merge_date', '').strip()
    diet = request.form.get('diet', 'none')

    if len(raw_ids) < 2:
        flash('Выберите минимум 2 анализа для объединения.', 'warning')
        return redirect(url_for('main.list_analyses'))

    try:
        merge_date = datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        flash('Неверный формат даты. Используйте ДД.ММ.ГГГГ.', 'danger')
        return redirect(url_for('main.list_analyses'))

    try:
        int_ids = [int(i) for i in raw_ids]
    except ValueError:
        flash('Некорректные идентификаторы анализов.', 'danger')
        return redirect(url_for('main.list_analyses'))

    analyses = (MedicalAnalysis.query
                .filter(MedicalAnalysis.id.in_(int_ids),
                        MedicalAnalysis.user_id == current_user.id)
                .order_by(MedicalAnalysis.date.desc())
                .all())

    if len(analyses) < 2:
        flash('Не удалось найти выбранные анализы.', 'danger')
        return redirect(url_for('main.list_analyses'))

    # Для каждого поля берём первое ненулевое значение (новейший анализ приоритетнее)
    merged_fields = {}
    for field in _NUMERIC_FIELDS:
        for a in analyses:
            val = getattr(a, field)
            if val is not None:
                merged_fields[field] = val
                break

    try:
        merged = MedicalAnalysis(user_id=current_user.id, date=merge_date,
                                 diet=diet, **merged_fields)
        for a in analyses:
            db.session.delete(a)
        db.session.add(merged)
        db.session.commit()
        flash(
            f'Объединено {len(analyses)} анализов в одну запись от '
            f'{merge_date.strftime("%d.%m.%Y")}.',
            'success'
        )
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при объединении: {str(e)}', 'danger')

    return redirect(url_for('main.list_analyses'))


@main_bp.route('/analyses/parse-pdf', methods=['POST'])
@login_required
def parse_pdf_route():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'Файл не передан'}), 400
    f = request.files['pdf_file']
    if not f.filename or not f.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Допустимы только PDF-файлы'}), 400
    try:
        data = parse_pdf(f.stream)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'Ошибка при разборе PDF: {str(e)}'}), 500


@main_bp.route('/analyses/chart-data')
@login_required
def chart_data():
    analyses = current_user.analyses.order_by(MedicalAnalysis.date.asc()).all()
    data = [{
        'date': a.date.strftime('%d.%m.%Y'),
        'glucose': a.glucose,
        'triglycerides': a.triglycerides,
        'hdl': a.hdl,
        'total_cholesterol': a.total_cholesterol,
        'vldl': a.vldl,
        'ldl': a.ldl,
        'alt': a.alt,
        'creatinine': a.creatinine,
        'ast': a.ast,
        'de_ritis_ratio': a.de_ritis_ratio,
        'ldl_hdl_ratio': a.ldl_hdl_ratio,
        'esr': a.esr,
        'hemoglobin': a.hemoglobin,
        'rbc': a.rbc,
        'hematocrit': a.hematocrit,
        'mcv': a.mcv,
        'mch': a.mch,
        'mchc': a.mchc,
        'rdw': a.rdw,
        'platelets': a.platelets,
        'mpv': a.mpv,
        'pdw': a.pdw,
        'pct': a.pct,
        'wbc': a.wbc,
        'neutrophils_abs': a.neutrophils_abs,
        'neutrophils_pct': a.neutrophils_pct,
        'lymphocytes_abs': a.lymphocytes_abs,
        'lymphocytes_pct': a.lymphocytes_pct,
        'monocytes_abs': a.monocytes_abs,
        'monocytes_pct': a.monocytes_pct,
        'eosinophils_abs': a.eosinophils_abs,
        'eosinophils_pct': a.eosinophils_pct,
        'basophils_abs': a.basophils_abs,
        'basophils_pct': a.basophils_pct,
        'albumin': a.albumin,
        'total_protein': a.total_protein,
        'ggt': a.ggt,
        'potassium': a.potassium,
        'calcium': a.calcium,
        'sodium': a.sodium,
        'phosphorus': a.phosphorus,
        'chloride': a.chloride,
        'bilirubin_total': a.bilirubin_total,
        'bilirubin_direct': a.bilirubin_direct,
        'bilirubin_indirect': a.bilirubin_indirect,
        'alkaline_phosphatase': a.alkaline_phosphatase,
        'urea': a.urea,
        'gfr': a.gfr,
        'ckf_total': a.ckf_total,
        'psa': a.psa,
        'microalbumin': a.microalbumin,
        'ferritin': a.ferritin,
        'insulin': a.insulin,
        'homa_ir': a.homa_ir,
        'vitamin_d': a.vitamin_d,
        'nechiporenko_leukocytes': a.nechiporenko_leukocytes,
        'nechiporenko_erythrocytes': a.nechiporenko_erythrocytes,
        'nechiporenko_cylinders': a.nechiporenko_cylinders,
        'urine_specific_gravity': a.urine_specific_gravity,
        'urine_ph': a.urine_ph,
        'urine_protein': a.urine_protein,
        'urine_urobilinogen': a.urine_urobilinogen,
    } for a in analyses]
    return jsonify(data)


@main_bp.route('/analyses/<int:id>')
@login_required
def view_analysis(id):
    analysis = MedicalAnalysis.query.get_or_404(id)
    if analysis.user_id != current_user.id:
        flash('У вас нет прав для просмотра этого анализа', 'danger')
        return redirect(url_for('main.list_analyses'))

    return render_template('analyses/view.html', analysis=analysis, norms=norms)


# ─────────────────────────────────────────────
#  Параметры тела / Похудение
# ─────────────────────────────────────────────

import math as _math


def _calc_visceral(measurements, height_cm, gender, latest_analysis):
    """Возвращает словарь с висцеральными индексами.
    Для каждого индекса ищет последний замер с достаточными данными.
    Возвращает дату замера если она отличается от последнего замера.
    """
    result = {'vai': None, 'vfa': None, 'c_index': None,
              'vai_risk': None, 'vfa_risk': None, 'c_risk': None,
              'c_date': None, 'vfa_date': None, 'vai_date': None}
    if not measurements or not height_cm:
        return result

    latest_id = measurements[0].id

    def _stale_date(m):
        return m.date if m.id != latest_id else None

    # --- C-index: нужны талия + вес ---
    m_c = next((m for m in measurements if m.waist and m.weight), None)
    if m_c:
        h_m = height_cm / 100
        wc_m = m_c.waist / 100
        denom = 0.109 * _math.sqrt(m_c.weight / h_m)
        if denom > 0:
            ci = round(wc_m / denom, 3)
            result['c_index'] = ci
            result['c_date'] = _stale_date(m_c)
            if gender == 'female':
                result['c_risk'] = 'ok' if ci < 1.18 else ('warn' if ci < 1.30 else 'high')
            else:
                result['c_risk'] = 'ok' if ci < 1.25 else ('warn' if ci < 1.35 else 'high')

    # --- VFA: нужна только талия ---
    m_vfa = next((m for m in measurements if m.waist), None)
    if m_vfa:
        if gender == 'female':
            vfa = round(1.26 * m_vfa.waist - 13.0, 1)
        else:
            vfa = round(1.47 * m_vfa.waist - 23.8, 1)
        result['vfa'] = vfa
        result['vfa_date'] = _stale_date(m_vfa)
        result['vfa_risk'] = 'ok' if vfa < 100 else ('warn' if vfa < 160 else 'high')

    # --- VAI: нужны талия + вес + TG + HDL из крови ---
    m_vai = next((m for m in measurements if m.waist and m.weight), None)
    if (m_vai and latest_analysis and
            latest_analysis.triglycerides and latest_analysis.hdl):
        h_m = height_cm / 100
        bmi = m_vai.weight / (h_m * h_m)
        tg = latest_analysis.triglycerides
        hdl = latest_analysis.hdl
        if gender == 'female':
            vai = round((m_vai.waist / (36.58 + 1.89 * bmi)) * (tg / 0.81) * (1.52 / hdl), 2)
            result['vai_risk'] = 'ok' if vai < 1.52 else ('warn' if vai < 2.53 else 'high')
        else:
            vai = round((m_vai.waist / (39.68 + 1.88 * bmi)) * (tg / 1.03) * (1.31 / hdl), 2)
            result['vai_risk'] = 'ok' if vai < 1.0 else ('warn' if vai < 2.52 else 'high')
        result['vai'] = vai
        result['vai_date'] = _stale_date(m_vai)

    return result


@main_bp.route('/body', methods=['GET', 'POST'])
@login_required
def body():
    form = BodyMeasurementForm()
    height_form = HeightForm()

    if form.validate_on_submit() and 'save_measurement' in request.form:
        try:
            raw_date = (form.date.data or '').strip()
            date_obj = None
            for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y'):
                try:
                    date_obj = datetime.strptime(raw_date, fmt)
                    break
                except ValueError:
                    continue
            if date_obj is None:
                date_obj = datetime.today()
            m = BodyMeasurement(
                date=date_obj,
                weight=form.weight.data,
                waist=form.waist.data,
                hips=form.hips.data,
                neck=form.neck.data,
                forearm=form.forearm.data,
                wrist=form.wrist.data,
                thigh=form.thigh.data,
                shin=form.shin.data,
                abdomen=form.abdomen.data,
                chest=form.chest.data,
                body_fat=form.body_fat.data,
                user_id=current_user.id,
            )
            db.session.add(m)
            db.session.commit()
            flash('Замер сохранён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
        return redirect(url_for('main.body'))

    if height_form.validate_on_submit() and 'save_height' in request.form:
        try:
            current_user.height = height_form.height.data
            if height_form.gender.data:
                current_user.gender = height_form.gender.data
            db.session.commit()
            flash('Данные сохранены!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
        return redirect(url_for('main.body'))

    measurements = (current_user.body_measurements
                    .order_by(BodyMeasurement.date.desc()).all())
    height_form.height.data = current_user.height
    height_form.gender.data = current_user.gender or ''
    if not form.date.data:
        form.date.data = datetime.today().strftime('%d.%m.%Y')

    # Данные для графика
    chart = [{
        'date': m.date.strftime('%d.%m.%Y'),
        'weight': m.weight,
        'waist': m.waist,
        'hips': m.hips,
        'neck': m.neck,
        'forearm': m.forearm,
        'wrist': m.wrist,
        'thigh': m.thigh,
        'shin': m.shin,
        'abdomen': m.abdomen,
        'chest': m.chest,
        'body_fat': m.body_fat,
    } for m in reversed(measurements)]

    # Последний анализ крови для VAI
    latest_analysis = (current_user.analyses
                       .order_by(MedicalAnalysis.date.desc()).first())

    # Висцеральные индексы (ищет последний замер с нужными данными для каждого)
    visceral = _calc_visceral(
        measurements,
        current_user.height,
        current_user.gender,
        latest_analysis,
    )

    # Последние замеры с достаточными данными для каждой карточки
    # (measurements отсортированы по убыванию даты)
    gender = current_user.gender
    last_bmi = next((m for m in measurements if m.weight), None)
    if gender == 'female':
        last_navy = next((m for m in measurements if m.waist and m.neck and m.hips), None)
    else:
        last_navy = next((m for m in measurements if m.waist and m.neck), None)
    last_whr = next((m for m in measurements if m.waist and m.hips), None)

    return render_template('body/index.html',
                           form=form, height_form=height_form,
                           measurements=measurements,
                           chart_data=chart,
                           height=current_user.height,
                           gender=gender,
                           latest_analysis=latest_analysis,
                           visceral=visceral,
                           last_bmi=last_bmi,
                           last_navy=last_navy,
                           last_whr=last_whr)


@main_bp.route('/body/<int:id>/edit', methods=['POST'])
@login_required
def edit_body(id):
    m = BodyMeasurement.query.get_or_404(id)
    if m.user_id != current_user.id:
        flash('Нет прав для редактирования', 'danger')
        return redirect(url_for('main.body'))
    form = BodyMeasurementForm()
    if form.validate_on_submit():
        try:
            raw_date = (form.date.data or '').strip()
            date_obj = None
            for fmt in ('%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y'):
                try:
                    date_obj = datetime.strptime(raw_date, fmt)
                    break
                except ValueError:
                    continue
            if date_obj is None:
                date_obj = m.date
            m.date = date_obj
            m.weight = form.weight.data
            m.waist = form.waist.data
            m.hips = form.hips.data
            m.neck = form.neck.data
            m.forearm = form.forearm.data
            m.wrist = form.wrist.data
            m.thigh = form.thigh.data
            m.shin = form.shin.data
            m.abdomen = form.abdomen.data
            m.chest = form.chest.data
            m.body_fat = form.body_fat.data
            db.session.commit()
            flash('Замер обновлён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    return redirect(url_for('main.body'))


@main_bp.route('/body/<int:id>/delete', methods=['POST'])
@login_required
def delete_body(id):
    m = BodyMeasurement.query.get_or_404(id)
    if m.user_id != current_user.id:
        flash('Нет прав для удаления', 'danger')
        return redirect(url_for('main.body'))
    try:
        db.session.delete(m)
        db.session.commit()
        flash('Замер удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    return redirect(url_for('main.body'))


# ---------------------------------------------------------------------------
# AI-анализ
# ---------------------------------------------------------------------------

def _build_ai_prompt(analysis):
    """Строит промпт для LLM на основе данных анализа."""
    diet_labels = {
        'none': 'Обычное питание',
        'intermittent_fasting': 'Интервальное голодание',
        'keto': 'Кето-диета',
        'low_carb': 'Низкоуглеводная диета',
        'vegetarian': 'Вегетарианство',
        'vegan': 'Веганство',
        'other': 'Другое',
    }

    lines = [
        f'Дата анализа: {analysis.date.strftime("%d.%m.%Y")}',
        f'Тип питания: {diet_labels.get(analysis.diet or "none", analysis.diet or "не указано")}',
        '',
        'РЕЗУЛЬТАТЫ АНАЛИЗОВ:',
    ]

    data = analysis.to_dict()
    skip = {'id', 'date', 'diet', 'de_ritis_ratio', 'ldl_hdl_ratio'}
    serology_keys = {'hbs_ag', 'hiv_ab', 'hepatitis_c_ab', 'treponema_ab'}
    serology_labels = {
        'hbs_ag': 'HBs-антиген (гепатит B)',
        'hiv_ab': 'Антитела/антиген HIV',
        'hepatitis_c_ab': 'Антитела к Hepatitis C',
        'treponema_ab': 'Антитела к Treponema pallidum',
    }

    out_of_range, in_range, sero_lines = [], [], []

    for key, value in data.items():
        if key in skip or value is None:
            continue
        if key in serology_keys:
            sero_lines.append(f'  {serology_labels[key]}: {"ПОЛОЖИТЕЛЬНЫЙ ⚠️" if value else "Отрицательный"}')
            continue

        norm = norms.get_norm(key)
        if not norm:
            continue

        low, high = norm['range']
        is_bad = (low is not None and value < low) or (high is not None and value > high)
        norm_str = f"{low if low is not None else '—'}–{high if high is not None else '—'} {norm['unit']}"
        row = f'  {norm["name"]}: {value:.2f} {norm["unit"]} (норма: {norm_str}) — {"⚠️ ВНЕ НОРМЫ" if is_bad else "✓ норма"}'
        (out_of_range if is_bad else in_range).append(row)

    if out_of_range:
        lines += ['\n--- Показатели ВНЕ НОРМЫ ---'] + out_of_range
    if in_range:
        lines += ['\n--- Показатели в норме ---'] + in_range
    if sero_lines:
        lines += ['\n--- Серология ---'] + sero_lines

    if analysis.ast and analysis.alt:
        dr = round(analysis.ast / analysis.alt, 2)
        lines.append(f'\n  Коэффициент Де Ритиса (АСТ/АЛТ): {dr} (норма: 0.8–1.33)')
    if analysis.ldl and analysis.hdl:
        lh = round(analysis.ldl / analysis.hdl, 2)
        lines.append(f'  Коэффициент ЛПНП/ЛПВП: {lh} (норма: ≤3.5)')

    lines += [
        '',
        'Дай структурированный анализ на русском языке:',
        '1. **Общий вывод** (2-3 предложения — общее состояние по результатам)',
        '2. **Разбор отклонений** (для каждого показателя вне нормы: что означает, возможные причины)',
        '3. **Связи между показателями** (паттерны, синдромы, риски)',
        '4. **Рекомендации** (питание, образ жизни, какие дополнительные анализы сдать)',
        '5. **Важно** (краткое напоминание о консультации врача)',
        '',
        'Используй заголовки разделов. Будь конкретным и информативным, но понятным для пациента без медицинского образования.',
    ]

    return '\n'.join(lines)


@main_bp.route('/analyses/<int:id>/ai', methods=['POST'])
@login_required
def analysis_ai(id):
    """Запрос AI-интерпретации анализа через Groq API."""
    from flask import current_app
    analysis = MedicalAnalysis.query.get_or_404(id)
    if analysis.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещён'}), 403

    regenerate = request.json and request.json.get('regenerate')

    if analysis.ai_analysis and not regenerate:
        return jsonify({'text': analysis.ai_analysis, 'cached': True})

    api_key = current_app.config.get('GROQ_API_KEY', '').strip()
    if not api_key:
        return jsonify({'error': 'GROQ_API_KEY не настроен. Добавьте ключ в файл .env'}), 500

    prompt = _build_ai_prompt(analysis)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'Ты — опытный врач-терапевт и клинический лабораторный диагност. '
                        'Анализируй медицинские результаты точно, структурированно и понятно для пациента. '
                        'Отвечай только на русском языке. Используй Markdown для форматирования. '
                        'Всегда указывай, что окончательная интерпретация требует очной консультации врача.'
                    ),
                },
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.3,
            max_tokens=2500,
        )
        text = resp.choices[0].message.content
        analysis.ai_analysis = text
        db.session.commit()
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500