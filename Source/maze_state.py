import copy 

class MazeState:
    def __init__(self, 
                 grid, 
                 height,
                 width, 
                 ares_position, 
                 stones_weight, 
                 switches_position):
        self.grid = grid                           # a 2D list represents the maze
        self.height = height                       # the height of maze
        self.width = width                         # the maximum width of maze
        self.ares_position = ares_position         # ares's position in maze, as a tuple (i, j)
        self.stones_weight = stones_weight         # a dictionary storing the stones' positions and weights: {(i, j): w}
        self.switches_position = switches_position # A set of positions of the switches
    
    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            weights = list(map(int,file.readline().split(' ')))
            grid = []
            lines = file.readlines()
            height = len(lines)
            width = 0
            for line in lines:
                chars = list(line.rstrip('\n'))
                grid.append(chars)
                width = max(width, len(chars))

        ares_position = None
        weights_index = 0
        stones_weight = {}
        switches_position = []
        for i in range(0, len(grid)):
            for j in range(0, len(grid[i])):
                if grid[i][j] == '@':
                    ares_position = (i, j)
                elif grid[i][j] == '$':
                    stones_weight[(i, j)] = weights[weights_index]
                    weights_index += 1
                elif grid[i][j] == '.':
                    switches_position.append((i, j))
                elif grid[i][j] == '*':
                    stones_weight[(i, j)] = weights[weights_index]
                    weights_index += 1
                    switches_position.append((i, j))
                elif grid[i][j] == '+':
                    switches_position.append((i, j))
                    ares_position = (i, j)

        return cls(grid, 
                   height, 
                   width, 
                   ares_position, 
                   stones_weight, 
                   tuple(switches_position))



    @classmethod 
    def from_other_maze_state(cls, other):
        return cls(copy.deepcopy(other.grid), 
                   other.height, 
                   other.width, 
                   other.ares_position, 
                   copy.deepcopy(other.stones_weight), 
                   other.switches_position)
    
    def is_goal_state(self):
        for (i, j) in self.stones_weight:
            if self.grid[i][j] != '*':
                return False
        return True
    
    def can_move_up(self):
        (i, j) = self.ares_position
        # if the cell above is empty
        if self.grid[i - 1][j] in (' ', '.'):
            return True
        # if the cell above is stone
        if self.grid[i - 1][j] in ('$', '*') and self.grid[i - 2][j] in (' ', '.'):
            return True
        return False
    
    def can_move_left(self):
        (i, j) = self.ares_position
        # if the left cell is empty
        if self.grid[i][j - 1] in (' ', '.'):
            return True
        # if the left cell is stone
        if self.grid[i][j - 1] in ('$', '*') and self.grid[i][j - 2] in (' ', '.'):
            return True
        return False
    
    def can_move_down(self):
        (i, j) = self.ares_position
        # if the cell below is empty
        if self.grid[i + 1][j] in (' ', '.'):
            return True
        # if the cell below is stone
        if self.grid[i + 1][j] in ('$', '*') and self.grid[i + 2][j] in (' ', '.'):
            return True
        return False
    
    def can_move_right(self):
        (i, j) = self.ares_position
        # if the right cell is empty
        if self.grid[i][j + 1] in (' ', '.'):
            return True
        # if the left cell is stone
        if self.grid[i][j + 1] in ('$', '*') and self.grid[i][j + 2] in (' ', '.'):
            return True
        return False
    
    def move_up(self):
        (i, j) = self.ares_position
        new_state = MazeState.from_other_maze_state(self)
        # no push stone
        if self.grid[i - 1][j] in (' ', '.'):
            # move ares
            new_state.ares_position = (i - 1, j)
            if self.grid[i - 1][j] == ' ':
                new_state.grid[i - 1][j] = '@'
            else:
                new_state.grid[i - 1][j] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
        # push stone
        elif self.grid[i - 1][j] in ('$', '*') and self.grid[i - 2][j] in (' ', '.'):
            # move the stone
            if self.grid[i - 2][j] == ' ':
                new_state.grid[i - 2][j] = '$'
            else:
                new_state.grid[i - 2][j] = '*'
            # move ares
            new_state.ares_position = (i - 1, j)
            if self.grid[i - 1][j] == '$':
                new_state.grid[i - 1][j] = '@'
            else:
                new_state.grid[i - 1][j] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
            # modify stones' positions
            weight = new_state.stones_weight.pop((i - 1, j))
            new_state.stones_weight[(i - 2, j)] = weight
        
        return new_state
    
    def move_left(self):
        (i, j) = self.ares_position
        new_state = MazeState.from_other_maze_state(self)
        # no push stone
        if self.grid[i][j - 1] in (' ', '.'):
            # move ares
            new_state.ares_position = (i, j - 1)
            if self.grid[i][j - 1] == ' ':
                new_state.grid[i][j - 1] = '@'
            else:
                new_state.grid[i][j - 1] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
        # push stone
        elif self.grid[i][j - 1] in ('$', '*') and self.grid[i][j - 2] in (' ', '.'):
            # move the stone
            if self.grid[i][j - 2] == ' ':
                new_state.grid[i][j - 2] = '$'
            else:
                new_state.grid[i][j - 2] = '*'
            # move ares
            new_state.ares_position = (i, j - 1)
            if self.grid[i][j - 1] == '$':
                new_state.grid[i][j - 1] = '@'
            else:
                new_state.grid[i][j - 1] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
            # modify stones' positions
            weight = new_state.stones_weight.pop((i, j - 1))
            new_state.stones_weight[(i, j - 2)] = weight
        
        return new_state

    def move_down(self):
        (i, j) = self.ares_position
        new_state = MazeState.from_other_maze_state(self)
        # no push stone
        if self.grid[i + 1][j] in (' ', '.'):
            # move ares
            new_state.ares_position = (i + 1, j)
            if self.grid[i + 1][j] == ' ':
                new_state.grid[i + 1][j] = '@'
            else:
                new_state.grid[i + 1][j] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
        # push stone
        elif self.grid[i + 1][j] in ('$', '*') and self.grid[i + 2][j] in (' ', '.'):
            # move the stone
            if self.grid[i + 2][j] == ' ':
                new_state.grid[i + 2][j] = '$'
            else:
                new_state.grid[i + 2][j] = '*'
            # move ares
            new_state.ares_position = (i + 1, j)
            if self.grid[i + 1][j] == '$':
                new_state.grid[i + 1][j] = '@'
            else:
                new_state.grid[i + 1][j] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
            # modify stones' positions
            weight = new_state.stones_weight.pop((i + 1, j))
            new_state.stones_weight[(i + 2, j)] = weight
        
        return new_state
    
    def move_right(self):
        (i, j) = self.ares_position
        new_state = MazeState.from_other_maze_state(self)
        # no push stone
        if self.grid[i][j + 1] in (' ', '.'):
            # move ares
            new_state.ares_position = (i, j + 1)
            if self.grid[i][j + 1] == ' ':
                new_state.grid[i][j + 1] = '@'
            else:
                new_state.grid[i][j + 1] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
        # push stone
        elif self.grid[i][j + 1] in ('$', '*') and self.grid[i][j + 2] in (' ', '.'):
            # move the stone
            if self.grid[i][j + 2] == ' ':
                new_state.grid[i][j + 2] = '$'
            else:
                new_state.grid[i][j + 2] = '*'
            # move ares
            new_state.ares_position = (i, j + 1)
            if self.grid[i][j + 1] == '$':
                new_state.grid[i][j + 1] = '@'
            else:
                new_state.grid[i][j + 1] = '+'
            # change content of the old ares position
            if self.grid[i][j] == '+': # ares on switch
                new_state.grid[i][j] = '.'
            else:
                new_state.grid[i][j] = ' '
            # modify stones' positions
            weight = new_state.stones_weight.pop((i, j + 1))
            new_state.stones_weight[(i, j + 2)] = weight
        
        return new_state
    
    def __eq__(self, other):
        if not isinstance(other, MazeState):
            return NotImplemented
        return (self.stones_weight == other.stones_weight
                and self.grid == other.grid)
                # and self.height == other.height
                # and self.width == other.width 
                # and self.ares_position == other.ares_position
                # and self.switches_position == other.switches_position
                # )

    def __hash__(self):
        return hash((tuple(tuple(row) for row in self.grid),
                     #self.height,
                     #self.width,
                     #self.ares_position, 
                     frozenset(self.stones_weight))) 
                     #self.switches_position))

# Compressed version of Mazestate
# Need a Mazestate object to decompress
# Use to make search algorithms more effective
class MazeStateCompress:
    def __init__(self, ares_position, stones_weight, switches_position):
        self.ares_position = ares_position
        self.stones_weight = stones_weight
        self.switches_position = switches_position

    @classmethod
    def from_original_maze_state(cls, maze_state: MazeState):
        return cls(maze_state.ares_position,
                   copy.deepcopy(maze_state.stones_weight),
                   maze_state.switches_position)
    @classmethod
    def from_other_compress_state(cls, other):
        return cls(other.ares_position,
                   copy.deepcopy(other.stones_weight),
                   other.switches_position)
    
    def __eq__(self, other):
        if not isinstance(other, MazeStateCompress):
            return NotImplemented
        return (self.ares_position == other.ares_position
                and self.stones_weight == other.stones_weight)
    
    def __hash__(self):
        return hash((self.ares_position,
                    frozenset(self.stones_weight)))
    
    def is_goal_state(self):
        for (i, j) in self.stones_weight:
            if (i, j) not in self.switches_position:
                return False
        return True
    
    def can_move_up(self, maze_state: MazeState):
        (i, j) = self.ares_position
        # if the cell above is empty
        if (maze_state.grid[i - 1][j] != '#' 
            and (i - 1, j) not in self.stones_weight):
            return True
        # if the cell above is stone
        if ((i - 1, j) in self.stones_weight
            and maze_state.grid[i - 2][j] != '#'
            and (i - 2, j) not in self.stones_weight):
                return True
        return False
    
    def can_move_left(self, maze_state: MazeState):
        (i, j) = self.ares_position
        # if the left cell is empty
        if (maze_state.grid[i][j - 1] != '#' 
            and (i, j - 1) not in self.stones_weight):
            return True
        # if the left cell is stone
        if ((i, j - 1) in self.stones_weight
            and maze_state.grid[i][j - 2] != '#'
            and (i, j - 2) not in self.stones_weight):
                return True
        return False
    
    def can_move_down(self, maze_state: MazeState):
        (i, j) = self.ares_position
        # if the cell above is empty
        if (maze_state.grid[i + 1][j] != '#' 
            and (i + 1, j) not in self.stones_weight):
            return True
        # if the cell above is stone
        if ((i + 1, j) in self.stones_weight
            and maze_state.grid[i + 2][j] != '#'
            and (i + 2, j) not in self.stones_weight):
                return True
        return False
    
    def can_move_right(self, maze_state: MazeState):
        (i, j) = self.ares_position
        # if the left cell is empty
        if (maze_state.grid[i][j + 1] != '#' 
            and (i, j + 1) not in self.stones_weight):
            return True
        # if the left cell is stone
        if ((i, j + 1) in self.stones_weight
            and maze_state.grid[i][j + 2] != '#'
            and (i, j + 2) not in self.stones_weight):
                return True
        return False
    
    def move_up(self):
        new_compress_state = MazeStateCompress.from_other_compress_state(self)
        (i, j) = self.ares_position
        new_compress_state.ares_position = (i - 1, j)
        if (i - 1, j) in new_compress_state.stones_weight:
            weight = new_compress_state.stones_weight.pop((i - 1, j))
            new_compress_state.stones_weight[(i - 2, j)] = weight
        
        return new_compress_state
    
    def move_left(self):
        new_compress_state = MazeStateCompress.from_other_compress_state(self)
        (i, j) = self.ares_position
        new_compress_state.ares_position = (i, j - 1)
        if (i, j - 1) in new_compress_state.stones_weight:
            weight = new_compress_state.stones_weight.pop((i, j - 1))
            new_compress_state.stones_weight[(i, j - 2)] = weight
        
        return new_compress_state

    def move_down(self):
        new_compress_state = MazeStateCompress.from_other_compress_state(self)
        (i, j) = self.ares_position
        new_compress_state.ares_position = (i + 1, j)
        if (i + 1, j) in new_compress_state.stones_weight:
            weight = new_compress_state.stones_weight.pop((i + 1, j))
            new_compress_state.stones_weight[(i + 2, j)] = weight
        
        return new_compress_state
    
    def move_right(self):
        new_compress_state = MazeStateCompress.from_other_compress_state(self)
        (i, j) = self.ares_position
        new_compress_state.ares_position = (i, j + 1)
        if (i, j + 1) in new_compress_state.stones_weight:
            weight = new_compress_state.stones_weight.pop((i, j + 1))
            new_compress_state.stones_weight[(i, j + 2)] = weight
        
        return new_compress_state
    
    def decompress(self, maze_state: MazeState):
        original_maze_state = MazeState.from_other_maze_state(maze_state)
        original_maze_state.ares_position = self.ares_position
        original_maze_state.stones_weight = copy.deepcopy(self.stones_weight)

        # reset old contents
        for (i, j) in maze_state.stones_weight:
            if (i, j) in self.switches_position:
                original_maze_state.grid[i][j] = '.'
            else:
                original_maze_state.grid[i][j] = ' '
        (i, j) = maze_state.ares_position
        if (i, j) not in self.switches_position:
            original_maze_state.grid[i][j] = ' '
        else:
            original_maze_state.grid[i][j] = '.'

        # insert new contents
        for (i, j) in self.stones_weight:
            if (i, j) in self.switches_position:
                original_maze_state.grid[i][j] = '*'
            else:
                original_maze_state.grid[i][j] = '$'

        (i, j) = self.ares_position
        if (i, j) in self.switches_position:
            original_maze_state.grid[i][j] = '+'
        else:
            original_maze_state.grid[i][j] = '@'

        return original_maze_state

        


         


        
    

        
    
