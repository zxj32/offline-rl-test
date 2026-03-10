import unittest

from test import Rover


class RoverTests(unittest.TestCase):
    def test_initial_state(self):
        rover = Rover()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=N)")

    def test_turn_left_full_cycle(self):
        rover = Rover()
        rover.turn_left()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=W)")
        rover.turn_left()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=S)")
        rover.turn_left()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=E)")
        rover.turn_left()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=N)")

    def test_turn_right_full_cycle(self):
        rover = Rover()
        rover.turn_right()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=E)")
        rover.turn_right()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=S)")
        rover.turn_right()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=W)")
        rover.turn_right()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=N)")

    def test_move_in_each_direction(self):
        rover = Rover()
        rover.move()  # N
        self.assertEqual(rover.report(), "(x=0, y=1, facing=N)")

        rover.turn_right()  # E
        rover.move()
        self.assertEqual(rover.report(), "(x=1, y=1, facing=E)")

        rover.turn_right()  # S
        rover.move()
        self.assertEqual(rover.report(), "(x=1, y=0, facing=S)")

        rover.turn_right()  # W
        rover.move()
        self.assertEqual(rover.report(), "(x=0, y=0, facing=W)")

    def test_execute_accepts_short_and_long_commands(self):
        rover = Rover()
        self.assertEqual(rover.execute("M"), "(x=0, y=1, facing=N)")
        self.assertEqual(rover.execute("RIGHT"), "(x=0, y=1, facing=E)")
        self.assertEqual(rover.execute("MOVE"), "(x=1, y=1, facing=E)")
        self.assertEqual(rover.execute("L"), "(x=1, y=1, facing=N)")
        self.assertEqual(rover.execute("LEFT"), "(x=1, y=1, facing=W)")
        self.assertEqual(rover.execute("R"), "(x=1, y=1, facing=N)")

    def test_execute_rejects_invalid_command(self):
        rover = Rover()
        with self.assertRaises(ValueError):
            rover.execute("X")


if __name__ == "__main__":
    unittest.main()
