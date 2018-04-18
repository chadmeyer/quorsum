import math
import numpy as np

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
   qjhat = 0
   for d in all_dice(d1,j):
      sub = prob_success_dice(d[j-1],t[j-1])
      for m in range(j-1):
         sub=sub*prob_k_dice_surviving_a_roll(d[m+1],d[m],t[m])
      qjhat=qjhat+sub
   return qjhat

def prob_making_exactly_j_steps(j,d1,t):
   return prob_making_at_least_j_steps(j,d1,t)-prob_making_at_least_j_steps(j+1,d1,t)



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

