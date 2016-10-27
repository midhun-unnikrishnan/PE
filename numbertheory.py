# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 22:53:41 2016

@author: midhununnikrishnan
"""
import numpy as np
import combinatorics as cb
        
def sumofdigits(G,k=1)->int:
    """find + of digits
    """
    su = 0
    while G > 0:
        if k == 1:
            su += (G%10)
        else:
            su += (G%10)**k
        G //=10
    return su    
 
_mrpt_num_trials = 10 # number of bases to test
 
def is_probable_prime(n,numtrials=10):
    """
    Miller-Rabin primality test. CODE PLAGIARIZED!!!! 
    minor modification of the code in:
    https://rosettacode.org/wiki/Miller%E2%80%93Rabin_primality_test#Python
 
    A return value of False means n is certainly not prime. A return value of
    True means n is very likely a prime.
     """
    _mrpt_num_trials = numtrials
    assert n >= 2
    # special case 2,3
    if n == 2 or n == 3:
        return True
    # ensure n is odd
    if n % 2 == 0:
        return False
    su = 0
    t = n
    while t>0:
        su += t%10
        t//=10
    if su%3==0:
        return False
    # write n-1 as 2**s * d
    # repeatedly try to divide n-1 by 2
    s = 0
    d = n-1
    while True:
        quotient, remainder = divmod(d, 2)
        if remainder == 1:
            break
        s += 1
        d = quotient
    assert(2**s * d == n-1)
 
    # test the base a to see whether it is a witness for the compositeness of n
    def try_composite(a):
        if pow(a, d, n) == 1:
            return False
        for i in range(s):
            if pow(a, 2**i * d, n) == n-1:
                return False
        return True # n is definitely composite
 
    for i in range(_mrpt_num_trials):
        a = np.random.randint(2,n)
        if try_composite(a):
            return False
 
    return True # no base tested showed n as composite

def sieve(lessthan:int=-1,numprimes:int=-1):
    """list of prime numbers using a simple Eratosthenes sieve
       numprimes := the number of consecutive primes from 2 to be computed
       lessthan := strict upper bound on the largest prime to be computed
       If both numprimes and lessthan are specified, lessthan is given
       precedence
    """
    if numprimes < 1 and lessthan < 3:
        raise Exception('invalid specifications')
    if lessthan > 1e18: # your computer can easily crash for less
        raise Exception('are you trying to crash your computer?') 
        
    q = np.zeros(lessthan+1)
    for j in range(2,(lessthan+1)//2):
        if q[j] == 0:
            for k in range(2,1+(lessthan-1)//j):
                q[int(k*j)] = 1
    primes = [x for x in range(2,lessthan) if q[x]==0]
    return primes

def isprime(N:int)->bool:
    """primality test
    """
    if N > 1 and all( N%j for j in range(2,1+int(np.sqrt(N)))):
        return True
    else:
        return False

def PrimeFactors(N):
    d = 2
    factors = []
    while N > 1:
        if N % d == 0:
            i=0
            while N % d == 0:
                N /= d
                i+=1
            factors.append((d,i))
        d+=1
        if d*d > N:
            if N > 1:
                factors.append((int(N),1))
            break
    return factors
    
class assistedPF:
    """ facility to efficiently factorize where multiple factorizations
        require to be done in sequence
    """
       
    __Numprimes = 10
    __sieve = []
    __nbool = []
    def __init__(self,N):
        self.__Numprimes = N
        self.__sieve = sieve(N)
        self.__nbool = [False]*N
        for i in self.__sieve:
            self.__nbool[i] = True

    def factorize(self,N):    
        """ factorize w.r.t the primes constructed - prime factors p for
            p > N are not captured
        """
        pfs = []
        if self.__nbool[N]:
            return [(N,1)]
        for d in self.__sieve:
            i = 0
            while N%d == 0:
                i += 1
                N //= d
            if i>0:
               pfs.append((d,i)) 
            if d > N:
                break
        return pfs
        
def factorcombine(factors):
    prod = 1
    for x in factors:
        prod *= x[0]**x[1]
    return prod
    
def sumofFactors(N:int)->int:
    """ finds the sum of all proper divisors of N
    """
    pf = PrimeFactors(N)
    prod = 1
    for q in pf:
        prod *= (q[0]**(q[1]+1)-1)//(q[0]-1)
    return prod-N
    
def gcd(a:int,b:int)->int:
    """ Euclid's algorithm for GCD of two integers
    """
    if a<=0 or b<=0:
        raise Exception('only positive integers as input to gcd')
    while True:
        if a==b:
        
            return a
        elif b==1 or a==1:
            return 1
        elif a>b:
            b = a-b
            a = a-b
        else:
            b = b-a
            a = b+a

def coprime(N):
    """ Cheap generator to iterate across all coprime pairs of integers
        ordered by the product of the pair.
        Generates only pairs comprised of numbers whose product is below N.
    """ 
    F = assistedPF(N)
    for i in range(1,N):
        P = F.factorize(i)
        for j in range(2**len(P)):
            bits = cb.int2list(2**len(P)+j,2)[1:]
            f1 = factorcombine([P[x] for x in range(len(P)) if bits[x]==0])
            f2 = factorcombine([P[x] for x in range(len(P)) if bits[x]==1])
            yield (f1,f2)
        

def sqrtiter(N):
    """ generates an infinite iterator for the continued fraction 
        coefficients of \sqrt{N}. i.e., ${a_0,a_1,a_2...}$ is yielded
        by this iterator where
        \sqrt{N} = a_0 + \frac{1}{a_1 + \frac{1}{a_2 + \dots}}
    """
    b,c = 0,1
    sqrt = np.sqrt(N)
    if int(sqrt)==sqrt:
        return 0
    history = []
    a = int((b+sqrt)/c)
    yield a
    while True:
        history.append((a,b,c))
        b = c*a - b
        c = (N - b**2)/c
        assert int(c) == c
        assert c>0
        a = int((b+sqrt)/c)
        yield a

