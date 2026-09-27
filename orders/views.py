
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm
from stock.models import StockMovement


@login_required
@permission_required("orders.view_order", raise_exception=True)
def order_list(request):
    orders = Order.objects.order_by("-created_at")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        orders = orders.filter(
            Q(number__icontains=query) | Q(client_name__icontains=query)
            | Q(client_phone__icontains=query)
        )
    if status in {"PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"}:
        orders = orders.filter(status=status)

    return render(
        request,
        "orders/list.html",
        {
            "orders": orders,
            "query": query,
            "status": status,
            "has_filters": bool(query or status),
        }
    )


@login_required
@permission_required("orders.add_order", raise_exception=True)
def order_create(request):

    if request.method == "POST":

        order_form = OrderForm(request.POST)
        item_form = OrderItemForm(request.POST)

        if order_form.is_valid() and item_form.is_valid():

            item = item_form.save(commit=False)
            product = item.product

            if item.quantity > product.stock_quantity:
                item_form.add_error(
                    "quantity",
                    "Stock insuffisant pour effectuer cette commande."
                )

                return render(
                    request,
                    "orders/form.html",
                    {
                        "order_form": order_form,
                        "item_form": item_form
                    }
                )

            item.unit_price = product.selling_price
            item.total = item.quantity * item.unit_price

            with transaction.atomic():
                order = order_form.save()
                item.order = order
                item.save()
                order.total = item.total
                order.save(update_fields=["total"])
                product.stock_quantity -= item.quantity
                product.save(update_fields=["stock_quantity"])
                StockMovement.objects.create(
                    product=product,
                    movement_type="OUT",
                    quantity=item.quantity,
                    reason=f"Commande {order.number}"
                )

            messages.success(request, "Commande créée avec succès.")
            return redirect(
                "orders:list" if request.user.has_perm("orders.view_order") else "home"
            )

    else:
        order_form = OrderForm()
        item_form = OrderItemForm()

    return render(
        request,
        "orders/form.html",
        {
            "order_form": order_form,
            "item_form": item_form
        }
    )



@login_required
@permission_required("orders.view_order", raise_exception=True)
def order_detail(request, pk):

    order = get_object_or_404(Order.objects.prefetch_related(
        "items__product"
    ), pk=pk)

    return render(
        request,
        "orders/detail.html",
        {
            "order": order
        }
    )


@login_required
@permission_required("orders.change_order", raise_exception=True)
def order_update(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    item = order.items.first()

    if request.method == "POST":
        order_form = OrderForm(request.POST, instance=order)
        item_form = OrderItemForm(request.POST, instance=item)
        if order_form.is_valid() and item_form.is_valid():
            with transaction.atomic():
                old_product = item.product
                old_quantity = item.quantity
                new_product = item_form.cleaned_data["product"]
                new_quantity = item_form.cleaned_data["quantity"]
                available = new_product.stock_quantity
                if new_product == old_product:
                    available += old_quantity
                if new_quantity > available:
                    item_form.add_error(
                        "quantity", "La quantité demandée dépasse le stock disponible."
                    )
                else:
                    old_product.stock_quantity += old_quantity
                    old_product.save(update_fields=["stock_quantity"])
                    new_product.stock_quantity -= new_quantity
                    new_product.save(update_fields=["stock_quantity"])
                    order_form.save()
                    item = item_form.save(commit=False)
                    item.order = order
                    item.unit_price = new_product.selling_price
                    item.total = new_quantity * item.unit_price
                    item.save()
                    order.total = item.total
                    order.save(update_fields=["total"])
                    messages.success(request, "Commande modifiée avec succès.")
                    if request.user.has_perm("orders.view_order"):
                        return redirect("orders:detail", pk=order.pk)
                    return redirect("home")
    else:
        order_form = OrderForm(instance=order)
        item_form = OrderItemForm(instance=item)

    return render(request, "orders/form.html", {
        "order_form": order_form,
        "item_form": item_form,
        "order": order,
    })


@login_required
@permission_required("orders.delete_order", raise_exception=True)
def order_delete(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    if request.method == "POST":
        with transaction.atomic():
            for item in order.items.select_related("product"):
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=["stock_quantity"])
            order.delete()
        messages.success(request, "Commande supprimée avec succès.")
        return redirect(
            "orders:list" if request.user.has_perm("orders.view_order") else "home"
        )
    return render(request, "orders/delete.html", {"order": order})


@login_required
@permission_required("orders.view_order", raise_exception=True)
def order_invoice(request, pk):
    from decimal import Decimal
    from xml.sax.saxutils import escape

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="facture-{order.number}.pdf"'

    navy = colors.HexColor("#102d52")
    ink = colors.HexColor("#17243a")
    muted = colors.HexColor("#718096")
    pale_blue = colors.HexColor("#eaf2ff")
    border = colors.HexColor("#d7e2f0")
    page_width, _ = A4
    page_margin = 18 * mm
    content_width = page_width - 2 * page_margin

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="InvoiceTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.white,
        alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceBrand",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=navy,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=ink,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceCell",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=ink,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceCellRight",
        parent=styles["InvoiceCell"],
        alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceHeaderCell",
        parent=styles["InvoiceCell"],
        fontName="Helvetica-Bold",
        textColor=navy,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceTotal",
        parent=styles["InvoiceCell"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        alignment=TA_RIGHT,
        textColor=navy,
    ))

    def format_currency(value):
        amount = Decimal(value)
        return f"{amount:,.2f}".replace(",", " ").replace(".", ",") + " FCFA"

    issued_at = order.created_at.strftime("%d/%m/%Y à %H:%M")
    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=page_margin,
        rightMargin=page_margin,
        topMargin=17 * mm,
        bottomMargin=22 * mm,
        title=f"Facture {order.number}",
        author="Frameload Stock",
    )

    content = []
    heading = Table(
        [[
            Paragraph("Frameload Stock", styles["InvoiceBrand"]),
            Paragraph(f"FACTURE<br/>{escape(order.number)}", styles["InvoiceTitle"]),
        ]],
        colWidths=[content_width * 0.55, content_width * 0.45],
    )
    heading.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), navy),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 13),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 13),
    ]))
    content.extend([heading, Spacer(1, 12 * mm)])

    content.append(Paragraph("Informations client", styles["InvoiceSection"]))
    client_info = Table(
        [[
            Paragraph(
                f"<b>Client :</b> {escape(order.client_name or 'Client non renseigné')}",
                styles["InvoiceBody"],
            ),
            Paragraph(
                f"<b>Téléphone :</b> {escape(order.client_phone or 'Non renseigné')}",
                styles["InvoiceBody"],
            ),
        ]],
        colWidths=[content_width * 0.55, content_width * 0.45],
    )
    client_info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f9fc")),
        ("BOX", (0, 0), (-1, -1), 0.6, border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    content.extend([client_info, Spacer(1, 10 * mm)])

    item_rows = [[
        Paragraph("PRODUIT", styles["InvoiceHeaderCell"]),
        Paragraph("QUANTITÉ", styles["InvoiceHeaderCell"]),
        Paragraph("PRIX UNITAIRE", styles["InvoiceHeaderCell"]),
        Paragraph("TOTAL", styles["InvoiceHeaderCell"]),
    ]]
    for line in order.items.select_related("product").all():
        item_rows.append([
            Paragraph(escape(line.product.name), styles["InvoiceCell"]),
            Paragraph(str(line.quantity), styles["InvoiceCellRight"]),
            Paragraph(format_currency(line.unit_price), styles["InvoiceCellRight"]),
            Paragraph(format_currency(line.total), styles["InvoiceCellRight"]),
        ])

    item_rows.append([
        Paragraph("", styles["InvoiceCell"]),
        Paragraph("", styles["InvoiceCell"]),
        Paragraph("TOTAL DE LA COMMANDE", styles["InvoiceTotal"]),
        Paragraph(format_currency(order.total), styles["InvoiceTotal"]),
    ])

    items_table = Table(
        item_rows,
        colWidths=[
            content_width * 0.40,
            content_width * 0.14,
            content_width * 0.24,
            content_width * 0.22,
        ],
        repeatRows=1,
        hAlign="LEFT",
    )
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pale_blue),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f7f9fc")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, border),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, border),
        ("LINEBELOW", (0, 1), (-1, -2), 0.35, border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("SPAN", (0, -1), (1, -1)),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    content.append(items_table)

    def draw_footer(pdf_canvas, _document):
        pdf_canvas.saveState()
        pdf_canvas.setStrokeColor(border)
        pdf_canvas.setLineWidth(0.6)
        pdf_canvas.line(page_margin, 17 * mm, page_width - page_margin, 17 * mm)
        pdf_canvas.setFont("Helvetica", 8)
        pdf_canvas.setFillColor(muted)
        pdf_canvas.drawString(page_margin, 12 * mm, f"Émise le {issued_at}")
        pdf_canvas.drawRightString(
            page_width - page_margin,
            12 * mm,
            f"Page {pdf_canvas.getPageNumber()}",
        )
        pdf_canvas.restoreState()

    document.build(content, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return response
