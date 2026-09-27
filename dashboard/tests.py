from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from categories.models import Category
from orders.models import Order, OrderItem
from products.models import Product
from sales.models import Sale, SaleItem
from suppliers.models import Supplier


class DashboardStatisticsTests(TestCase):
    def setUp(self):
        manager_group, _ = Group.objects.get_or_create(name="MANAGER")
        self.user = get_user_model().objects.create_user(
            username="dashboard-manager",
            password="test-password",
        )
        self.user.groups.add(manager_group)
        self.client.force_login(self.user)

        self.category = Category.objects.create(name="Test category")
        self.product = Product.objects.create(
            name="Best seller",
            category=self.category,
            purchase_price=Decimal("5.00"),
            selling_price=Decimal("10.00"),
            stock_quantity=2,
            minimum_stock=5,
        )
        self.out_of_stock_product = Product.objects.create(
            name="Unavailable product",
            category=self.category,
            purchase_price=Decimal("3.00"),
            selling_price=Decimal("7.00"),
            stock_quantity=0,
            minimum_stock=2,
        )
        Supplier.objects.create(name="Test supplier")

    def test_dashboard_statistics_count_sales_but_not_orders(self):
        today = timezone.localdate()
        sale = Sale.objects.create(
            client_name="Today customer",
            total=Decimal("20.00"),
        )
        sale.created_at = timezone.now()
        Sale.objects.filter(pk=sale.pk).update(created_at=sale.created_at)
        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=2,
            unit_price=Decimal("10.00"),
            total=Decimal("20.00"),
        )

        completed_order = Order.objects.create(
            client_name="Completed customer",
            total=Decimal("30.00"),
            status="COMPLETED",
        )
        completed_order.created_at = timezone.now()
        Order.objects.filter(pk=completed_order.pk).update(
            created_at=completed_order.created_at
        )
        OrderItem.objects.create(
            order=completed_order,
            product=self.product,
            quantity=3,
            unit_price=Decimal("10.00"),
            total=Decimal("30.00"),
        )

        old_sale = Sale.objects.create(total=Decimal("40.00"))
        Sale.objects.filter(pk=old_sale.pk).update(
            created_at=timezone.now() - timedelta(days=35)
        )

        pending_order = Order.objects.create(
            total=Decimal("500.00"),
            status="PENDING",
        )
        OrderItem.objects.create(
            order=pending_order,
            product=self.product,
            quantity=50,
            unit_price=Decimal("10.00"),
            total=Decimal("500.00"),
        )

        response = self.client.get(reverse("dashboard:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_products"], 2)
        self.assertEqual(response.context["total_categories"], 1)
        self.assertEqual(response.context["total_suppliers"], 1)
        self.assertEqual(response.context["total_stock"], 2)
        self.assertEqual(response.context["total_sales"], 2)
        self.assertEqual(response.context["chiffre_affaires"], Decimal("60.00"))
        self.assertEqual(response.context["ventes_aujourd_hui"], 1)
        self.assertEqual(
            response.context["chiffre_affaires_aujourd_hui"],
            Decimal("20.00"),
        )
        self.assertEqual(
            response.context["chiffre_affaires_ce_mois"],
            Decimal("20.00"),
        )
        self.assertEqual(response.context["commandes_en_attente"], 1)
        self.assertEqual(response.context["produits_stock_faible"], 1)
        self.assertEqual(response.context["produits_en_rupture"], 1)
        self.assertEqual(response.context["top_products"][0]["name"], "Best seller")
        self.assertEqual(
            response.context["top_products"][0]["quantity_sold"],
            2,
        )
        self.assertEqual(len(response.context["daily_revenue"]), 7)
        self.assertEqual(response.context["daily_revenue"][-1]["date"], today)
        self.assertEqual(
            response.context["daily_revenue"][-1]["date_label"],
            f"{['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][today.weekday()]} {today:%d/%m}",
        )
        self.assertEqual(
            response.context["daily_revenue"][-1]["total"],
            Decimal("20.00"),
        )

    def test_dashboard_is_limited_to_management_users(self):
        employee = get_user_model().objects.create_user(
            username="dashboard-employee",
            password="test-password",
        )
        self.client.force_login(employee)

        response = self.client.get(reverse("dashboard:index"))

        self.assertEqual(response.status_code, 403)

    def test_sidebar_displays_the_users_role(self):
        response = self.client.get(reverse("dashboard:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<small>Manager</small>")
