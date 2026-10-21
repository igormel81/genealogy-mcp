"""Read-only event citation coverage, never a verdict that the cited claim is true."""
import collections

PERSON_EVENTS = ('birth', 'baptism', 'christening', 'death', 'burial', 'residence')


def report(data, root_person_id='', generations=4, limit=100):
    if type(generations) is not int or not 0 <= generations <= 10:
        raise ValueError('generations: integer 0–10 required')
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError('limit: integer 1–1000 required')
    people = {p['id']: p for p in data.get('people', [])}
    sources = {s['id']: s for s in data.get('sources', [])}
    families = data.get('families', [])
    root = root_person_id or data.get('root_person_id')
    if root and root not in people:
        raise ValueError('no such root person: ' + str(root))
    parents = collections.defaultdict(set)
    for family in families:
        for child in family.get('children', []):
            # Adoptive relationships are not silently treated as biological ancestry.
            if child not in family.get('adopted_children', []):
                parents[child].update(p for p in family.get('partners', []) if p in people)
    depth = {}
    todo = collections.deque([(root, 0)]) if root else collections.deque((pid, 0) for pid in people)
    while todo:
        pid, generation = todo.popleft()
        if pid in depth:
            continue
        depth[pid] = generation
        if generation < generations:
            todo.extend((parent, generation + 1) for parent in sorted(parents[pid]))
    rows = []

    def refs_for(record):
        refs = record.get('source_ids', []) or []
        if not isinstance(refs, list):
            raise ValueError('source_ids must be a list')
        return list(dict.fromkeys(str(sid) for sid in refs))

    def add(record_id, event, value, person_ids, broad_refs):
        refs = refs_for(value)
        linked, broken = [], []
        for sid in refs:
            source = sources.get(sid)
            if source is None:
                broken.append(sid)
            else:
                linked.append({'id': sid, 'title': source.get('title', ''),
                               'locator': source.get('locator', ''), 'url': source.get('url', ''),
                               'transcription': str(source.get('scope') or '')[:2000],
                               'transcription_truncated': len(str(source.get('scope') or '')) > 2000,
                               'needs_locator': not bool(source.get('locator')),
                               'hidden': bool(source.get('hidden'))})
        status = 'broken_reference' if broken else 'missing_reference' if not refs else 'needs_locator' if any(s['needs_locator'] for s in linked) else 'reference_present'
        rows.append({'record_id': record_id, 'event': event, 'date': value.get('date'),
                     'place': value.get('place_as_recorded') or value.get('place'),
                     'person_ids': person_ids, 'generation': min(depth[pid] for pid in person_ids),
                     'status': status, 'citations': linked, 'broken_source_ids': broken,
                     'record_level_source_ids': broad_refs,
                     'next': 'Locate an original document for this event' if status == 'missing_reference' else
                             'Repair the missing source records' if status == 'broken_reference' else
                             'Add archive locator or edition and page' if status == 'needs_locator' else
                             'Read the original and verify each date, place and identity; a reference is not proof'})

    for pid in depth:
        p = people[pid]
        if p.get('placeholder'):
            continue
        for key in PERSON_EVENTS:
            value = p.get(key)
            if isinstance(value, dict) and any(value.get(k) for k in ('date', 'place', 'place_as_recorded', 'note')):
                add(pid, key, value, [pid], refs_for(p))
    for family in families:
        members = [pid for pid in family.get('partners', []) if pid in depth]
        value = family.get('marriage')
        if members and isinstance(value, dict) and any(value.get(k) for k in ('date', 'place', 'place_as_recorded', 'note')):
            add(family['id'], 'marriage', value, members, refs_for(family))
    rank = {'broken_reference': 0, 'missing_reference': 1, 'needs_locator': 2, 'reference_present': 3}
    rows.sort(key=lambda row: (row['generation'], rank[row['status']], row['record_id'], row['event']))
    return {'root_person_id': root, 'generations': generations, 'people_considered': len(depth),
            'events': len(rows), 'counts': dict(collections.Counter(row['status'] for row in rows)),
            'items': rows[:limit], 'truncated': max(0, len(rows) - limit),
            'note': 'Coverage only, not proof or confidence scoring. A person/family-level source does not automatically support an event. Event references do not establish which individual fields the original actually supports. Parentage evidence needs separate review; an event with no recorded date/place is not counted.'}
