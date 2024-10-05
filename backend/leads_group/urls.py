from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from .views import LeadGroupViewSet, LeadViewSet, CustomFieldViewSet, LeadGroupTypeViewSet
from . import views
router = DefaultRouter()
router.register(r'lead-group-types', LeadGroupTypeViewSet)
router.register(r'lead-groups', LeadGroupViewSet, basename='leadgroup')

lead_groups_router = NestedSimpleRouter(router, r'lead-groups', lookup='lead_group')
lead_groups_router.register(r'leads', LeadViewSet, basename='leadgroup-leads')
lead_groups_router.register(r'custom-fields', CustomFieldViewSet, basename='leadgroup-customfields')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(lead_groups_router.urls)),
    path('lead-groups/<int:group_id>/embed-form/', views.get_embed_form, name='get_embed_form'),
]
