from django.db import models
from django.contrib.auth.models import User


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    topic = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} - {self.topic} ({self.created_at.strftime('%Y-%m-%d')})"


class TestSubmission(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)  

    def __str__(self):
        return f"Submission by {self.user.username} for {self.test.topic} on {self.submitted_at.strftime('%Y-%m-%d')}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.name} - {self.email}"
    

class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
    completed_sections = models.JSONField(default=list) 

    def __str__(self):
        return f"{self.user.username} - {self.course_name} Progress"
    

class StudyRoom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    course_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_study_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='joined_study_rooms', blank=True)

    def __str__(self):
        return f"{self.name} ({self.course_name}) by {self.created_by.username}"


class Message(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} in {self.room.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class UserNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.user.username} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


