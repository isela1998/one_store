from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin

from mf.crud.models import Method_pay
from mf.crud.forms import MethodPayForm
from mf.crud.functions import *

class MethodListView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'method/list.html'
    permission_required = 'view_method_pay', 'add_method_pay', 'change_method_pay', 'delete_method_pay'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            # sede = request.POST['sede']
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Method_pay.objects.using(db).all().exclude(pk=1):
                    data.append(i.toJSON())
                try:
                    Method_pay.objects.get(pk=1)
                except:
                    method = Method_pay()
                    method.name = 'NO APLICA'
                    method.type_symbol = 'NA'
                    method.save()
            elif action == 'add':
                method = Method_pay()
                method.name = request.POST['name']
                method.type_symbol = request.POST['type_symbol']
                method.save(using='default')
            elif action == 'edit':
                method = Method_pay.objects.using(db).get(pk=request.POST['id'])
                method.name = request.POST['name']
                method.type_symbol = request.POST['type_symbol']
                method.save(using='default')
            elif action == 'delete':
                Method_pay.objects.using('default').get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Métodos de Pago'
        context['list_url'] = reverse_lazy('crud:method_list')
        context['dl'] = get_dollar()
        context['form'] = MethodPayForm()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

