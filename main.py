from turtle import Turtle, Screen


class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = right - left
        self.height = top - bottom
        self.center_x = left + self.width / 2
        self.center_y = bottom + self.height / 2

    def has_inside(self, x, y):
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class Cell(Rect):
    WIDTH = 100
    PADDING = 15

    def __init__(self, row, col):
        self.row = row
        self.col = col
        super().__init__(
            left=Grid.LEFT + Cell.WIDTH * col,
            top=Grid.TOP - Cell.WIDTH * row,
            right=Grid.LEFT + Cell.WIDTH * (col + 1),
            bottom=Grid.TOP - Cell.WIDTH * (row + 1)
        )
        self.marker_rect = Rect(
            left=self.left + Cell.PADDING,
            top=self.top - Cell.PADDING,
            right=self.right - Cell.PADDING,
            bottom=self.bottom + Cell.PADDING
        )
        self.marker = None
        self.score = 0

    def is_unmarked(self):
        return self.marker is None


class Grid(Rect):
    LEFT = -Cell.WIDTH * 3 / 2
    TOP = Cell.WIDTH * 3 / 2
    RIGHT = Cell.WIDTH * 3 / 2
    BOTTOM = -Cell.WIDTH * 3 / 2

    def __init__(self):
        super().__init__(Grid.LEFT, Grid.TOP, Grid.RIGHT, Grid.BOTTOM)
        self.cells = [[Cell(row, col) for col in range(3)] for row in range(3)]

    def print_cells(self):
        for row in range(3):
            print([cell.marker for cell in self.cells[row]])

    def print_scores(self):
        for row in range(3):
            print([cell.score for cell in self.cells[row]])

    def all_cells(self):
        return [cell for row in self.cells for cell in row]

    def get_unmarked_cells(self):
        return [cell for cell in self.all_cells() if cell.is_unmarked()]

    def get_clicked_cell(self, x, y):
        for cell in self.all_cells():
            if cell.has_inside(x, y):
                return cell

    def get_row(self, row):
        return self.cells[row]

    def get_column(self, column):
        return [self.cells[row][column] for row in range(3)]

    def get_ascending_diagonal(self):
        return [self.cells[i][2 - i] for i in range(3)]

    def get_descending_diagonal(self):
        return [self.cells[i][i] for i in range(3)]

    def check_tie(self):
        return len(self.get_unmarked_cells()) == 0

    def check_win(self, marker):
        for row in range(3):
            checklist = self.get_row(row)
            if all([marker == cell.marker for cell in checklist]):
                return True, checklist, "row"
        for column in range(3):
            checklist = self.get_column(column)
            if all([marker == cell.marker for cell in checklist]):
                return True, checklist, "column"
        checklist = self.get_ascending_diagonal()
        if all([marker == cell.marker for cell in checklist]):
            return True, checklist, "ascending diagonal"
        checklist = self.get_descending_diagonal()
        if all([marker == cell.marker for cell in checklist]):
            return True, checklist, "descending diagonal"
        return False, None, None

    def get_winning_cells(self, marker):
        winning_cells = []

        def get_winning_cell_in_list(checklist):
            if sum([marker == cell.marker for cell in checklist]) == 2:
                for cell in checklist:
                    if cell.is_unmarked():
                        winning_cells.append(cell)

        for row in range(3):
            row_list = self.get_row(row)
            get_winning_cell_in_list(row_list)
        for column in range(3):
            column_list = self.get_column(column)
            get_winning_cell_in_list(column_list)
        get_winning_cell_in_list(self.get_ascending_diagonal())
        get_winning_cell_in_list(self.get_descending_diagonal())
        return winning_cells


class MARKER:
    X = "x"
    O = "o"
    RED = "red"
    BLUE = "blue"


class Player:
    def __init__(self, marker, color):
        self.marker = marker
        self.color = color
        self.opponent_marker = MARKER.X if self.marker == MARKER.O else MARKER.O


class Computer(Player):
    def __init__(self, marker, color):
        super().__init__(marker, color)

    def get_score(self, grid: Grid, score=0, turn=1):
        # Check if you have won
        won, _, _ = grid.check_win(self.marker)
        if won:
            score += 10 ** (9 - turn)
            return score

        # Check if you are about to lose
        losing_cells = grid.get_winning_cells(self.opponent_marker)
        about_to_lose = len(losing_cells) > 0
        if about_to_lose:
            score -= 10 ** (9 - turn)
            return score

        # Check if there's a tie
        if grid.check_tie():
            return score

        next_turn = turn + 1
        # Check if you are about to win
        winning_cells = grid.get_winning_cells(self.marker)
        about_to_win = len(winning_cells) > 0
        # Predict player's next turn
        if about_to_win:
            score += 10 ** (9 - next_turn)
            # Check if you have created a trap
            if len(winning_cells) > 1:
                score += 10 ** (9 - next_turn)
                return score
            # Predict that the player is going to block you
            winning_cells[0].marker = self.opponent_marker
            for cell in grid.get_unmarked_cells():
                cell.marker = self.opponent_marker
                score = self.get_score(grid, score, next_turn + 1)
                cell.marker = None
            winning_cells[0].marker = None
        else:
            for opponent_cell in grid.get_unmarked_cells():
                opponent_cell.marker = self.opponent_marker
                # Check if you are about to lose
                losing_cells = grid.get_winning_cells(self.opponent_marker)
                about_to_lose = len(losing_cells) > 0
                if about_to_lose:
                    losing_cells[0].marker = self.marker
                    score = self.get_score(grid, score, next_turn + 1)
                    losing_cells[0].marker = None
                else:
                    for cell in grid.get_unmarked_cells():
                        cell.marker = self.marker
                        score = self.get_score(grid, score, next_turn + 1)
                        cell.marker = None
                opponent_cell.marker = None
        return score

    def choose_cell(self, grid: Grid):
        options = grid.get_unmarked_cells()
        for cell in options:
            cell.marker = self.marker
            cell.score = self.get_score(grid)
            cell.marker = None
        grid.print_scores()
        return max(options, key=lambda option: option.score)


class GameScreen(Screen):
    def __init__(self):
        super().__init__()
        self.delay(15)
        self.enable_clicks = True


class GamePen(Turtle):
    DEFAULT_SPEED = 6
    DEFAULT_SIZE = 3

    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.speed(GamePen.DEFAULT_SPEED)
        self.pensize(GamePen.DEFAULT_SIZE)

    def draw_line(self, start_x, start_y, end_x, end_y):
        self.penup()
        self.goto(start_x, start_y)
        self.pendown()
        self.goto(end_x, end_y)

    def draw_rect(self, rect: Rect):
        self.penup()
        self.goto(rect.left, rect.top)
        self.pendown()
        self.setx(rect.right)
        self.sety(rect.bottom)
        self.setx(rect.left)
        self.sety(rect.top)

    def draw_grid(self):
        self.showturtle()
        for i, j, down in [(x, y, y) if line < 2 else (y, x, y) for line, x in enumerate([1, 2] * 2) for y in [0, 3]]:
            self.pen(pendown=bool(down))
            self.goto(Grid.LEFT + Cell.WIDTH * i, Grid.TOP - Cell.WIDTH * j)
        self.hideturtle()

    def draw_o(self, cell: Cell):
        radius = cell.marker_rect.width / 2
        self.penup()
        self.goto(cell.center_x, cell.marker_rect.bottom)
        self.pendown()
        self.speed(0)
        for _ in range(20):
            self.circle(radius, extent=360 / 20)
        self.speed(GamePen.DEFAULT_SPEED)

    def draw_x(self, cell: Cell):
        self.draw_line(cell.marker_rect.left, cell.marker_rect.top, cell.marker_rect.right, cell.marker_rect.bottom)
        self.draw_line(cell.marker_rect.right, cell.marker_rect.top, cell.marker_rect.left, cell.marker_rect.bottom)

    def mark(self, cell: Cell, player: Player):
        self.showturtle()
        self.pencolor(player.color)
        if player.marker == MARKER.X:
            self.draw_x(cell)
        elif player.marker == MARKER.O:
            self.draw_o(cell)
        cell.marker = player.marker
        self.hideturtle()

    def strikethrough(self, cells, cond, color):
        self.showturtle()
        self.pencolor(color)
        self.pensize(5)
        if cond == "row":
            left = cells[0].left
            right = cells[2].right
            y = cells[0].center_y
            self.draw_line(left, y, right, y)
        elif cond == "column":
            top = cells[0].top
            bottom = cells[2].bottom
            x = cells[0].center_x
            self.draw_line(x, top, x, bottom)
        elif cond == "ascending diagonal":
            right = cells[0].right
            top = cells[0].top
            left = cells[2].left
            bottom = cells[2].bottom
            self.draw_line(right, top, left, bottom)
        elif cond == "descending diagonal":
            left = cells[0].left
            top = cells[0].top
            right = cells[2].right
            bottom = cells[2].bottom
            self.draw_line(left, top, right, bottom)
        self.pensize(GamePen.DEFAULT_SIZE)
        self.hideturtle()


class STATE:
    MENU = 1
    PLAY = 2
    GAME_OVER = 3


class Game:
    def __init__(self):
        self.screen = GameScreen()
        self.screen.onclick(self.click_handler)
        self.pen = GamePen()
        self.grid = Grid()
        self.player = Player(MARKER.X, MARKER.BLUE)
        self.computer = Computer(MARKER.O, MARKER.RED)
        self.current_player = self.computer
        self.state = STATE.MENU

    def run(self):
        self.screen.mainloop()

    def change_current_player(self):
        self.current_player = self.player if self.current_player == self.computer else self.computer

    def play_move(self, cell):
        self.pen.mark(cell, self.current_player)
        win, cells, cond = self.grid.check_win(self.current_player.marker)
        self.grid.print_cells()
        if win:
            self.pen.strikethrough(cells, cond, self.current_player.color)
        else:
            self.change_current_player()
            if self.current_player == self.computer:
                self.computer_turn()

    def computer_turn(self):
        cell = self.computer.choose_cell(self.grid)
        self.play_move(cell)

    def start_game(self):
        self.state = STATE.PLAY
        self.pen.draw_grid()
        if self.current_player == self.computer:
            self.play_move(self.grid.all_cells()[0])

    def menu_handler(self, x, y):
        pass

    def game_handler(self, x, y):
        cell = self.grid.get_clicked_cell(x, y)
        if cell is not None and cell.is_unmarked():
            self.play_move(cell)

    def game_over_handler(self, x, y):
        pass

    def click_handler(self, x, y):
        if not self.screen.enable_clicks:
            return
        self.screen.enable_clicks = False
        if self.state == STATE.MENU:
            self.menu_handler(x, y)
        elif self.state == STATE.PLAY:
            self.game_handler(x, y)
        elif self.state == STATE.GAME_OVER:
            self.game_over_handler(x, y)
        self.screen.enable_clicks = True


if __name__ == "__main__":
    game = Game()
    game.run()
