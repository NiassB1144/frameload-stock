from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from categories.models import Category
from orders.models import Order
from products.models import Product
from sales.models import Sale, SaleItem
from stock.models import StockMovement


class SalesListTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="sales-viewer",
            password="test-password",
        )
        permission = Permission.objects.get(
            content_type__app_label="sales",
            codename="view_sale",
        )
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

    def test_list_contains_sales_only(self):
        sale = Sale.objects.create(
            client_name="Sale customer",
            total=Decimal("25.00"),
        )
        completed_order = Order.objects.create(
            number="CMD-COMPLETE",
            client_name="Completed customer",
            total=Decimal("50.00"),
            status="COMPLETED",
        )
        Order.objects.create(
            number="CMD-PENDING",
            client_name="Pending customer",
            total=Decimal("100.00"),
            status="PENDING",
        )

        response = self.client.get(reverse("sales:list"))

        self.assertEqual(response.status_code, 200)
        records = response.context["sales"]
        self.assertEqual(response.context["total_sales"], 1)
        self.assertEqual(
            {record["reference"] for record in records},
            {f"Vente #{sale.pk}"},
        )
        self.assertContains(response, "Ventes enregistrées")

    def test_list_displays_sold_products_and_quantities(self):
        category = Category.objects.create(name="Sales list category")
        product = Product.objects.create(
            name="Clavier sans fil",
            category=category,
            purchase_price=Decimal("10.00"),
            selling_price=Decimal("25.00"),
            stock_quantity=4,
        )
        sale = Sale.objects.create(client_name="Sale customer", total=Decimal("50.00"))
        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=2,
            unit_price=Decimal("25.00"),
            total=Decimal("50.00"),
        )

        response = self.client.get(reverse("sales:list"))

        self.assertContains(response, "Clavier sans fil")
        self.assertContains(response, "× 2")
        self.assertEqual(response.context["sales"][0]["items"][0]["quantity"], 2)

    def test_search_does_not_return_orders(self):
        Order.objects.create(
            number="CMD-SEARCH",
            total=Decimal("15.00"),
            status="COMPLETED",
        )
        response = self.client.get(reverse("sales:list"), {"q": "CMD-SEARCH"})
        response = self.client.get(reverse("sales:list"), {"q": "CMD-SEARCH"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["sales"], [])

    def test_search_without_matches_shows_specific_empty_state(self):
        response = self.client.get(reverse("sales:list"), {"q": "not-found"})

        self.assertContains(response, "Aucune vente ne correspond à votre recherche.")


class SaleSubmissionScenarioTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="sale-creator",
            password="Test-password-123!",
        )
        permission = Permission.objects.get(
            content_type__app_label="sales",
            codename="add_sale",
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)
        category = Category.objects.create(name="Sale category")
        self.product = Product.objects.create(
            name="Sale product",
            category=category,
            purchase_price=Decimal("5.00"),
            selling_price=Decimal("10.00"),
            stock_quantity=2,
        )

    def post_sale(self, quantity):
        return self.client.post(
            reverse("sales:create"),
            {
                "client_name": "Test client",
                "client_phone": "",
                "product": self.product.pk,
                "quantity": quantity,
            },
        )

    def test_quantity_must_be_greater_than_zero(self):
        response = self.post_sale(0)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La quantité doit être supérieure à 0.")
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(self.product.stock_quantity, 2)

    def test_insufficient_stock_does_not_create_partial_sale(self):
        response = self.post_sale(3)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stock insuffisant pour effectuer cette vente.")
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(SaleItem.objects.count(), 0)
        self.assertEqual(StockMovement.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 2)

    def test_successful_sale_shows_message_and_updates_stock(self):
        response = self.client.post(
            reverse("sales:create"),
            {
                "client_name": "Test client",
                "client_phone": "",
                "product": self.product.pk,
                "quantity": 1,
            },
            follow=True,
        )

        self.assertContains(response, "Vente enregistrée avec succès.")
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(SaleItem.objects.count(), 1)
        self.assertEqual(StockMovement.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 1)

# Create your tests here.
