from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse


class EmployeeProductNavigationTests(TestCase):
    def setUp(self):
        employee_group, _ = Group.objects.get_or_create(name="EMPLOYEE")
        self.employee = get_user_model().objects.create_user(
            username="employee-product-user",
            password="test-password",
        )
        self.employee.groups.add(employee_group)
        add_permission = Permission.objects.get(
            content_type__app_label="products",
            codename="add_product",
        )
        self.employee.user_permissions.add(add_permission)
        self.client.force_login(self.employee)

    def test_employee_can_return_to_product_list_after_opening_add_form(self):
        response = self.client.get(reverse("products:create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("products:list")}"')
        self.assertNotContains(response, 'href="/connexion/"')

        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 200)

    def test_search_without_matches_has_search_specific_empty_state(self):
        response = self.client.get(reverse("products:list"), {"q": "not-found"})

        self.assertContains(response, "Aucun produit ne correspond à votre recherche.")
