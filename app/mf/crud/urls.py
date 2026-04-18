from django.urls import path
from mf.crud.views.dashboard.views import *
from mf.crud.views.companyInfo.views import *
from mf.crud.views.events.views import *
from mf.crud.views.category.views import *
from mf.crud.views.brand.views import *
from mf.crud.views.type.views import *
from mf.crud.views.product.views import *
from mf.crud.views.client.views import *
from mf.crud.views.method.views import *
from mf.crud.views.sale.views import *
from mf.crud.views.credit.views import *
from mf.crud.views.debt.views import *
from mf.crud.views.budget.views import *

app_name = 'crud'

urlpatterns = [
    # Dashboard
    path('inicio/', DashboardView.as_view(), name='dashboard'),
    # Company Info
    path('informacion/', CompanyInfoView.as_view(), name='companyinfo'),
    # Calendar
    path('eventos/list/', EventosListView.as_view(), name='events'),
    # NEW URLS
    # Category
    path('categorias/list/', CategoryListView.as_view(), name='category_list'),
    # Brand
    path('marcas/list/', BrandListView.as_view(), name='brand_list'),
    # Type
    path('tipos/list/', TypeListView.as_view(), name='type_list'),
    # Products
    path('productos/list/', ProductListView.as_view(), name='products_list'),
    # Inventary
    path('productos/inventario/pdf/', InventaryPdfView.as_view(), name='inventary_pdf'),
    # Clients
    path('clientes/', ClientView.as_view(), name='client'),
    # Pay Method
    path('metodos/pagos/list/', MethodListView.as_view(), name='method_list'),
    # Sale
    path('ventas/listado/', SaleListView.as_view(), name='sale_list'),
    path('ventas/registrar/', SaleCreateView.as_view(), name='sale_create'),
    path('ventas/factura/pdf/<int:s>/', SaleInvoicePdfView.as_view(), name='sale_invoice_pdf'),
    path('ventas/reporte/pdf/<int:type>/<str:start>/<str:end>/', SalesPdfView.as_view(), name='reportSales'),
    # Credit
    path('ventas/creditos/', CreditListView.as_view(), name='credit_list'),
    path('ventas/creditos/reporte/pdf/<str:start>/<str:end>/', CreditReportPdfView.as_view(), name='reportCredits'),
    # Debt
    path('cuentas/pagar/', DebtListView.as_view(), name='debt_list'),
    path('cuentas/pagar/reporte/pdf/<str:start>/<str:end>/', DebtReportPdfView.as_view(), name='reportDebts'),
    # Budget
    path('presupuesto/listado/', BudgetListView.as_view(), name='budget_list'),
    path('presupuesto/pdf/<int:s>/', BudgetInvoicePdfView.as_view(), name='budget_invoice_pdf'),
]