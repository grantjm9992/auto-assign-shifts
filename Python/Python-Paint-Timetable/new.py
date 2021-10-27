import time
import pymssql
import calendar
import json
import datetime
import copy
import data as d
from datetime import datetime
from time import mktime
from random import shuffle


##Configuration for the competencias##
class classes:
    violations = list()
    u_Singular = list()
    u_Series = list()

##Configuration for SQL##
class servConnect:
    server = "SRVN16\SQLEXPRESS"
    user = "agora"
    password = "number16"

    def runQuery(query, _rows, _alias, _database, dict):
        dict = True
        r = list()
        conn = pymssql.connect(servConnect.server, servConnect.user, servConnect.password, _database)
        cursor = conn.cursor(as_dict=dict)
        cursor.execute(query)
        for row in cursor:
            s = {}
            for i in range(0, len(_rows)):
                s[_alias[i]] = str(row[_rows[i]]).rstrip()
            r.append(s)
        return r

##Configuration for the competencies##
class config:
    dateformat = '%Y-%m-%d %H:%M:%S'
    penalties = [
        {'Description': 'BT LT', 't_id': 1, 'c_id': 1, 'score': 0},
        {'Description': 'BT GE Groups', 't_id': 1, 'c_id': 2, 'score': 0},
        {'Description': 'BT Exams', 't_id': 1, 'c_id': 3, 'score': 20},
        {'Description': 'BT In Company', 't_id': 1, 'c_id': 5, 'score': 50},
        {'Description': 'BT 121', 't_id': 1, 'c_id': 6, 'score': 70},        
        {'Description': 'ET Exams', 't_id': 2, 'c_id': 3, 'score': 0},
        {'Description': 'ET GE Groups', 't_id': 2, 'c_id': 2, 'score': 20},
        {'Description': 'ET In Company', 't_id': 2, 'c_id': 5, 'score': 30},
        {'Description': 'ET 121', 't_id': 2, 'c_id': 6, 'score': 50},
        {'Description': 'ET LT', 't_id': 2, 'c_id': 1, 'score': 120},        
        {'Description': 'NT 121', 't_id': 3, 'c_id': 6, 'score': 0},
        {'Description': 'NT In Company', 't_id': 3, 'c_id': 5, 'score': 20},
        {'Description': 'NT GE Groups', 't_id': 3, 'c_id': 2, 'score': 45}
    ]
    
    maxPerDay = 7
    maxPerWeek = 35
    maxSpread = 8
    maxTogether = 0


####Check constraints####
def f(p, c, cl, h, com):
    a1 = teacherAvailable(p, c, cl)
    a2 = teacherCan(p, c, h, com)
    a3 = maxDaily(p, c, cl)
    a4 = maxWeekly(p, c, cl)
    a5 = maxSpread(p['id'], c, cl)
    s = [a1, a2, a3, a4, a5]
    return equalArray(s)

##Imperative constraints##

##Teacher is avaliable to teach the class
def teacherAvailable(p, c, cl):
    z = True
    v = list(filter(lambda k: int(k['teacherId']) == int(p['id']), cl))
    s_1 = int(datetime.strptime(c['start'], config.dateformat).timestamp())
    e_1 = int(datetime.strptime(c['end'], config.dateformat).timestamp())
    for i in range(0, len(v)):
        s_2 = int(datetime.strptime(v[i]['start'], config.dateformat).timestamp())
        e_2 = int(datetime.strptime(v[i]['end'], config.dateformat).timestamp())
        if(check(s_1, e_1, s_2, e_2) == False):
            z = False
            break
    return z

##Teacher has the ability to teach the class
def teacherCan(p, c, h, com):    
    _c = list()
    _ha = list()
    _com = list(filter(lambda k: int(k['groupId']) == int(c['groupId']), com))
    _h = list(filter(lambda k: int(k['teacherId']) == int(p['id']), h))
    for i in range(0, len(_h)):
        _ha.append(_h[i]['habilidad'])
    for i in range(0, len(_com)):
        _c.append(_com[i]['habilidad'])
    return set(_c).issubset(_ha)


##Soft constraints##

##Only x hours of teaching a day
def maxDaily(p, c, cl):
    t_ = 0
    classes = list(filter(lambda k: int(k['teacherId']) == int(p['id']) and isSameDay(k, c) == True and int(k['typeId']) < 7, cl))
    for i in range(0, len(classes)):
        s = int(datetime.strptime(classes[i]['start'], config.dateformat).timestamp())
        e = int(datetime.strptime(classes[i]['end'], config.dateformat).timestamp())
        d = (e - s) / 3600
        t_ = t_ + d
        
    c_s = int(datetime.strptime(c['start'], config.dateformat).timestamp())
    c_e = int(datetime.strptime(c['end'], config.dateformat).timestamp())
    c_l = (c_e - c_s) / 3600
    if (t_ + c_l) <= config.maxPerDay:
        return True
    else:
        return False


##Only x hours of teaching a week
def maxWeekly(p, c, cl):
    t_ = 0
    classes = list(filter(lambda k: int(k['teacherId']) == int(p['id']) and weekOfYear(k['start']) == weekOfYear(c['start']) and int(k['typeId']) < 7, cl))
    for i in range(0, len(classes)):
        s = int(datetime.strptime(classes[i]['start'],config.dateformat).timestamp())
        e = int(datetime.strptime(classes[i]['end'],config.dateformat).timestamp())
        t_ += (e - s) / 3600

    s1 = int(datetime.strptime(c['start'],config.dateformat).timestamp())
    e1 = int(datetime.strptime(c['end'],config.dateformat).timestamp())
    d_ = (e1 - s1) / 3600
    if (t_ + d_) <= config.maxPerWeek:
        return True
    else:
        return False

#Only x hours between the start and end of a shift
def maxSpread(teacherId, clase, clases):
    z = True
    s = int(datetime.strptime(clase['start'], config.dateformat).timestamp())
    e = int(datetime.strptime(clase['end'], config.dateformat).timestamp())
    k = list(filter(lambda k: int(k['teacherId']) == int(teacherId), clases))
    for i in range(0, len(k)):        
        s1 = int(datetime.strptime(k[i]['start'], config.dateformat).timestamp())
        e1 = int(datetime.strptime(k[i]['end'], config.dateformat).timestamp())
        d1 = abs((e - s1)/3600)
        d2 = abs((s - e1)/3600)
        if max(d1, d2) > config.maxSpread:
            z = False
    return z





##Minimise penalties##
def minCost(c, l, cl):
    cost = 150
    teacher = {}
    for i in range(0, len(l)):
        t_id = int(l[i]['typeId'])
        c_id = int(c['typeId'])
        x = list(filter(lambda k: k['t_id'] == t_id and k['c_id'] == c_id, config.penalties))
        if(len(x) > 0):
            if x[0]['score'] < cost:
                teacher = l[i]
                cost = x[0]['score']
    if (teacher):
        setTeacher(teacher, c, cl)
        return cost
    else:
        return 0
    
##Helper functions###


##Returns boolean whether all values in the input array are equal
def equalArray(array):
    array = iter(array)
    try:
        primero = next(array)
    except StopIteration:
        return True
    return all(primero == r for r in array)


##Assigns the teacher to the class
def setTeacher(p, c, cl):
    for i in range(0, len(cl)):
        if int(cl[i]['id']) == int(c['id']):
            cl[i]['teacherId'] = p['id']

##Sets the teachers' hours based on the classes already assigned##
##Takes into account any differences in contracts##
def setTeacherHours(classes, profesores):
    for j in range(0, len(profesores)):
        x = 0
        k = list(filter(lambda k: int(k['teacherId']) == int(profesores[j]['id']), classes))
        for i in range(0, len(k)):
            x += getClassLength(k[i])
        profesores[j]['hours'] = x + float(profesores[j]['handicap'])/6
        if profesores[j]['blnSabado'] == 1:
            profesores[j]['hours'] += 1

##Calculates the average hours based on
##the number of classes and teachers##
def _getAverageHours(classes, profesores):
    l = 0
    k = classes
    for i in range(0, len(k)):
        l += getClassLength(k[i])
    l_bar = l / len(profesores)
    return l_bar

##Returns the length of a class in hours
def getClassLength(c):
    s1 = int(datetime.strptime(c['start'],config.dateformat).timestamp())
    e1 = int(datetime.strptime(c['end'],config.dateformat).timestamp())
    return (e1 - s1)/3600

#Returns a boolean of if two events are on the same day
def isSameDay(c1, c2):
    s1 = datetime.strptime(c1['start'], config.dateformat).date()
    s2 = datetime.strptime(c2['start'], config.dateformat).date()
    if s1 == s2:
        return True
    else:
        return False


#Returns an integer value for the week of the year of a date
def weekOfYear(date):
    d = time.strptime(date, config.dateformat)
    dt = datetime.fromtimestamp(mktime(d))
    w = datetime.date(dt).isocalendar()[1]
    return

#Returns a boolean value as to whether two events overlap
## (RETURNS REVERSE VALUE)
def check(s1, e1, s2, e2):
    if s1 >= e2:
        z = True
    elif s2 >= e1:
        z = True
    else:
        z = False
    return z

#Returns a list of teachers who are over or under the average
#hours defined by x depending on the over_under parameter
def _teachersOverUnder(x, profesores, over_under):
    if over_under == True:
        return list(filter(lambda k: k['hours'] > (x + 0.5), profesores))
    else:
        return list(filter(lambda k: k['hours'] > (x - 0.5), profesores))

#Attempt at a first iteration of the classes
def _firstIteration(p, cl, h, com):
    global _cost
    _cost = 0
    for i in range(0, len(cl)):
        k = list(filter(lambda k: f(k, cl[i], cl, h, com) == True, p))
        _cost += minCost(cl[i], k, cl)

##Sets globals to values from queries defined in q1-q5
def getData(start, end, db):
    database = db
    q1 = "SELECT * FROM Eventos WHERE numIdAula > 1 AND numIdStatus = 1 AND fecFechaInicio > '" + start + "' AND fecFechaInicio < '" + end + "'"
    r1 = ['numIdEvento', 'fecFechaInicio', 'fecFechaFin', 'numIdGrupo', 'numIdProfesor', 'numIdSerie', 'numIdTipoEvento']
    a1 = ['id', 'start', 'end', 'groupId', 'teacherId', 'serie', 'typeId']

    q2 = "SELECT DISTINCT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND numIdUsuario NOT IN (SELECT numIdProfesor FROM Eventos WHERE numIdTipoEvento = 10 AND fecFechaInicio >='" + start + "' AND fecFechaFin <= '" + end + "')"
    r2 = ['numIdUsuario', 'numHoras', 'blnSabado', 'numIdTipoProfesor']
    a2 = ['id', 'handicap', 'blnSabado', 'typeId']

    q3 = "SELECT * FROM Competencias"
    r3 = ['numIdHabilidad', 'numIdUsuario']
    a3 = ['habilidad', 'teacherId']

    q4 = "SELECT DISTINCT numIdClase, numIdHabilidad  FROM CompetenciasClases"
    r4 = ['numIdHabilidad', 'numIdClase']
    a4 = ['habilidad', 'groupId']

    q5 = "SELECT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND blnMorning = 1"
    r5 = ['numIdUsuario', 'numHoras', 'blnSabado', 'numIdTipoProfesor']
    a5 = ['id', 'handicap', 'blnSabado', 'typeId']

    global ev, pr, c, cc, pm

    ev = servConnect.runQuery(q1, r1, a1, database, True)
    pr = servConnect.runQuery(q2, r2, a2, database, True)
    c = servConnect.runQuery(q3, r3, a3, database, True)
    cc = servConnect.runQuery(q4, r4, a4, database, True)
    pm = servConnect.runQuery(q5, r5, a5, database, True)

getData('2018-04-25 00:00:00', '2018-04-25 23:59:59', 'New_Test')

_firstIteration(pr, ev, c, cc)
