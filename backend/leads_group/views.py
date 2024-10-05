from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import LeadGroupType, LeadGroup, Lead, CustomField
from .serializers import LeadGroupSerializer, LeadSerializer, LeadGroupTypeSerializer, CustomFieldSerializer
from rest_framework.decorators import api_view
import json
import csv
from io import StringIO
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class LeadGroupTypeViewSet(viewsets.ModelViewSet):
    queryset = LeadGroupType.objects.all()
    serializer_class = LeadGroupTypeSerializer

    @action(detail=False, methods=['POST'])
    def create_custom(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
        lead_group_type = LeadGroupType.objects.create(name=name, is_custom=True)
        serializer = self.get_serializer(lead_group_type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    

class LeadGroupViewSet(viewsets.ModelViewSet):
    queryset = LeadGroup.objects.all()
    serializer_class = LeadGroupSerializer

    def get_queryset(self):
        queryset = LeadGroup.objects.all()
        lead_group_type_id = self.request.query_params.get('lead_group_type_id')
        if lead_group_type_id:
            queryset = queryset.filter(lead_group_type_id=lead_group_type_id)
        return queryset
    

    @action(detail=True, methods=['GET'])
    def fields(self, request, pk=None):
        lead_group = self.get_object()
        active_fields = lead_group.active_fields
        default_fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'website', 'address']
        available_fields = ['company', 'website', 'address']  # Add more as needed
        removed_fields = lead_group.removed_fields
        all_fields = list(set(default_fields + active_fields))
        return Response({
            'active_fields': all_fields,
            'available_fields': [f for f in available_fields if f not in all_fields],
            'removed_fields': removed_fields
        })


    @action(detail=True, methods=['POST'])
    def add_field(self, request, pk=None):
        lead_group = self.get_object()
        field = request.data.get('field')
        if field and field not in lead_group.active_fields:
            lead_group.active_fields.append(field)
            if field in lead_group.removed_fields:
                lead_group.removed_fields.remove(field)  # Remove from removed fields if it was there
            lead_group.save()
        return Response(lead_group.active_fields)

    @action(detail=True, methods=['POST'])
    def remove_field(self, request, pk=None):
        lead_group = self.get_object()
        field = request.data.get('field')
        if field in lead_group.active_fields:
            lead_group.active_fields.remove(field)
            if field not in lead_group.removed_fields:
                lead_group.removed_fields.append(field)  # Add to removed fields if not already there
            lead_group.save()
        return Response(lead_group.active_fields)
    

    @action(detail=True, methods=['GET'])
    def export(self, request, pk=None):
        lead_group = self.get_object()
        leads = Lead.objects.filter(group=lead_group)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="leads_export_{lead_group.id}.csv"'
        
        writer = csv.writer(response)
        
        # Get all custom fields for this lead group
        custom_fields = CustomField.objects.filter(lead_group=lead_group)
        
        # Create header row with standard fields and custom fields
        header = ['First Name', 'Last Name', 'Email', 'Phone', 'Company', 'Website', 'Address']
        header.extend([field.name for field in custom_fields])
        writer.writerow(header)
        
        for lead in leads:
            row = [lead.first_name, lead.last_name, lead.email, lead.phone, lead.company, lead.website, lead.address]
            for field in custom_fields:
                row.append(lead.custom_fields.get(field.name, ''))
            writer.writerow(row)
        
        return response


    @action(detail=True, methods=['POST'])
    def import_leads(self, request, pk=None):
        lead_group = self.get_object()
        mapping = json.loads(request.data.get('mapping', '{}'))
        new_fields = json.loads(request.data.get('new_fields', '{}'))
        csv_file = request.FILES.get('file')

        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            csv_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(StringIO(csv_data))
            
            with transaction.atomic():
                # Create new custom fields
                for csv_header, field_name in new_fields.items():
                    CustomField.objects.create(lead_group=lead_group, name=field_name)
                    lead_group.active_fields.append(field_name)
                lead_group.save()

                for row in csv_reader:
                    lead_data = {}
                    custom_fields = {}
                    for csv_header, field_name in mapping.items():
                        if field_name == 'new':
                            field_name = new_fields[csv_header]
                        if field_name in ['first_name', 'last_name', 'email', 'phone', 'company', 'website', 'address']:
                            lead_data[field_name] = row[csv_header]
                        else:
                            custom_fields[field_name] = row[csv_header]
                    
                    lead = Lead.objects.create(group=lead_group, **lead_data, custom_fields=custom_fields)

            return Response({'message': 'Leads imported successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def update_form_structure(self, request, pk=None):
        lead_group = self.get_object()
        lead_group.form_structure = request.data.get('form_structure', [])
        lead_group.save()
        return Response({'status': 'form structure updated'})



class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer

    def get_queryset(self):
        lead_group_id = self.kwargs['lead_group_pk']
        return Lead.objects.filter(group_id=lead_group_id)

    def create(self, request, *args, **kwargs):
        lead_group_id = self.kwargs['lead_group_pk']
        request.data['group'] = lead_group_id
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        lead_group_id = self.kwargs['lead_group_pk']
        custom_fields = self.request.data.get('custom_fields', {})
        serializer.save(group_id=lead_group_id, custom_fields=custom_fields)

    def update(self, request, *args, **kwargs):
        lead_group_id = self.kwargs['lead_group_pk']
        request.data['group'] = lead_group_id
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        custom_fields = self.request.data.get('custom_fields', {})
        serializer.save(custom_fields=custom_fields)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=False, methods=['POST'])
    def bulk_delete(self, request, lead_group_pk=None):
        lead_ids = request.data.get('lead_ids', [])
        if not lead_ids:
            return Response({"error": "No lead IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = Lead.objects.filter(group_id=lead_group_pk, id__in=lead_ids).delete()[0]

        return Response({
            "message": f"Successfully deleted {deleted_count} leads",
            "deleted_count": deleted_count
        }, status=status.HTTP_200_OK)
    

@csrf_exempt
def get_embed_form(request, group_id):
    try:
        lead_group = LeadGroup.objects.get(id=group_id)
        return JsonResponse({
            'form_structure': lead_group.form_structure,
            'group_id': group_id
        })
    except LeadGroup.DoesNotExist:
        return JsonResponse({'error': 'Lead group not found'}, status=404)    

@api_view(['GET'])
def get_custom_fields_for_lead_group(request, group_id):
    try:
        lead_group = LeadGroup.objects.get(id=group_id)
    except LeadGroup.DoesNotExist:
        return Response({'error': 'Lead group not found'}, status=status.HTTP_404_NOT_FOUND)
    # Assuming we store field definitions somewhere, return them here
    # For simplicity, we'll return a static list
    fields = ['first_name', 'last_name', 'email', 'phone', 'title', 'company', 'status']
    return Response(fields)

class CustomFieldViewSet(viewsets.ModelViewSet):
    serializer_class = CustomFieldSerializer

    def get_queryset(self):
        lead_group_id = self.kwargs['lead_group_pk']
        return CustomField.objects.filter(lead_group_id=lead_group_id)

    def perform_create(self, serializer):
        lead_group_id = self.kwargs['lead_group_pk']
        serializer.save(lead_group_id=lead_group_id)

@api_view(['POST'])
def add_custom_field_to_lead_group(request, group_id):
    # Retrieve the lead group object
    try:
        lead_group = LeadGroup.objects.get(id=group_id)
    except LeadGroup.DoesNotExist:
        return Response({'error': 'Lead group not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Extract field name from request data
    field_name = request.data.get('name')
    if not field_name:
        return Response({'error': 'Field name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Add custom field logic here
    # For simplicity, let's assume the custom field is added to the lead group
    
    return Response({'message': f'Custom field "{field_name}" added to lead group {lead_group.id}'}, status=status.HTTP_201_CREATED)
