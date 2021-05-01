from django.db import models


class Visit(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField(auto_now_add=True)
    doctor_id = models.IntegerField(blank=False)
    username = models.IntegerField(blank=False)
    status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.id
