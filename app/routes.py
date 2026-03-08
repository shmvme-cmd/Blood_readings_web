from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import MedicalAnalysis
from app.forms import AnalysisForm
from app.norms import MedicalNorms
from app.pdf_parser import parse_pdf

main_bp = Blueprint('main', __name__)
norms = MedicalNorms()


@main_bp.route('/')
def index():
    return render_template('index.html')


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

            de_ritis_ratio = ast / alt if (ast is not None and alt) else None
            ldl_hdl_ratio = ldl / hdl if (ldl is not None and hdl) else None

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
                bilirubin_total=form.bilirubin_total.data,
                bilirubin_direct=form.bilirubin_direct.data,
                bilirubin_indirect=form.bilirubin_indirect.data,
                alkaline_phosphatase=form.alkaline_phosphatase.data,
                urea=form.urea.data,
                gfr=form.gfr.data,
                ckf_total=form.ckf_total.data,
                psa=form.psa.data,
                microalbumin=form.microalbumin.data,
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
            analysis.bilirubin_total = form.bilirubin_total.data
            analysis.bilirubin_direct = form.bilirubin_direct.data
            analysis.bilirubin_indirect = form.bilirubin_indirect.data
            analysis.alkaline_phosphatase = form.alkaline_phosphatase.data
            analysis.urea = form.urea.data
            analysis.gfr = form.gfr.data
            analysis.ckf_total = form.ckf_total.data
            analysis.psa = form.psa.data
            analysis.microalbumin = form.microalbumin.data
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
    'bilirubin_total', 'bilirubin_direct', 'bilirubin_indirect',
    'alkaline_phosphatase', 'urea', 'gfr', 'ckf_total', 'psa', 'microalbumin',
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
        'bilirubin_total': a.bilirubin_total,
        'bilirubin_direct': a.bilirubin_direct,
        'bilirubin_indirect': a.bilirubin_indirect,
        'alkaline_phosphatase': a.alkaline_phosphatase,
        'urea': a.urea,
        'gfr': a.gfr,
        'ckf_total': a.ckf_total,
        'psa': a.psa,
        'microalbumin': a.microalbumin,
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