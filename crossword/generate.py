import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for i in self.domains.keys():
            lst = []
            for j in self.domains[i]:
                if len(j) != i.length:
                    lst.append(j)
            for k in lst:
                self.domains[i].remove(k)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        updated = False
        overlap = self.crossword.overlaps[x, y]

        if not overlap:
            return False
        else:
            v1 = overlap[0]
            v2 = overlap[1]
            lst = []

            for i in self.domains[x]:
                for j in self.domains[y]:
                    if i[v1] == j[v2]:
                        break
                    else:
                        lst.append(i)
            for i in lst:
                self.domains[x].remove(i)
                updated = True
        return updated

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            queue = []
            for i in self.domains.keys():
                for j in self.domains.keys():
                    if i != j:
                        queue.append((i, j))
        else:
            queue = [i for i in arcs]
        while len(queue) > 0:
            arc = queue[0]
            queue.remove(arc)
            if self.revise(arc[0], arc[1]):
                if not self.domains[arc[0]]:
                    return False
                for i in self.crossword.neighbors(arc[0]):
                    if i != arc[1]:
                        queue.append((i, arc[0]))
            else:
                return True
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for i in self.domains.keys():
            if i not in assignment.keys() or assignment[i] is None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        lst = []
        for k, v in assignment.items():
            if v in lst:
                return False
            lst.append(v)
            if k.length != len(v):
                return False
            for i in self.crossword.neighbors(k):
                if i in assignment:
                    if (assignment[i][self.crossword.overlaps[k, i][1]]
                            != v[self.crossword.overlaps[k, i][0]]):
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        dict = {}
        for i in self.domains[var]:
            if i not in assignment:
                cnt = 0
                for k in self.crossword.neighbors(var):
                    if k in self.domains[var]:
                        if i in self.domains[k]:
                            cnt += 1
                dict[i] = cnt
        return sorted(dict, key=lambda key: dict[key])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        deg = 0
        val = 999999
        for i in self.domains.keys():
            if i not in assignment:
                if val > len(self.domains[i]):
                    val = len(self.domains[i])
                    var = i
                    if not self.crossword.neighbors(i):
                        deg = 0
                    else:
                        deg = len(self.crossword.neighbors(i))
                elif val == len(self.domains[i]):
                    if deg < len(self.crossword.neighbors(i)):
                        val = len(self.domains[i])
                        var = i
                        deg = len(self.crossword.neighbors(i))
                else:
                    var = i
                    val = len(self.domains[i])
                    deg = 0
        return var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        v = self.select_unassigned_variable(assignment)
        for i in self.order_domain_values(v, assignment):
            assignment[v] = i
            if self.consistent(assignment) and self.ac3():
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[v]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
