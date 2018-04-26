
import math
import numpy as np
import numpy.linalg as la
import quorsum as Q
import copy

class spath(object):
    """ A 'single' path, for which the pawn must go """
    def __init__(self,t):
        self.t = t
        try:
            self.l = len(t)
        except(TypeError):
            self.l=1
            self.t=[t]
    def __len__(self):
        return self.l
    def __getitem__(self,k):
        return self.t[k]
    def __setitem__(self,k,v):
        self.t[k]=v

class excursion(object):
    """ an alternate path to go from istart to iend """
    def __init__(self,istart,iend,t):
        pass

class cstate(object):
    """ A color state object
    In a full game of quorsum there are 4 possible states of any tile, black
    or white; locked or not.  This could most easily be encoded as a binary
    number: 00, 01, 10, 11 where the "ones" bit is color and the "twos bit"
    is the lock.  Now, for simplified analysis, we will only consider ns states
    which could be 1->4.  
    1 means all the same color, no chance of flipping
    2 means some could be flipped but we are ignoring the locking mechanism
    3 means that we include the possibility of a tile being flipped and locked
       The 1 color in this case should be the pawn
    4 All dynamics included """
    def __init__(self,b):
        self.b = b
        if b < 0 or b > 4: 
            raise ValueError("The value of b = "+str(b)+" is out of range")
    def color(self):
        return self.b%2
    def lock_state(self):
        return self.b/2
    def locked(self):
        if self.lock_state() == 1:
            return True
        else:
            return False
    def flip(self,check=True):
        if check and self.locked():
            raise RuntimeError("Can't flip a locked state")
        self.b=(self.color()+1)%2+2*self.lock_state()
    def lock(self,check=True):
        if check and self.locked():
            raise RuntimeError("Can't lock a locked state")
        if not self.locked(): self.b=(self.b+2)
    def __str__(self):
        return str(self.b)

class pawn(object):
    def __init__(self,color=1,player=0,target=None):
        self.color = color
        self.player = player
        self.target = None

class state(object):
    def __init__(self,p,q):
        try:
            self.q = copy.deepcopy(q)
            self.q = list(self.q)
        except(TypeError):
            self.q=[copy.copy(q)]
        try:
            self.p = list(p)
        except(TypeError):
            self.p=[copy.copy(p)]
        self.l = len(self.q)
        self.np = len(self.p)
    def __str__(self):
        return 'P: '+str(self.p)+' Q: '+str(map(str,self.q))

class single_path_problem(object):
    def __init__(self,sp,flist,ncolors=2):
        if isinstance(sp,spath):
            self.path = sp
        else:
            self.path = spath(sp)
        self.color = 1
        self.flipped_tiles=flist
        self.flipped_tiles.sort()
        working_list = []
        for i in range(self.path.l):
            working_list.append(cstate(self.color))
        for i in flist:
            working_list[i-1].flip()
        indices = [0]+self.flipped_tiles+[len(self.path)+1]
        self.all_states=[]
        working_flist = copy.deepcopy(self.flipped_tiles)
        for i in range(len(flist)+1):
            if i>0:
                working_list[working_flist[0]-1].flip()
                del working_flist[0]
            for p in range(indices[i],indices[i+1]):
                self.all_states.append(state(p,working_list))
                for b in range(1,ncolors**(len(flist)-i)):
                    copied_wlist = copy.deepcopy(working_list)
                    for r, f in enumerate(working_flist):
                        if (b/(2**r))%2==1: 
                            copied_wlist[f-1].flip()
                    self.all_states.append(state(p,copied_wlist))
        self.ns = len(self.all_states)
    def transition_matrix(self,strat):
        ns = self.ns
        tm = np.zeros((ns,ns))
        for i in range(ns):
            for j in range(ns):
                dice = strat.dice_choices(self.all_states[i],self.path)
                tm[i,j] = 1.0
                for k in range(self.path.l):
                    tm[i,j] = tm[i,j]*prob_transition_tile(dice[1][k],self.path[k],self.all_states[i].q[k],self.all_states[j].q[k])
                if dice[0][0] > 0: 
                    tm[i,j]=tm[i,j]*Q.p_j_steps(self.all_states[j].p[0],dice[0][0],mod_p(self.path,self.all_states[i].p[0],self.all_states[j]))
                elif self.all_states[i].p != self.all_states[j].p: tm[i,j]=0
        return tm
                
def mod_p(path,p,state):
    modpath = copy.deepcopy(path)
    for i, qi in enumerate(state.q):
        if i < p: 
            modpath[i] = 1
        elif qi.color() == 0:
            modpath[i] = 7
    return modpath

class strategy(object):
    def __init__(self):
        pass
    def dice_choices(self,state,path):
        toflip = []
        for i,t in enumerate(state.q):
            if t.color() == 0 and (not t.locked()):  toflip.append(i)
        if len(toflip) == 0:
           return [[4],[0]*state.l]
        elif len(toflip) == 1:
           df = [0]*state.l
           df[toflip[0]] = 2
           return [[2],df]
        elif len(toflip) == 2:
           df = [0]*state.l
           df[toflip[0]] = 2
           df[toflip[1]] = 1
           return [[1],df]
        else:
           df = [0]*state.l
           df[toflip[0]] = 2
           df[toflip[1]] = 2
           return [[0],df]

class flipandroll4(strategy):
    def dice_choices(self,state,path):
        df = [0]*state.l
        p = min(state.p[0],state.l-1) # should guard against the l,l matrix element
        if state.q[p].color() == 0:
            df[state.p[0]] = 4
            return [[0],df]
        else:
            return [[4],df]
           
class flipandroll2(strategy):
    def dice_choices(self,state,path):
        df = [0]*state.l
        toflip = []
        for i,t in enumerate(state.q):
            if t.color() == 0 and (not t.locked()):  toflip.append(i)
        if len(toflip) == 0:
           return [[4],df]
        else:
           df[toflip[0]] = 2
           return [[2],df]

def prob_transition_tile(d,t,q1,q2):
    if q1.locked():
        if q2.b == q1.b - 2:
            return 1.0
        else:
            return 0.0
    else:
        p = Q.p_win(d,t)
        if q1.color() == q2.color():
           return 1-p
        else: return p

def moments_of_absorption(tm):
    tmt = tm[:-1,:-1]
    l = tmt.shape[0]
    N = la.inv(np.eye(l)-tmt)
    t1 = np.sum(N[0,:])
    t2 = np.sum(np.matmul(2*N-np.eye(l),N)[0,:])
    t3 = np.sum(np.matmul(6*la.matrix_power(N,2)-6*N+np.eye(l),N)[0,:])
    t4 = np.sum(np.matmul(24*la.matrix_power(N,3)-36*la.matrix_power(N,2)+14*N-np.eye(l),N)[0,:])
    sigma = np.sqrt(t2)
    gamma = t3/t2**1.5
    kurt  = t4/t2**2-3
    return t1, sigma, gamma, kurt
