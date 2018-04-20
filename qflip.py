
import math
import numpy as np
import numpy.linalg as la
import quorsum as Q

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
            self.q = list(q)
        except(TypeError):
            self.q=[q]
        try:
            self.p = list(p)
        except(TypeError):
            self.p=[p]
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
        working_flist = list(self.flipped_tiles)
        for i in range(len(flist)+1):
            if i>0:
                working_list[working_flist[0]-1].flip()
                del working_flist[0]
            for p in range(indices[i],indices[i+1]):
                self.all_states.append(state(p,working_list))
                print map(str,working_list), map(str,self.all_states[0].q)
                for b in range(1,ncolors**(len(flist)-i)):
                    copied_wlist = list(working_list)
                    for r, f in enumerate(working_flist):
                        print b, r, f
                        if (b/(2**r))%2==1: 
                            print 'flipped', f
                            copied_wlist[f-1].flip()
                    self.all_states.append(state(p,copied_wlist))

