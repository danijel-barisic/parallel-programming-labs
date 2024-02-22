import math
import numpy as np
from numba import cuda

N = 20000

@cuda.jit
def calculate_distances(x, y, distances):
    i, j = cuda.grid(2)
    
    if i < N and j < N and i < j:
        xi = x[i]
        yi = y[i]
        xj = x[j]
        yj = y[j]
        dx = xi - xj
        dy = yi - yj
        distance = math.sqrt(dx*dx + dy*dy)
        distances[i, j] = distance

def main():
    x = np.random.random(N).astype(np.float32)
    y = np.random.random(N).astype(np.float32)
    distances = np.zeros((N, N), dtype=np.float32)
    
    threads_per_block = (16, 16)
    blocks_per_grid = (
        (N + threads_per_block[0] - 1) // threads_per_block[0],
        (N + threads_per_block[1] - 1) // threads_per_block[1]
    )
    
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_distances = cuda.to_device(distances)
    
    calculate_distances[blocks_per_grid, threads_per_block](d_x, d_y, d_distances)
    
    d_distances.copy_to_host(distances)
    
    sum_distances = np.sum(distances)
    num_distances = N * (N - 1) // 2
    average_distance = sum_distances / num_distances
    
    print("Prosjek udaljenosti:", average_distance)

if __name__ == '__main__':
    main()
