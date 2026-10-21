"""A research plan: which records exist for this country and period, in which order to search them, and where."""
import datetime

from . import guides, sources, workflow

PERIOD_RECORDS = [   # (from, to, countries or "*", kinds, guide) — what to look at, oldest last
    (1918, 9999, "RU UA BY MD", ["vital", "household", "military", "repression"], "household_book"),
    (1941, 1945, "RU UA BY MD LT LV EE", ["military"], "wwii"),
    (1914, 1918, "RU UA BY MD PL LT LV EE", ["military"], "wwi"),
    (1897, 1897, "RU UA BY MD PL LT LV EE", ["census"], "census"),
    (1720, 1920, "RU UA BY MD", ["church", "confession"], "metric_book"),
    (1719, 1858, "RU UA BY", ["revision"], "revision_list"),
    (1812, 1858, "MD", ["revision"], "revision_list"),
    (1790, 1960, "*", ["census"], "census"),
    (1820, 1960, "US CA AR BR UY CL MX", ["emigration"], "passenger_list"),
    (1792, 9999, "FR BE NL IT DE GB IE ES PT PL AT HU RO", ["vital"], "civil_registration_europe"),
    (1500, 1950, "MX BR AR CL PE CO CU UY PY VE EC BO GT CR", ["church", "vital"], "latin_america"),
]


def plan(country="", year_from=None, year_to=None, known="", lang="en", limit=20, context=None, lead_id=""):
    ru = lang == "ru"
    context = context or workflow.context({})
    settings = context['policy']
    codes = sources.countries(country)
    y1, y2 = int(year_from or 1700), int(year_to or 2000)
    steps = [
        ("Ask the oldest relatives first and collect the home archive (documents, photos with inscriptions, letters, military papers)."
         if not ru else "Сначала расспросите старших родственников и соберите домашний архив (документы, фото с надписями, письма, военные бумаги)."),
        ("Write down what is known as facts with their source; set one question (e.g. «who were the parents of X, born about 1890 in Y»)."
         if not ru else "Запишите известное как факты с источником; поставьте один вопрос («кто родители X, родившегося около 1890 г. в Y»)."),
        ("Pin the place down: what the village/town was called then, its province and district, and its parish."
         if not ru else "Уточните место: как называлось село/город тогда, в какой губернии и уезде, к какому приходу относилось."),
        ("Make the list of name variants (name_variants) and search every source with all of them."
         if not ru else "Составьте варианты имён (name_variants) и ищите во всех источниках по всем вариантам."),
    ]
    priority = []
    if codes & {'RU', 'UA', 'BY', 'MD'} and y2 >= (1919 if codes == {'MD'} else 1918):
        priority.append(("For civil-registration events, first ask the owner for family certificates or an eligible registry-office request; verify local dates and custody. If the owner must act, pause this line and save a waiting_owner lead."
                         if not ru else "Для событий гражданской регистрации сначала нужны семейные свидетельства или действие владельца через ЗАГС/ДРАЦС/ASP; уточните местные сроки и держателя. Для Бессарабии проверьте гражданские акты с 1919 года. Если нужны действия владельца, приостановите линию: waiting_owner, blocked_by, next."))
    priority += ([
        "Fully transcribe the documents already held, including parents, godparents, marriage witnesses and siblings, before a new search.",
        "Find the bride's parish for the marriage; search births of all children, not only the direct ancestor. If registers have gaps, check confession and revision lists household by household.",
        "Finish and log each stage before the next; consult project_coverage before reading images. Secondary publications and other trees are pointers to originals, never proof of kinship.",
    ] if not ru else [
        "До нового поиска полностью выпишите уже найденные документы: родителей, восприемников, поручителей, братьев и сестёр.",
        "Венчание ищите прежде всего в приходе невесты; рождения — по всем детям. При пробелах метрик проверьте весь двор по исповедным ведомостям и ревизиям.",
        "Каждый этап завершите и запишите до следующего; перед сканами вызовите project_coverage. Публикации и чужие деревья — подсказки к оригиналам, а не доказательство родства.",
    ])
    steps[2:2] = priority
    records, guide_keys = [], []
    for a, b, where, kinds, gk in PERIOD_RECORDS:
        if b < y1 or a > y2:
            continue
        if where != "*" and codes and not codes & set(where.split()):
            continue
        records += kinds
        if gk not in guide_keys:
            guide_keys.append(gk)
    # Reference works and trees complement the primary record types; they are searched
    # only after the preceding workflow stages, not silently dropped by kind filtering.
    records = list(dict.fromkeys(records + ["books", "directories", "newspapers", "catalogs", "trees"]))
    found = sources.find(country, y1, y2, records or None)
    by_access = sorted(found, key=lambda s: (0 if codes & set(s["countries"]) else 1, {"free": 0, "free_account": 1, "mixed": 2, "paid": 3, "request": 4}.get(s["access"], 5)))
    steps.append(("Search the free online sources (country first), newest records first — they lead back:"
                  if not ru else "Пройдите бесплатные базы (сначала по стране), от новых записей к старым — они ведут назад:"))
    steps.append(("Check a find against what you know (check_match) before attaching it; keep a log of negative results."
                  if not ru else "Каждую находку проверяйте (check_match), прежде чем добавить в древо; записывайте и отрицательные результаты."))
    if settings['allow_archive_requests'] and not context.get('policy_review_required'):
        steps.append("For files unavailable online, keep the reference and consider a reading-room visit. Draft a request only if the owner wants one; never send it yourself."
                     if not ru else "Для неоцифрованного дела сохраните шифр и шаг «читальный зал». Черновик запроса готовьте только по желанию владельца; сами не отправляйте.")
    else:
        steps.append("Project policy prohibits archive requests: use online scans, family documents or an owner task; otherwise save a reading_room lead with the reference."
                     if not ru else "Политика проекта запрещает запросы в архивы: онлайн-сканы, семейные документы, задача владельцу; иначе наводка reading_room с шифром дела.")
    if not settings['allow_living_research']:
        steps.append("Do not investigate the current lives of living relatives; ask them directly. Do not publish their private data."
                     if not ru else "Не исследуйте нынешнюю жизнь живых родственников; спрашивайте их самих. Не публикуйте личные сведения.")
    waiting = [x for x in context.get('waiting_questions', []) if lead_id and x.get('id') == lead_id]
    active = context.get('active_questions', [])
    stop = bool(context.get('policy_review_required')) or bool(waiting) or bool(len(active) >= settings['max_active_questions'] and not any(x.get('id') == lead_id for x in active))
    question_stage = next((x.get('stage', 'family') for x in context.get('questions', active) if x.get('id') == lead_id), 'family')
    latest_checks = {x['source_id']: x for x in context.get('source_checks', []) if lead_id and x.get('lead_id') == lead_id and x.get('stage') == question_stage}
    stop_reason = ('review_project_policy' if context.get('policy_review_required') else 'question_blocked' if waiting else 'active_question_limit' if stop else '')
    if stop:
        steps.insert(0, ('STOP: ' + stop_reason + '. Resolve this before another search.' if not ru else 'СТОП: ' + stop_reason + '. Устраните причину до нового поиска.'))
    catalogue_ids = {s['id'] for s in by_access}
    local = [r for r in context.get('resources', []) if r.get('id') not in catalogue_ids]
    checklist = [{'id': s['id'], 'name': s.get('name', s['id']), 'url': s.get('url', ''),
                  'outcome': latest_checks.get(s['id'], {}).get('outcome', 'unchecked')} for s in by_access + local]
    return {
        "question": known,
        'status': 'review_project_policy' if context.get('policy_review_required') else 'waiting' if stop else 'ready',
        'stop_reason': stop_reason,
        'waiting_on': waiting,
        'policy': settings,
        'overdue_owner_tasks': context.get('overdue_owner_tasks', []),
        'stages': list(workflow.STAGES),
        'project_instructions': context.get('project_instructions', ''),
        'source_checklist': checklist,
        'project_resources': local,
        'as_of': datetime.date.today().isoformat(),
        "steps": steps,
        "record_kinds": {k: sources.RECORD_KINDS.get(k, (k, k))[1 if ru else 0] for k in records},
        "guides": {k: guides.GUIDES[k]["title"][1 if ru else 0] for k in guide_keys},
        "sources": [] if stop else [{"id": s["id"], "name": s["name"], "url": s["url"], "access": s["access"], "years": s["years"] if s.get("coverage_known", True) else None,
                     "coverage_known": s.get("coverage_known", True),
                     **({"availability_note": s["availability_note_ru" if ru else "availability_note"]} if s.get("availability_note") else {}),
                     "how": s["how_ru" if ru else "how"]} for s in by_access[:limit]],
        "more_sources": max(0, len(by_access) - limit),
    }
