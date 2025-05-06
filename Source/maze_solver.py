import maze_state as ms
import heapq
import tracemalloc
from memory_profiler import memory_usage
import time
from abc import ABC, abstractmethod
from collections import deque

# Abstract class
class MazeSolver(ABC):
    def __init__(self, initial_state: ms.MazeState):
        self.initial_state = initial_state
        self.compress_initial_state = ms.MazeStateCompress.from_original_maze_state(initial_state)
        self.time_consume = 0       # time consumed to solve the maze, in milliseconds (ms)
        self.memory_consume = 0     # peak memory consumed to solve the maze, in megabytes (MB)
        self.cost = 0               # the cost, in this case, the total weight pushed along the found path
        self.state_visited = 0      # number of states explored by the algorithm
        self.path = []              # list of states in the found path, in reverse order
        self.str_path = ''          # the string representation of the found path
    
    @classmethod
    def from_file(cls, file_path):
        maze_state = ms.MazeState.from_file(file_path)
        return cls(maze_state)
    
    @abstractmethod
    def solve_maze(self):
        pass

    def solve_and_track_memory(self):
        before = memory_usage()[0]
        res = memory_usage(self.solve_maze, interval=0.05, retval=True, max_usage=True, max_iterations=1)
        self.memory_consume = res[0] - before
        return res[1]
        
    
    @classmethod
    def from_maze_state(cls, state):
        return cls(state)
    
    @classmethod
    def str_step(cls, prev_state, current_state):
        # return the character represents the step from prev_state to current_state
        (cur_i, cur_j) = current_state.ares_position
        (prev_i, prev_j) = prev_state.ares_position
        if cur_i == prev_i:
            if cur_j == prev_j - 1:
                return 'L' if (cur_i, cur_j) in prev_state.stones_weight else 'l'
            elif cur_j == prev_j + 1:
                return 'R' if (cur_i, cur_j) in prev_state.stones_weight else 'r'
        elif cur_j == prev_j:
            if cur_i == prev_i - 1:
                return 'U' if (cur_i, cur_j) in prev_state.stones_weight else 'u'
            elif cur_i == prev_i + 1:
                return 'D' if (cur_i, cur_j) in prev_state.stones_weight else 'd'
        
        return '?' # should not reach here
    
    @classmethod
    def step_cost(cls, prev_state, current_state):
        # return the cost of 1-step moving from prev_state to current_state
        (i, j) = current_state.ares_position
        if (i, j) not in prev_state.stones_weight:
            return 0
        return prev_state.stones_weight[(i, j)] 
    
    # a state is deadlock if one or more stones 
    # are not on switches and cannot be moved by Ares
    # see deadlock patterns in deadlock_patterns.txt
    def is_deadlock(self, compress_state: ms.MazeStateCompress):
        for (i, j) in compress_state.stones_weight:
            if (i, j) in compress_state.switches_position:
                continue
            # pattern 1
            positions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
            for _ in range(0, 4):
                di_1, dj_1 = positions[_]
                di_2, dj_2 = positions[_ + 1]
                if (self.initial_state.grid[i + di_1][j + dj_1] == '#' 
                    and self.initial_state.grid[i + di_2][j +dj_2] == '#'):
                    return True
            
            # pattern 2
            positions = [(-1, 0), (-1,-1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
            for _ in range(0, 7, 2):
                di_1, dj_1 = positions[_]
                di_2, dj_2 = positions[_ + 1]
                di_3, dj_3 = positions[_ + 2]
                if (
                    (self.initial_state.grid[i + di_1][j + dj_1] == '#' 
                    or (i + di_1, j + dj_1) in compress_state.stones_weight)
                    and 
                    (self.initial_state.grid[i + di_2][j + dj_2] == '#' 
                    or (i + di_2, j + dj_2) in compress_state.stones_weight)
                    and 
                    (self.initial_state.grid[i + di_3][j + dj_3] == '#' 
                    or (i + di_3, j + dj_3) in compress_state.stones_weight)
                   ):
                    return True
                
            # pattern 3
            for (di_1, dj_1, di_2, dj_2, di_3, dj_3) in ((1, 1, 0, 1, -1, 0), 
                                                         (-1, 1, -1, 0, 0, -1),
                                                         (-1, -1, 0, -1, 1, 0),
                                                         (1, -1, 1, 0, 0, 1),
                                                         (0, 1, -1, 0, -1, -1),
                                                         (-1, 0, 0, -1, 1, -1),
                                                         (0, -1, 1, 0, 1, 1),
                                                         (1, 0, 0, 1, -1, 1)):
                if (self.initial_state.grid[i + di_1][j + dj_1] == '#'
                    and (i + di_2, j + dj_2) in compress_state.stones_weight
                    and self.initial_state.grid[i + di_3][j + dj_3] == '#'):
                    return True
            
            # pattern 4
            for (di_1, dj_1, di_2, dj_2, di_3, dj_3, di_4, dj_4) in ((1, 1, 0, 1, -1, 0, -1, -1),
                                                                     (-1, 1, -1, 0, 0, -1, 1, -1),
                                                                     (-1, -1, 0, -1, 1, 0, 1, 1),
                                                                     (1, -1, 1, 0, 0, 1, -1, 1)):
                if ((i + di_2, j + dj_2) in compress_state.stones_weight
                    and (i + di_3, j + dj_3) in compress_state.stones_weight
                    and self.initial_state.grid[i + di_1][j + dj_1] == '#'
                    and self.initial_state.grid[i + di_4][j + dj_4] == '#'):
                    return True
                 
        return False
    

# MazeSolver class using BFS algorithm
class MazeSolverBFS(MazeSolver):
    def __init__(self, initial_state):
        super().__init__(initial_state)
    
    def solve_maze(self):
        start_time = time.time()
        self.cost = 0
        self.path = []
        self.str_path = ''
        self.state_visited = 1

        if self.initial_state.is_goal_state():
            self.path = [self.initial_state]
            self.time_consume = (time.time() - start_time) * 1000
            return True

        trace = {self.compress_initial_state: None}
        visited = {self.compress_initial_state}
        q = deque()
        q.append(self.compress_initial_state)

        def trace_back(state: ms.MazeStateCompress):
            while state in trace:
                self.path.append(state.decompress(self.initial_state))
                if trace[state] != None:
                    self.str_path = MazeSolver.str_step(trace[state], state) + self.str_path
                    self.cost = self.cost + MazeSolver.step_cost(trace[state], state)
                state = trace[state]
        
        while q:
            state = q.popleft()
            if self.is_deadlock(state):
                continue
            for (check, move) in [(state.can_move_up, state.move_up), 
                                  (state.can_move_left, state.move_left), 
                                  (state.can_move_down, state.move_down), 
                                  (state.can_move_right, state.move_right)]:
                if not check(self.initial_state):
                    continue
                new_state = move()
                if new_state not in visited:
                    self.state_visited += 1
                    trace[new_state] = state
                    if new_state.is_goal_state():
                        trace_back(new_state)
                        self.time_consume = (time.time() - start_time) * 1000
                        return True
                    visited.add(new_state)
                    q.append(new_state)

        self.time_consume = (time.time() - start_time) * 1000
        return False

# MazeSolver class using DFS algorithm
class MazeSolverDFS(MazeSolver):
    def __init__(self, initial_state):
        super().__init__(initial_state)
    
    def solve_maze(self):
        start_time = time.time()
        self.cost = 0
        self.path = []
        self.str_path = ''
        self.state_visited = 1

        if self.initial_state.is_goal_state():
            self.path = [self.initial_state]
            self.time_consume = (time.time() - start_time) * 1000
            return True
        
        trace = {self.compress_initial_state: None}
        visited = {self.compress_initial_state}
        q = deque()
        q.append(self.compress_initial_state)

        def trace_back(state: ms.MazeStateCompress):
            while state in trace:
                self.path.append(state.decompress(self.initial_state))
                if trace[state] != None:
                    self.str_path = MazeSolver.str_step(trace[state], state) + self.str_path
                    self.cost = self.cost + MazeSolver.step_cost(trace[state], state)
                state = trace[state]
        
        while q:
            state = q.pop()
            if self.is_deadlock(state):
                continue
            for (check, move) in [(state.can_move_up, state.move_up), 
                                  (state.can_move_left, state.move_left), 
                                  (state.can_move_down, state.move_down), 
                                  (state.can_move_right, state.move_right)]:
                if not check(self.initial_state):
                    continue
                new_state = move()
                if new_state not in visited:
                    self.state_visited += 1
                    trace[new_state] = state
                    if new_state.is_goal_state():
                        trace_back(new_state)
                        self.time_consume = (time.time() - start_time) * 1000
                        return True
                    visited.add(new_state)
                    q.append(new_state)

        self.time_consume = (time.time() - start_time) * 1000
        return False

# MazeSolver class using UCS algorithm
class MazeSolverUCS(MazeSolver):
    def __init__(self, initial_state):
        super().__init__(initial_state)
    
    def solve_maze(self):
        start_time = time.time()
        self.cost = 0
        self.path = []
        self.str_path = ''
        self.state_visited = 0

        trace = {}
        visited = set()
        pq = []

        def trace_back(state: ms.MazeStateCompress):
            while state in trace:
                self.path.append(state.decompress(self.initial_state))
                if trace[state] != None:
                    self.str_path = MazeSolver.str_step(trace[state], state) + self.str_path
                    self.cost = self.cost + MazeSolver.step_cost(trace[state], state)
                state = trace[state]
        
        class HeapNode:
            def __init__(self, cost, step, current_state, prev_state):
                self.cost = cost
                self.step = step
                self.current_state = current_state
                self.prev_state = prev_state

            def __lt__(self, other):
                if self.cost == other.cost:
                    return self.step < other.step
                return self.cost < other.cost
        
        heapq.heappush(pq, HeapNode(0, 0, self.compress_initial_state, None))
        while pq:
            heap_node = heapq.heappop(pq)
            cost = heap_node.cost
            step = heap_node.step
            state = heap_node.current_state
            prev_state = heap_node.prev_state

            if state in visited:
                continue

            self.state_visited += 1

            if self.is_deadlock(state):
                continue

            trace[state] = prev_state
            visited.add(state)

            if state.is_goal_state():
                trace_back(state)
                self.time_consume = (time.time() - start_time) * 1000
                return True

            for (check, move) in [(state.can_move_up, state.move_up), 
                                  (state.can_move_left, state.move_left), 
                                  (state.can_move_down, state.move_down), 
                                  (state.can_move_right, state.move_right)]:
                if not check(self.initial_state):
                    continue
                new_state = move()
                if new_state not in visited:
                    (i, j) = new_state.ares_position
                    heapq.heappush(pq, 
                                   HeapNode(cost + MazeSolver.step_cost(state, new_state), 
                                            step + 1, new_state, state))

        self.time_consume = (time.time() - start_time) * 1000
        return False
    
# MazeSolver class using A* algorithm
class MazeSolverAStar(MazeSolver):
    def __init__(self, initial_state):
        super().__init__(initial_state)

    def heuristic_value(self, state):
        # sum of distance from each stone to the closest switch, multiply the weight of the stone
        hcost = 0
        for (i, j) in state.stones_weight:
            min_distance = 2000000000
            for (x, y) in self.initial_state.switches_position:
                distance = abs(i - x) + abs(j - y)
                min_distance = min(min_distance, distance)
            hcost += min_distance * state.stones_weight[(i, j)]
        
        # distance from Ares to the closest stone
        (x, y) = state.ares_position
        hstep = 2000000000
        for (i, j) in state.stones_weight:
            distance = abs(i - x) + abs(j - y)
            hstep = min(min_distance, distance)

        return hcost, hstep
    
    def solve_maze(self):
        start_time = time.time()
        self.cost = 0
        self.path = []
        self.str_path = ''
        self.state_visited = 0

        trace = {}
        visited = set()
        pq = []

        def trace_back(state: ms.MazeStateCompress):
            while state in trace:
                self.path.append(state.decompress(self.initial_state))
                if trace[state] != None:
                    self.str_path = MazeSolver.str_step(trace[state], state) + self.str_path
                    self.cost = self.cost + MazeSolver.step_cost(trace[state], state)
                state = trace[state]
        
        class HeapNode:
            def __init__(self, heuristic_value, cost, step, current_state, prev_state):
                self.heuristic_value = heuristic_value
                self.cost = cost
                self.step = step 
                self.current_state = current_state
                self.prev_state = prev_state

            def __lt__(self, other):
                self_cost = self.heuristic_value[0] + self.cost
                other_cost = other.heuristic_value[0] + other.cost
                if self_cost == other_cost: # same hcost
                    return self.heuristic_value[1] + self.step < other.heuristic_value[1] + other.step
                return self_cost < other_cost
        
        heapq.heappush(pq, HeapNode(self.heuristic_value(self.compress_initial_state),
                                    0, 0, self.compress_initial_state, None))
        while pq:
            heap_node = heapq.heappop(pq)
            cost = heap_node.cost
            step = heap_node.step
            state = heap_node.current_state
            prev_state = heap_node.prev_state

            if state in visited:
                continue

            self.state_visited += 1

            if self.is_deadlock(state):
                continue

            trace[state] = prev_state
            visited.add(state)

            if state.is_goal_state():
                trace_back(state)
                self.time_consume = (time.time() - start_time) * 1000
                return True

            for (check, move) in [(state.can_move_up, state.move_up), 
                                  (state.can_move_left, state.move_left), 
                                  (state.can_move_down, state.move_down), 
                                  (state.can_move_right, state.move_right)]:
                if not check(self.initial_state):
                    continue
                new_state = move()
                if new_state not in visited:
                    heapq.heappush(pq, 
                                   HeapNode(self.heuristic_value(new_state), 
                                            cost + MazeSolver.step_cost(state, new_state),
                                            step + 1,
                                            new_state, state))

        self.time_consume = (time.time() - start_time) * 1000
        return False
    

def check(maze_solver: MazeSolver):
    maze_solver.solve_maze()
    # for state in maze_solver.path:
    #     for row in state.grid:
    #         print(row)
    #     print("\n")
    print("so state tham: ", maze_solver.state_visited)
    print("cost: ", maze_solver.cost)
    print("step: ", len(maze_solver.path) - 1)
    print("mem use: ", maze_solver.memory_consume)
    print("time: ", maze_solver.time_consume)
    print(maze_solver.str_path)

# temp = ms.MazeState(None, None, None, None, None, None)
bfs = MazeSolverBFS.from_file('input-08.txt')
dfs = MazeSolverDFS.from_file('input-08.txt')
ucs = MazeSolverUCS.from_file('input-08.txt')
a_star = MazeSolverAStar.from_file('input-01.txt') 

# start_time = time.time()
# check(dfs)
# end_time = time.time()
# elapsed_time = end_time - start_time
# print(f"Elapsed time: {(elapsed_time * 1000):.4f} ms")

# start_time = time.time()
# check(ucs)
# end_time = time.time()
# elapsed_time = end_time - start_time
# print(f"Elapsed time: {(elapsed_time * 1000):.4f} ms")

# check(a_star)


#check(dfs)
#check(ucs)






    

        