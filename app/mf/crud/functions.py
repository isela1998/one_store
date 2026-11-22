from django.contrib.auth.models import Group
from mf.user.models import User
from django.utils import timezone
from datetime import date, datetime, timedelta
from mf.crud.models import Eventos
from mf.crud.models import CompanyInfo, Dolar
from decimal import InvalidOperation
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
from django.db.models import ProtectedError
import os
import re
from django.conf import settings
from django.contrib.staticfiles import finders

GENERIC_ERROR = 'Ocurrió un error inesperado. Intenta de nuevo o avisa al administrador.'

# Nombres de columna de la base de datos -> etiqueta legible para el usuario
FIELD_LABELS = {
    'code': 'código',
    'ci': 'CI/RIF',
    'name': 'nombre',
    'username': 'nombre de usuario',
    'invoice_number': 'número de factura',
}


class UserError(Exception):
    """Error con un mensaje pensado para mostrarse tal cual al usuario."""


def log_error(logger, e, message, *args):
    """Errores esperados (UserError) como warning; los inesperados con traza completa."""
    if isinstance(e, UserError):
        logger.warning(message + ' | %s', *args, e)
    else:
        logger.exception(message, *args)


def error_message(e):
    """Devuelve el mensaje que se le muestra al usuario para la excepción `e`.

    Los errores conocidos se traducen a un mensaje concreto; solo los que no se
    pueden explicar al usuario devuelven el mensaje genérico. El detalle técnico
    queda en el log (logger.exception en cada vista).
    """
    if isinstance(e, UserError):
        return str(e)
    if isinstance(e, ProtectedError):
        return 'No se puede eliminar este registro porque está siendo usado por otros registros (ventas, productos, etc.).'
    if isinstance(e, IntegrityError):
        msg = str(e)
        low = msg.lower()
        match = re.search(r'\((.+?)\)=\((.*?)\)', msg)
        if 'already exists' in low or 'ya existe' in low or 'unique' in low or 'unicidad' in low:
            if match:
                field = match.group(1).split(',')[0].strip()
                return 'Ya existe un registro con ese {}: {}.'.format(FIELD_LABELS.get(field, field), match.group(2))
            return 'Ya existe un registro con esos mismos datos.'
        if 'foreign key' in low or 'llave foránea' in low or 'clave foránea' in low:
            return 'No se puede completar la operación porque el registro está relacionado con otros datos.'
        if 'null value' in low or 'not-null' in low or 'nulo' in low:
            column = re.search(r'column \"?(\w+)\"?', msg) or re.search(r'columna \"?(\w+)\"?', msg)
            if column:
                return 'Falta completar un dato obligatorio ({}).'.format(FIELD_LABELS.get(column.group(1), column.group(1)))
            return 'Falta completar un dato obligatorio.'
        return GENERIC_ERROR
    if isinstance(e, ObjectDoesNotExist):
        return 'El registro solicitado no existe o fue eliminado. Recarga la página e intenta de nuevo.'
    if isinstance(e, ValidationError):
        return ' '.join(e.messages)
    if isinstance(e, KeyError):
        field = e.args[0] if e.args else ''
        return 'Falta un dato obligatorio en el formulario ({}). Recarga la página e intenta de nuevo.'.format(field)
    if isinstance(e, (InvalidOperation, ValueError)):
        return 'Uno de los valores ingresados (número o fecha) no tiene un formato válido.'
    if isinstance(e, ZeroDivisionError):
        return 'La tasa del dólar está en 0. Actualízala en el inicio e intenta de nuevo.'
    if isinstance(e, DatabaseError):
        low = str(e).lower()
        if 'deadlock' in low:
            return 'Otra operación estaba usando los mismos datos al mismo tiempo. Intenta de nuevo.'
        if any(k in low for k in ('could not connect', 'server closed', 'terminating connection', 'timeout', 'connection')):
            return 'Se perdió la conexión con la base de datos. Espera unos segundos e intenta de nuevo.'
    return GENERIC_ERROR

def convertToDecimalFormat(n):
    return n.replace('.', '').replace(',', '.')

def get_dollar():
    data = []
    try:
        dolar1 = Dolar.objects.using('default').get(pk=1)
        dl1 = float(dolar1.dolar)
    except Dolar.DoesNotExist:
        new_dolar1 = Dolar()
        new_dolar1.dolar = '0.00'
        new_dolar1.save()

        dolar1 = Dolar.objects.using('default').get(pk=1)
        dl1 = float(dolar1.dolar)
    
    data = {
        'dolar1': dl1,
    }
    return data

def ValidatePermissions(perms, requestGroup):
    autorized = False
    try:
        permsRequired = perms
        pk = requestGroup.id

        group = Group.objects.get(pk=pk)
        permsRequired = perms

        for p in permsRequired:
            if not group.permissions.filter(codename=p).exists():
                autorized = False
                break
            else:
                autorized = True
    except:
        autorized = False
    return autorized

def resolve_pdf_uri(uri):
    """
    Convierte las URIs HTML (estáticos y media) en rutas absolutas del sistema
    para que xhtml2pdf pueda acceder a esos recursos.
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
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

def require_dollar_rate(rate):
    """Lanza UserError si la tasa del dólar no está configurada (<= 0)."""
    if rate is None or float(rate) <= 0:
        raise UserError('La tasa del dólar no está configurada. Actualízala en el inicio antes de continuar.')
    return rate


def require_perm(user, codename):
    """Lanza UserError si el grupo del usuario no tiene el permiso `codename`."""
    if not ValidatePermissions([codename], user.groups.first()):
        raise UserError('Disculpe, usted no tiene permisos para ejecutar esta acción')

def get_q_events_today():
    data = 0
    try:
        start = date.today()
        end = start + timedelta(days=7)
        start_date = start.strftime('%Y-%m-%d')
        end_date = end.strftime('%Y-%m-%d')
        total = 0

        search = Eventos.objects.all()
        if len(start_date) and len(end_date):
            search = search.filter(day__range=[start_date, end_date])
            for s in search:
                total = int(total) + 1
            data = total
    except:
        pass
    return data

def get_events_today():
    data = []
    total = 0
    start = date.today()
    end = start + timedelta(days=7)
    start_date = start.strftime('%Y-%m-%d')
    end_date = end.strftime('%Y-%m-%d')

    search = Eventos.objects.all()
    if len(start_date) and len(end_date):
        search = search.filter(day__range=[start_date, end_date])
    for s in search:
        data.append(
            {
                'name': s.name,
                'description': s.description,
                'day': s.day.strftime('%Y-%m-%d'),
            }
        )
    return data

def numero_a_letras(numero):
    indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"),
                 ("MIL", "MIL"), ("BILLON", "BILLONES")]
    entero = int(numero)
    decimal = int(round((numero - entero)*100))
    # print 'decimal : ',decimal
    contador = 0
    numero_letras = ""
    while entero > 0:
        a = entero % 1000
        if contador == 0:
            en_letras = convierte_cifra(a, 1).strip()
        else:
            en_letras = convierte_cifra(a, 0).strip()
        if a == 0:
            numero_letras = en_letras+" "+numero_letras
        elif a == 1:
            if contador in (1, 3):
                numero_letras = indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" " + \
                    indicador[contador][0]+" "+numero_letras
        else:
            numero_letras = en_letras+" " + \
                indicador[contador][1]+" "+numero_letras
        numero_letras = numero_letras.strip()
        contador = contador + 1
        entero = int(entero / 1000)
    numero_letras = numero_letras+" PESOS MLC"
    return numero_letras

def convierte_cifra(numero, sw):
    lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS",
                     "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
    lista_decena = ["", ("DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                    ("VEINTE", "VEINTI"), ("TREINTA",
                                           "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                    ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                    ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                    ("NOVENTA", "NOVENTA Y ")
                    ]
    lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES",
                    "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
    centena = int(numero / 100)
    decena = int((numero - (centena * 100))/10)
    unidad = int(numero - (centena * 100 + decena * 10))
    # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

    texto_centena = ""
    texto_decena = ""
    texto_unidad = ""

    # Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad) != 0:
            texto_centena = texto_centena[1]
        else:
            texto_centena = texto_centena[0]

    # Valida las decenas
    texto_decena = lista_decena[decena]
    if decena == 1:
        texto_decena = texto_decena[unidad]
    elif decena > 1:
        if unidad != 0:
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]
    # Validar las unidades
    # print "texto_unidad: ",texto_unidad
    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw]

    return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)

def getMonthName(numberMonth):
    monthName = 'Mes'
    if numberMonth == 1:
        monthName = 'Enero'
    elif numberMonth == 2:
        monthName = 'Febrero'
    elif numberMonth == 3:
        monthName = 'Marzo'
    elif numberMonth == 4:
        monthName = 'Abril'
    elif numberMonth == 5:
        monthName = 'Mayo'
    elif numberMonth == 6:
        monthName = 'Junio'
    elif numberMonth == 7:
        monthName = 'Julio'
    elif numberMonth == 8:
        monthName = 'Agosto'
    elif numberMonth == 9:
        monthName = 'Septiembre'
    elif numberMonth == 10:
        monthName = 'Octubre'
    elif numberMonth == 11:
        monthName = 'Noviembre'
    elif numberMonth == 12:
        monthName = 'Diciembre'
    return monthName

def getCompanyData():
    try:
        c = CompanyInfo.objects.get(pk=1)
        data = c.toJSON()
        company = {
            'name': data['name'] ,
            'comercialName': data['comercialName'] ,
            'nit': data['nit'] ,
            'address': data['address'] ,
            'city': data['city'] ,
            'phone': data['phone'] ,
            'email': data['email'] ,
            'services': data['services'] ,
            'logo': data['logo'],
        }
    except:
        c = CompanyInfo()
        c.name = 'Name'
        c.comercialName = 'Comercial Name'
        c.nit = 'J0000000-4'
        c.address = 'Address'
        c.city = 'City'
        c.phone = '+58412000000'
        c.email = 'email@gmai.com'
        c.services = 'services'
        c.logo = 'logo.png'
        c.save()

        company = {
            'name': c.name,
            'comercialName': c.comercialName,
            'nit': c.nit,
            'address': c.address,
            'city': c.city,
            'phone': c.phone,
            'email': c.email,
            'services': c.services,
            'logo': c.logo,
        }
    return company

def getStaticUrl():
    url = 'http://localhost:8000/'
    return url