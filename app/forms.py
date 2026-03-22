from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from app.models import User


class FlexFloatField(FloatField):
    """FloatField принимающий как '.' так и ',' в качестве десятичного разделителя."""
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.').strip())
            except (ValueError, AttributeError):
                self.data = None


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
    glucose = FlexFloatField('Глюкоза', validators=[Optional()])
    triglycerides = FlexFloatField('Триглицериды', validators=[Optional()])
    hdl = FlexFloatField('ЛПВП', validators=[Optional()])
    total_cholesterol = FlexFloatField('Общий холестерин', validators=[Optional()])
    vldl = FlexFloatField('ЛПОНП', validators=[Optional()])
    ldl = FlexFloatField('ЛПНП', validators=[Optional()])
    alt = FlexFloatField('АЛТ', validators=[Optional()])
    creatinine = FlexFloatField('Креатинин', validators=[Optional()])
    ast = FlexFloatField('АСТ', validators=[Optional()])
    # Клинический анализ крови
    esr = FlexFloatField('СОЭ (по Вестергрену)', validators=[Optional()])
    hemoglobin = FlexFloatField('Гемоглобин общий', validators=[Optional()])
    rbc = FlexFloatField('Количество эритроцитов', validators=[Optional()])
    hematocrit = FlexFloatField('Гематокрит', validators=[Optional()])
    mcv = FlexFloatField('Средний объём эритроцита (MCV)', validators=[Optional()])
    mch = FlexFloatField('Среднее содержание Hb в эритроците (MCH)', validators=[Optional()])
    mchc = FlexFloatField('Средняя концентрация Hb в эритроците (MCHC)', validators=[Optional()])
    rdw = FlexFloatField('Ширина распределения эритроцитов (RDW)', validators=[Optional()])
    platelets = FlexFloatField('Количество тромбоцитов', validators=[Optional()])
    mpv = FlexFloatField('Средний объём тромбоцитов (MPV)', validators=[Optional()])
    pdw = FlexFloatField('Ширина распределения тромбоцитов (PDW)', validators=[Optional()])
    pct = FlexFloatField('Тромбокрит (PCT)', validators=[Optional()])
    wbc = FlexFloatField('Количество лейкоцитов', validators=[Optional()])
    neutrophils_abs = FlexFloatField('Нейтрофилы абс.', validators=[Optional()])
    neutrophils_pct = FlexFloatField('Нейтрофилы %', validators=[Optional()])
    lymphocytes_abs = FlexFloatField('Лимфоциты абс.', validators=[Optional()])
    lymphocytes_pct = FlexFloatField('Лимфоциты %', validators=[Optional()])
    monocytes_abs = FlexFloatField('Моноциты абс.', validators=[Optional()])
    monocytes_pct = FlexFloatField('Моноциты %', validators=[Optional()])
    eosinophils_abs = FlexFloatField('Эозинофилы абс.', validators=[Optional()])
    eosinophils_pct = FlexFloatField('Эозинофилы %', validators=[Optional()])
    basophils_abs = FlexFloatField('Базофилы абс.', validators=[Optional()])
    basophils_pct = FlexFloatField('Базофилы %', validators=[Optional()])
    # Биохимия дополнительная
    albumin                = FlexFloatField('Альбумин, г/л', validators=[Optional()])
    total_protein          = FlexFloatField('Белок общий, г/л', validators=[Optional()])
    ggt                    = FlexFloatField('ГГТ (гамма-глутамилтранспептидаза), Ед/л', validators=[Optional()])
    potassium              = FlexFloatField('Калий, ммоль/л', validators=[Optional()])
    calcium                = FlexFloatField('Кальций общий, ммоль/л', validators=[Optional()])
    sodium                 = FlexFloatField('Натрий, ммоль/л', validators=[Optional()])
    phosphorus             = FlexFloatField('Фосфор неорганический, ммоль/л', validators=[Optional()])
    chloride               = FlexFloatField('Хлор, ммоль/л', validators=[Optional()])
    bilirubin_total        = FlexFloatField('Билирубин общий', validators=[Optional()])
    bilirubin_direct       = FlexFloatField('Билирубин прямой', validators=[Optional()])
    bilirubin_indirect     = FlexFloatField('Билирубин непрямой', validators=[Optional()])
    alkaline_phosphatase   = FlexFloatField('Щелочная фосфатаза (ЩФ)', validators=[Optional()])
    urea                   = FlexFloatField('Мочевина', validators=[Optional()])
    gfr                    = FlexFloatField('СКФ (скорость клубочковой фильтрации)', validators=[Optional()])
    ckf_total              = FlexFloatField('КФК (креатинфосфокиназа)', validators=[Optional()])
    psa                    = FlexFloatField('ПСА общий', validators=[Optional()])
    microalbumin           = FlexFloatField('Микроальбумин (суточный)', validators=[Optional()])
    # Гормоны и инсулинорезистентность
    ferritin               = FlexFloatField('Ферритин, мкг/л', validators=[Optional()])
    insulin                = FlexFloatField('Инсулин, мкМЕ/мл', validators=[Optional()])
    homa_ir                = FlexFloatField('Инсулинорезистентность (HOMA-IR)', validators=[Optional()])
    vitamin_d              = FlexFloatField('Витамин D (25-OH), нг/мл', validators=[Optional()])
    # Анализ мочи по Нечипоренко
    nechiporenko_leukocytes      = FlexFloatField('Лейкоциты по Нечипоренко, Ед/мл', validators=[Optional()])
    nechiporenko_erythrocytes    = FlexFloatField('Эритроциты по Нечипоренко, Ед/мл', validators=[Optional()])
    nechiporenko_cylinders       = FlexFloatField('Цилиндры по Нечипоренко, Ед/мл', validators=[Optional()])
    # Общий анализ мочи
    urine_specific_gravity       = FlexFloatField('Удельный вес мочи', validators=[Optional()])
    urine_ph                     = FlexFloatField('pH мочи', validators=[Optional()])
    urine_protein                = FlexFloatField('Белок в моче', validators=[Optional()])
    urine_urobilinogen           = FlexFloatField('Уробилиноген в моче', validators=[Optional()])
    urine_glucose                = FlexFloatField('Глюкоза в моче', validators=[Optional()])
    urine_bilirubin              = FlexFloatField('Билирубин в моче', validators=[Optional()])
    urine_ketones                = FlexFloatField('Кетоновые тела в моче', validators=[Optional()])
    urine_blood                  = FlexFloatField('Кровь/гемоглобин в моче', validators=[Optional()])
    urine_leukocytes_semi        = FlexFloatField('Лейкоциты полуколич. (LEU)', validators=[Optional()])
    urine_leukocytes_micro       = FlexFloatField('Лейкоциты микроскопия (в п/зр)', validators=[Optional()])
    urine_erythrocytes_changed   = FlexFloatField('Эритроциты изменённые (в п/зр)', validators=[Optional()])
    urine_erythrocytes_unchanged = FlexFloatField('Эритроциты неизменённые (в п/зр)', validators=[Optional()])
    # Качественные параметры мочи
    urine_nitrites                 = FlexFloatField('Нитриты', validators=[Optional()])
    urine_cylinders_hyaline        = FlexFloatField('Цилиндры гиалиновые (в п/зр)', validators=[Optional()])
    urine_cylinders_granular       = FlexFloatField('Цилиндры зернистые (в п/зр)', validators=[Optional()])
    urine_cylinders_waxy           = FlexFloatField('Цилиндры восковидные (в п/зр)', validators=[Optional()])
    urine_cylinders_epithelial     = FlexFloatField('Цилиндры эпителиальные (в п/зр)', validators=[Optional()])
    urine_cylinders_leukocyte      = FlexFloatField('Цилиндры лейкоцитарные (в п/зр)', validators=[Optional()])
    urine_trichomonas              = FlexFloatField('Трихомонады', validators=[Optional()])
    urine_yeast                    = FlexFloatField('Дрожжевые клетки', validators=[Optional()])
    urine_bacteria                 = FlexFloatField('Бактерии', validators=[Optional()])
    urine_mucus                    = FlexFloatField('Слизь', validators=[Optional()])
    urine_phosphates_amorphous     = FlexFloatField('Аморфные фосфаты', validators=[Optional()])
    urine_urates                   = FlexFloatField('Ураты', validators=[Optional()])
    urine_crystals_triplephosphate = FlexFloatField('Кристаллы трипельфосфаты', validators=[Optional()])
    urine_crystals_uric_acid       = FlexFloatField('Кристаллы мочевой кислоты', validators=[Optional()])
    urine_crystals_oxalate         = FlexFloatField('Кристаллы оксалата кальция', validators=[Optional()])
    urine_epithelium_renal         = FlexFloatField('Эпителий почечный (в п/зр)', validators=[Optional()])
    urine_epithelium_transitional  = FlexFloatField('Эпителий переходный (в п/зр)', validators=[Optional()])
    urine_spermatozoa              = FlexFloatField('Сперматозоиды', validators=[Optional()])
    urine_epithelium_flat          = FlexFloatField('Эпителий плоский (в п/зр)', validators=[Optional()])
    urine_color                    = StringField('Цвет мочи', validators=[Optional()])
    urine_transparency             = StringField('Прозрачность мочи', validators=[Optional()])
    # Серологические тесты
    hbs_ag         = BooleanField('HBs-антиген (гепатит B)')
    hiv_ab         = BooleanField('Антитела/антиген HIV')
    hepatitis_c_ab = BooleanField('Антитела к Hepatitis C')
    treponema_ab   = BooleanField('Антитела к Treponema pallidum (сифилис)')
    submit = SubmitField('Сохранить')


class BodyMeasurementForm(FlaskForm):
    date     = StringField('Дата (ДД.ММ.ГГГГ)', validators=[Optional()])
    weight   = FlexFloatField('Вес (кг)', validators=[Optional()])
    waist    = FlexFloatField('Талия (см)', validators=[Optional()])
    hips     = FlexFloatField('Бёдра (см)', validators=[Optional()])
    neck     = FlexFloatField('Шея (см)', validators=[Optional()])
    forearm  = FlexFloatField('Предплечье (см)', validators=[Optional()])
    wrist    = FlexFloatField('Запястье (см)', validators=[Optional()])
    thigh    = FlexFloatField('Бедро (см)', validators=[Optional()])
    shin     = FlexFloatField('Голень (см)', validators=[Optional()])
    abdomen  = FlexFloatField('Живот (см)', validators=[Optional()])
    chest    = FlexFloatField('Грудь (см)', validators=[Optional()])
    body_fat = FlexFloatField('% жира', validators=[Optional()])
    submit   = SubmitField('Сохранить замер')


class HeightForm(FlaskForm):
    height = FlexFloatField('Рост (см)', validators=[Optional()])
    gender = SelectField('Пол', choices=[
        ('', 'Не указан'),
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ], default='')
    submit = SubmitField('Сохранить')
