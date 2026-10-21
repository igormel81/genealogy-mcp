"""Project-specific research policy and explicit progress, without executing project text."""
import datetime

STAGES = ('family', 'civil_registry', 'existing_documents', 'primary_records', 'secondary_sources')
DEFAULT_POLICY = {'max_active_questions': 3, 'allow_archive_requests': True, 'allow_living_research': False,
                  'owner_tasks': []}


def policy(value=None):
    value = dict(value or {})
    unknown = set(value) - set(DEFAULT_POLICY)
    if unknown:
        raise ValueError(f"unknown policy keys: {', '.join(sorted(unknown))}")
    out = {**DEFAULT_POLICY, **value}
    if type(out['max_active_questions']) is not int or not 1 <= out['max_active_questions'] <= 20:
        raise ValueError('max_active_questions: integer from 1 to 20')
    for key in ('allow_archive_requests', 'allow_living_research'):
        if type(out[key]) is not bool:
            raise ValueError(f'{key}: boolean required')
    if not isinstance(out['owner_tasks'], list) or any(not isinstance(t, dict) or not t.get('id') or not t.get('next') for t in out['owner_tasks']):
        raise ValueError('owner_tasks: list of {id, next, optional due, optional status}')
    ids = [t['id'] for t in out['owner_tasks']]
    if len(ids) != len(set(ids)):
        raise ValueError('owner task ids must be unique')
    for task in out['owner_tasks']:
        if task.get('due'):
            try:
                datetime.date.fromisoformat(task['due'])
            except (TypeError, ValueError):
                raise ValueError('owner task due: ISO date required') from None
    return out


def prepare_lead(record, previous, leads, settings, log):
    rec = {**(previous or {}), **record}
    if not isinstance(rec.get('next'), str) or not rec['next'].strip():
        raise ValueError("a lead needs next: the specific next step, 'waiting for owner: ...', or 'reading room only'")
    rec.setdefault('checked', None)  # null means never checked; do not invent a check date
    if rec['checked'] is not None:
        try:
            datetime.date.fromisoformat(rec['checked'])
        except (TypeError, ValueError):
            raise ValueError('checked: ISO date or null if not yet checked') from None
    expected = rec.get('expected_sources', [])
    if not isinstance(expected, list) or any(not isinstance(x, str) or not x.strip() for x in expected):
        raise ValueError('expected_sources: list of source ids')
    rec.setdefault('status', 'open')
    if rec['status'] not in ('open', 'active', 'waiting_owner', 'reading_room', 'closed'):
        raise ValueError('lead status: open | active | waiting_owner | reading_room | closed')
    rec.setdefault('stage', 'family')
    if rec['stage'] not in STAGES:
        raise ValueError('stage: ' + ' | '.join(STAGES))
    if rec['status'] == 'waiting_owner' and not rec.get('blocked_by'):
        raise ValueError('waiting_owner needs blocked_by: the owner task or missing document')
    if rec['status'] == 'active':
        if rec.get('blocked_by'):
            raise ValueError('this question is blocked; record the owner response and clear blocked_by before resuming')
        active = [x for x in leads if x.get('status') == 'active' and x.get('id') != rec.get('id')]
        if len(active) >= settings['max_active_questions']:
            raise ValueError('finish or pause an active question before starting another')
    old_stage = (previous or {}).get('stage', 'family')
    if rec['stage'] != old_stage:
        if STAGES.index(rec['stage']) > STAGES.index(old_stage) + 1:
            raise ValueError('finish or explicitly mark each intervening stage not applicable before moving on')
        if not rec.get('checked') or not record.get('stage_result'):
            raise ValueError('before changing stage, record checked and stage_result (including why a stage is not applicable)')
        expected = (previous or {}).get('expected_sources', [])
        latest = {x.get('source_id'): x for x in log if x.get('lead_id') == rec.get('id') and x.get('stage') == old_stage}
        done = {source_id for source_id, check in latest.items() if check.get('outcome') in ('checked', 'not_relevant')}
        missing = set(expected) - done
        if missing:
            raise ValueError('sources still unchecked (unavailable is not a negative search): ' + ', '.join(sorted(missing)))
    return rec


def context(data, settings=None):
    p = policy(settings if settings is not None else data.get('policy'))
    today = datetime.date.today().isoformat()
    return {'policy': p, 'stages': list(STAGES),
            'questions': data.get('research_leads', []),
            'active_questions': [x for x in data.get('research_leads', []) if x.get('status') == 'active'],
            'waiting_questions': [x for x in data.get('research_leads', []) if x.get('status') in ('waiting_owner', 'reading_room') or x.get('blocked_by')],
            'overdue_owner_tasks': [t for t in p['owner_tasks'] if t.get('status') != 'closed' and t.get('due') and t['due'] < today],
            'resources': data.get('research_resources', []),
            'source_checks': [x for x in data.get('research_log', []) if x.get('source_id')]}
