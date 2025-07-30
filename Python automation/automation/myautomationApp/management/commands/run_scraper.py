from myautomationApp.models import MostWanted
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from myautomationApp.scraper import compare_data, apply_changes_to_db
import logging

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        changes = compare_data()

# show results in cli
        if changes['new'] or changes['deleted']:
            self.stdout.write("=== Changes Detected ===")

            if changes['new']:
                self.stdout.write(self.style.NOTICE(f"New: {len(changes['new'])}"))
                for record in changes['new']:
                    self.stdout.write(f"- {record}")

            if changes['deleted']:
                self.stdout.write(self.style.NOTICE(f"Deleted: {len(changes['deleted'])}"))
                for record in changes['deleted']:
                    self.stdout.write(f"- {record}")
        # Send email if change detected
            self.send_email_notification(changes)
        else:
            self.stdout.write(self.style.NOTICE("No changes detected"))
            return

# 3. Wait for user confirmation
        if input("\nSave these changes? [y/N] ").lower() != 'y':
            self.stdout.write("Changes cancelled")
            return

        apply_changes_to_db(changes)

    def send_email_notification(self, changes):

        from django.core.mail import send_mail
        from django.conf import settings

        # put it in logs for future check
        logger = logging.getLogger('scheduler')
        logger.info(changes)


        subject = "Scraper: Changes Detected!"
        message = "Scraper found some changes\n\n"

        if changes['new']:
            message = message + f"New Records {len(changes['new'])}:\n"
        if changes['deleted']:
            message += f"Deleted Records {len(changes['deleted'])}:\n"

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["test@gmail.com"], # smpt only for gmail in set
                fail_silently=False,
            )
            print("Email notification sent!")
            logger.info("Email notification sent!")
        except Exception as e:
            print(f"Failed to send email: {e}")
            logger.error(f"Failed to send email: {e}")
