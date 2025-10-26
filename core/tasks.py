from django.core.management import call_command
from huey import crontab
from huey.contrib.djhuey import periodic_task


@periodic_task(crontab(hour="0", minute="0"))
def task_generate_images():
    call_command("generateimages")
