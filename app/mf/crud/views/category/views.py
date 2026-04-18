from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from crum import get_current_request
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction

from django.contrib.auth.mixins import LoginRequiredMixin
from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin

from mf.crud.models import Category, Dolar
from mf.crud.forms import CategoryForm
from mf.crud.functions import *

class CategoryListView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'category/list.html'
    permission_required = 'view_category', 'add_category', 'change_category', 'delete_category'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        request = get_current_request()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = request.POST['sede']
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Category.objects.using(db).all():
                    data.append(i.toJSON())
            elif action == 'add':
                with transaction.atomic():
                    ctg = Category()
                    ctg.name = request.POST['name']
                    ctg.save()
            elif action == 'edit':
                ctg = Category.objects.using(db).get(pk=request.POST['id'])
                ctg.name = request.POST['name']
                ctg.save()
            elif action == 'delete':
                with transaction.atomic():
                    Category.objects.using('default').get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = getCompanyData()
        context['list_url'] = reverse_lazy('crud:category_list')
        context['title'] = 'Listado de Categorías'
        context['dl'] = get_dollar()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        context['form'] = CategoryForm()
        return context
