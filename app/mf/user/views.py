from django.shortcuts import render

# Create your views here.
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView

from mf.user.forms import UserForm
from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from mf.crud.functions import *

from mf.user.models import User

class UserListView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    model = User
    template_name = 'user/list.html'
    permission_required = 'view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        bd = 'default'
        try:
            db = 'default'
            action = request.POST['action']
            perm = {'add': 'add_user', 'edit': 'change_user', 'delete': 'delete_user'}.get(action)
            if perm and not ValidatePermissions([perm], request.user.groups.first()):
                return JsonResponse({'error': 'Disculpe, usted no tiene permisos para ejecutar esta acción'})
            if action in ('edit', 'delete') and str(request.POST.get('id')) == '1':
                return JsonResponse({'error': 'Este usuario no puede ser modificado'})
            if action == 'delete' and str(request.POST.get('id')) == str(request.user.pk):
                return JsonResponse({'error': 'No puede eliminar su propio usuario'})
            if action in ('add', 'edit') and request.POST.get('group') == '1' and not request.user.is_superuser:
                return JsonResponse({'error': 'Solo un administrador puede asignar el grupo de administrador'})
            if action == 'searchdata':
                data = []
                for i in User.objects.all().exclude(pk=1):
                    data.append(i.toJSON())
            elif action == 'add':
                perms = ['add_user',]
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    u = User()
                    u.first_name = request.POST['first_name']
                    u.last_name = request.POST['last_name']
                    u.username = request.POST['username']
                    u.set_password(request.POST['password'])
                    if request.POST['group'] == '1':
                        u.is_superuser = True
                    else:
                        u.is_superuser = False
                    u.group = request.POST['group']
                    u.save() 
                    u.groups.add(request.POST['group'])
            elif action == 'edit':
                u = User.objects.get(pk=request.POST['id'])
                u.first_name = request.POST['first_name']
                u.last_name = request.POST['last_name']
                u.username = request.POST['username']
                if request.POST.get('password'):
                    u.set_password(request.POST['password'])
                
                if request.POST['group'] == '1':
                    u.is_superuser = True
                else:
                    u.is_superuser = False
                u.save() 
                
                u.groups.clear()
                u.groups.add(request.POST['group'])
            elif action == 'delete':
                User.objects.get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mi usuario'
        context['list_url'] = reverse_lazy('user:users_list')
        context['form'] = UserForm()
        context['today'] = date.today()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context
