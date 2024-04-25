from datetime import datetime, timedelta

from django_cron import CronJobBase, Schedule

from app.models import Authorization


class ClearAuthCodeJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.clear_auth_code'

    def do(self):
        current_time = datetime.now()
        offset = 15
        offset_time = current_time + timedelta(minutes=offset)
        records_to_delete = Authorization.objects.filter(Authorization.create_at <= offset_time)

        records_to_delete.delete()