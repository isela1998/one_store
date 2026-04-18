from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin

from mf.crud.forms import EventosForm
from mf.crud.models import Eventos
from mf.crud.functions import *


class EventosListView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'calendar/calendar.html'
    permission_required = 'view_eventos'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            db = 'default'
            action = request.POST['action']
            if action == 'get_events':
                data = []
                for i in Eventos.objects.using('default').all():
                    valores = {
                        'id': i.id,
                        'title': i.name,
                        'description': i.description,
                        'backgroundColor': i.color,
                        'borderColor': i.color,
                        'start': i.day,
                        'allDay': True,
                    }
                    data.append(valores)
            elif action == 'get_all_events':
                data = []
                for i in Eventos.objects.using('default').all():
                    data.append(i.toJSON())
            elif action == 'add':
                perms = ['add_eventos', ]
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    p = Eventos()
                    p.name = request.POST['name']
                    p.description = request.POST['description']
                    p.day = request.POST['day']
                    p.color = request.POST['css']
                    p.save(using='default')
                    RegisterOperation(db, request.user.pk,
                                      'Registró un nuevo evento en el calendario')
            elif action == 'delete':
                perms = ['delete_eventos', ]
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    p = Eventos.objects.using(
                        'default').get(pk=request.POST['id'])
                    p.delete()
                    RegisterOperation(db, request.user.pk,
                                      'Eliminó un evento del calendario')
            else:
                data['error'] = "Ha ocurrido un error"
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eventos'
        context['form'] = EventosForm()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        context['today'] = date.today()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['dl'] = get_dollar()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context
