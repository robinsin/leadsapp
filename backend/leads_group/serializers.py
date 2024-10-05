from rest_framework import serializers
from .models import Lead, LeadGroup, CustomField, LeadGroupType

class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = ['id', 'name', 'field_type']


class LeadGroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadGroupType
        fields = ['id', 'name', 'is_custom']

class LeadGroupSerializer(serializers.ModelSerializer):
    lead_group_type = LeadGroupTypeSerializer(read_only=True)
    lead_group_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LeadGroupType.objects.all(), source='lead_group_type', write_only=True
    )

    class Meta:
        model = LeadGroup
        fields = '__all__'

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'group', 'first_name', 'last_name', 'email', 'phone', 'company', 'company_name', 'website', 'address', 'custom_fields', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        lead_group_type = data['group'].lead_group_type.name
        if lead_group_type == 'Company' and not data.get('company_name'):
            raise serializers.ValidationError({"company_name": "This field is required for Company lead groups."})
        elif lead_group_type == 'Newsletter' and not data.get('email'):
            raise serializers.ValidationError({"email": "This field is required for Newsletter lead groups."})
        return data



