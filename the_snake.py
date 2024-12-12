from random import choice
import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость игры:
SPEED = 10

# Все ячейки поля:
ALL_CELLS = {(x * GRID_SIZE, y * GRID_SIZE) for x in range(GRID_WIDTH)
             for y in range(GRID_HEIGHT)}

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


def draw_cell(position, color):
    """
    Draw a single cell on the game board.

    Args:
        position (tuple): The (x, y) coordinates of the cell.
        color (tuple): The color of the cell in RGB format.
    """
    rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class GameObject:
    """Base class for game objects."""

    def __init__(self, position=(0, 0), color=(255, 255, 255)):
        """
        Initialize the GameObject.

        Args:
            position (tuple): The (x, y) coordinates of the object.
            color (tuple): The color of the object in RGB format.
        """
        self.position = position
        self.color = color
        self.body_color = color  # Добавляем атрибут body_color

    def draw(self):
        """Draw the object on the game board."""
        draw_cell(self.position, self.body_color) 


class Apple(GameObject):
    """Apple object class that inherits from GameObject."""

    def __init__(self, snake_positions=None):
        """
        Initialize the Apple object.

        Args:
            snake_positions (list): List of positions occupied by the snake.
        """
        if snake_positions is None:
            snake_positions = []  
        position = self.generate_position(snake_positions)
        super().__init__(position, APPLE_COLOR)

    def generate_position(self, snake_positions):
        """
        Generate a random position for the apple that does not overlap
        the snake.

        Args:
            snake_positions (list): List of positions occupied by the snake.

        Returns:
            tuple: The (x, y) position of the apple.
        """
        free_cells = ALL_CELLS - set(snake_positions)
        return choice(tuple(free_cells))

    def randomize_position(self, snake_positions):
        """
        Randomly repositions the apple, ensuring it does not overlap
        with the snake's positions.

        Args:
            snake_positions (list): List of positions occupied by the snake.
        """
        self.position = self.generate_position(snake_positions)


class Snake(GameObject):
    """Snake object class that inherits from GameObject."""

    def __init__(self):
        """Initialize the Snake object."""
        self.reset()
        self.body_color = SNAKE_COLOR  # Добавляем атрибут body_color
        super().__init__(self.positions[0], self.body_color)

    def reset(self):
        """Reset the snake to its starting position and direction."""
        self.positions = [(GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT 
                           // 2 * GRID_SIZE)]
        self.direction = RIGHT
        self.next_direction = None
        self.growing = False

    def move(self):
        """
        Move the snake in the current direction.

        If the snake eats an apple, it grows. If the snake collides with
        itself,
        it resets to the starting position.
        """
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH, 
                    (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT)

        if self.growing:
            self.growing = False
        else:
            self.positions.pop()

        if len(self.positions) > 1 and new_head in self.positions:
            self.reset()  # Удаляем хвост при самоукусе
        else:
            self.positions.insert(0, new_head)

        # Обновляем позицию объекта Snake для отрисовки
        self.position = self.positions[0]

    def grow(self):
        """Trigger the snake to grow on the next move."""
        self.growing = True

    def set_direction(self, key):
        """
        Set the direction of the snake based on user input.

        Args:
            key (int): The keycode of the pressed key.
        """
        new_direction = {
            pygame.K_UP: UP,
            pygame.K_DOWN: DOWN,
            pygame.K_LEFT: LEFT,
            pygame.K_RIGHT: RIGHT
        }.get(key)
        if new_direction and new_direction != OPPOSITE_DIRECTIONS[self.
                                                                  direction]:
            self.next_direction = new_direction

    def update_direction(self):
        """Update the snake's direction based on the last input."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Return the current position of the snake's head."""
        return self.positions[0]

    def draw(self):
        """Draw the snake on the game board."""
        super().draw()  # Draw the head
        for position in self.positions[1:]:
            draw_cell(position, self.body_color)  # Draw the body


def handle_keys(snake):
    """
    Handle user input for controlling the snake and exiting the game.

    Args:
        snake (Snake): The Snake object to control.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            snake.set_direction(event.key)


def main():
    """Main function to initialize and run the game loop."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    record = 0

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка съедания яблока
        if snake.positions[0] == apple.position:
            snake.grow()
            apple = Apple(snake.positions)
            record = max(record, len(snake.positions))

        # Обновление заголовка
        pygame.display.set_caption(f'Змейка - Рекорд: {record}')

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
