from django.db import models


class SolveHistory(models.Model):
    colors = models.JSONField()
    moves = models.JSONField()
    move_count = models.IntegerField()
    solve_time_ms = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Solve #{self.id} - {self.move_count} moves - {self.created_at:%Y-%m-%d %H:%M}"
