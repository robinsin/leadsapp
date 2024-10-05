from django.db import models



class LeadGroupType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_custom = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class LeadGroup(models.Model):
    lead_group_type = models.ForeignKey(LeadGroupType, related_name='leadgroups', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active_fields = models.JSONField(default=list)
    removed_fields = models.JSONField(default=list)
    form_structure = models.JSONField(default=list)
    #lead_group_type = models.ForeignKey(LeadGroupType, on_delete=models.CASCADE, default=1)  # Assuming 1 is the ID for the default type
    #lead_group_type = models.ForeignKey(LeadGroupType, on_delete=models.CASCADE, null=True)
    #lead_group_type = models.ForeignKey(LeadGroupType, on_delete=models.CASCADE)

    #lead_group_type = models.ForeignKey(LeadGroupType, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.lead_group_type:
            self.lead_group_type = LeadGroupType.objects.get(name='Contact')
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class Lead(models.Model):
    group = models.ForeignKey(LeadGroup, related_name='leads', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    custom_fields = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CustomField(models.Model):
    lead_group = models.ForeignKey(LeadGroup, related_name='custom_fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50)  # e.g., 'text', 'number', 'date', etc.

    def __str__(self):
        return f"{self.name} ({self.lead_group.name})"

