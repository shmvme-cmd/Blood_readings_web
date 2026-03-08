import re
import pdfplumber
from datetime import datetime


# Сопоставление ключевых слов из PDF с полями модели.
# Порядок важен: более специфичные паттерны должны проверяться раньше общих.
# Все паттерны применяются с флагом re.DOTALL (. совпадает с \n в многострочных ячейках).
FIELD_PATTERNS = {
    # Биохимия
    'glucose':            [r'глюкоз(?!а\s+полуколич)', r'glucose(?!.*urine)'],
    'triglycerides':      [r'триглицерид', r'triglycerid'],
    'hdl':                [r'лпвп', r'\bhdl\b', r'холестерин.*высок', r'липопротеин.*высок'],
    'ldl':                [r'лпнп', r'\bldl\b', r'холестерин.*низк', r'липопротеин.*низк'],
    'vldl':               [r'лпонп', r'\bvldl\b', r'липопротеин.*очень'],
    'total_cholesterol':  [r'общий холестерин', r'холестерин общ', r'total.?cholesterol'],
    'alt':                [r'аланин', r'\bалт\b', r'\balt\b'],
    'ast':                [r'аспартат', r'\bаст\b', r'\bast\b'],
    'creatinine':         [r'креатинин', r'creatinine'],
    # ОАК: сначала более специфичные (с "абсолютн"/"относит"), потом общие
    'esr':                [r'скорость оседания', r'вестергрен', r'панченков', r'\bсоэ\b', r'\besr\b'],
    # Гемоглобин — паттерн специфичен чтобы не пересекаться с MCH/MCHC
    'hemoglobin':         [r'гемоглобин общ', r'гемоглобин$', r'\bhgb\b', r'\bhb\b', r'hemoglobin'],
    # Эритроциты — "количество эритроцит" чтобы не захватить MCH/RDW/ESR
    'rbc':                [r'количество эритроцит', r'\brbc\b', r'red blood cell'],
    'hematocrit':         [r'гематокрит', r'hematocrit', r'\bhct\b'],
    # MCV — "объем эритроцита" отличается от "содержание" (MCH) и "концентрация" (MCHC)
    'mcv':                [r'средн.*объ.*эритр', r'\bmcv\b'],
    # MCH — "содержание гемоглобина в"
    'mch':                [r'содержание гемоглоб', r'\bmch\b'],
    # MCHC — "концентрация гемоглобина в"
    'mchc':               [r'концентрация гемоглоб', r'\bmchc\b'],
    # RDW — "ширина ... эритроцит" (не тромбоцит → это PDW)
    'rdw':                [r'ширина.*эритроцит', r'\brdw\b'],
    # Тромбоциты
    'platelets':          [r'количество тромбоц', r'\bplt\b', r'platelet'],
    'mpv':                [r'средн.*объ.*тромбоц', r'\bmpv\b'],
    'pdw':                [r'ширина.*тромбоц', r'\bpdw\b'],
    'pct':                [r'тромбокрит', r'общий объем тромбоц', r'\bpct\b'],
    # Лейкоциты
    'wbc':                [r'количество лейкоц', r'\bwbc\b', r'white blood'],
    # Формула: abs/pct различаются по "абсолютн" vs "относит"
    'neutrophils_abs':    [r'абсолютн.*нейтроф', r'нейтрофил.*абс', r'neut#', r'neu#'],
    'neutrophils_pct':    [r'относит.*нейтроф', r'нейтрофил.*%', r'neutrophil.*%', r'neut%'],
    'lymphocytes_abs':    [r'абсолютн.*лимфоц', r'лимфоцит.*абс', r'lymph.*abs', r'lym#'],
    'lymphocytes_pct':    [r'относит.*лимфоц', r'лимфоцит.*%', r'lymph.*%', r'lym%'],
    'monocytes_abs':      [r'абсолютн.*моноц', r'моноцит.*абс', r'mono.*abs', r'mon#'],
    'monocytes_pct':      [r'относит.*моноц', r'моноцит.*%', r'mono.*%', r'mon%'],
    'eosinophils_abs':    [r'абсолютн.*эозиноф', r'эозинофил.*абс', r'eos.*abs', r'eos#'],
    'eosinophils_pct':    [r'относит.*эозиноф', r'эозинофил.*%', r'eos.*%'],
    'basophils_abs':      [r'абсолютн.*базоф', r'базофил.*абс', r'baso.*abs', r'bas#'],
    'basophils_pct':      [r'относит.*базоф', r'базофил.*%', r'baso.*%'],
    # Биохимия дополнительная
    'bilirubin_total':        [r'билирубин общ', r'bilirubin.*total', r'определение билирубина общ'],
    'bilirubin_direct':       [r'билирубин.{0,2}прям', r'bilirubin.*direct', r'\bконъюгирован', r'моноглюкурон', r'диглюкурон', r'моноглюкорон', r'диглюкорон'],
    'bilirubin_indirect':     [r'билирубин.{0,3}непрям', r'bilirubin.*indirect', r'неконъюгирован', r'непрямого.*своб'],
    'alkaline_phosphatase':   [r'щелочн.*фосфатаз', r'\bщф\b', r'alkaline.*phosphatase', r'\balp\b', r'определение щелочн'],
    'urea':                   [r'\bмочевин', r'\burea\b', r'\bbun\b', r'определение мочевин'],
    'gfr':                    [r'скорость клубочков', r'клубочков.*фильтрац', r'\bскф\b', r'\bgfr\b'],
    'ckf_total':              [r'креатинфосфокиназ', r'\bкфк\b', r'\bcpk\b', r'creatine.*kinase', r'общей креатин'],
    'psa':                    [r'\bпса\b', r'\bpsa\b', r'простатспецифич', r'исследование пса'],
    'microalbumin':           [r'микроальбумин', r'microalbumin'],
    # Анализ мочи
    'urine_specific_gravity': [r'удельный вес', r'specific gravity'],
    'urine_ph':               [r'ph мочи', r'реакция мочи', r'^\s*ph\s*$'],
    'urine_protein':          [r'белок полуколич', r'белок количест', r'\bpro\b.*г/л', r'белок.*мочи'],
    'urine_urobilinogen':     [r'уробилиноген', r'urobilinogen', r'\burg\b'],
    'urine_glucose':          [r'глюкоза\s+полуколич', r'глюкоза.*\bglu\b', r'\bglu\b.*глюкоз'],
    'urine_bilirubin':        [r'билирубин.*полуколич', r'\bbil\b.*мкмоль', r'билирубин.*\bbil\b'],
    'urine_ketones':          [r'кетонов', r'\bket\b', r'ketone'],
    'urine_blood':            [r'кровь\s+качеств', r'\bblood\b.*мг/л', r'гемоглобин.*мочи'],
    'urine_leukocytes_semi':  [r'лейкоциты\s+полуколич', r'\bleu\b', r'leukocyte.*count/мкл'],
    'urine_leukocytes_micro': [r'^лейкоциты$', r'лейкоциты\s+\d', r'лейкоциты\s+в\s+п'],
    'urine_erythrocytes_changed':   [r'эритроциты\s+изм[её]н', r'rbc.*changed'],
    'urine_erythrocytes_unchanged': [r'эритроциты\s+неизм[её]н', r'rbc.*unchanged'],
    # Качественные показатели мочи (0=не обнаружено, 1+=обнаружено)
    'urine_nitrites':                  [r'нитрит', r'\bnit\b', r'nitrite'],
    'urine_cylinders_hyaline':         [r'цилиндр.*гиалин', r'hyaline.*cyl'],
    'urine_cylinders_granular':        [r'цилиндр.*зернист', r'granular.*cyl'],
    'urine_cylinders_waxy':            [r'цилиндр.*восковид', r'waxy.*cyl'],
    'urine_cylinders_epithelial':      [r'цилиндр.*эпителиальн', r'epithelial.*cyl'],
    'urine_cylinders_leukocyte':       [r'цилиндр.*лейкоцит', r'leukocyte.*cyl'],
    'urine_trichomonas':               [r'trichomonas', r'трихомон'],
    'urine_yeast':                     [r'дрожжев', r'yeast'],
    'urine_bacteria':                  [r'бактери', r'bacteria'],
    'urine_mucus':                     [r'слизь', r'\bmucus\b'],
    'urine_phosphates_amorphous':      [r'аморфн.*фосфат', r'amorphous.*phosphate'],
    'urine_urates':                    [r'урат', r'\burate\b'],
    'urine_crystals_triplephosphate':  [r'кристалл.*трипельфосфат', r'triple.*phosphate'],
    'urine_crystals_uric_acid':        [r'кристалл.*мочевой кислот', r'uric.*acid.*cryst'],
    'urine_crystals_oxalate':          [r'оксалат', r'oxalate'],
    'urine_epithelium_renal':          [r'эпителий.*почечн', r'эпителий.*почечен', r'renal.*epith'],
    'urine_epithelium_transitional':   [r'эпителий.*переходн', r'transitional.*epith'],
    'urine_spermatozoa':               [r'сперматоз', r'sperm'],
    'urine_epithelium_flat':           [r'эпителий.*плоск', r'squamous.*epith', r'flat.*epith'],
}

# Текстовые поля (не числовые)
TEXT_FIELD_PATTERNS = {
    'urine_color':        [r'\bцвет\b', r'\bcolou?r\b'],
    'urine_transparency': [r'прозрачность', r'transparency', r'clarity'],
}

QUALITATIVE_PATTERNS = {
    'hbs_ag':         [r'антиген\s+hbs', r'hbs.{0,5}антиген', r'исследование антигена hbs', r'\bhbsag\b'],
    'hiv_ab':         [r'антител.*антиген.*hiv', r'hiv', r'вич'],
    'hepatitis_c_ab': [r'hepatitis\s+c', r'гепатит\s+c', r'антител.*hcv', r'\bhcv\b'],
    'treponema_ab':   [r'treponema\s+pallidum', r'трепонем', r'сифилис', r'igm.*igg.*иф[аэ]'],
}

# Паттерны для распознавания дат
DATE_PATTERNS = [
    r'(\d{2})[.\-/](\d{2})[.\-/](\d{4})',   # DD.MM.YYYY или DD-MM-YYYY
    r'(\d{4})[.\-/](\d{2})[.\-/](\d{2})',   # YYYY-MM-DD
]


def _find_date(text):
    """Ищет дату анализа в тексте PDF."""
    # Попробуем найти дату рядом с ключевыми словами
    context_pattern = re.compile(
        r'(?:дата|date|выдан|взятия|забора|сбора|результат).{0,30}?'
        r'(\d{2}[.\-/]\d{2}[.\-/]\d{4})',
        re.IGNORECASE
    )
    m = context_pattern.search(text)
    if m:
        return _parse_date(m.group(1))

    # Иначе берём первую найденную дату в документе
    for line in text.splitlines():
        for pat in DATE_PATTERNS:
            m = re.search(pat, line)
            if m:
                groups = m.groups()
                if len(groups[0]) == 4:          # YYYY-MM-DD
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                else:                             # DD.MM.YYYY
                    return _parse_date(m.group(0))
    return None


def _parse_date(s):
    """Парсит строку даты DD.MM.YYYY / DD-MM-YYYY."""
    s = s.replace('-', '.').replace('/', '.')
    try:
        return datetime.strptime(s, '%d.%m.%Y')
    except ValueError:
        return None


def _extract_number(text):
    """Извлекает первое число (включая десятичные) из строки.
    'не обнаружено' → 0.0, 'единично' → 1.0, 'обнаружено' → 1.0."""
    t = text.strip().lower()
    if re.search(r'не обнаруж|не определ|отсутств|absent|not found', t):
        return 0.0
    if re.search(r'единично|единичн', t):
        return 1.0
    if re.search(r'(?<!не )обнаружено|(?<!не )обнаружен\b', t):
        return 1.0
    m = re.search(r'(\d+[.,]\d+|\d+)', text)
    if m:
        return float(m.group(1).replace(',', '.'))
    return None


def _match_text_field(label):
    """По метке строки возвращает название текстового поля или None."""
    label_lower = label.lower().strip()
    for field, patterns in TEXT_FIELD_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, label_lower, re.DOTALL):
                return field
    return None


def _match_field(label):
    """По метке строки возвращает название поля модели или None."""
    label_lower = label.lower().strip()
    for field, patterns in FIELD_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, label_lower, re.DOTALL):
                return field
    return None


def parse_pdf(file_stream):
    """
    Парсит PDF из файлового потока.
    Возвращает dict с найденными полями и датой.
    """
    result = {}
    full_text = ''

    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            full_text += text + '\n'

            # Попробуем таблицы — они дают лучшую структуру
            for table in (page.extract_tables() or []):
                for row in table:
                    if not row:
                        continue
                    # Проверяем первые 2 ячейки как возможную метку
                    field = None
                    label_idx = 0
                    for idx in range(min(2, len(row))):
                        candidate = row[idx] or ''
                        field = _match_field(candidate)
                        if field:
                            label_idx = idx
                            break

                    if field and field not in result:
                        # Ищем числовое значение в ячейках после метки
                        for cell in row[label_idx + 1:]:
                            if cell:
                                val = _extract_number(str(cell))
                                if val is not None:
                                    result[field] = val
                                    break
                    elif not field:
                        # Пробуем текстовые поля (цвет, прозрачность)
                        for idx2 in range(min(2, len(row))):
                            candidate = row[idx2] or ''
                            tf = _match_text_field(candidate)
                            if tf and tf not in result:
                                val_cell = row[idx2 + 1] if len(row) > idx2 + 1 else None
                                if val_cell and val_cell.strip():
                                    result[tf] = val_cell.strip()
                                break

    # Парсим по строкам текста для полей, не найденных в таблицах
    for line in full_text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Шаг 1: явные разделители (таб, |, :)
        parts = re.split(r'[\t|:]+', line_stripped)
        if len(parts) < 2:
            # Шаг 2: два и более пробела (напр. "АЛТ  25  Ед/л  5-40")
            parts = re.split(r'\s{2,}', line_stripped)
        if len(parts) < 2:
            # Шаг 3: метка — всё до первого числа (напр. "Глюкоза 5.4 ммоль/л")
            m = re.match(r'^([^\d]+?)\s+(\d[\d.,]*)', line_stripped)
            if m:
                parts = [m.group(1), m.group(2)]
            else:
                continue

        field = _match_field(parts[0])
        if field and field not in result:
            # Ищем первое число в оставшихся частях
            for part in parts[1:]:
                val = _extract_number(part)
                if val is not None:
                    result[field] = val
                    break

    # Дата
    date = _find_date(full_text)
    if date:
        result['date'] = date.strftime('%d.%m.%Y')

    # Качественные тесты (положительный / отрицательный)
    text_lower = full_text.lower()
    for field, patterns in QUALITATIVE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower, re.DOTALL):
                # Ищем результат: отрицательный → False, положительный → True
                positive = bool(re.search(r'положительн', text_lower))
                result[field] = positive
                break

    return result
