from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db import transaction
from datetime import date, datetime, timedelta
import json
from django.utils import timezone


from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.models import Product, Sale, Credit, DetCredit, Budget, DetSale, DetBudget, Client, Method_pay, Dolar
from mf.crud.forms import SaleForm, ClientForm, MethodPayForm
from mf.crud.functions import *
from django.db.models import Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

class SaleListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Sale
    template_name = 'sale/list.html'
    permission_required = 'view_sale'

    @method_decorator(csrf_exempt)
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
                for i in Sale.objects.using(db).filter(datejoined__gte=request.POST['start'], datejoined__lte=request.POST['end']):
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
                datejoined = date.today().strftime('%Y-%m-%d')
                sale = Sale.objects.using(db).get(pk=request.POST['id'])
                if(sale.status == 2):
                    data['error'] = 'Ya esta venta fue anulada anteriormente'
                else:
                    with transaction.atomic():
                        det = DetSale.objects.using(db).filter(sale_id=request.POST['id'])
                        for i in det:
                            pw = Product.objects.using(db).get(pk=i.prod_id)
                            pw.quantity = float(pw.quantity) + float(i.quantity)
                            pw.save(using=db)
                        sale.status = 2
                        sale.save(using=db)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
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

class SaleCreateView(CreateView, LoginRequiredMixin, ValidatePermissionMixin):
    model = Sale
    form_class = SaleForm
    template_name = 'sale/create.html'
    permission_required = 'add_sale'

    @method_decorator(csrf_exempt)
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
                term = request.POST['term']
                code = Product.objects.using(db).filter(code__icontains=term).exclude(quantity=0)[0:10]
                products = Product.objects.using(db).filter(product__icontains=term).exclude(quantity__lt=0)[0:10]
                brand = Product.objects.using(db).filter(brand__icontains=term).exclude(quantity__lt=0)[0:10]
                for i in code:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'||' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + item['price_dl'] + '$'
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in brand:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'|| ' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + item['price_dl'] + '$'
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in products:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'|| ' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + item['price_dl'] + '$'
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
                self.addSale(db, request.POST, request.user)
            elif action == 'addBudget':
                datejoined = date.today().strftime('%Y-%m-%d')
                dolar = Dolar.objects.using(db).get(pk=1)
                dl = float(dolar.dolar)

                with transaction.atomic():
                    sales = json.loads(request.POST['sales'])
                    sale = Budget()
                    sale.user = request.user.username
                    sale.datejoined = datejoined
                    sale.client_id = int(request.POST['searchClient'])
                    sale.subtotal = float(request.POST['quantity_dolars'])
                    sale.discount = float(sales['discount'])
                    sale.total = float(request.POST['quantity_dolars']) - float(sales['discount'])
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
            elif action == 'addClient':
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
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
  
    def addSale(self, db, requestPOST, requestUser):
        data = []
        datejoined = date.today().strftime('%Y-%m-%d')
        dolar = Dolar.objects.using(db).get(pk=1)
        dl = float(dolar.dolar)

        clientId = int(requestPOST['searchClient'])
        sales = json.loads(requestPOST['sales'])

        # Validate pay
        saveCreditDetail = 0
        with transaction.atomic():
            sale = Sale()
            dateHour = timezone.localtime(timezone.now())
            total = float(sales['total']) - float(sales['discount'])
            sale.user = requestUser.username
            sale.datejoined = datejoined
            sale.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
            sale.client_id = clientId
            sale.subtotal = float(sales['total'])
            sale.discount = float(sales['discount'])
            sale.total = total
            sale.totalBs = total * float(dl)
            type_sale = requestPOST['inlineRadioOptions']
            if type_sale == 'option1':
                sale.type_sale = 'Al Contado'
                sale.method_pay_id = requestPOST['method_pay']
                sale.received = float(requestPOST['received'])
                sale.method_pay1_id = requestPOST['method_pay1']
                sale.received1 = float(requestPOST['received1'])
                sale.method_pay2_id = requestPOST['method_pay2']
                sale.received2 = float(requestPOST['received2'])
            elif type_sale == 'option2':
                saveCreditDetail = 1
                sale.type_sale = 'Crédito'
                sale.method_pay_id = 1
                sale.received = '0.00'
                sale.exchange = '0.00'
                sale.method_pay1_id = 1
                sale.received1 = '0.00'
                sale.exchange1 = '0.00'
                sale.method_pay2_id = 1
                sale.received2 = '0.00'
                sale.exchange2 = '0.00'
                sale.status = 1
            sale.rate = float(dl)
            sale.description = requestPOST['description']
            sale.invoice_number = self.get_lastet_invoice(db)
            sale.save(using=db)

            if saveCreditDetail == 1:
                try:
                    updateCredit = Credit.objects.get(client__id=clientId)
                    updateCredit.last_credit_date = datejoined
                    updateCredit.datehour = sale.datehour
                    updateCredit.totalDebt = float(updateCredit.totalDebt) + float(total)
                    updateCredit.save()

                    newDet = DetCredit()
                    newDet.last_credit_date = datejoined
                    newDet.datehour = sale.datehour
                    newDet.credit_id = updateCredit.id
                    newDet.sale_id = sale.id
                    newDet.operation = '+'
                    newDet.quantity = float(total)
                    newDet.description = 'Factura # ' + str(sale.invoice_number)
                    newDet.save()
                except:
                    newCredit = Credit()
                    newCredit.client_id = clientId
                    newCredit.last_credit_date = datejoined
                    newCredit.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                    newCredit.totalDebt = total
                    newCredit.save()

                    newDet = DetCredit()
                    newDet.last_credit_date = datejoined
                    newDet.datehour = sale.datehour
                    newDet.credit_id = newCredit.id
                    newDet.sale_id = sale.id
                    newDet.operation = '+'
                    newDet.quantity = float(total)
                    newDet.description = 'Factura # ' + str(sale.invoice_number)
                    newDet.save()

            for i in sales['products']:
                det = DetSale()
                pw = Product.objects.using(db).get(pk=i['id'])
                pw.quantity = float(pw.quantity) - float(i['quantity'])

                det.sale_id = sale.id
                det.prod_id = i['id']
                det.quantity = float(i['quantity'])
                det.price = pw.price_dl
                det.total = float(pw.price_dl) * float(i['quantity'])
                det.rate = float(dl)
                pw.save(using=db)
                det.save(using=db)
        data = {
            'id': sale.id,
            # 'location': 'http://192.168.88.249/panel/sale/add/'
        }
        return data

    def get_methods_pay(self):
        data = []
        for i in Method_pay.objects.all():
            data.append(i.toJSON())
        return data

    def get_lastet_invoice(self, db):
        try:
            lastSale = Sale.objects.using(db).last()
            last_invoice = lastSale.invoice_number
            new_invoice = int(last_invoice) + 1
        except:
            new_invoice = 1
        n_invoice = f"{new_invoice:0>8}"
        return n_invoice

    def get_lastet_budget(self):
        try:
            budget = Budget.objects.last()
            last_budget = budget.budget_number
            new_budget = int(last_budget) + 1
            n_budget = f"{new_budget:0>8}"
        except:
            new_budget = 1
            n_budget = f"{new_budget:0>8}"
        return n_budget

    def get_lastet_invoice_number(self):
        try:
            order = DeliveryOrder.last()
            last_order = order.number
            new_order = int(last_order) + 1
            n_order = f"{new_order:0>8}"
        except:
            new_order = 1
            n_order = f"{new_order:0>8}"
        return n_order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'MÓDULO DE FACTURACIÓN - NUEVA VENTA'
        context['formClient'] = ClientForm()
        context['formMethod'] = MethodPayForm()
        context['methods'] = self.get_methods_pay()
        context['invoice_number'] = self.get_lastet_invoice_number()
        context['action'] = 'add'
        context['dl'] = get_dollar()
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
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path

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
                'icon': 'https://jeantren-86cc3b8c232c.herokuapp.com/media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="/Users/Isela/Desktop/'+n_order+'.pdf"'
             
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('crud:sale_list'))

class SalesPdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'add_sale'

    def link_callback(self, uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path

    def getByPayMethod(self, start, end):
        data = []
        try:
            totalSales = 0
            for m in Method_pay.objects.all().exclude(pk=1):
                idMethodPay = m.id
                name = m.name
                quantity = 0
                total = 0
                total_bs = 0
                type_total = m.type_symbol
                sales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end).exclude(status=2)
                for s in sales:
                    detail = s.toJSON()
                    totalSales = float(totalSales) + float(detail['total'])
                    if detail['method_pay']['id'] == idMethodPay:
                        quantity += 1
                        if type_total == '$':
                            total += float(detail['received'])
                        elif type_total == 'Bs':
                            total_bs += float(detail['received'])
                    if detail['method_pay1']['id'] == idMethodPay:
                        quantity += 1
                        if type_total == '$':
                            total += float(detail['received1'])
                        elif type_total == 'Bs':
                            total_bs += float(detail['received1'])
                    if detail['method_pay2']['id'] == idMethodPay:
                        quantity += 1
                        if type_total == '$':
                            total += float(detail['received2'])
                        elif type_total == 'Bs':
                            total_bs += float(detail['received2'])
                result = {
                    'id': idMethodPay,
                    'method': name,
                    'quantity': quantity,
                    'total': round(total, 2),
                    'total_bs': round(total_bs, 2),
                    'type_total': type_total,
                }
                data.append(result)
        except:
            pass
        return data

    def getByProducts(self, start, end):
        data = []
        try:
            allSales = DetSale.objects.filter(sale__datejoined__gte=start, sale__datejoined__lte=end).exclude(sale__status=2)
            
            codes = []
            for i in allSales:
                item = i.toJSON()
                code = {
                    'code': item['prod']['code']
                }
                if not code in codes:
                    codes.append(code)

            totalGeneral = 0
            quantityGeneral = 0
            for i in codes:
                quantity = 0
                prod = 'details'
                price = 0
                total = 0
                for sale in allSales:
                    s = sale.toJSON()
                    if s['prod']['code'] == i['code']:
                        quantity += float(s['quantity'])
                        prod = s['prod']['product'] + ' ' + s['prod']['type_product']['name']
                        price = float(s['prod']['price_dl'])
                        totalQuantity = float(price) * float(s['quantity'])
                        total += totalQuantity
                    else:
                        pass
                product = {
                    'code': i['code'],
                    'quantity': quantity,
                    'prod': prod,
                    'price': price,
                    'total': total,
                }
                data.append(product)
        except:
            pass
        return data

    def getByTypeSales(self, start, end):
        data = []
        cash = 0
        credit = 0
        totalCash = 0
        totalCredit = 0

        try:
            allSales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end).exclude(status=2)
            for a in allSales:
                i = a.toJSON()
                if i['type_sale'] == 'Al Contado':
                    cash = cash + 1
                    totalCash = float(totalCash) + float(i['total'])
                elif i['type_sale'] == 'Crédito':
                    credit = credit + 1
                    totalCredit += float(i['total'])
            data = {
                'cash': cash,
                'credit': credit,
                'totalCash': round(totalCash, 2),
                'totalCredit': round(totalCredit, 2),
            }
        except:
            pass
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
        except:
            pass
        return data

    def getPayments(self, start, end):
        data = []
        try:
            allPayment = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end, operation='-')
            for p in allPayment:
                item = p.toJSON()
                credit = Credit.objects.get(pk=p.credit.id)
                client = credit.client.names + ' ' + ' ' + credit.client.identity + '' + credit.client.ci
                detail = {
                    'date': item['last_credit_date'].strftime('%d/%m/%Y'),
                    'client': client,
                    'quantity': float(item['quantity'])
                }
                data.append(detail)
        except:
            pass
        return data
    
    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            payMethod = []
            typeSales = []
            byProducts = []
            discountSales = []
            payments = []

            if self.kwargs['type'] == 1: 
                template = get_template('sale/reportSales.html')
                payMethod = self.getByPayMethod(self.kwargs['start'], self.kwargs['end'])
                typeSales = self.getByTypeSales(self.kwargs['start'], self.kwargs['end'])
                discountSales = self.getDiscountSales(self.kwargs['start'], self.kwargs['end'])
                payments = self.getPayments(self.kwargs['start'], self.kwargs['end'])
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
            try:
                for i in payments:
                    totalPayments += float(i['quantity'])
            except:
                pass

            totalsByProducts = 0
            totalProducts = 0
            try:
                for i in byProducts:
                    totalsByProducts += float(i['total'])
                    totalProducts += float(i['quantity'])
            except:
                pass
            totalTypeSales = 0
            try:
                totalTypeSales = float(typeSales['totalCash']) + float(typeSales['totalCredit'])
            except:
                pass
            
            server_url = request.build_absolute_uri('/')
            dataCompany = getCompanyData()
            context = {
                'day': self.kwargs['start'] + ' - ' + self.kwargs['end'],
                'detTypeSales': typeSales,
                'payMethod': payMethod,
                'totalTypeSales': totalTypeSales,
                'discountSales': discountSales,
                'totalDiscounts': totalDiscounts,
                'totalPayments': totalPayments,
                'payments': payments,
                'totals': round(totals, 2),
                'totalsBs': round(totalsBs, 2),
                'byProducts': byProducts,
                'totalsByProducts': totalsByProducts,
                'totalProducts': totalProducts,
                'comp': dataCompany,
                'url': getStaticUrl(),
                'icon': 'https://jeantren-86cc3b8c232c.herokuapp.com/media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('crud:sale_list'))

