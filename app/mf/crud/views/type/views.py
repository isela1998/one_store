from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.urls import reverse_lazy

from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.forms import TypeProductForm
from mf.crud.models import Type_product
from mf.crud.functions import *

class TypeListView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'type/list.html'
    permission_required = 'view_type_product', 'add_type_product', 'change_type_product', 'delete_type_product'

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
                for i in Type_product.objects.using(db).all():
                    data.append(i.toJSON())
            elif action == 'add':
                type_p = Type_product()
                type_p.name = request.POST['name']
                type_p.save(using='default')
                RegisterOperation(db, request.user.pk, 'Registró una nuevo tipo de producto')      
            elif action == 'edit':
                type_p = Type_product.objects.using(db).get(pk=request.POST['id'])
                type_p.name = request.POST['name']
                type_p.save(using='default')
                RegisterOperation(db, request.user.pk, 'Editó un tipo de producto')      
            elif action == 'delete':
                Type_product.objects.using('default').get(pk=request.POST['id']).delete()
                RegisterOperation(db, request.user.pk, 'Eliminó un tipo de producto')      
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tipos de productos'
        context['list_url'] = reverse_lazy('crud:type_list')
        context['form'] = TypeProductForm()
        context['dl'] = get_dollar()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context
