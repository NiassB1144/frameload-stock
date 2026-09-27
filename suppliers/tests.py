from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class SupplierSearchStateTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="supplier-viewer",
            password="Test-password-123!",
        )
        permission = Permission.objects.get(
            content_type__app_label="suppliers",
            codename="view_supplier",
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

    def test_search_without_matches_shows_specific_empty_state(self):
        response = self.client.get(reverse("suppliers:list"), {"q": "not-found"})

        self.assertContains(response, "Aucun fournisseur ne correspond à votre recherche.")
