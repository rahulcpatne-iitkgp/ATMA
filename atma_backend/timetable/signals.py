from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import TimeSlot, Department, Batch

@receiver(post_migrate)
def populate_timeslots(sender, **kwargs):
    if sender.name != "timetable":
        return

    DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    SLOT_CHOICES = {
        'A': ('08:00:00', '09:00:00'),
        'B': ('09:00:00', '10:00:00'),
        'C': ('10:00:00', '11:00:00'),
        'D': ('11:00:00', '12:00:00'),
        'E': ('12:00:00', '13:00:00'),
        'F': ('14:00:00', '15:00:00'),
        'G': ('15:00:00', '16:00:00'),
        'H': ('16:00:00', '17:00:00'),
    }

    # Check if timeslots are already populated
    if TimeSlot.objects.exists():
        return  # Skip population if data exists

    for day in DAYS_OF_WEEK:
        for slot, (start, end) in SLOT_CHOICES.items():
            TimeSlot.objects.create(
                day=day,
                slot=slot,
            )
    print("TimeSlots populated successfully.")