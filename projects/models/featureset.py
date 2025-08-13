from django.db import models

class FeatureSet(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='feature_sets')
    features = models.JSONField(default=list)

    def __str__(self):
        return self.name