from django.contrib.auth.models import Group
from mf.user.models import User
from django.utils import timezone
from datetime import date, datetime, timedelta
from mf.crud.models import Eventos
from mf.crud.models import CompanyInfo, Dolar

def convertToDecimalFormat(n):
    return n.replace('.', '').replace(',', '.')

def get_dollar():
    data = []
    try:
        dolar1 = Dolar.objects.using('default').get(pk=1)
        dl1 = float(dolar1.dolar)
    except:
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

def RegisterOperation(db, user, action):
    date = timezone.localtime(timezone.now())
    result = 0
    try:
        h = HistoryOperations()
        h.datejoined = date.strftime('%Y-%m-%d | %H:%M:%S %p')
        h.userSession_id = user
        h.description = action
        h.save()
    except:
        result = 1
    return result

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