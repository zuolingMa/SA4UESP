# -*- coding: cp936 -*-
import openpyxl
import math
import random
import copy

def create_cij(stu_file,crs_file):
    '''
    read datas from file and create the conflict matrix
    input stu_file and crs_file
    output cij
    '''
    global m,n
    m=0
    n=0
    for line in open(stu_file,"r"):
        m+=1    #count the number of students
    for line in open(crs_file,"r"):
        n+=1    #count the number of exams
    #store datas into stus[]
    stus = []
    fileHandle = open(stu_file,"r")
    new = []
    for i in range(m):
        everystu = fileHandle.readline().split(" ")
        for j in everystu:
            if(j=='\n'):
                continue
            new.append(int(j))
        stus.append(new)
        new = []
    #create cij
    cij = [[0 for col in range(n)] for row in range(n)]
    for row in range(m):
        for i in stus[row]:
            for j in stus[row]:
                cij[i-1][j-1]+=1
    return cij

def mark_hardest(exam_list,s_initial,cij):
    '''
    mark the most conflicting exam while compute the initial timetable
    the most conflicting means it has the minimal available timeslots
    input exam_list and timeslots and cij
    output the location of hardest exam in exam_list
    '''
    #create available_list to count the number of available timeslots for each exam
    available_list = [0 for i in range(n)]
    minimun = 999
    location = 0
    for i in range(n):
        if exam_list[i]!=-1: #已经分配的考试没有必要再计算可分配时隙
            continue
        for j in s_initial: 
            if j==[]: #对于目前的时间表【】可用
                available_list[i]+=1
                continue
            available = True
            for k in j: #全部不冲突可用
                if cij[i][k]!=0: #只要有一个冲突，就不可用
                    available = False
                    break
            if available:
                available_list[i]+=1             
        if available_list[i]<minimun:
            minimun=available_list[i]
            location = i
    if minimun==0:
        location = -1
    return location

def check_feasibility(timetable,cij):
    '''
    check the feasibility of the timetable
    '''
    for i in timetable:
        for j in i:
            for k in i:
                if j==k:
                    continue
                if cij[j][k]!=0:
                    print 'this timetable is infeasible'
                    return False
    print 'this timetable is feasible'
    return True

def evaluate(timetable,cij):
    timeslots = len(timetable)
    score = 0
    for i in range(timeslots):
        p = 16
        for j in timetable[i+1:i+6]:
            for x in timetable[i]:
                for y in j:
                    if cij[x][y] != 0:
                        score += cij[x][y]*p
            p = p/2
    score = score/float(m)
    return score

def contact_score(timetable,cij,t1,t2,que1,que2):
    score = 0
    for i in que1:
        p = 16
        for x in range(5):
            t = t1-x-1
            if t<0:
                continue
            for j in timetable[t]:
                if cij[i][j] != 0:
                    score += cij[i][j]*p
            p = p/2
        p = 16
        for t in timetable[t1+1:t1+6]:
            for j in t:
                if cij[i][j] != 0:
                    score += cij[i][j]*p
            p = p/2
    for i in que2:
        p = 16
        for x in range(5):
            t = t2-x-1
            if t<0:
                continue
            for j in timetable[t]:
                if cij[i][j] != 0:
                    score += cij[i][j]*p
            p = p/2
        p = 16
        for t in timetable[t2+1:t2+6]:
            for j in t:
                if cij[i][j] != 0:
                    score += cij[i][j]*p
            p = p/2
    score = score/float(m)
    return score
            
    
def n1(s,cij):
    '''
    Kempe chain
    '''
    timetable = copy.deepcopy(s)
    deviation = 0
    t = len(timetable)
    t1 = random.randint(0,t-1)
    while timetable[t1] == []:
        t1 = random.randint(0,t-1)
    t2 = random.randint(0,t-1)
    while(t1 == t2):
        t2 = random.randint(0,t-1)
    que1 = []
    que2 = []
    p1 = 0
    p2 = 0
    e = random.choice(timetable[t1])
    que1.append(e)
    while(p1<len(que1) or p2<len(que2)):
        while(p1<len(que1)):
            for i in que1[p1:]:
                for j in timetable[t2]:
                    if cij[i][j] == 0:
                        continue
                    if j in que2:
                        continue
                    que2.append(j)
                p1 += 1
        while(p2<len(que2)):
            for i in que2[p2:]:
                for j in timetable[t1]:
                    if cij[i][j] == 0:
                        continue
                    if j in que1:
                        continue
                    que1.append(j)
                p2 += 1

    deviation -= contact_score(timetable,cij,t1,t2,que1,que2)

    for i in que1:
        timetable[t1].remove(i)
    for i in que2:
        timetable[t2].remove(i)
    timetable[t1].extend(que2)
    timetable[t2].extend(que1)
    
    deviation += contact_score(timetable,cij,t2,t1,que1,que2)
    return timetable,deviation

def n2(s,cij):
    '''
    Exam shifting
    '''
    timetable = copy.deepcopy(s)
    deviation = 0
    tlist = []
    for i in range(len(timetable)):
        tlist.append(i)
    random.shuffle(tlist)
    for t in tlist:
        if timetable[t] == []:
            continue
        elist = timetable[t][:]
        random.shuffle(elist)
        ttlist = tlist[:]
        ttlist.remove(t)
        random.shuffle(ttlist)
        for e1 in elist:
            conflict = False
            for tt in ttlist:
                for e2 in timetable[tt]:
                    if cij[e1][e2] != 0:
                        conflict = True
                        break
                if not conflict:
                    que1 = [e1]
                    que2 = []
                    deviation -= contact_score(timetable,cij,t,tt,que1,que2)
                    timetable[t].remove(e1)
                    timetable[tt].append(e1)
                    deviation += contact_score(timetable,cij,tt,t,que1,que2)
                    return timetable,deviation
    return timetable,deviation

def n3(s,cij):
    '''
    Timeslots interchange
    '''
    timetable = copy.deepcopy(s)
    deviation = 0
    t = len(timetable)
    t1 = random.randint(0,t-1)
    t2 = random.randint(0,t-1)
    while(t1 == t2):
        t2 = random.randint(0,t-1)
    deviation -= contact_score(timetable,cij,t1,t2,timetable[t1],timetable[t2])
    temp = timetable[t1]
    timetable[t1] = timetable[t2]
    timetable[t2] = temp
    deviation += contact_score(timetable,cij,t1,t2,timetable[t1],timetable[t2])
    return timetable,deviation

def collecting_datas():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'SA4UESP_results'








    
