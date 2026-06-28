from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
#python manage.py makemigrations
#python manage.py migrate
#.venv\Scripts\Activate.ps1
class Program(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    equipment = models.TextField(blank=True)
    image_url = models.URLField(blank=True)#blank=True znači: u adminu to polje može ostati prazno.
    price_eur = models.DecimalField(max_digits = 8, decimal_places = 2)

    CATEGORY_CHOICES = [
    ('HOME', 'Home Workout'),
    ('GYM', 'Gym Workout'),
    ]

    DIFFICULTY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='HOME'
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='BEGINNER'
    )

    duration_weeks = models.PositiveIntegerField(default=1)

    recommended_schedule = models.TextField(blank=True)

    def __str__(self):
        return self.title  #prikazi title kao naslov / Program object (1)


class Video(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    order = models.PositiveIntegerField(default=1)
    duration_minutes = models.PositiveIntegerField(default=10)
    week_number = models.PositiveIntegerField(default=1)
    is_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class PurchasedProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
       unique_together = ('user', 'program')

    def __str__(self):
        return f"{self.user.username} - {self.program.title}" #PurchasedProgram object (1) - test123 - Beach Body
                                                              #PurchasedProgram object (2) - test123 - Build a Boot

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'program')

    def __str__(self):
        return f"{self.user.username} - {self.program.title} ({self.rating}/5)"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'program')

    def __str__(self):
        return f"{self.user.username} - {self.program.title}"