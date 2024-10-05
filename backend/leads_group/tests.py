from django.test import TestCase
from rest_framework.test import APIClient
from .models import LeadGroup, Lead

class LeadImportExportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lead_group = LeadGroup.objects.create(name='Test Group')

    def test_export_leads(self):
        Lead.objects.create(group=self.lead_group, first_name='John', last_name='Doe', email='john@example.com')
        response = self.client.get(f'/api/lead-groups/{self.lead_group.id}/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_import_leads(self):
        csv_data = 'First Name,Last Name,Email\nJane,Doe,jane@example.com'
        mapping = {'First Name': 'first_name', 'Last Name': 'last_name', 'Email': 'email'}
        response = self.client.post(
            f'/api/lead-groups/{self.lead_group.id}/import_leads/',
            {'file': csv_data, 'mapping': mapping},
            format='multipart'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(Lead.objects.first().first_name, 'Jane')

