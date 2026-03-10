class Rover:
    DIRECTIONS = ["N", "E", "S", "W"]

    def __init__(self, x=0, y=0, direction="N"):
        self.x = x
        self.y = y
        self.direction = direction

    def turn_left(self):
        idx = self.DIRECTIONS.index(self.direction)
        self.direction = self.DIRECTIONS[(idx - 1) % 4]

    def turn_right(self):
        idx = self.DIRECTIONS.index(self.direction)
        self.direction = self.DIRECTIONS[(idx + 1) % 4]

    def move(self):
        if self.direction == "N":
            self.y += 1
        elif self.direction == "E":
            self.x += 1
        elif self.direction == "S":
            self.y -= 1
        elif self.direction == "W":
            self.x -= 1

    def report(self):
        return f"(x={self.x}, y={self.y}, facing={self.direction})"

    def execute(self, command):
        cmd = command.strip().upper()

        if cmd in ("L", "LEFT"):
            self.turn_left()
        elif cmd in ("R", "RIGHT"):
            self.turn_right()
        elif cmd in ("M", "MOVE"):
            self.move()
        else:
            raise ValueError(
                f"Unsupported command: {command}. Use LEFT/RIGHT/MOVE (or L/R/M)."
            )

        return self.report()


def run_commands(commands):
    rover = Rover()
    print(f"Start: {rover.report()}")

    for i, command in enumerate(commands, start=1):
        state = rover.execute(command)
        print(f"After command {i} ({command}): {state}")


if __name__ == "__main__":
    # Example command sequence.
    demo_commands = ["M", "M", "R", "M", "L", "M"]
    run_commands(demo_commands)