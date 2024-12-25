from django.db import models
from django.contrib.auth.models import User



class Projects(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Graded', 'Graded'),
    ]

    # Student Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20, unique=True)  # Unique student identifier
    email = models.EmailField()  # Student's email for notifications
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)  # Project owner

    # Project Information
    title = models.CharField(max_length=255)
    url = models.CharField(blank=True, default="", max_length=255)
    description = models.TextField()
    #file = models.FileField(upload_to=f'projects/')  # File upload for project
    file = models.URLField(max_length=500)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Grading Information
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # Grading status
    grade = models.CharField(max_length=5, blank=True, null=True)  # Grade (e.g., A+, 95)
    graded_at = models.DateTimeField(blank=True, null=True)  # When the project was graded
    grading_note = models.TextField(blank=True, null=True)  # Note or feedback from the teacher

    def __str__(self):
        return f"{self.student_id} - {self.title}"
