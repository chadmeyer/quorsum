import math
import numpy as np
from numpy.linalg import inv, matrix_power

def prob_success_dice(d,t): # paper s(d,t) eqn 1
   return 1-((t-1)/6.0)**d

def ncr(n,r):
   return math.factorial(n)/(math.factorial(r)*math.factorial(n-r))

def prob_k_dice_surviving_a_roll(k,d,t): # paper s_k(d,t) eqn 2
   return ncr(d,k)*(prob_success_dice(1,t))**k*(1-prob_success_dice(1,t))**(d-k)

def prob_making_at_least_j_steps(j,d1,t): #eqn 3, \hat{q}_j
   try:
      l = len(t)
   except(TypeError):
      l = 1
   if j > l: return 0
   if j == 0: return 1
   qjhat = 0
   for d in all_dice(d1,j):
      sub = prob_success_dice(d[j-1],t[j-1])
      for m in range(j-1):
         sub=sub*prob_k_dice_surviving_a_roll(d[m+1],d[m],t[m])
      qjhat=qjhat+sub
   return qjhat

def prob_making_exactly_j_steps(j,d1,t): #eqn 4 q_j
   return prob_making_at_least_j_steps(j,d1,t)-prob_making_at_least_j_steps(j+1,d1,t)

def prob_starting_on_i_ending_on_j(i,j,d1,t): # eqn 5 q_{ij}
   tnew = list(t)
   for n in range(i):
      tnew[n] = 1
   return prob_making_exactly_j_steps(j,d1,tnew)

def multiflip_prob(t,l,qi,qj,df):
    l = len(t)
    n = len(l)+1
    if len(qi) != n-1 or len(qj) != n-1 or len(df) != n=1:
        raise ValueError('Arguments l,qi,qj and df must be lists of the same length')
    p=1
    for r,lr in enumerate l:
        pr = prob_success_dice(df[r],t[l[r]-1])
        if qi[r] == qj[r]:
            pr = 1.0-pr
        p = p * pr
    return p

def transition_matrix(t,d1=4):
   l = len(t)
   tm = np.zeros((l+1,l+1))
   for i in range(l+1):
      for j in range(l+1):
         tm[i,j] = prob_starting_on_i_ending_on_j(i,j,d1,t)
   return tm


def transition_matrix_flip(t,l,d):
    pass

def turns_to_victory(t,i=0,d1=4):
   Q = transition_matrix(t,d1)
   QT = Q[:-1,:-1]
   l = len(t)
   s = inv(np.eye(l)-QT)
   ans = 0
   for n in range(i,l):
      ans = ans + s[i,n]
   return ans

def prob_of_completion_in_n_turns(t,n,d1=4):
   Q = transition_matrix(t,d1)
   Qp = matrix_power(Q,n)
   return Qp[0,-1]
   
def prob_flip_move(dt,dm,t):
    return prob_success_dice(dt,t)*prob_success_dice(dm,t)

class all_dice(object):
   def __init__(self,d1,j):
      self.j = j
      self.d1 = d1
      self.successful_rolls=[]
      for i in range(j):
         self.successful_rolls.append(d1)
      self.first = True
   def __iter__(self):
      return self
   def next(self):
      return self.__next__()
   def __next__(self):
      if self.first is True:
         self.first = False
         return self.successful_rolls
      carry = 1
      for i in range(self.j-1):
         n = self.successful_rolls[-(i+1)]
         if carry == 1:
            if n == 1:
               carry = 1
            else:
               new_roll = self.successful_rolls[-(i+1)] - 1
               for j in range(i+1):
                  self.successful_rolls[-(j+1)]=new_roll
               carry = 0
         else: break
      if carry == 1:
         raise StopIteration
      else:
         return self.successful_rolls

