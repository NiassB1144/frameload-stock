from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class CategorySearchStateTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="category-viewer",
            password="Test-password-123!",
        )
        permission = Permission.objects.get(
            content_type__app_label="categories",
            codename="view_category",
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

    def test_search_without_matches_shows_specific_empty_state(self):
        response = self.client.get(reverse("categories:list"), {"q": "not-found"})

        self.assertContains(response, "Aucune catégorie ne correspond à votre recherche.")
