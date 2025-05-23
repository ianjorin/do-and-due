from chore_tracker.models import Group, Event
from datetime import datetime
from dateutil.relativedelta import relativedelta

TIME_THRESHOLD = relativedelta(days=90)

def update_recurring_events(group):
    events = Event.objects.filter(group=group)

    for event in events:
        if event.repeat_every is None or event.repeat_every=='':
            continue
        
        if event.repeat_every=="Daily":
            t_delta = relativedelta(days=1)
        elif event.repeat_every=="Weekly":
            t_delta = relativedelta(weeks=1)
        elif event.repeat_every=="Monthly":
            t_delta = relativedelta(months=1)
        else: # Malformed value
            continue

        end_time = datetime.date(datetime.today() + TIME_THRESHOLD)
        start_time = event.first_date
        cur_time = start_time + t_delta
        while cur_time <= end_time:

            future_events = Event.objects.filter(group=group, first_date=cur_time, name=event.name)
            if len(future_events) == 0: # Here we will need to make future events
                new_event = Event.objects.create(
                    # ID should be created automatically
                    name=event.name,
                    first_date=cur_time, # This should be the only difference
                    repeat_every=event.repeat_every,
                    group=group,
                    #members=event.members,
                    is_complete=False,
                )
                new_event.members.set(event.members.all())
            cur_time += t_delta

def delete_recurrences(event):
    if event.repeat_every is None or event.repeat_every=='':
        return
    future_events = Event.objects.filter(group=event.group, 
                                         name=event.name, 
                                         repeat_every=event.repeat_every,
                                         first_date__gt=event.first_date)
    for fe in future_events:
        fe.delete()
