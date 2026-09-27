from decimal import Decimal
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from categories.models import Category
from products.models import Product
from stock.models import StockMovement
from .models import Order, OrderItem


class OrderInvoiceTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="invoice-user",
            password="test-password",
        )
        permission = Permission.objects.get(
            content_type__app_label="orders",
            codename="view_order",
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        category = Category.objects.create(name="Invoice category")
        self.products = [
            Product.objects.create(
                name=(
                    "Équipement professionnel avec un nom très long "
                    "qui doit passer sur plusieurs lignes sans déborder "
                    f"{number}"
                ),
                category=category,
                purchase_price=Decimal("5.00"),
                selling_price=Decimal("10.00"),
                stock_quantity=1,
                minimum_stock=1,
            )
            for number in range(2)
        ]
        self.order = Order.objects.create(
            client_name="Client de démonstration",
            client_phone="0102030405",
            total=Decimal("20000.00"),
        )
        for product in self.products:
            OrderItem.objects.create(
                order=self.order,
                product=product,
                quantity=1,
                unit_price=Decimal("10000.00"),
                total=Decimal("10000.00"),
            )

    def test_invoice_download_is_a_valid_pdf_with_ordered_columns(self):
        response = self.client.get(
            reverse("orders:invoice", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(
            f'facture-{self.order.number}.pdf',
            response["Content-Disposition"],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertTrue(response.content.rstrip().endswith(b"%%EOF"))
        self.assertEqual(
            len(re.findall(rb"/Type\s*/Page\b", response.content)),
            1,
        )

    def test_order_search_without_matches_shows_specific_empty_state(self):
        response = self.client.get(reverse("orders:list"), {"q": "not-found"})

        self.assertContains(response, "Aucune commande ne correspond à votre recherche.")


class OrderSubmissionScenarioTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="order-creator",
            password="Test-password-123!",
        )
        permission = Permission.objects.get(
            content_type__app_label="orders",
            codename="add_order",
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)
        category = Category.objects.create(name="Order category")
        self.product = Product.objects.create(
            name="Order product",
            category=category,
            purchase_price=Decimal("5.00"),
            selling_price=Decimal("10.00"),
            stock_quantity=2,
        )

    def post_order(self, quantity):
        return self.client.post(
            reverse("orders:create"),
            {
                "client_name": "Test client",
                "client_phone": "",
                "status": "PENDING",
                "product": self.product.pk,
                "quantity": quantity,
            },
        )

    def test_zero_quantity_is_rejected_without_creating_order(self):
        response = self.post_order(0)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La quantité doit être supérieure à 0.")
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_insufficient_stock_does_not_create_partial_order(self):
        response = self.post_order(3)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock insuffisant pour effectuer cette commande.")
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(StockMovement.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 2)

    def test_successful_order_shows_message(self):
        response = self.client.post(
            reverse("orders:create"),
            {
                "client_name": "Test client",
                "client_phone": "",
                "status": "PENDING",
                "product": self.product.pk,
                "quantity": 1,
            },
            follow=True,
        )

        self.assertContains(response, "Commande créée avec succès.")
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(StockMovement.objects.count(), 1)
