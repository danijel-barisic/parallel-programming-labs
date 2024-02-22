from mpi4py import MPI
import random
import time
import numpy as np

NO_FORK = 0
DIRTY_FORK = 1
DIRTY_FORK_SENDABLE = np.array(DIRTY_FORK)
CLEAN_FORK = 2
CLEAN_FORK_SENDABLE = np.array(CLEAN_FORK)
WANT_FORK = 3
WANT_FORK_SENDABLE = np.array(WANT_FORK)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

left_neighbour = (rank - 1) % size
right_neighbour = (rank + 1) % size

left_fork = DIRTY_FORK if rank == 0 else NO_FORK
right_fork = NO_FORK if rank == size - 1 else DIRTY_FORK

left_requires = False
right_requires = False

fork_letter_map = {DIRTY_FORK: "P", CLEAN_FORK: "C", NO_FORK: "-", }


def print_state(state_message):
    fork_state = fork_letter_map[left_fork] + fork_letter_map[right_fork]
    print("\t" * rank + state_message + "(" + fork_state + ")", flush=True)


def request_forks():
    global left_requires
    global right_requires
    global left_fork
    global right_fork
    global left_neighbour
    global right_neighbour

    print_state("GLA") # zahtjev za vilicama, gladan filozof
    comm.Send(WANT_FORK_SENDABLE, dest=left_neighbour)
    comm.Send(WANT_FORK_SENDABLE, dest=right_neighbour)

    while True:
        status = MPI.Status()
        while not comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status):
            if left_requires:
                if left_fork == DIRTY_FORK:
                    left_fork = NO_FORK
                    left_requires = False
                    comm.Send(CLEAN_FORK_SENDABLE, dest=left_neighbour)

            if right_requires:
                if right_fork == DIRTY_FORK:
                    right_fork = NO_FORK
                    right_requires = False
                    comm.Send(CLEAN_FORK_SENDABLE, dest=right_neighbour)

            time.sleep(1)

        message = np.empty(1, dtype=int)
        comm.Recv(buf=message, source=status.Get_source())

        if message[0] == DIRTY_FORK or message[0] == CLEAN_FORK:
            if status.Get_source() == left_neighbour:
                left_fork = message[0]
            if status.Get_source() == right_neighbour:
                right_fork = message[0]

            if left_fork in (DIRTY_FORK, CLEAN_FORK) and right_fork in (DIRTY_FORK, CLEAN_FORK):
                break

        elif message[0] == WANT_FORK:
            if status.Get_source() == left_neighbour:
                if left_fork == CLEAN_FORK or left_fork == NO_FORK:
                    left_requires = True
                elif left_fork == DIRTY_FORK:
                    left_fork = NO_FORK
                    comm.Send(CLEAN_FORK_SENDABLE, dest=left_neighbour)
            elif status.Get_source() == right_neighbour:
                if right_fork == CLEAN_FORK or right_fork == NO_FORK:
                    right_requires = True
                elif right_fork == DIRTY_FORK:
                    right_fork = NO_FORK
                    comm.Send(CLEAN_FORK_SENDABLE, dest=right_neighbour)


def think():
    global left_requires
    global right_requires
    global left_fork
    global right_fork
    global left_neighbour
    global right_neighbour

    print_state("MIS")
    sleep_time = random.randint(1, 3)
    for i in range(0, sleep_time):
        # time.sleep(random.uniform(0, 1))
        status = MPI.Status()

        if comm.Iprobe(status=status):
            message = np.empty(1, dtype=int)
            comm.Recv(message)

            if message[0] == WANT_FORK:
                if status.Get_source() == left_neighbour:
                    if left_fork == CLEAN_FORK or left_fork == NO_FORK:
                        left_requires = True
                    elif left_fork == DIRTY_FORK:
                        left_fork = NO_FORK
                        comm.Send(CLEAN_FORK_SENDABLE, dest=left_neighbour)
                elif status.Get_source() == right_neighbour:
                    if right_fork == CLEAN_FORK or right_fork == NO_FORK:
                        right_requires = True
                    elif right_fork == DIRTY_FORK:
                        right_fork = NO_FORK
                        comm.Send(CLEAN_FORK_SENDABLE, dest=right_neighbour)
            else:
                if message[0] == CLEAN_FORK or message[0] == DIRTY_FORK:
                    if status.Get_source() == left_neighbour:
                        left_fork=message[0]
                    elif status.Get_source() == right_neighbour:
                        right_fork=message[0]
        time.sleep(1)


def eat():
    global left_requires
    global right_requires
    global left_fork
    global right_fork
    global left_neighbour
    global right_neighbour

    print_state("JED") # pocinje jest
    time.sleep(random.randint(1, 3))
    left_fork = DIRTY_FORK
    right_fork = DIRTY_FORK
    if left_requires:
        left_fork = NO_FORK
        left_requires = False
        comm.Send(CLEAN_FORK_SENDABLE, dest=left_neighbour)
    elif right_fork:
        right_fork = NO_FORK
        right_requires = False
        comm.Send(CLEAN_FORK_SENDABLE, dest=right_neighbour)

while True:
    think()
    request_forks()
    eat()

MPI.Finalize()
