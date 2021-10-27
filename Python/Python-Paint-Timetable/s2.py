import helper2
import copy
import datetime
import pymssql
from random import shuffle

def getData(start, end, db):
    database = db
    q1 = "SELECT * FROM Eventos WHERE numIdAula > 1 AND numIdStatus = 1 AND fecFechaInicio > '" + start + "' AND fecFechaInicio < '" + end + "'"
    r1 = ['numIdEvento', 'fecFechaInicio', 'fecFechaFin', 'numIdGrupo', 'numIdProfesor', 'numIdSerie']
    a1 = ['id', 'start', 'end', 'classId', 'teacherId', 'serie']

    q2 = "SELECT DISTINCT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND numIdUsuario NOT IN (SELECT numIdProfesor FROM Eventos WHERE numIdTipoEvento = 10 AND fecFechaInicio >='" + start + "' AND fecFechaFin <= '" + end + "')"
    r2 = ['numIdUsuario', 'numHoras', 'blnSabado']
    a2 = ['teacherId', 'handicap', 'blnSabado']

    q3 = "SELECT * FROM Competencias"
    r3 = ['numIdHabilidad', 'numIdUsuario']
    a3 = ['habilidad', 'userid']

    q4 = "SELECT DISTINCT numIdClase, numIdHabilidad  FROM CompetenciasClases"
    r4 = ['numIdHabilidad', 'numIdClase']
    a4 = ['habilidad', 'groupId']

    q5 = "SELECT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND blnMorning = 1"
    r5 = ['numIdUsuario', 'numHoras', 'blnSabado']
    a5 = ['teacherId', 'handicap', 'blnSabado']

    q6 = "SELECT * FROM Profesores WHERE numIdUsuario > 0 AND blnDisponible = 1 AND blnMorning = 1"
    r6 = ['numIdUsuario', 'numHoras', 'blnSabado']
    a6 = ['teacherId', 'handicap', 'blnSabado']

    global ev, pr, c, cc, pm, ps, evT

    ev = helper2.servConnect.runQuery(q1, r1, a1, database, True)
    pr = helper2.servConnect.runQuery(q2, r2, a2, database, True)
    c = helper2.servConnect.runQuery(q3, r3, a3, database, True)
    cc = helper2.servConnect.runQuery(q4, r4, a4, database, True)
    pm = helper2.servConnect.runQuery(q5, r5, a5, database, True)
    ps = helper2.servConnect.runQuery(q6, r6, a6, database, True)


def _reassign(profesores, classes, cComp, comp, sol):
    avg = helper2._getAverageHours(classes, profesores) - 1.2
    tO = helper2._teachersOverUnder(avg, profesores, True)
    for i in range(0, len(tO)):
        br = False
        C_tO = helper2._getTeacherClasses(tO[i]['teacherId'], classes)
        tU = helper2._teachersOverUnder(avg, profesores, False)
        tU = sorted(tU, key=lambda k: k['hours'])
        for j in range(0, len(C_tO)):
            for k in range(0, len(tU)):
                if helper2._availableTeacherThatCan(cComp, comp, C_tO[j], classes, tU[k], sol) == True:
                    for m in range(0, len(classes)):
                        if classes[m]['id'] == C_tO[j]['id']:
                            classes[m]['teacherId'] = tU[k]['teacherId']
                            helper2.setTeacherHours(classes, profesores)
                            br = True
                            break
                    break
            if br == True:
                break
        if br == True:
            break

def re(profesores, classes, cComp, comp):
    avg = helper2._getAverageHours(classes, profesores)
    tO = helper2._teachersOverUnder(avg, profesores, True)
    t = list()
    for i in range(0, len(tO)):
        t.append(int(tO[i]['teacherId']))
    cl = list(filter(lambda k: int(k['teacherId']) in t and int(k['serie']) == 0, classes))
    tU = helper2._teachersOverUnder(avg, profesores, False)
    i = 0
    while i < 200:
        for j in range(0, len(cl)):
            for k in range(0, len(tU)):
                if helper2._checkConstraints(0, tU[k], classes, cl[j], cComp, comp) == True:
                    for l in range(0, len(classes)):
                        if int(classes[l]['id']) == int(cl[j]['id']):
                            classes[l]['teacherId'] == int(tU[k]['teacherId'])
                    break
            helper2.setTeacherHours(classes, profesores)
            tO = helper2._teachersOverUnder(avg, profesores, True)
            t = list()
            for i in range(0, len(tO)):
                t.append(int(tO[i]['teacherId']))
            cl = list(filter(lambda k: int(k['teacherId']) in t and int(k['serie']) == 0, classes))
        i += 1
        

    
def _initialAssignment(profesores, classes, cComp, comp, sol):
    for i in range(0, len(classes)):
        if helper2.classNeedsTeacher(classes[i]) == True:
            if int(classes[i]['serie']) <= 0:
                for j in range(0, len(profesores)):
                    if helper2._availableTeacherThatCan(cComp, comp, classes[i], classes, profesores[j], sol) == True:
                        helper2.assignClass(profesores[j], classes[i])
                        break
        helper2.setTeacherHours(classes, profesores)

def _check(classes):
    helper2.classes.unassigned_Series = list()
    helper2.classes.unassigned_Singular = list()
    for i in range(0, len(classes)):
        if helper2.classNeedsTeacher(classes[i]) == True:
            if int(classes[i]['serie']) > 0:
                if int(classes[i]['serie']) not in helper2.classes.unassigned_Series:
                    helper2.classes.unassigned_Series.append(int(classes[i]['serie']))
            else:
                helper2.classes.unassigned_Singular.append(i)
    if len(helper2.classes.unassigned_Series) > 0 or len(helper2.classes.unassigned_Singular) > 0:
        return True
    else:
        return False

    
def _drivingRoutes(classes, cComp):
    d_s = list()
    for i in range(0, len(classes)):
        if helper2._classHasNeed(classes[i], 8, cComp) == True:
            if int(classes[i]['serie']) not in d_s:
                d_s.append(int(classes[i]['serie']))
    return d_s

def _drivingTeachers(profesores, comp):
    d_t = list()
    for i in range(0, len(profesores)):
        if helper2._teacherHasAbility(profesores[i], 8, comp) == True:
            d_t.append(i)
    return d_t

def _assignDrivingRoutes(_p, profesores, series, classes, comp, cComp):
    for i in range(0, len(series)):
        _serie = helper2._getClassesInSeries(series[i], classes)
        for j in range(0, len(_p)):
            if helper2._initialSerie(_serie, profesores[_p[j]], cComp, comp, classes) == True:
                for k in range(0, len(_serie)):
                    helper2.assignClass(profesores[_p[j]], classes[_serie[k]])
                break

def _assignRoutes(profesores, classes, cComp, comp):
    for i in range(0, len(helper2.classes.unassigned_Series)):
        _serie = helper2._getClassesInSeries(helper2.classes.unassigned_Series[i], classes)
        for j in range(0, len(profesores)):
            if helper2._initialSerie(_serie, profesores[j], cComp, comp, classes) == True:
                for k in range(0, len(_serie)):
                    helper2.assignClass(profesores[j], classes[_serie[k]])
                helper2.setTeacherHours(classes, profesores)
                profesores = sorted(profesores, key=lambda k: k['hours'])
                break

def _swapForAbility(profesores, classes, cComp, comp, sol):
    k = list(filter(lambda k: int(k['teacherId']) == -1 and int(k['serie']) == 0, classes))
    for i in range(0, len(k)):
        for j in range(0, len(profesores)):
            if helper2._teacherThatCan(cComp, comp, k[i], classes, profesores[j], sol):
                clashing = helper2.findClashingClasses(profesores[j]['teacherId'], k[i], classes)
                for x in range(0, len(clashing)):
                    classes[clashing[x]]['teacherId'] = -1
                for x in range(0, len(classes)):
                    if int(classes[x]['id']) == int(k[i]['id']):
                        classes[x]['teacherId'] == profesores[j]['teacherId']
                        break
                break


solutions = [
    [35, 7, 8, 4.5],
    [35, 7, 8, 6],
    [35, 7, 10, 4.5],
    [35, 7, 10, 6],
    [35, 7, 12, 4.5],
    [35, 7, 12, 6]
]

explanations = [
    'Nothing. Perfect',
    'Too many consecutive hours',
    'Shift too long',
    'Shift too long; Too many consecutive hours',
    'Shift too long',
    'Shift too long; Too many consecutive hours',
    'Exceeding daily working hours',
    'Exceeding daily working hours; Too many consecutive hours',
    'Exceeding daily working hours; Shift too long',
    'Exceeding daily working hours; Shift too long; Too many consecutive hours',
    'Exceeding daily working hours; Shift too long',
    'Exceeding daily working hours; Shift too long; Too many consecutive hours',
    'Exceeding weekly working hours',
    'Exceeding weekly working hours',
    'Exceeding daily working hours',
    'Shift too long',
    'Too many consecutive hours'
]

dates = [{'start': '2018-03-30 00:00:00', 'end' : '2018-03-30 23:59:59'}]
dbs = ["Puffin"]
for db_i in range(0, len(dbs)):
    for d_i in range(0, (len(dates))):
        for jj in range(0, len(solutions)):
            getData(dates[d_i]['start'], dates[d_i]['end'], dbs[db_i])
            helper2.setTeacherHours(ev, pr)
            pr = sorted(pr, key=lambda k: k['hours'])
            _check(ev)
            
            t = _drivingTeachers(pr, c)
            r = _drivingRoutes(ev, cc)
            _assignDrivingRoutes(t, pr, r, ev, c, cc)
            
            helper2.setTeacherHours(ev, pr)
            pr = sorted(pr, key=lambda k: k['hours'])
            _check(ev)
            _assignRoutes(pr, ev, cc, c)
            
            helper2.setTeacherHours(ev, pr)
            pr = sorted(pr, key=lambda k: k['hours'])
            _check(ev)
            helper2.setTeacherHours(ev, pr)
            shuffle(pr)
            pr = sorted(pr, key=lambda k: k['hours'])
            shuffle(ev)
            ev = sorted(ev, key=lambda k: k['start'])
            shuffle(pm)
            
            _initialAssignment(pm, ev, cc, c, solutions[jj])
            helper2.setTeacherHours(ev, pr)
            shuffle(pr)
            pr = sorted(pr, key=lambda k: k['hours'])
            shuffle(ev)
            ev = sorted(ev, key=lambda k: k['start'], reverse=True)
            
            _initialAssignment(pr, ev, cc, c, solutions[jj])
            helper2.setTeacherHours(ev, pr)
            pr = sorted(pr, key=lambda k: k['hours'])
            _check(ev)
            
            _swapForAbility(pr, ev, cc, c, solutions[jj])
            _initialAssignment(pr, ev, cc, c, solutions[jj])
            i = 0
            
            while i < 50:
                    _reassign(pr, ev, cc, c, solutions[jj])
                    helper2.setTeacherHours(ev, pr)
                    pr = sorted(pr, key=lambda k: k['hours'])
                    i += 1

        conn = pymssql.connect(helper2.servConnect.server, helper2.servConnect.user, helper2.servConnect.password, dbs[db_i])
        cursor = conn.cursor()
        l = list()
        for i in range(0, len(ev)):
                l.append((ev[i]['teacherId'], ev[i]['id']))
        cursor.executemany("UPDATE Eventos SET numIdProfesor = %d WHERE numIdEvento = %d", l)
        conn.commit()
