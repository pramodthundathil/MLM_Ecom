from django.core.management.base import BaseCommand
from Home.models import CustomUser, Business_Volume

class Command(BaseCommand):
    help = 'Calculate and update designations for all users'

    def handle(self, *args, **kwargs):
        all_users = CustomUser.objects.all()

        for user in all_users:
            total_bv = self.calculate_total_bv(user)

            # Update designation based on total BV
            if total_bv > 50000 and user.designation == "Executive":
                user.designation = "Chief Executive"
                user.save()

            # Check for promotion to Manager
            direct_members = CustomUser.objects.filter(parent=user)
            active_executives_count = sum(1 for member in direct_members if member.designation == "Executive" and member.is_active)

            if user.designation == "Chief Executive" and len(direct_members) >= 7 and active_executives_count >= 5:
                user.designation = "Manager"
                user.save()

            # Check for promotion to General Manager
            active_chief_executives_count = sum(1 for member in direct_members if member.designation == "Chief Executive" and member.is_active)
            if user.designation == "Manager" and len(direct_members) >= 10 and active_chief_executives_count >= 5:
                user.designation = "General Manager"
                user.save()

            # Check for promotion to Director
            active_managers_count = sum(1 for member in direct_members if member.designation == "Manager" and member.is_active)
            if user.designation == "Manager" and len(direct_members) >= 12 and active_managers_count >= 6:
                user.designation = "Director"
                user.save()

            self.stdout.write(self.style.SUCCESS(f'Processed {user.email}'))

    def calculate_total_bv(self, user):
        """
        Recursively calculate the total purchase BV for a user and all their descendants.
        """
        # Get the BV for the current user
        my_bv = Business_Volume.objects.get(user=user)
        total_bv = my_bv.purchase_bv

        # Get all direct children of the user
        direct_members = CustomUser.objects.filter(parent=user)

        # Recursively calculate BV for each child
        for child in direct_members:
            total_bv += self.calculate_total_bv(child)

        return total_bv
