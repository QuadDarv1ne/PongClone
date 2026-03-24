# Android and cross-platform entry point
from PyPong.pong import PongGame


def main() -> None:
    """Main entry point for the game"""
    game = PongGame()
    game.run()


if __name__ == "__main__":
    main()
