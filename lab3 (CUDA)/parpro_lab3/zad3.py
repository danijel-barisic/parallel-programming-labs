import sys
import math
import time
from numba import cuda
import numpy as np


@cuda.jit
def boundarypsi_kernel(psi, m, b, h, w):
    i, j = cuda.grid(2)

    if b + 1 <= i <= b + w - 1:
        psi[i, 0] = float(i - b)
    elif i >= b + w:
        psi[i, 0] = float(w)

    if j <= h:
        psi[m + 1, j] = float(w)
    elif h + 1 <= j <= h + w - 1:
        psi[m + 1, j] = float(w - j + h)

@cuda.jit
def jacobistep_kernel(psinew, psi, m, n):
    i, j = cuda.grid(2)
    if i <= m and j <= n:
        psinew[i, j] = (psi[i - 1, j] + psi[i + 1, j] + psi[i, j - 1] + psi[i, j + 1]) * 0.25

@cuda.jit
def copy_array_kernel(psinew, psi):
    i, j = cuda.grid(2)
    psi[i, j] = psinew[i, j]

def compute_error(psitmp, psi, m, n, bnorm):
    error = np.sqrt(np.sum((psitmp[1:m+1, 1:n+1] - psi[1:m+1, 1:n+1]) ** 2))
    error = error / bnorm[0]
    return error

def run_cfd(scalefactor, numiter):
    bbase = 10
    hbase = 15
    wbase = 5
    mbase = 32
    nbase = 32

    b = bbase * scalefactor
    h = hbase * scalefactor
    w = wbase * scalefactor
    m = mbase * scalefactor
    n = nbase * scalefactor

    psi = np.zeros((m + 2, n + 2))
    psinew = np.zeros_like(psi)
    bnorm = np.zeros(1)

    threadsperblock = (16, 16)
    blockspergrid_m = (m + threadsperblock[0] - 1) // threadsperblock[0]
    blockspergrid_n = (n + threadsperblock[1] - 1) // threadsperblock[1]
    blockspergrid = (blockspergrid_m, blockspergrid_n)
    
    boundarypsi_kernel[blockspergrid, threadsperblock](psi, np.int32(m),  np.int32(b), np.int32(h), np.int32(w))

    bnorm[0] = math.sqrt(np.sum(psi ** 2))

    tstart = time.time()

    for iter in range(1, numiter + 1):
        jacobistep_kernel[blockspergrid, threadsperblock](psinew, psi, np.int32(m), np.int32(n))
        error = compute_error(psinew, psi, m, n, bnorm)

        if error < tolerance:
            print("Converged on iteration", iter)
            break

        copy_array_kernel[blockspergrid, threadsperblock](psinew, psi)

        if iter % printfreq == 0:
            print("Completed iteration", iter, "error =", error)

    if iter > numiter:
        iter = numiter

    tstop = time.time()
    ttot = tstop - tstart
    titer = ttot / iter

    print("\n... finished")
    print("After", iter, "iterations, the error is", error)
    print("Time for", iter, "iterations was", ttot, "seconds")
    print("Each iteration took", titer, "seconds")


if len(sys.argv) != 3:
    print("Usage: program <scalefactor> <numiter>")
    sys.exit(1)

scalefactor = int(sys.argv[1])
numiter = int(sys.argv[2])
tolerance = 0.0
printfreq = 50

run_cfd(scalefactor, numiter)
