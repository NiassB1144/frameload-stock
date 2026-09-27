from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from categories.models import Category
from products.models import Product
from stock.forms import StockMovementForm


class StockAlertAcknowledgementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stock-alert-user",
            password="test-password",
        )
        permission = Permission.objects.get(
            content_type__app_label="stock",
            codename="view_stockmovement",
        )
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        category = Category.objects.create(name="Test category")
        self.product = Product.objects.create(
            name="Low stock product",
            category=category,
            purchase_price="1.00",
            selling_price="2.00",
            stock_quantity=2,
            minimum_stock=5,
        )

    def test_acknowledging_alert_hides_badge_until_stock_changes(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'class="notification-badge">1</span>')

        response = self.client.post(reverse("acknowledge_stock_alerts"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"acknowledged": True})

        response = self.client.get(reverse("home"))
        self.assertNotContains(response, 'class="notification-badge">1</span>')

        self.client.get(reverse("logout"))
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, 'class="notification-badge">1</span>')

        self.product.stock_quantity = 1
        self.product.save(update_fields=["stock_quantity"])
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'class="notification-badge">1</span>')

    def test_acknowledgement_requires_post(self):
        response = self.client.get(reverse("acknowledge_stock_alerts"))
        self.assertEqual(response.status_code, 405)

    def test_user_without_permission_cannot_acknowledge_alerts(self):
        user = get_user_model().objects.create_user(
            username="unprivileged-user",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("acknowledge_stock_alerts"))
        self.assertEqual(response.status_code, 403)

    def test_stock_viewer_can_consult_but_cannot_add_movements(self):
        response = self.client.get(reverse("stock:list"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("stock:create"))
        self.assertNotContains(response, "Nouveau mouvement")
        self.assertNotContains(response, "Ajouter un mouvement")

        response = self.client.get(reverse("stock:create"))
        self.assertEqual(response.status_code, 403)

    def test_search_without_matches_has_search_specific_empty_state(self):
        response = self.client.get(reverse("stock:list"), {"q": "not-found"})

        self.assertContains(response, "Aucun mouvement de stock ne correspond à votre recherche.")


class StockMovementValidationTests(TestCase):
    def test_zero_quantity_is_rejected(self):
        form = StockMovementForm(
            {
                "product": 1,
                "movement_type": "IN",
                "quantity": 0,
                "reason": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["quantity"],
            ["La quantité doit être supérieure à 0."],
        )


class StockMovementSubmissionTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="stock-creator",
            password="Test-password-123!",
        )
        permission = Permission.objects.get(
            content_type__app_label="stock",
            codename="add_stockmovement",
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)
        category = Category.objects.create(name="Movement category")
        self.product = Product.objects.create(
            name="Movement product",
            category=category,
            purchase_price="1.00",
            selling_price="2.00",
            stock_quantity=2,
        )

    def test_insufficient_stock_keeps_quantity_and_creates_no_movement(self):
        response = self.client.post(
            reverse("stock:create"),
            {
                "product": self.product.pk,
                "movement_type": "OUT",
                "quantity": 3,
                "reason": "Test",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock insuffisant pour effectuer cette sortie.")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 2)
        self.assertFalse(self.product.stock_movements.exists())
