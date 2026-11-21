from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db import connections, transaction
from datetime import date, datetime, timedelta
import json
from django.utils import timezone
from decimal import Decimal

from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.models import Product, Sale, Credit, DetCredit, Budget, DetSale, DetBudget, Client, Method_pay, Dolar, CashMovement
from mf.crud.forms import SaleForm, ClientForm, MethodPayForm, ProductForm, CashMovementForm
from mf.crud.functions import *
from django.db.models import F, Prefetch, Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

# Claves de pg_advisory_xact_lock para la numeración de facturas y presupuestos
INVOICE_LOCK_KEY = 80010001
BUDGET_LOCK_KEY = 80010002

class SaleListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Sale
    template_name = 'sale/list.html'
    permission_required = 'view_sale'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = request.POST['sede']
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                sales_qs = Sale.objects.using(db).filter(
                    datejoined__gte=request.POST['start'], datejoined__lte=request.POST['end']
                ).select_related('client', 'method_pay', 'method_pay1', 'method_pay2').prefetch_related(
                    Prefetch('detsale_set', queryset=DetSale.objects.select_related('prod__category', 'prod__type_product'))
                )
                for i in sales_qs:
                    item = i.toJSON()
                    if(i.status == 0):
                        css = 'badge badge-success text-dark pointer-1'
                        status = 'Pagada'
                    elif(i.status == 1):
                        css = 'badge badge-warning text-dark pointer-1'
                        status = 'Crédito'
                    elif(i.status == 2):
                        css = 'badge badge-danger text-dark pointer-1'
                        status = 'Anulada'
                    item['statusName'] = status
                    item['css'] = css
                    data.append(item)
            elif action == 'return':
                require_perm(request.user, 'change_sale')
                reason = (request.POST.get('reason') or '').strip()
                if not reason:
                    raise UserError('Debe indicar el motivo de la anulación')
                if len(reason) > 255:
                    raise UserError('El motivo de la anulación no puede superar los 255 caracteres')
                with transaction.atomic(using=db):
                    sale = Sale.objects.using(db).select_for_update().get(pk=request.POST['id'])
                    if sale.status == 2:
                        raise UserError('Ya esta venta fue anulada anteriormente')

                    for i in DetSale.objects.using(db).filter(sale_id=sale.id):
                        Product.objects.using(db).filter(pk=i.prod_id).update(
                            quantity=F('quantity') + i.quantity
                        )

                    if sale.type_sale == 'Crédito':
                        det_credits = DetCredit.objects.using(db).filter(sale=sale)

                        for dc in det_credits:
                            credit_header = dc.credit
                            credit_header.totalDebt -= dc.quantity
                            credit_header.save(using=db)

                            dc.delete(using=db)

                    sale.status = 2
                    sale.cancelled_by = request.user.username
                    sale.cancelled_at = timezone.now()
                    sale.cancel_reason = reason
                    sale.save(using=db)
                logger.info('[sale.return] OK venta=%s factura=%s usuario=%s motivo=%s',
                            sale.id, sale.invoice_number, request.user, reason)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            log_error(logger, e, '[%s] error en acción=%s usuario=%s', __name__, request.POST.get('action'), request.user)
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['create_url'] = reverse_lazy('crud:sale_create')
        context['dl'] = get_dollar()
        context['list_url'] = reverse_lazy('crud:sale_list')
        context['month'] = date.today().month
        context['monthName'] = getMonthName(int(date.today().month))
        context['year'] = date.today().year
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class SaleCreateView(LoginRequiredMixin, ValidatePermissionMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale/create.html'
    permission_required = 'add_sale'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = request.POST['sede']
            action = request.POST['action']
            if action == 'search_products':
                data = []

                term = request.POST.get('term', '').strip()
                if not term:
                    return JsonResponse(data, safe=False)

                code = Product.objects.using(db).filter(code__icontains=term).exclude(quantity__lte=0).exclude(status=0)[0:10]
                products = Product.objects.using(db).filter(product__icontains=term).exclude(quantity__lte=0).exclude(status=0)[0:10]
                brand = Product.objects.using(db).filter(brand__icontains=term).exclude(quantity__lte=0).exclude(status=0)[0:10]
                for i in code:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'||' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + '$: ' + item['price_dl'] + ' / Bs: ' + item['price_bs']
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in brand:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'|| ' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + '$: ' + item['price_dl'] + ' / Bs: ' + item['price_bs']
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in products:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'|| ' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + '$: ' + item['price_dl'] + ' / Bs: ' + item['price_bs']
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
            elif action == 'search_client':
                data = []
                term = request.POST['term']
                client = Client.objects.using(db).filter(names__icontains=term)[0:10]
                ci = Client.objects.using(db).filter(ci__icontains=term)[0:10]
                for i in client:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = i.names + ' ' + i.identity + '-' + i.ci
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in ci:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = i.names + ' ' + i.identity + '-' + i.ci
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
            elif action == 'add':
                data = self.addSale(db, request.POST, request.user)
            elif action == 'cashMovement':
                require_perm(request.user, 'add_cashmovement')
                dolar = Dolar.objects.using(db).filter(pk=1).first()
                dl = float(dolar.dolar) if dolar else 0
                require_dollar_rate(dl)

                method = Method_pay.objects.get(pk=request.POST['method_pay'])
                type_symbol = method.type_symbol

                c = CashMovement()
                c.user_id = request.user.id
                c.tipo = request.POST['tipo']
                c.method_pay_id = method.id

                if type_symbol == 'Bs':
                    c.amount_bs = Decimal(request.POST['amount_bs'])
                    c.amount_dl = Decimal(request.POST['amount_bs']) / Decimal(dl)  
                else:
                    c.amount_dl = Decimal(request.POST['amount_bs'])
                    c.amount_bs = Decimal(request.POST['amount_bs']) * Decimal(dl)  

                c.description = request.POST['description']
                c.save()
            elif action == 'addBudget':
                datejoined = date.today().strftime('%Y-%m-%d')
                dolar = Dolar.objects.using(db).get(pk=1)
                dl = float(dolar.dolar)
                
                try:
                    with transaction.atomic():
                        sales = json.loads(request.POST['sales'])
                        sale = Budget()
                        sale.user = request.user.username
                        sale.datejoined = datejoined
                        sale.client_id = int(request.POST['searchClient'])
                        sale.subtotal = float(request.POST['quantity_dolars']) + float(sales['discount'])
                        sale.discount = float(sales['discount'])
                        sale.total = float(request.POST['quantity_dolars'])
                        sale.description = request.POST['description']
                        sale.rate = float(dl)
                        sale.budget_number = self.get_lastet_budget()
                        sale.save(using=db)              

                        for i in sales['products']:
                            det = DetBudget()
                            det.budget_id = sale.id
                            det.prod_id = i['id']
                            det.quantity = float(i['quantity'])
                            det.price = float(i['price_dl'])
                            det.total = float(i['quantity']) * float(i['price_dl'])
                            det.rate = float(dl)
                            det.save(using=db)
                        data = {
                            'id': sale.id,
                        }
                except Exception as e:
                    log_error(logger, e, '[sale.addBudget] usuario=%s', request.user)
                    data = {
                        'error': error_message(e)
                    }
            elif action == 'addClient':
                require_perm(request.user, 'add_client')
                cli = Client()
                cli.names = request.POST['names']
                cli.identity = request.POST['identity']
                cli.ci = request.POST['ci']
                cli.address = request.POST['address']
                cli.contact = request.POST['contact']
                cli.save(using='default')
                data = {
                    'id': cli.pk,
                    'names': cli.names,
                    'ci': cli.identity + '-' + cli.ci
                }
            elif action == 'addProduct':
                perms = ['add_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    dolar = Dolar.objects.using(db).get(pk=1)
                    iva = float(1.16)

                    # cost = float(request.POST['cost'])
                    # gain_margin = price_dl - cost

                    price_dl = float(request.POST['price_dl'])
                    price_bs = price_dl * float(dolar.dolar)
                    cost = float(request.POST['cost'])
                    price = price_bs / iva
                    
                    quantity = float(request.POST['quantity'])
                    if quantity < 0:
                        raise UserError('La cantidad no puede ser negativa')
                    
                    with transaction.atomic():
                        p = Product()
                        p.category_id = request.POST['category']
                        p.type_product_id = request.POST['type_product']
                        p.product = request.POST['product']
                        p.code = request.POST['code']
                        p.brand = request.POST['brand']
                        p.description = request.POST['description']
                        p.quantity = quantity
                        p.cost = cost
                        p.price_dl = price_dl
                        p.price = price
                        p.price_bs = price_bs
                        p.save()     
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)

    def addSale(self, db, requestPOST, requestUser):
        data = {}
        datejoined = date.today().strftime('%Y-%m-%d')

        dolar_obj = Dolar.objects.using(db).filter(pk=1).first()
        dl = Decimal(str(dolar_obj.dolar)) if dolar_obj else Decimal('0')
        require_dollar_rate(dl)

        clientId = int(requestPOST['searchClient'])
        sales = json.loads(requestPOST['sales'])

        saveCreditDetail = False
        
        try:
            with transaction.atomic(using=db):
                sale = Sale()
                dateHour = timezone.localtime(timezone.now())
                
                discount = Decimal(str(sales['discount']))
                subtotal = Decimal(str(sales['total'])) + discount
                total = subtotal - discount
                
                sale.user = requestUser.username
                sale.datejoined = datejoined
                sale.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                sale.client_id = clientId
                sale.subtotal = subtotal
                sale.discount = discount
                sale.total = total
                sale.totalBs = total * dl
                sale.rate = dl
                sale.description = requestPOST.get('description', '')
                sale.invoice_number = self.get_lastet_invoice(db)
                
                type_sale = requestPOST['inlineRadioOptions']
                
                if type_sale == 'option1':
                    sale.type_sale = 'Al Contado'
                    sale.method_pay_id = requestPOST['method_pay']
                    sale.received = Decimal(str(requestPOST.get('received', '0.00')))
                    sale.method_pay1_id = requestPOST['method_pay1']
                    sale.received1 = Decimal(str(requestPOST.get('received1', '0.00')))
                    sale.method_pay2_id = requestPOST['method_pay2']
                    sale.received2 = Decimal(str(requestPOST.get('received2', '0.00')))
                elif type_sale == 'option2':
                    saveCreditDetail = True
                    sale.type_sale = 'Crédito'
                    sale.method_pay_id = 1
                    sale.received = Decimal('0.00')
                    sale.exchange = Decimal('0.00')
                    sale.method_pay1_id = 1
                    sale.received1 = Decimal('0.00')
                    sale.exchange1 = Decimal('0.00')
                    sale.method_pay2_id = 1
                    sale.received2 = Decimal('0.00')
                    sale.exchange2 = Decimal('0.00')
                    sale.status = 1
                    
                sale.save(using=db)

                if saveCreditDetail:
                    try:
                        updateCredit = Credit.objects.using(db).get(client__id=clientId)
                        updateCredit.last_credit_date = datejoined
                        updateCredit.datehour = sale.datehour
                        updateCredit.totalDebt = Decimal(str(updateCredit.totalDebt)) + total
                        updateCredit.save(using=db)
                        credit_id = updateCredit.id
                    except Credit.DoesNotExist:
                        newCredit = Credit()
                        newCredit.client_id = clientId
                        newCredit.last_credit_date = datejoined
                        newCredit.datehour = sale.datehour
                        newCredit.totalDebt = total
                        newCredit.save(using=db)
                        credit_id = newCredit.id

                    newDet = DetCredit()
                    newDet.last_credit_date = datejoined
                    newDet.datehour = sale.datehour
                    newDet.credit_id = credit_id
                    newDet.method_pay_id = 1
                    newDet.sale_id = sale.id
                    newDet.operation = '+'
                    newDet.quantity = total
                    newDet.quantitybs = total * dl
                    newDet.description = f"Factura # {sale.invoice_number}"
                    newDet.save(using=db)

                # Bloquear todos los productos del carrito en orden fijo (por id) evita
                # deadlocks entre ventas simultáneas con los mismos productos.
                ids = sorted({int(i['id']) for i in sales['products']})
                list(Product.objects.using(db).select_for_update().filter(pk__in=ids).order_by('pk'))

                for i in sales['products']:
                    pw = Product.objects.using(db).select_for_update().get(pk=i['id'])
                    cantidad_vendida = Decimal(str(i['quantity']))

                    if cantidad_vendida <= 0:
                        raise UserError(f"Se detectó una cantidad inválida ({cantidad_vendida}) para el producto '{pw.category.name} - {pw.product} ({pw.type_product.name})'. Por favor, verifique e intente de nuevo.")

                    stock_actual = Decimal(str(pw.quantity))

                    if stock_actual < cantidad_vendida:
                        stock_formateado = int(stock_actual) if stock_actual % 1 == 0 else float(stock_actual)
                        cant_formateada = int(cantidad_vendida) if cantidad_vendida % 1 == 0 else float(cantidad_vendida)        
                        raise UserError(f"Stock insuficiente para '{pw.category.name} - {pw.product} ({pw.type_product.name})'. Disponible: {stock_formateado}, Solicitado: {cant_formateada}")
                    
                    pw.quantity = stock_actual - cantidad_vendida
                    pw.save(using=db)

                    det = DetSale()
                    det.sale_id = sale.id
                    det.prod_id = i['id']
                    det.quantity = cantidad_vendida
                    det.price = Decimal(str(pw.price_dl))
                    det.total = Decimal(str(pw.price_dl)) * cantidad_vendida
                    det.rate = dl
                    det.save(using=db)
                    
            data = { 'id': sale.id }
            logger.info('[sale.add] OK venta=%s factura=%s usuario=%s productos=%s',
                        sale.id, sale.invoice_number, requestUser.username, len(sales['products']))

        except Exception as e:
            log_error(logger, e, '[sale.add] FALLÓ usuario=%s cliente=%s payload=%s',
                             requestUser.username, clientId, str(sales)[:1000])
            data = {
                'error': error_message(e)
            }

        return data

    def get_methods_pay(self):
        data = []
        for i in Method_pay.objects.all():
            data.append(i.toJSON())
        return data

    def _next_number(self, queryset, field, db, lock_key):
        # Candado de PostgreSQL que dura lo que dura la transacción: serializa la
        # generación del número entre ventas simultáneas (se libera al confirmar).
        with connections[db].cursor() as cursor:
            cursor.execute('SELECT pg_advisory_xact_lock(%s)', [lock_key])

        recent = list(queryset.order_by('-id').values_list(field, flat=True)[:50])
        if not recent:
            return f"{1:0>8}"
        for value in recent:
            if str(value).strip().isdigit():
                return f"{int(value) + 1:0>8}"
        raise UserError('No se pudo determinar el siguiente número: los últimos registros no tienen numeración numérica.')

    def get_lastet_invoice(self, db):
        return self._next_number(Sale.objects.using(db), 'invoice_number', db, INVOICE_LOCK_KEY)

    def get_lastet_budget(self):
        return self._next_number(Budget.objects.using('default'), 'budget_number', 'default', BUDGET_LOCK_KEY)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'MÓDULO DE FACTURACIÓN - NUEVA VENTA'
        context['formClient'] = ClientForm()
        context['formMethod'] = MethodPayForm()
        context['formProduct'] = ProductForm()
        context['formCashMovement'] = CashMovementForm()
        context['methods'] = self.get_methods_pay()
        context['action'] = 'add'
        context['dl1'] = get_dollar()
        context['det'] = []
        context['cli'] = []
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class SaleInvoicePdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'add_sale'

    def link_callback(self, uri, rel):
        return resolve_pdf_uri(uri)

    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            db = 'default'
            template = get_template('sale/invoice.html')
            direction = []
            
            sale = Sale.objects.using(db).get(pk=self.kwargs['s'])

            server_url = request.build_absolute_uri('/')

            dataCompany = getCompanyData()
            context = {
                'sale': sale,
                'comp': dataCompany,
                'url': getStaticUrl(),
                'icon': server_url + 'media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="/Users/Isela/Desktop/'+n_order+'.pdf"'
             
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except Exception as e:
            log_error(logger, e, '[%s] error generando PDF usuario=%s', __name__, request.user)
            messages.error(request, 'No se pudo generar el PDF. Intenta de nuevo o avisa al administrador.')
        return HttpResponseRedirect(reverse_lazy('crud:sale_list'))

class SalesPdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'add_sale'

    def link_callback(self, uri, rel):
        return resolve_pdf_uri(uri)

    def getByPayMethod(self, start, end, exchange_rate=1.0):
        data = []
        grand_total_usd = 0.0 
        
        try:
            # Traemos las consultas nativas (filtramos una sola vez para velocidad)
            sales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end).exclude(status=2)
            credits = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end).exclude(operation='+').exclude(status=0).exclude(status=2)
            
            for m in Method_pay.objects.all().exclude(pk=1):
                idMethodPay = m.id
                name = m.name
                type_total = m.type_symbol  # '$' or 'Bs'
                
                sales_amount = 0.0
                payments_amount = 0.0
                cash_in = 0.0
                cash_out = 0.0
                quantity = 0
                
                for s in sales:
                    if s.method_pay_id == idMethodPay and float(s.received) > 0:
                        sales_amount += float(s.received)
                        quantity += 1  # Suma operación
                        
                    if s.method_pay1_id == idMethodPay and float(s.received1) > 0:
                        sales_amount += float(s.received1)
                        quantity += 1  # Suma operación
                        
                    if s.method_pay2_id == idMethodPay and float(s.received2) > 0:
                        sales_amount += float(s.received2)
                        quantity += 1  # Suma operación

                for c in credits:
                    if c.method_pay_id == idMethodPay:
                        quantity += 1 
                        if type_total == '$':
                            payments_amount += float(c.quantity)
                        elif type_total == 'Bs':
                            payments_amount += float(c.quantitybs)

                movements = CashMovement.objects.filter(
                    date_time__date__gte=start, 
                    date_time__date__lte=end,
                    method_pay_id=idMethodPay, 
                    status=1
                )
                for mov in movements:
                    quantity += 1  # Suma operación movimiento manual
                    if mov.tipo == 'INGRESO':
                        if type_total == '$': cash_in += float(mov.amount_dl)
                        elif type_total == 'Bs': cash_in += float(mov.amount_bs)
                    elif mov.tipo == 'EGRESO':
                        if type_total == '$': cash_out += float(mov.amount_dl)
                        elif type_total == 'Bs': cash_out += float(mov.amount_bs)

                net_final = (sales_amount + payments_amount + cash_in) - cash_out
                net_final = round(net_final, 2)
                
                if type_total == '$':
                    grand_total_usd += net_final
                elif type_total == 'Bs':
                    if float(exchange_rate) > 0:
                        grand_total_usd += round(net_final / float(exchange_rate), 2)

                result = {
                    'id': idMethodPay,
                    'method': name,
                    'currency': type_total,
                    'quantity': quantity,  # <--- Agregado al diccionario para tu HTML
                    'sales_amount': round(sales_amount, 2),
                    'payments_amount': round(payments_amount, 2),
                    'cash_in': round(cash_in, 2),
                    'cash_out': round(cash_out, 2),
                    'net_final': round(net_final, 2),
                }
                data.append(result)
                
        except Exception as e:
            logger.exception('[%s] error generando reporte por método de pago', __name__)

        return data, round(grand_total_usd, 2)

    def getByTypeSales(self, start, end, exchange_rate):
        data = {}
        cash = credit = payments = 0
        acumulado_usd = acumulado_bs = totalCredit = totalPayments = 0.0

        try:
            allPayments = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end).exclude(operation='+').exclude(status=0).exclude(status=2)
            allSales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end).exclude(status=2)
            
            for a in allSales:
                if a.type_sale == 'Al Contado':
                    cash += 1
                    if a.method_pay and a.received > 0:
                        if str(a.method_pay.type_symbol).strip() == 'Bs': acumulado_bs += float(a.received)
                        else: acumulado_usd += float(a.received)
                    
                    if a.method_pay1 and a.received1 > 0:
                        if str(a.method_pay1.type_symbol).strip() == 'Bs': acumulado_bs += float(a.received1)
                        else: acumulado_usd += float(a.received1)
                            
                    if a.method_pay2 and a.received2 > 0:
                        if str(a.method_pay2.type_symbol).strip() == 'Bs': acumulado_bs += float(a.received2)
                        else: acumulado_usd += float(a.received2)
                    
                elif a.type_sale == 'Crédito':
                    credit += 1
                    totalCredit += float(a.total)
                    
            for a in allPayments:
                payments += 1
                totalPayments += float(a.quantity)
                
            totalCash = acumulado_usd + round(acumulado_bs / float(exchange_rate), 2)
                
            data = {
                'cash': cash, 'credit': credit, 'payments': payments,
                'totalCash': round(totalCash, 2),
                'totalCredit': round(totalCredit, 2),
                'totalPayments': round(totalPayments, 2),
            }
        except Exception as e:
            logger.exception('[%s] error generando reporte por tipo de venta', __name__)
            
        return data

    def getDiscountSales(self, start, end):
        data = []
        try:
            sales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end, discount__gt=0).exclude(status=2)
            for s in sales:
                info = {
                    'date': s.datejoined.strftime('%d/%m/%Y'),
                    'client': s.client.names + ' ' + s.client.ci,
                    'invoice': '#' + s.invoice_number,
                    'discount': float(s.discount)
                }
                data.append(info)
        except Exception:
            logger.exception('[%s] error armando datos del reporte', __name__)
        return data

    def getPayments(self, start, end):
        data = []
        try:
            allPayment = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end, operation='-').exclude(status=0).exclude(status=2)
            for p in allPayment:
                quantity = 0
                quantityBs = 0
                item = p.toJSON()
                typeSimbol = p.method_pay.type_symbol
                credit = Credit.objects.get(pk=p.credit.id)
                client = credit.client.names + ' ' + ' ' + credit.client.identity + '' + credit.client.ci
                if typeSimbol == '$':
                    quantity += float(item['quantity'])
                elif typeSimbol == 'Bs':
                    quantityBs += float(item['quantitybs'])
                detail = {
                    'date': item['last_credit_date'].strftime('%d/%m/%Y'),
                    'client': client,
                    'method': p.method_pay.name,
                    'quantity': quantity,
                    'quantityBs': quantityBs
                }
                data.append(detail)
        except Exception:
            logger.exception('[%s] error armando datos del reporte', __name__)
        return data

    def getCashMovements(self, start, end, exchange_rate):
        data = []
        try:
            allMovements = CashMovement.objects.filter(
                date_time__date__gte=start, 
                date_time__date__lte=end, 
                status=1
            ).order_by('-date_time')
            
            total_ingresos = 0
            total_egresos = 0
            total_ingresos_dl = 0
            total_egresos_dl = 0
            
            for m in allMovements:
                item = m.toJSON()
                
                amount = 0
                amount_bs = float(item['amount_bs'])
                amount_dl = float(item['amount_dl'])

                method = Method_pay.objects.get(pk=m.method_pay.id)

                if(method.type_symbol == 'Bs'):
                    amount = amount_bs
                    if(m.tipo == 'INGRESO'):
                        total_ingresos += amount
                    else:
                        total_egresos += amount
                else:
                    amount = amount_dl
                    if(m.tipo == 'INGRESO'):
                        total_ingresos_dl += amount
                    else:
                        total_egresos_dl += amount
                
                hora_local = timezone.localtime(m.date_time)
                date_formatted = hora_local.strftime('%d/%m/%Y %I:%M %p')
                
                detail = {
                    'date': date_formatted,
                    'user': m.user.username,
                    'tipo': m.tipo,
                    'method': m.method_pay.name,
                    'description': m.description.capitalize(),
                    'amount': amount,
                    'symbol': method.type_symbol
                }
                data.append(detail)

            if float(exchange_rate) > 0:
                ingresos_convertidos_bs = total_ingresos / float(exchange_rate)
                egresos_convertidos_bs = total_egresos / float(exchange_rate)
            else:
                ingresos_convertidos_bs = 0.0
                egresos_convertidos_bs = 0.0
                
            gran_total_ingresos_usd = total_ingresos_dl + ingresos_convertidos_bs
            gran_total_egresos_usd = total_egresos_dl + egresos_convertidos_bs
                
            total_neto_global_usd = gran_total_ingresos_usd - gran_total_egresos_usd
                
            return {
                'movements': data,
                'total_mov_caja': round(total_neto_global_usd, 2)
            }
            
        except Exception as e:
            logger.exception('[%s] error generando reporte de movimientos de caja', __name__)
            return {'movements': [], 'totals': {}}
    
    def getByProducts(self, start, end):
        data = []
        try:
            allSales = DetSale.objects.filter(
                sale__datejoined__gte=start, sale__datejoined__lte=end
            ).exclude(sale__status=2).select_related('prod__type_product')

            # Una sola pasada: acumula por código de producto (en orden de aparición)
            acc = {}
            for d in allSales:
                p = d.prod
                qty = float(d.quantity)
                price = float(p.price_dl)
                row = acc.setdefault(p.code, {'quantity': 0.0, 'total': 0.0})
                row['quantity'] += qty
                row['prod'] = p.product + ' ' + p.type_product.name
                row['price'] = price
                row['cost'] = float(p.cost)
                row['total'] += price * qty

            for code, row in acc.items():
                data.append({
                    'code': code,
                    'quantity': row['quantity'],
                    'prod': row['prod'],
                    'cost': row['cost'],
                    'price': row['price'],
                    'total_dl': row['price'] * row['quantity'],
                    'gain': (row['price'] - row['cost']) * row['quantity'],
                    'total': row['total'],
                })
        except Exception:
            logger.exception('[%s] error armando datos del reporte', __name__)
        return data

    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            payMethod = []
            typeSales = []
            byProducts = []
            discountSales = []
            payments = []
            movements = {'movements': [], 'total_mov_caja': 0}
            grand_total = 0

            dolar = Dolar.objects.get(pk=1)
            dl = float(dolar.dolar)

            if self.kwargs['type'] == 1: 
                template = get_template('sale/reportSales.html')
                payMethod, grand_total = self.getByPayMethod(self.kwargs['start'], self.kwargs['end'], exchange_rate=dl)
                typeSales = self.getByTypeSales(self.kwargs['start'], self.kwargs['end'], exchange_rate=dl)
                discountSales = self.getDiscountSales(self.kwargs['start'], self.kwargs['end'])
                payments = self.getPayments(self.kwargs['start'], self.kwargs['end'])
                movements = self.getCashMovements(self.kwargs['start'], self.kwargs['end'], exchange_rate=dl)
            elif self.kwargs['type'] == 2:
                template = get_template('sale/reportProducts.html')
                byProducts = self.getByProducts(self.kwargs['start'], self.kwargs['end'])

            totals = 0
            totalsBs = 0
            try:
                for i in payMethod:
                    totals = float(totals) + float(i['total'])
                    totalsBs = float(totalsBs) + float(i['total_bs'])
            except:
                pass

            totalDiscounts = 0
            try:
                for i in discountSales:
                    totalDiscounts += float(i['discount'])
            except:
                pass

            totalPayments = 0
            totalPaymentsBs = 0
            try:
                for i in payments:
                    totalPayments += float(i['quantity'])
                    totalPaymentsBs += float(i['quantityBs'])
            except:
                pass

            totalsByProducts = 0
            totalProducts = 0
            totalPSales = 0
            try:
                for i in byProducts:
                    totalsByProducts += float(i['total'])
                    totalProducts += float(i['gain'])
                    totalPSales += float(i['total_dl'])
            except:
                pass

            totalIncome = 0
            totalTypeSales = 0
            try:
                totalIncome = float(typeSales['totalCash']) + float(typeSales['totalPayments'])
                totalTypeSales = float(typeSales['totalCash']) + float(typeSales['totalCredit']) + float(typeSales['totalPayments'])
            except:
                pass

            server_url = request.build_absolute_uri('/')
            dataCompany = getCompanyData()
            context = {
                'day': self.kwargs['start'] + ' - ' + self.kwargs['end'],
                'detTypeSales': typeSales,
                'payMethod': payMethod,
                'grand_total_usd': grand_total,
                'totalTypeSales': totalTypeSales,
                'totalIncome': totalIncome,
                'discountSales': discountSales,
                'totalDiscounts': totalDiscounts,
                'totalPayments': totalPayments,
                'totalPaymentsBs': totalPaymentsBs,
                'payments': payments,
                'movements': movements,
                'totals': round(totals, 2),
                'totalsBs': round(totalsBs, 2),
                'byProducts': byProducts,
                'totalsByProducts': totalsByProducts,
                'totalProducts': totalProducts,
                'totalPSales': totalPSales,
                'comp': dataCompany,
                'url': getStaticUrl(),
                'icon': server_url + '/media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except Exception as e:
            log_error(logger, e, '[%s] error generando PDF usuario=%s', __name__, request.user)
            messages.error(request, 'No se pudo generar el PDF. Intenta de nuevo o avisa al administrador.')
        return HttpResponseRedirect(reverse_lazy('crud:sale_list'))

