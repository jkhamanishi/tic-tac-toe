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

    @classmethod
    def from_center(cls, x, y, width, height):
        left = x - width / 2
        right = x + width / 2
        bottom = y - height / 2
        top = y + height / 2
        return cls(left, top, right, bottom)

    def get_def(self):
        return self.left, self.top, self.right, self.bottom

    def has_inside(self, x, y):
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class TextBox(Rect):
    def __init__(self, text: str, x, y, width=0, height=0, border_width=0, font_size=15, color="black"):
        super().__init__(x - width / 2, y + height / 2, x + width / 2, y - height / 2)
        self.text = text
        self.border_width = border_width
        self.font_size = font_size
        self.color = color


class Button(TextBox):
    def __init__(self, name, text: str, x, y, width, height, border_width, font_size=15):
        super().__init__(text, x, y, width, height, border_width, font_size)
        self.name = name


class Cell(Rect):
    WIDTH = 40
    PADDING = 5

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
    def __init__(self, marker=MARKER.O, color=MARKER.BLUE, order="first"):
        self.marker = marker
        self.color = color
        self.order = order
        self.opponent_marker = MARKER.X if self.marker == MARKER.O else MARKER.O


class Computer(Player):
    def __init__(self, marker=MARKER.X, color=MARKER.RED, order="second"):
        super().__init__(marker, color, order,)

    def get_score(self, grid: Grid, score=0, turn=1):
        # Check if there's a tie
        if grid.check_tie():
            return score

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


class MenuScreen:
    row_top = 30
    row_spacing = 40

    def __init__(self):
        self.title = TextBox("Tic Tac Toe", 0, 100, font_size=30)
        self.settings = MenuScreen.Settings()
        self.set_default_settings()
        self.start_button = Button("start", "start", 0, -100, 80, 40, border_width=2)

    class Settings:
        def __init__(self):
            self.list = ["marker", "color", "order"]
            self.player = dict.fromkeys(self.list)
            self.computer = dict.fromkeys(self.list)
            self.switches = dict.fromkeys(self.list)

    class SettingOption:
        def __init__(self, value, column=None, row=None, color="black"):
            y = 60 if row is None else MenuScreen.row_top - MenuScreen.row_spacing * row
            col_spacing = 80
            x = -col_spacing if (column is None and value == "Player") or column == 0 else col_spacing
            self.value = value
            self.textbox = TextBox(self.value, x, y, color=color)

        def change_value(self, value):
            self.value = value
            self.textbox.text = value

    class SwitchButton:
        def __init__(self, setting, row):
            y = MenuScreen.row_top - MenuScreen.row_spacing * row
            self.textbox = Button(setting, "switch", 0, y, width=50, height=20, border_width=1, font_size=10)

    def set_default_settings(self):
        # setting defaults
        player = Player().__dict__
        computer = Computer().__dict__
        self.settings.player["name"] = MenuScreen.SettingOption("Player")
        self.settings.computer["name"] = MenuScreen.SettingOption("Computer")
        for row, setting in enumerate(self.settings.list):
            self.settings.player[setting] = MenuScreen.SettingOption(player[setting], 0, row, player["color"])
            self.settings.computer[setting] = MenuScreen.SettingOption(computer[setting], 1, row, computer["color"])
            self.settings.switches[setting] = MenuScreen.SwitchButton(setting, row)

    def get_clicked_button(self, x, y):
        button_list = [
            self.settings.switches.get("marker").textbox,
            self.settings.switches.get("color").textbox,
            self.settings.switches.get("order").textbox,
            self.start_button
        ]
        for button in button_list:
            if button.has_inside(x, y):
                return button.name

    def switch_setting(self, change_setting):
        player_old = self.settings.player[change_setting].value
        computer_old = self.settings.computer[change_setting].value
        self.settings.computer[change_setting].change_value(player_old)
        self.settings.player[change_setting].change_value(computer_old)
        if change_setting == "color":
            for setting in self.settings.list:
                self.settings.player[setting].textbox.color = computer_old
                self.settings.computer[setting].textbox.color = player_old


class GameOverScreen:
    def __init__(self, condition=None):
        self.message = TextBox(condition, 0, 100, font_size=30)
        self.play = Button("play", "again", -60, -100, 80, 40, border_width=2)
        self.menu = Button("menu", "menu", 60, -100, 80, 40, border_width=2)

    def get_clicked_button(self, x, y):
        for button in [self.play, self.menu]:
            if button.has_inside(x, y):
                return button.name


class GamePenWrappers:
    @staticmethod
    def show_turtle(func):
        def wrapper(*args, **kwargs):
            pen = args[0]
            pen.showturtle()
            func(*args, **kwargs)
            pen.hideturtle()
        return wrapper

    @staticmethod
    def draw_instantly(func):
        def wrapper(*args, **kwargs):
            pen = args[0]
            pen.getscreen().tracer(0)
            pen.speed(0)
            func(*args, **kwargs)
            pen.speed(GamePen.DEFAULT_SPEED)
            pen.getscreen().tracer(1)
        return wrapper


class GamePen(Turtle):
    DEFAULT_SPEED = 6
    DEFAULT_SIZE = 3

    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.speed(GamePen.DEFAULT_SPEED)
        self.pensize(GamePen.DEFAULT_SIZE)
        self.hideturtle()
        self.getscreen().delay(20)

    def write_text(self, text: str, x, y, font_size):
        self.up()
        self.goto(x, y - font_size * 0.75)
        self.write(text, align="center", font=('Arial', font_size, 'normal'))

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

    def draw_textbox(self, textbox: TextBox):
        self.pencolor(textbox.color)
        if textbox.border_width:
            self.pensize(textbox.border_width)
            self.draw_rect(textbox)
        self.write_text(textbox.text, textbox.center_x, textbox.center_y, textbox.font_size)
        self.pensize(GamePen.DEFAULT_SIZE)
        self.pencolor("black")

    @GamePenWrappers.show_turtle
    def draw_grid(self):
        for i, j, down in [(x, y, y) if line < 2 else (y, x, y) for line, x in enumerate([1, 2] * 2) for y in [0, 3]]:
            self.pen(pendown=bool(down))
            self.goto(Grid.LEFT + Cell.WIDTH * i, Grid.TOP - Cell.WIDTH * j)

    def draw_o(self, cell: Cell):
        radius = cell.marker_rect.width / 2
        self.penup()
        self.goto(cell.center_x, cell.marker_rect.bottom)
        self.pendown()
        self.speed(0)
        divisions = 10
        for _ in range(divisions):
            self.circle(radius, extent=360/divisions)
        self.speed(GamePen.DEFAULT_SPEED)

    def draw_x(self, cell: Cell):
        self.draw_line(cell.marker_rect.left, cell.marker_rect.top, cell.marker_rect.right, cell.marker_rect.bottom)
        self.draw_line(cell.marker_rect.right, cell.marker_rect.top, cell.marker_rect.left, cell.marker_rect.bottom)

    @GamePenWrappers.show_turtle
    def mark(self, cell: Cell, player: Player):
        self.pencolor(player.color)
        if player.marker == MARKER.X:
            self.draw_x(cell)
        elif player.marker == MARKER.O:
            self.draw_o(cell)
        cell.marker = player.marker

    @GamePenWrappers.show_turtle
    def strikethrough(self, cells, cond, color):
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

    @GamePenWrappers.draw_instantly
    def draw_menu_screen(self, menu_screen: MenuScreen):
        self.clear()
        self.draw_textbox(menu_screen.title)
        for column in [col for col in vars(menu_screen.settings).values() if isinstance(col, dict)]:
            for setting in column.values():
                self.draw_textbox(setting.textbox)
        self.draw_textbox(menu_screen.start_button)

    @GamePenWrappers.draw_instantly
    def draw_game_over_screen(self, over_screen: GameOverScreen):
        for textbox in vars(over_screen).values():
            self.draw_textbox(textbox)


class STATE:
    MENU = 1
    PLAY = 2
    GAME_OVER = 3


class Game:
    def __init__(self):
        self.screen = Screen()
        self.screen_setup()
        self.pen = GamePen()
        self.menu = MenuScreen()
        self.grid = Grid()
        self.game_over = GameOverScreen()
        self.player = Player()
        self.computer = Computer()
        self.current_player = self.player
        self.state = STATE.MENU
        self.draw_menu()

    def run(self):
        self.screen.mainloop()

    def screen_setup(self):
        try:
            with open(".replit"):
                self.screen.getcanvas().winfo_toplevel().attributes('-fullscreen', True)
        except FileNotFoundError:
            self.screen.screensize(250, 250)
            self.screen.setup(300, 300)
        finally:
            self.screen.onclick(self.click_handler)
            self.screen.enable_clicks = True

    def reset(self):
        self.grid = Grid()
        self.current_player = self.player if self.player.order == "first" else self.computer

    def change_current_player(self):
        self.current_player = self.player if self.current_player == self.computer else self.computer

    def play_move(self, cell):
        self.pen.mark(cell, self.current_player)
        self.grid.print_cells()
        # check if they won
        win, cells, cond = self.grid.check_win(self.current_player.marker)
        if win:
            self.pen.strikethrough(cells, cond, self.current_player.color)
            self.end_game("you win!" if self.current_player == self.player else "you lose")
        elif self.grid.check_tie():
            self.end_game("tie")
        else:
            # continue game
            self.change_current_player()
            if self.current_player == self.computer:
                self.computer_turn()

    def computer_turn(self):
        cell = self.computer.choose_cell(self.grid)
        self.play_move(cell)

    def start_game(self):
        self.pen.clear()
        self.state = STATE.PLAY
        self.pen.draw_grid()
        if self.current_player == self.computer:
            self.play_move(self.grid.all_cells()[0])

    def draw_menu(self):
        self.pen.draw_menu_screen(self.menu)

    def end_game(self, condition):
        self.state = STATE.GAME_OVER
        self.game_over = GameOverScreen(condition)
        self.pen.draw_game_over_screen(self.game_over)
        self.reset()

    def menu_handler(self, x, y):
        button_name = self.menu.get_clicked_button(x, y)
        if button_name in self.menu.settings.list:
            self.menu.switch_setting(button_name)
            self.pen.draw_menu_screen(self.menu)
            self.player = Player(marker=self.menu.settings.player.get("marker").value,
                                 color=self.menu.settings.player.get("color").value,
                                 order=self.menu.settings.player.get("order").value)
            self.computer = Computer(marker=self.menu.settings.computer.get("marker").value,
                                     color=self.menu.settings.computer.get("color").value,
                                     order=self.menu.settings.computer.get("order").value)
            self.current_player = self.player if self.player.order == "first" else self.computer
        elif button_name == "start":
            self.start_game()

    def game_handler(self, x, y):
        cell = self.grid.get_clicked_cell(x, y)
        if cell is not None and cell.is_unmarked():
            self.play_move(cell)

    def game_over_handler(self, x, y):
        button_name = self.game_over.get_clicked_button(x, y)
        if button_name == "play":
            self.start_game()
        elif button_name == "menu":
            self.draw_menu()
            self.state = STATE.MENU

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
