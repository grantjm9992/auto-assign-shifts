import time
import pymssql
import calendar
import json
import copy
import datetime
from datetime import datetime
from time import mktime


class classes:
    violations = list()
    unassigned_Series = list()
    unassigned_Singular = list()

#Connection class. Use for queries to DB
class servConnect:
    #Connection constants
    server = "SRVN16\SQLEXPRESS"
    user = "agora"
    password = "number16"
    #Function to run query.
    def runQuery(query, _rows, _alias, database, _dict):

        r = list()
        
        conn = pymssql.connect(servConnect.server, servConnect.user, servConnect.password, database)
        cursor = conn.cursor(as_dict=_dict)
        cursor.execute(query)
        for row in cursor:
            s = {}
            for i in range(0, len(_rows)):
                s[_alias[i]] = str(row[_rows[i]]).rstrip()
            r.append(s)

        return r

class config:
    dateformat = '%Y-%m-%d %H:%M:%S'

    
#####################################################
##################Helper Functions###################

def _getClassesInSeries(seriesId, classes):
    _serie = list()
    for i in range(0, len(classes)):
        if int(classes[i]['serie']) == seriesId:
            _serie.append(i)
    return _serie

def _teacherHasAbility(teacher, abilityId, comp):
    flag = False
    for i in range(0, len(comp)):
        if comp[i]['userid'] == teacher['teacherId'] and int(comp[i]['habilidad']) == abilityId:
            flag = True
            break
    return flag

def _classHasNeed(_class, _abilityId, _cComp):
    flag = False
    for i in range(0, len(_cComp)):
        if _cComp[i]['groupId'] == _class['classId'] and int(_cComp[i]['habilidad']) == _abilityId:
            flag = True
            break
    return flag


def weekOfYear(date):
    d = time.strptime(date, config.dateformat)
    dt = datetime.fromtimestamp(mktime(d))
    w = datetime.date(dt).isocalendar()[1]
    return w

def check(s1, e1, s2, e2):
    if s1 >= e2:
        z = True
    elif s2 >= e1:
        z = True
    else:
        z = False
    return z
    
#####################################################
###############Imperative Constraints################

def classNeedsTeacher(c):
    if int(c['teacherId']) > 0:
        return False
    else:
        return True
    return


def teacherLibre(teacherId, cl, cls):
    clase = (cl)
    clases = (cls)
    
    z = True
    d = time.strptime('2017-11-12 08:00:00', config.dateformat)
    s_1 = calendar.timegm(time.strptime(clase['start'], config.dateformat))
    e_1 = calendar.timegm(time.strptime(clase['end'], config.dateformat))
    for i in range(0, len(clases)):
        if clases[i]['teacherId'] == teacherId:
            s_2 = calendar.timegm(time.strptime(clases[i]['start'], config.dateformat))
            e_2 = calendar.timegm(time.strptime(clases[i]['end'], config.dateformat))
            if(check(s_1, e_1, s_2, e_2) == False):
                z = False
                break            
    return z

    
#####################################################
##################Soft Constraints###################


def teacherHasAbility(classCompetencies, competencies, c, teacher):
    cComp = (classCompetencies)
    Comp = (competencies)
    clase = (c)
    profesor = (teacher)
    
    arr = list()
    x = True
    for j in range(0, len(cComp)):
        if int(cComp[j]['groupId']) == int(clase['classId']):
            if int(cComp[j]['groupId']) > 0:
                arr.append(int(cComp[j]['habilidad']))
    n = 0
    ar = list()
    for k in range(0, len(Comp)):
        if int(Comp[k]['userid']) == int(profesor['teacherId']):
            ar.append(int(Comp[k]['habilidad']))

    return(set(arr).issubset(ar))
def maxPerDay(teacherId, clase, classes, m):
    t_ = 0
    d = datetime.strptime(clase['start'], config.dateformat)
    d_s = int(d.replace(hour=00, minute=00, second=00).timestamp())
    d_e = int(d.replace(hour=23, minute=59, second=59).timestamp())

    c_s = int(datetime.strptime(clase['start'], config.dateformat).timestamp())
    c_e = int(datetime.strptime(clase['end'], config.dateformat).timestamp())

    for i in range(0, len(classes)):
        id_ = classes[i]['teacherId']
        s = int(datetime.strptime(classes[i]['start'], config.dateformat).timestamp())
        e = int(datetime.strptime(classes[i]['end'], config.dateformat).timestamp())
        if int(id_) == int(teacherId):
            if isSameDay(classes[i], clase) == True:
                d = (e - s) / 3600
                t_ = t_ + d

    c_l = (c_e - c_s) / 3600
    if (t_ + c_l) <= m:
        return True
    else:
        return False

def maxALaSemana(teacherId, clase, cls, m):
    c = clase
    tot = 0
    x = datetime.strptime(c['start'], config.dateformat)
    w_s = weekOfYear(c['start'])
    for i in range(0, len(cls)):
        if cls[i]['teacherId'] == teacherId:
            s = datetime.strptime(cls[i]['start'],config.dateformat)
            e = datetime.strptime(cls[i]['end'],config.dateformat)
            st = int(s.timestamp())
            et = int(e.timestamp())
            w_i = weekOfYear(cls[i]['start'])
            if w_s == w_i:
                dt = (et - st) / 3600
                tot = tot + dt
    s1 = datetime.strptime(c['start'],config.dateformat)
    e1 = datetime.strptime(c['end'],config.dateformat)
    dt_s1 = int(s1.timestamp())
    dt_e1 = int(e1.timestamp())
    d1 = (dt_e1 - dt_s1) / 3600
    tot = tot + d1
    if tot <= m:
        return True
    else:
        return False               

def maxSpread(teacherId, clase, clases, m):
    z = True
    s = int(datetime.strptime(clase['start'], config.dateformat).timestamp())
    e = int(datetime.strptime(clase['end'], config.dateformat).timestamp())
    k = list(filter(lambda k: int(k['teacherId']) == int(teacherId), clases))
    for i in range(0, len(k)):        
        s1 = int(datetime.strptime(k[i]['start'], config.dateformat).timestamp())
        e1 = int(datetime.strptime(k[i]['end'], config.dateformat).timestamp())
        d1 = abs((e - s1)/3600)
        d2 = abs((s - e1)/3600)
        if max(d1, d2) > m:
            z = False
    return z

def isSameDay(c1, c2):
    s1 = datetime.strptime(c1['start'], config.dateformat).date()
    s2 = datetime.strptime(c2['start'], config.dateformat).date()
    if s1 == s2:
        return True
    else:
        return False

def allClassesCovered(classes):
    v = 0
    for i in range(0, len(classes)):
        if int(classes[i]['teacherId']) <= 0:
            v = v + 1
    return v

def _availableTeacherThatCan(cComp, comp, clase, classes, profesor, sol):
    a = teacherLibre(profesor['teacherId'], clase, classes)
    b = teacherHasAbility(cComp, comp, clase, profesor)
    c = maxPerDay(profesor['teacherId'], clase, classes, sol[1])
    d = maxALaSemana(profesor['teacherId'], clase, classes, sol[0])
    e = maxSpread(profesor['teacherId'], clase, classes, sol[2])
    f = longestRun(classes, clase, profesor, sol[3])
    s = [a, b, c, d, e, f]
    return equalArray(s)


def equalArray(array):
    array = iter(array)
    try:
        primero = next(array)
    except StopIteration:
        return True
    return all(primero == r for r in array)


def getClassLength(c):
    s1 = int(datetime.strptime(c['start'],config.dateformat).timestamp())
    e1 = int(datetime.strptime(c['end'],config.dateformat).timestamp())
    return (e1 - s1)/3600
    


def getViolations(k):
    v_1 = "More than 8 hours between start and finish"
    v_2 = "More than 30 hours a week"
    v_3 = "More than 6 contact hours a day"
    v_4 = "Teacher doesn't have the training required"
    V = [v_4, v_3, v_2, v_1]
    if (k - 2) < len(V):
        return V[k - 2]
                                
    
def assignClass(profesor, clase):
    clase['teacherId'] = profesor['teacherId']
                                

def setTeacherHours(classes, profesores):
    for j in range(0, len(profesores)):
        x = 0
        k = list(filter(lambda k: int(k['teacherId']) == int(profesores[j]['teacherId']), classes))
        for i in range(0, len(k)):
            x += getClassLength(k[i])
        profesores[j]['hours'] = x + float(profesores[j]['handicap'])/5
        if profesores[j]['blnSabado'] == 1:
            profesores[j]['hours'] += 5

def setSaturdayHours(classes, profesores):
    for j in range(0, len(profesores)):
        x = 0
        k = list(filter(lambda k: int(k['teacherId']) == int(profesores[j]['teacherId']), classes))
        for i in range(0, len(k)):
            x += getClassLength(k[i])
        profesores[j]['hours'] = x + 2

def getShiftMins(classes):
    _classes = sorted(classes, key=lambda k: k['start'])
    _v = list()
    for i in range(0, len(_classes)):
        v = 0
        s_1 = calendar.timegm(time.strptime(classes[i]['start'], config.dateformat))
        e_1 = calendar.timegm(time.strptime(classes[i]['end'], config.dateformat))
        for j in range(0, len(_classes)):
            s_2 = calendar.timegm(time.strptime(classes[j]['start'], config.dateformat))
            e_2 = calendar.timegm(time.strptime(classes[j]['end'], config.dateformat))
            if check(s_1, e_1, s_2, e_2) == False:
                v = v + 1
        _v.append({'time': time.strptime(classes[i]['start'], config.dateformat), 'number': v})
    return(_v)
            
def sortClasses(classes, bln):
    return sorted(classes, key=lambda k: (datetime.strptime(k['start'], config.dateformat).hour)*60 + datetime.strptime(k['start'], config.dateformat).minute, reverse=bln)

def longestRun(c, cl, p, m):
    C = list(filter(lambda k: int(k['teacherId']) == int(p['teacherId']), c))
    C.append(cl)
    ci = list()
    f = '%Y-%m-%d %H:%M:%S'
    d = 0
    d2 = 0
    d3 = 0
    d4 = 0
    for i in range(0, len(C) - 1):
            if int(d3) == 0:
                ci.append(i)
                d2 += (datetime.strptime(C[i]['end'], f) - datetime.strptime(C[i]['start'], f)).seconds
            d4 = (datetime.strptime(C[i+1]['start'], f) - datetime.strptime(C[i]['end'], f)).seconds
            if int(d4) == 0:
                d3 = 1
                d2 += (datetime.strptime(C[i]['end'], f) - datetime.strptime(C[i]['start'], f)).seconds
                ci.append(i+1)
                if i == len(C) - 2:
                    ct = copy.deepcopy(ci)
                    d = d2
            else:
                d3 = 0
                if d2 > d:
                    d = d2
                    ct = copy.deepcopy(ci)
                    ci = list()
                d2 = 0
    k = len(C) - 2
    if k > 1:
        if k in ct and (d/3600) > m:
            return False
        else:
            return True
    else:
        if d/3600 > m:
            return False
        else:
            return True

def findClashingClasses(teacherId, clase, classes):
    c_s = int(datetime.strptime(clase['start'], config.dateformat).timestamp())
    c_e = int(datetime.strptime(clase['end'], config.dateformat).timestamp())

    c_c = list()

    for i in range(0, len(classes)):
        s = int(datetime.strptime(classes[i]['start'], config.dateformat).timestamp())
        e = int(datetime.strptime(classes[i]['end'], config.dateformat).timestamp())
        if int(classes[i]['serie']) == 0 and classes[i]['teacherId'] == teacherId and not s >= c_e and not e <= c_s:
            c_c.append(i)
    return c_c

def findClassesALaVez(clase, classes):
    c_s = int(datetime.strptime(clase['start'], config.dateformat).timestamp())
    c_e = int(datetime.strptime(clase['end'], config.dateformat).timestamp())

    c_c = list()

    for i in range(0, len(classes)):
        s = int(datetime.strptime(classes[i]['start'], config.dateformat).timestamp())
        e = int(datetime.strptime(classes[i]['end'], config.dateformat).timestamp())
        if not s >= c_e and not e <= c_s:
            c_c.append(i)
    return c_c
    

def _teacherThatCan(cComp, comp, clase, classes, profesor, sol):
    if classNeedsTeacher(clase) == True:
        a = teacherHasAbility(cComp, comp, clase, profesor)
        d = maxSpread(profesor['teacherId'], clase, classes, sol[2])
        s = [a, d]
        return equalArray(s)
    else:
        return False
#Check constraints with option <gamma> of reducing those applied
def _checkConstraints(gamma, profesor, classes, clase, cComp, comp):
        a = teacherLibre(profesor['teacherId'], clase, classes)
        b = teacherHasAbility(cComp, comp, clase, profesor)
        c = maxPerDay(profesor['teacherId'], clase, classes)
        d = maxALaSemana(profesor['teacherId'], clase, classes)
        e = maxSpread(profesor['teacherId'], clase, classes)
        s = [a, b, c, d, e]
        return equalArray(s)

#Use only on first iteration!! Checks if a teacher meets all of the requirements of all the classes in a series
def _initialSerie(_series, profesor, cComp, comp, classes):
    v = True
    for k in range(0, len(_series)):
        if not ((teacherHasAbility(cComp, comp, classes[_series[k]], profesor) == True and teacherLibre(profesor['teacherId'], classes[_series[k]], classes) == True)):
            v = False
            break
    return v

######
#TEST#
######
def _getSeries_(clase, classes):
    _series = list(filter(lambda k: k['serie'] == clase['serie'], classes))

#Returns a matrix of indices of classes in a series
def _getSeries(clase, classes):
    _series = list()
    for i in range(0, len(classes)):
        if classes[i]['serie'] == clase['serie']:
            _series.append(i)
    return _series

def _getTeacherClasses(teacherId, classes):
    tc = list(filter(lambda k: k['teacherId'] == teacherId and int(k['serie']) <= 0, classes))
    return tc

def _teachersOverUnder(x, profesores, over):
    tO = list()
    if over == True:
        for i in range(0, len(profesores)):
            if profesores[i]['hours'] > x + 0.5:
                tO.append(profesores[i])
    elif over == False:
        for i in range(0, len(profesores)):
            if profesores[i]['hours'] < x - 0.5:
                tO.append(profesores[i])
    return tO


def _getAverageHours(classes, profesores):
    l = 0
    k = classes
    for i in range(0, len(k)):
        l += getClassLength(k[i])
    l_bar = l / len(profesores)
    return l_bar
