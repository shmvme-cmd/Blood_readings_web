from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False, server_default='0')
    analyses = db.relationship('MedicalAnalysis', backref='patient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MedicalAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)
    diet = db.Column(db.String(32), default='none')
    glucose = db.Column(db.Float)
    triglycerides = db.Column(db.Float)
    hdl = db.Column(db.Float)
    total_cholesterol = db.Column(db.Float)
    vldl = db.Column(db.Float)
    ldl = db.Column(db.Float)
    alt = db.Column(db.Float)
    creatinine = db.Column(db.Float)
    ast = db.Column(db.Float)
    de_ritis_ratio = db.Column(db.Float)
    ldl_hdl_ratio = db.Column(db.Float)
    # Клинический анализ крови
    esr = db.Column(db.Float)
    hemoglobin = db.Column(db.Float)
    rbc = db.Column(db.Float)
    hematocrit = db.Column(db.Float)
    mcv = db.Column(db.Float)
    mch = db.Column(db.Float)
    mchc = db.Column(db.Float)
    rdw = db.Column(db.Float)
    platelets = db.Column(db.Float)
    mpv = db.Column(db.Float)
    pdw = db.Column(db.Float)
    pct = db.Column(db.Float)
    wbc = db.Column(db.Float)
    neutrophils_abs = db.Column(db.Float)
    neutrophils_pct = db.Column(db.Float)
    lymphocytes_abs = db.Column(db.Float)
    lymphocytes_pct = db.Column(db.Float)
    monocytes_abs = db.Column(db.Float)
    monocytes_pct = db.Column(db.Float)
    eosinophils_abs = db.Column(db.Float)
    eosinophils_pct = db.Column(db.Float)
    basophils_abs = db.Column(db.Float)
    basophils_pct = db.Column(db.Float)
    # Биохимия дополнительная
    bilirubin_total        = db.Column(db.Float)
    bilirubin_direct       = db.Column(db.Float)
    bilirubin_indirect     = db.Column(db.Float)
    alkaline_phosphatase   = db.Column(db.Float)
    urea                   = db.Column(db.Float)
    gfr                    = db.Column(db.Float)
    ckf_total              = db.Column(db.Float)
    psa                    = db.Column(db.Float)
    microalbumin           = db.Column(db.Float)
    # Анализ мочи
    urine_specific_gravity       = db.Column(db.Float)
    urine_ph                     = db.Column(db.Float)
    urine_protein                = db.Column(db.Float)
    urine_urobilinogen           = db.Column(db.Float)
    urine_glucose                = db.Column(db.Float)
    urine_bilirubin              = db.Column(db.Float)
    urine_ketones                = db.Column(db.Float)
    urine_blood                  = db.Column(db.Float)
    urine_leukocytes_semi        = db.Column(db.Float)
    urine_leukocytes_micro       = db.Column(db.Float)
    urine_erythrocytes_changed   = db.Column(db.Float)
    urine_erythrocytes_unchanged = db.Column(db.Float)
    # Качественные параметры мочи
    urine_nitrites                 = db.Column(db.Float)
    urine_cylinders_hyaline        = db.Column(db.Float)
    urine_cylinders_granular       = db.Column(db.Float)
    urine_cylinders_waxy           = db.Column(db.Float)
    urine_cylinders_epithelial     = db.Column(db.Float)
    urine_cylinders_leukocyte      = db.Column(db.Float)
    urine_trichomonas              = db.Column(db.Float)
    urine_yeast                    = db.Column(db.Float)
    urine_bacteria                 = db.Column(db.Float)
    urine_mucus                    = db.Column(db.Float)
    urine_phosphates_amorphous     = db.Column(db.Float)
    urine_urates                   = db.Column(db.Float)
    urine_crystals_triplephosphate = db.Column(db.Float)
    urine_crystals_uric_acid       = db.Column(db.Float)
    urine_crystals_oxalate         = db.Column(db.Float)
    urine_epithelium_renal         = db.Column(db.Float)
    urine_epithelium_transitional  = db.Column(db.Float)
    urine_spermatozoa              = db.Column(db.Float)
    urine_epithelium_flat          = db.Column(db.Float)
    urine_color                    = db.Column(db.String(64))
    urine_transparency             = db.Column(db.String(64))
    # Серологические тесты (качественные: True=положительный, False=отрицательный)
    hbs_ag         = db.Column(db.Boolean)
    hiv_ab         = db.Column(db.Boolean)
    hepatitis_c_ab = db.Column(db.Boolean)
    treponema_ab   = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%d.%m.%Y'),
            'diet': self.diet,
            'glucose': self.glucose,
            'triglycerides': self.triglycerides,
            'hdl': self.hdl,
            'total_cholesterol': self.total_cholesterol,
            'vldl': self.vldl,
            'ldl': self.ldl,
            'alt': self.alt,
            'creatinine': self.creatinine,
            'ast': self.ast,
            'de_ritis_ratio': self.de_ritis_ratio,
            'ldl_hdl_ratio': self.ldl_hdl_ratio,
            'esr': self.esr,
            'hemoglobin': self.hemoglobin,
            'rbc': self.rbc,
            'hematocrit': self.hematocrit,
            'mcv': self.mcv,
            'mch': self.mch,
            'mchc': self.mchc,
            'rdw': self.rdw,
            'platelets': self.platelets,
            'mpv': self.mpv,
            'pdw': self.pdw,
            'pct': self.pct,
            'wbc': self.wbc,
            'neutrophils_abs': self.neutrophils_abs,
            'neutrophils_pct': self.neutrophils_pct,
            'lymphocytes_abs': self.lymphocytes_abs,
            'lymphocytes_pct': self.lymphocytes_pct,
            'monocytes_abs': self.monocytes_abs,
            'monocytes_pct': self.monocytes_pct,
            'eosinophils_abs': self.eosinophils_abs,
            'eosinophils_pct': self.eosinophils_pct,
            'basophils_abs': self.basophils_abs,
            'basophils_pct': self.basophils_pct,
            'bilirubin_total': self.bilirubin_total,
            'bilirubin_direct': self.bilirubin_direct,
            'bilirubin_indirect': self.bilirubin_indirect,
            'alkaline_phosphatase': self.alkaline_phosphatase,
            'urea': self.urea,
            'gfr': self.gfr,
            'ckf_total': self.ckf_total,
            'psa': self.psa,
            'microalbumin': self.microalbumin,
            'urine_specific_gravity': self.urine_specific_gravity,
            'urine_ph': self.urine_ph,
            'urine_protein': self.urine_protein,
            'urine_urobilinogen':           self.urine_urobilinogen,
            'urine_glucose':                self.urine_glucose,
            'urine_bilirubin':              self.urine_bilirubin,
            'urine_ketones':                self.urine_ketones,
            'urine_blood':                  self.urine_blood,
            'urine_leukocytes_semi':        self.urine_leukocytes_semi,
            'urine_leukocytes_micro':       self.urine_leukocytes_micro,
            'urine_erythrocytes_changed':   self.urine_erythrocytes_changed,
            'urine_erythrocytes_unchanged': self.urine_erythrocytes_unchanged,
            'urine_nitrites':                 self.urine_nitrites,
            'urine_cylinders_hyaline':        self.urine_cylinders_hyaline,
            'urine_cylinders_granular':       self.urine_cylinders_granular,
            'urine_cylinders_waxy':           self.urine_cylinders_waxy,
            'urine_cylinders_epithelial':     self.urine_cylinders_epithelial,
            'urine_cylinders_leukocyte':      self.urine_cylinders_leukocyte,
            'urine_trichomonas':              self.urine_trichomonas,
            'urine_yeast':                    self.urine_yeast,
            'urine_bacteria':                 self.urine_bacteria,
            'urine_mucus':                    self.urine_mucus,
            'urine_phosphates_amorphous':     self.urine_phosphates_amorphous,
            'urine_urates':                   self.urine_urates,
            'urine_crystals_triplephosphate': self.urine_crystals_triplephosphate,
            'urine_crystals_uric_acid':       self.urine_crystals_uric_acid,
            'urine_crystals_oxalate':         self.urine_crystals_oxalate,
            'urine_epithelium_renal':         self.urine_epithelium_renal,
            'urine_epithelium_transitional':  self.urine_epithelium_transitional,
            'urine_spermatozoa':              self.urine_spermatozoa,
            'urine_epithelium_flat':          self.urine_epithelium_flat,
            'urine_color':                    self.urine_color,
            'urine_transparency':             self.urine_transparency,
            'hbs_ag':         self.hbs_ag,
            'hiv_ab':         self.hiv_ab,
            'hepatitis_c_ab': self.hepatitis_c_ab,
            'treponema_ab':   self.treponema_ab,
        }

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))