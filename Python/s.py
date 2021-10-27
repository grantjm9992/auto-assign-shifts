import helper
import copy
import datetime
from random import shuffle

def getData(start, end, db):
    database = db
    q1 = "SELECT * FROM Eventos WHERE numIdAula > 1 AND numIdStatus = 1 AND fecFechaInicio > '" + start + "' AND fecFechaInicio < '" + end + "'"
    r1 = ['numIdEvento', 'fecFechaInicio', 'fecFechaFin', 'numIdGrupo', 'numIdProfesor', 'numIdSerie', 'blnPrePainted']
    a1 = ['id', 'start', 'end', 'classId', 'teacherId', 'serie', 'blnPrePainted']

    q2 = "SELECT DISTINCT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND numIdUsuario NOT IN (SELECT numIdProfesor FROM Eventos WHERE numIdTipoEvento = 10 AND fecFechaInicio >='" + start + "' AND fecFechaFin <= '" + end + "')"
    r2 = ['numIdUsuario', 'numHoras', 'blnSabado']
    a2 = ['teacherId', 'handicap', 'blnSabado']

    q3 = "SELECT * FROM Competencias"
    r3 = ['numIdHabilidad', 'numIdUsuario']
    a3 = ['habilidad', 'userid']

    q4 = "SELECT DISTINCT numIdClase, numIdHabilidad  FROM CompetenciasClases"
    r4 = ['numIdHabilidad', 'numIdClase']
    a4 = ['habilidad', 'groupId']

    q5 = "SELECT DISTINCT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND blnMorning = 1 AND numIdUsuario NOT IN (SELECT numIdProfesor FROM Eventos WHERE numIdTipoEvento = 10 AND fecFechaInicio >='" + start + "' AND fecFechaFin <= '" + end + "')"
    r5 = ['numIdUsuario', 'numHoras', 'blnSabado']
    a5 = ['teacherId', 'handicap', 'blnSabado']

    q6 = "SELECT * FROM Eventos WHERE numIdAula > 1 AND numIdStatus = 1 AND fecFechaInicio > '" + start + "' AND fecFechaInicio < '" + end + "'"

    global ev, pr, c, cc, pm, evh

    ev = helper.servConnect.runQuery(q1, r1, a1, database, True)
    pr = helper.servConnect.runQuery(q2, r2, a2, database, True)
    c = helper.servConnect.runQuery(q3, r3, a3, database, True)
    cc = helper.servConnect.runQuery(q4, r4, a4, database, True)
    pm = helper.servConnect.runQuery(q5, r5, a5, database, True)
    evh = helper.servConnect.runQuery(q6, r1, a1, database, True)
    

def create(_profesores, _classes, cComp, comp, pm):
    start = datetime.datetime.now()
    _check(_classes)
    t = _drivingTeachers(_profesores, comp)
    r = _drivingRoutes(_classes, cComp)
    _assignDrivingRoutes(t, _profesores, r, _classes, comp, cComp)
    _check(_classes)
    print("Driving classes assigned")
    _assignRoutes(_profesores, _classes, cComp, comp)
    _check(_classes)
    print("Routes assigned")
    helper.setTeacherHours(_classes, _profesores)
    _profesores = sorted(_profesores, key=lambda k: k['hours'])
    _classes = sorted(_classes, key=lambda k: k['start'], reverse = False)

    blank_profesores = copy.deepcopy(_profesores)
    blank_classes = copy.deepcopy(_classes)
    
    it = 100
    o = len(_classes)

    
    while it > 0:
        print(str(datetime.datetime.now()) + ": Iteration: " + str(101 - it))
        temp_classes = copy.deepcopy(_classes)
        temp_profesores = copy.deepcopy(_profesores)
        temp_profesores = list(filter(lambda k: k['hours'] <= 7, temp_profesores))
        shuffle(temp_profesores)
        _initialAssignment(pm, temp_classes, cComp, comp)
        temp_profes = copy.deepcopy(_profesores)
        helper.setTeacherHours(temp_classes, temp_profes)
        temp_profesores = sorted(temp_profes, key=lambda k: k['hours'])
        temp_classes = sorted(temp_classes, key=lambda k: k['start'], reverse = True)
        _initialAssignment(temp_profes, temp_classes, cComp, comp)

        _check(temp_classes)

        _swapForAbility(temp_profes, temp_classes, cComp, comp)

        _check(temp_classes)

        temp = len(helper.classes.unassigned_Singular)

        last_it = 101 - it
        
        if temp < o:
            global new_classes
            global new_profesores
            new_classes = copy.deepcopy(temp_classes)
            new_profesores = copy.deepcopy(temp_profes)
            o = temp
        if temp <= 2:
            it = -1
        else:
            it += - 1

    helper.setTeacherHours(new_classes, new_profesores)
    
    end = datetime.datetime.now()
    print(str(end - start) + ": " + str(o) + " unassigned after " + str(last_it) + " iterations")

    ####################################################################################################
    print("Looking to improve hour spread")
    avg = helper._getAverageHours(new_classes, new_profesores)
    tO = helper._teachersOverUnder(avg, new_profesores, True)
    it = 0
    while it < 20:
        _reassign(new_profesores, new_classes, cComp, comp)
        tO = helper._teachersOverUnder(avg, new_profesores, True)
        it += 1

def _reassign(profesores, classes, cComp, comp):
    avg = helper._getAverageHours(classes, profesores)
    tO = helper._teachersOverUnder(avg, profesores, True)
    for i in range(0, len(tO)):
        br = False
        C_tO = helper._getTeacherClasses(tO[i]['teacherId'], classes)
        tU = helper._teachersOverUnder(avg, profesores, False)
        tU = sorted(tU, key=lambda k: k['hours'])
        for j in range(0, len(C_tO)):
            for k in range(0, len(tU)):
                if helper._availableTeacherThatCan(cComp, comp, C_tO[j], classes, tU[k]) == True:
                    for m in range(0, len(classes)):
                        if classes[m]['id'] == C_tO[j]['id']:
                            classes[m]['teacherId'] = tU[k]['teacherId']
                            helper.setTeacherHours(classes, profesores)
                            br = True
                            break
                    break
            if br == True:
                break
        if br == True:
            break

def re(profesores, classes, cComp, comp):
    avg = helper._getAverageHours(classes, profesores)
    tO = helper._teachersOverUnder(avg, profesores, True)
    t = list()
    for i in range(0, len(tO)):
        t.append(int(tO[i]['teacherId']))
    cl = list(filter(lambda k: int(k['teacherId']) in t and int(k['serie']) == 0, classes))
    tU = helper._teachersOverUnder(avg, profesores, False)
    i = 0
    while i < 200:
        for j in range(0, len(cl)):
            for k in range(0, len(tU)):
                if helper._checkConstraints(0, tU[k], classes, cl[j], cComp, comp) == True:
                    for l in range(0, len(classes)):
                        if int(classes[l]['id']) == int(cl[j]['id']):
                            classes[l]['teacherId'] == int(tU[k]['teacherId'])
                    break
            helper.setTeacherHours(classes, profesores)
            tO = helper._teachersOverUnder(avg, profesores, True)
            t = list()
            for i in range(0, len(tO)):
                t.append(int(tO[i]['teacherId']))
            cl = list(filter(lambda k: int(k['teacherId']) in t and int(k['serie']) == 0, classes))
        i += 1
        

    
def _initialAssignment(profesores, classes, cComp, comp):
    for i in range(0, len(classes)):
        if helper.classNeedsTeacher(classes[i]) == True:
            if int(classes[i]['serie']) <= 0:
                if classes[i]['blnPrePainted'] == 'False':
                    for j in range(0, len(profesores)):
                        if helper._availableTeacherThatCan(cComp, comp, classes[i], classes, profesores[j]) == True:
                            helper.assignClass(profesores[j], classes[i])
                            break
        helper.setTeacherHours(classes, profesores)

def _check(classes):
    helper.classes.unassigned_Series = list()
    helper.classes.unassigned_Singular = list()
    for i in range(0, len(classes)):
        if helper.classNeedsTeacher(classes[i]) == True:
            if int(classes[i]['serie']) > 0:
                if int(classes[i]['serie']) not in helper.classes.unassigned_Series:
                    helper.classes.unassigned_Series.append(int(classes[i]['serie']))
            else:
                helper.classes.unassigned_Singular.append(i)
    if len(helper.classes.unassigned_Series) > 0 or len(helper.classes.unassigned_Singular) > 0:
        return True
    else:
        return False

    
def _drivingRoutes(classes, cComp):
    d_s = list()
    for i in range(0, len(classes)):
        if helper._classHasNeed(classes[i], 8, cComp) == True:
            if int(classes[i]['serie']) not in d_s:
                d_s.append(int(classes[i]['serie']))
    return d_s

def _drivingTeachers(profesores, comp):
    d_t = list()
    for i in range(0, len(profesores)):
        if helper._teacherHasAbility(profesores[i], 8, comp) == True:
            d_t.append(i)
    return d_t

def _assignDrivingRoutes(_p, profesores, series, classes, comp, cComp):
    for i in range(0, len(series)):
        _serie = helper._getClassesInSeries(series[i], classes)
        for j in range(0, len(_p)):
            if helper._initialSerie(_serie, profesores[_p[j]], cComp, comp, classes) == True:
                for k in range(0, len(_serie)):
                    helper.assignClass(profesores[_p[j]], classes[_serie[k]])
                break

def _assignRoutes(profesores, classes, cComp, comp):
    for i in range(0, len(helper.classes.unassigned_Series)):
        _serie = helper._getClassesInSeries(helper.classes.unassigned_Series[i], classes)
        for j in range(0, len(profesores)):
            if helper._initialSerie(_serie, profesores[j], cComp, comp, classes) == True:
                for k in range(0, len(_serie)):
                    helper.assignClass(profesores[j], classes[_serie[k]])
                helper.setTeacherHours(classes, profesores)
                profesores = sorted(profesores, key=lambda k: k['hours'])
                break

def _swapForAbility(profesores, classes, cComp, comp):
    k = list(filter(lambda k: int(k['teacherId']) == -1 and int(k['serie']) == 0, classes))
    for i in range(0, len(k)):
        for j in range(0, len(profesores)):
            if helper._teacherThatCan(cComp, comp, k[i], classes, profesores[j]):
                clashing = helper.findClashingClasses(profesores[j]['teacherId'], k[i], classes)
                for x in range(0, len(clashing)):
                    classes[clashing[x]]['teacherId'] = -1
                for x in range(0, len(classes)):
                    if int(classes[x]['id']) == int(k[i]['id']):
                        classes[x]['teacherId'] == profesores[j]['teacherId']
                        break
                break

def go():
    start = input("start: %Y-%m-%d %H:%M:%S")
    end = input("end: %Y-%m-%d %H:%M:%S")
    getData(start, end)
    for i in range(0, len(ev)):
        ev[i]['teacherId'] = -1
        ev[i]['serie'] = int(ev[i]['serie'])
    create(pr, ev, cc, c, pm)
    s1 = datetime.datetime.strptime(start, helper.config.dateformat)
    ef = datetime.datetime.strptime(end, helper.config.dateformat)
    global cT
    cT = list()
    while s1 < ef:
        s2 = s1
        cl = {'start': str(s2)}
        c_day = list(filter(lambda k: helper.isSameDay(cl, k) == True, new_classes))
        i = 0
        while i < 20:
            helper.setTeacherHours(c_day, new_profesores)
            _reassign(new_profesores, c_day, data.cc, data.c)
            i += 1
        for i in range(0, len(c_day)):
            cT.append(c_day[i])
        s1 += datetime.timedelta(days=1)
    helper.setTeacherHours(cT, new_profesores)
    j = 0
    while j < 25:
        _reassign(new_profesores, cT, data.cc, data.c)
        j += 1


dates = helper.returnNextWeekDates()

dbs = ["Paraqueet"]
for db_i in range(0, len(dbs)):
    import pymssql
    conn = pymssql.connect(helper.servConnect.server, helper.servConnect.user, helper.servConnect.password, dbs[db_i])
    cursor = conn.cursor()
    cursor.execute('UPDATE Eventos SET blnPrePainted = 1 WHERE numIdProfesor > 0')
    conn.commit()
    cursor.execute('UPDATE Eventos SET blnPrePainted = 0 WHERE numIdProfesor < 1')
    conn.commit()
    for d_i in range(0, len(dates)):
        getData(dates[d_i]['start'], dates[d_i]['end'], dbs[db_i])
        helper.setTeacherHours(ev, pr)
        pr = sorted(pr, key=lambda k: k['hours'])
        _check(ev)
        t = _drivingTeachers(pr, c)
        r = _drivingRoutes(ev, cc)
        _assignDrivingRoutes(t, pr, r, ev, c, cc)
        helper.setTeacherHours(ev, pr)
        pr = sorted(pr, key=lambda k: k['hours'])
        _check(ev)
        _assignRoutes(pr, ev, cc, c)
        helper.setTeacherHours(ev, pr)
        pr = sorted(pr, key=lambda k: k['hours'])
        _check(ev)
        helper.setTeacherHours(ev, pr)
        pr = sorted(pr, key=lambda k: k['hours'])
        shuffle(ev)
        ev = sorted(ev, key=lambda k: k['start'])
        shuffle(pm)
        _initialAssignment(pm, ev, cc, c)
        helper.setTeacherHours(ev, pr)
        shuffle(pr)
        pr = sorted(pr, key=lambda k: k['hours'])
        shuffle(ev)
        ev = sorted(ev, key=lambda k: k['start'], reverse=True)
        _initialAssignment(pr, ev, cc, c)
        helper.setTeacherHours(ev, pr)
        pr = sorted(pr, key=lambda k: k['hours'])
        _check(ev)
        _swapForAbility(pr, ev, cc, c)
        _initialAssignment(pr, ev, cc, c)
        i = 0
        while i < 50:
                _reassign(pr, ev, cc, c)
                helper.setTeacherHours(ev, pr)
                pr = sorted(pr, key=lambda k: k['hours'])
                i += 1
        
        l = list()
        for i in range(0, len(ev)):
                l.append((ev[i]['teacherId'], ev[i]['id']))
        cursor.executemany("UPDATE Eventos SET numIdProfesor = %d WHERE numIdEvento = %d", l)
        conn.commit()
        cursor.execute("UPDATE Eventos SET strColorProfesor = (SELECT strColorProfesor FROM Profesores WHERE Profesores.numIdUsuario = Eventos.numIdProfesor), strColorAula = (SELECT strColorTexto FROM Profesores WHERE Profesores.numIdUsuario = Eventos.numIdProfesor)")
        cursor.execute("UPDATE Eventos SET strColorProfesor = 'grey', strColorAula = 'white' WHERE numIdStatus > 1")
        conn.commit()
                
        print('Finished day: ' + str(dates[d_i]))
