from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message='Обязательное поле')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Обязательное поле')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message='Обязательное поле')])
    email = StringField('Email', validators=[DataRequired(message='Обязательное поле'), Email(message='Некорректный email')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Обязательное поле')])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(message='Обязательное поле'), EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя пользователя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот email уже зарегистрирован.')


class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message='Обязательное поле')])
    email = StringField('Email', validators=[DataRequired(message='Обязательное поле'), Email(message='Некорректный email')])
    current_password = PasswordField('Текущий пароль', validators=[Optional()])
    new_password = PasswordField('Новый пароль', validators=[Optional()])
    new_password2 = PasswordField('Повторите новый пароль', validators=[Optional(), EqualTo('new_password', message='Пароли не совпадают')])
    submit = SubmitField('Сохранить изменения')


class AdminUserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message='Обязательное поле')])
    email = StringField('Email', validators=[DataRequired(message='Обязательное поле'), Email(message='Некорректный email')])
    password = PasswordField('Пароль (оставьте пустым, чтобы не менять)', validators=[Optional()])
    password2 = PasswordField('Повторите пароль', validators=[Optional(), EqualTo('password', message='Пароли не совпадают')])
    is_admin = BooleanField('Администратор')
    submit = SubmitField('Сохранить')


class AnalysisForm(FlaskForm):
    id = HiddenField()
    date = StringField('Дата (ДД.ММ.ГГГГ)', validators=[DataRequired(message='Обязательное поле')])
    diet = SelectField('Тип питания на момент сдачи', choices=[
        ('none',                  'Обычное питание'),
        ('intermittent_fasting',  'Интервальное голодание'),
        ('keto',                  'Кето-диета'),
        ('low_carb',              'Низкоуглеводная диета'),
        ('vegetarian',            'Вегетарианство'),
        ('vegan',                 'Веганство'),
        ('other',                 'Другое'),
    ], default='none')
    glucose = FloatField('Глюкоза', validators=[Optional()])
    triglycerides = FloatField('Триглицериды', validators=[Optional()])
    hdl = FloatField('ЛПВП', validators=[Optional()])
    total_cholesterol = FloatField('Общий холестерин', validators=[Optional()])
    vldl = FloatField('ЛПОНП', validators=[Optional()])
    ldl = FloatField('ЛПНП', validators=[Optional()])
    alt = FloatField('АЛТ', validators=[Optional()])
    creatinine = FloatField('Креатинин', validators=[Optional()])
    ast = FloatField('АСТ', validators=[Optional()])
    # Клинический анализ крови
    esr = FloatField('СОЭ (по Вестергрену)', validators=[Optional()])
    hemoglobin = FloatField('Гемоглобин общий', validators=[Optional()])
    rbc = FloatField('Количество эритроцитов', validators=[Optional()])
    hematocrit = FloatField('Гематокрит', validators=[Optional()])
    mcv = FloatField('Средний объём эритроцита (MCV)', validators=[Optional()])
    mch = FloatField('Среднее содержание Hb в эритроците (MCH)', validators=[Optional()])
    mchc = FloatField('Средняя концентрация Hb в эритроците (MCHC)', validators=[Optional()])
    rdw = FloatField('Ширина распределения эритроцитов (RDW)', validators=[Optional()])
    platelets = FloatField('Количество тромбоцитов', validators=[Optional()])
    mpv = FloatField('Средний объём тромбоцитов (MPV)', validators=[Optional()])
    pdw = FloatField('Ширина распределения тромбоцитов (PDW)', validators=[Optional()])
    pct = FloatField('Тромбокрит (PCT)', validators=[Optional()])
    wbc = FloatField('Количество лейкоцитов', validators=[Optional()])
    neutrophils_abs = FloatField('Нейтрофилы абс.', validators=[Optional()])
    neutrophils_pct = FloatField('Нейтрофилы %', validators=[Optional()])
    lymphocytes_abs = FloatField('Лимфоциты абс.', validators=[Optional()])
    lymphocytes_pct = FloatField('Лимфоциты %', validators=[Optional()])
    monocytes_abs = FloatField('Моноциты абс.', validators=[Optional()])
    monocytes_pct = FloatField('Моноциты %', validators=[Optional()])
    eosinophils_abs = FloatField('Эозинофилы абс.', validators=[Optional()])
    eosinophils_pct = FloatField('Эозинофилы %', validators=[Optional()])
    basophils_abs = FloatField('Базофилы абс.', validators=[Optional()])
    basophils_pct = FloatField('Базофилы %', validators=[Optional()])
    # Биохимия дополнительная
    bilirubin_total        = FloatField('Билирубин общий', validators=[Optional()])
    bilirubin_direct       = FloatField('Билирубин прямой', validators=[Optional()])
    bilirubin_indirect     = FloatField('Билирубин непрямой', validators=[Optional()])
    alkaline_phosphatase   = FloatField('Щелочная фосфатаза (ЩФ)', validators=[Optional()])
    urea                   = FloatField('Мочевина', validators=[Optional()])
    gfr                    = FloatField('СКФ (скорость клубочковой фильтрации)', validators=[Optional()])
    ckf_total              = FloatField('КФК (креатинфосфокиназа)', validators=[Optional()])
    psa                    = FloatField('ПСА общий', validators=[Optional()])
    microalbumin           = FloatField('Микроальбумин (суточный)', validators=[Optional()])
    # Анализ мочи
    urine_specific_gravity       = FloatField('Удельный вес мочи', validators=[Optional()])
    urine_ph                     = FloatField('pH мочи', validators=[Optional()])
    urine_protein                = FloatField('Белок в моче', validators=[Optional()])
    urine_urobilinogen           = FloatField('Уробилиноген в моче', validators=[Optional()])
    urine_glucose                = FloatField('Глюкоза в моче', validators=[Optional()])
    urine_bilirubin              = FloatField('Билирубин в моче', validators=[Optional()])
    urine_ketones                = FloatField('Кетоновые тела в моче', validators=[Optional()])
    urine_blood                  = FloatField('Кровь/гемоглобин в моче', validators=[Optional()])
    urine_leukocytes_semi        = FloatField('Лейкоциты полуколич. (LEU)', validators=[Optional()])
    urine_leukocytes_micro       = FloatField('Лейкоциты микроскопия (в п/зр)', validators=[Optional()])
    urine_erythrocytes_changed   = FloatField('Эритроциты изменённые (в п/зр)', validators=[Optional()])
    urine_erythrocytes_unchanged = FloatField('Эритроциты неизменённые (в п/зр)', validators=[Optional()])
    # Качественные параметры мочи
    urine_nitrites                 = FloatField('Нитриты', validators=[Optional()])
    urine_cylinders_hyaline        = FloatField('Цилиндры гиалиновые (в п/зр)', validators=[Optional()])
    urine_cylinders_granular       = FloatField('Цилиндры зернистые (в п/зр)', validators=[Optional()])
    urine_cylinders_waxy           = FloatField('Цилиндры восковидные (в п/зр)', validators=[Optional()])
    urine_cylinders_epithelial     = FloatField('Цилиндры эпителиальные (в п/зр)', validators=[Optional()])
    urine_cylinders_leukocyte      = FloatField('Цилиндры лейкоцитарные (в п/зр)', validators=[Optional()])
    urine_trichomonas              = FloatField('Трихомонады', validators=[Optional()])
    urine_yeast                    = FloatField('Дрожжевые клетки', validators=[Optional()])
    urine_bacteria                 = FloatField('Бактерии', validators=[Optional()])
    urine_mucus                    = FloatField('Слизь', validators=[Optional()])
    urine_phosphates_amorphous     = FloatField('Аморфные фосфаты', validators=[Optional()])
    urine_urates                   = FloatField('Ураты', validators=[Optional()])
    urine_crystals_triplephosphate = FloatField('Кристаллы трипельфосфаты', validators=[Optional()])
    urine_crystals_uric_acid       = FloatField('Кристаллы мочевой кислоты', validators=[Optional()])
    urine_crystals_oxalate         = FloatField('Кристаллы оксалата кальция', validators=[Optional()])
    urine_epithelium_renal         = FloatField('Эпителий почечный (в п/зр)', validators=[Optional()])
    urine_epithelium_transitional  = FloatField('Эпителий переходный (в п/зр)', validators=[Optional()])
    urine_spermatozoa              = FloatField('Сперматозоиды', validators=[Optional()])
    urine_epithelium_flat          = FloatField('Эпителий плоский (в п/зр)', validators=[Optional()])
    urine_color                    = StringField('Цвет мочи', validators=[Optional()])
    urine_transparency             = StringField('Прозрачность мочи', validators=[Optional()])
    # Серологические тесты
    hbs_ag         = BooleanField('HBs-антиген (гепатит B)')
    hiv_ab         = BooleanField('Антитела/антиген HIV')
    hepatitis_c_ab = BooleanField('Антитела к Hepatitis C')
    treponema_ab   = BooleanField('Антитела к Treponema pallidum (сифилис)')
    submit = SubmitField('Сохранить')
