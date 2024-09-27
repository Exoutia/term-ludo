import random
from collections import deque
from dataclasses import dataclass
from enum import Enum

NUMBER_OF_PAWNS_PER_PLAYER = 4
END_POS_BEFORE_START = 2


class Color(Enum):
    RED = 0
    GREEN = 1
    YELLOW = 2
    BLUE = 3
    PURPLE = 4
    ORANGE = 5


@dataclass
class Pawn:
    color: Color
    start_pos: int
    end_pos: int
    cur_pos: int = -1
    final_phase: int = 6
    final_phase_left: int = 6
    in_final_phase: bool = False

    @property
    def is_restricted(self):
        return self.cur_pos == -1

    def unrestrict(self):
        self.cur_pos = self.start_pos

    @property
    def has_won(self):
        return self.final_phase_left == 0


@dataclass
class Player:
    name: str
    color: Color
    pawns: list[Pawn]

    @property
    def has_won(self):
        return all(pawn.has_won for pawn in self.pawns)

    @property
    def restricted_pawns(self):
        return [i for i, pawn in enumerate(self.pawns) if pawn.is_restricted]

    @property
    def unrestricted_pawns(self):
        return [i for i, pawn in enumerate(self.pawns) if not pawn.is_restricted]


def create_board(number_of_players: int = 4):
    NUMBER_OF_PLAYERS = max(4, number_of_players)

    board: list[str] = ["⬜"] * (13 * NUMBER_OF_PLAYERS)
    mul = 0

    color_emoji = {"GREEN": "🟩", "RED": "🟥", "BLUE": "🟦", "YELLOW": "🟨"}

    for i in range(NUMBER_OF_PLAYERS):
        color = Color(i)
        ind = 13 * mul
        board[ind] = color_emoji.get(color.name, color.name)
        board[ind - 2] = "↑" + color_emoji.get(color.name, color.name)
        board[ind - 5] = "⭐"
        mul += 1
    return board


def roll_dice():
    return random.randint(1, 6)


def print_board(board, pawns):
    for i, val in enumerate(board):
        if i in pawns:
            val = "@"
        print(f"{val}", end=" ")
    print()


def move_pawn(pawn: Pawn, roll_num: int, board: list[str]):
    for _ in range(roll_num):
        if pawn.cur_pos == pawn.end_pos and not pawn.in_final_phase:
            print("Pawn has entered the final phase.")
            pawn.in_final_phase = True
            pawn.final_phase_left -= 1
            pawn.cur_pos = 52
        elif pawn.in_final_phase and not pawn.has_won:
            pawn.final_phase_left -= 1
            print(f"pawn is in final phase {pawn.final_phase_left}")
        elif not pawn.has_won:
            pawn.cur_pos = (pawn.cur_pos + 1) % len(board)
    print("you have moved")

    if pawn.has_won:
        print("Pawn has won the competition")


def create_pawns(color: Color, number_of_players: int = 4):
    start_pos = color.value * 13
    end_pos = (
        number_of_players * 13 - END_POS_BEFORE_START
        if start_pos == 0
        else start_pos - END_POS_BEFORE_START
    )
    return [Pawn(color, start_pos, end_pos) for _ in range(NUMBER_OF_PAWNS_PER_PLAYER)]


def create_players(number_of_players: int) -> list[Player]:
    return [
        Player(Color(i).name, Color(i), create_pawns(Color(i), number_of_players))
        for i in range(number_of_players)
    ]


def create_game():
    number_of_players = int(input("Enter the number of players (min 4, max 6): "))
    players = create_players(number_of_players)
    board = create_board()
    return board, players


def select_pawn_to_move(cur_player: Player) -> Pawn:
    pawns_unrestricted_index = cur_player.unrestricted_pawns
    for ind in pawns_unrestricted_index:
        print(f"pawn {ind} at {cur_player.pawns[ind].cur_pos}")
    pawn_ind = int(input("enter the index of pawn you want to move: "))
    return cur_player.pawns[pawn_ind]


def get_all_pawns_present_on_board(players: list[Player]):
    pawns_pos = []
    for player in players:
        for i in player.unrestricted_pawns:
            pawns_pos.append(player.pawns[i].cur_pos)
    return pawns_pos


def show_player_info(cur_player: Player):
    print("Now it's ", cur_player.name, "Turn.")
    numbers_of_restricted_pawns = len(cur_player.restricted_pawns)
    pawns_unrestricted_index = cur_player.unrestricted_pawns
    print(f"you have {numbers_of_restricted_pawns}")
    print(f"you have {len(pawns_unrestricted_index)}")
    if numbers_of_restricted_pawns != 4:
        for ind in pawns_unrestricted_index:
            print(f"pawn {ind} at {cur_player.pawns[ind].cur_pos}")


def unrestrict_first_pawn_from_palyers_pawns(cur_player):
    ind = cur_player.restricted_pawns[0]
    cur_player.pawns[ind].unrestrict()


def main():
    running = True
    completed = False

    # TODO: create the player playing system
    # TODO: Create the way to players can play select the goti to play
    # Create a function to setup whole game with the number of player's selected the game.'

    board, players = create_game()
    turn: deque[Player] = deque(players, 4)

    while running and not completed:
        cur_player = turn.popleft()
        show_player_info(cur_player)

        pressed = input("Enter r to roll_dice, q to quit: ").lower()
        match pressed:
            case "q":
                running = False
            case "r":
                num = roll_dice()
                print("You rolled ", num)
                if num == 6:
                    turn.appendleft(cur_player)
                    if len(cur_player.unrestricted_pawns) == 0:
                        print("You have no movalbe pawns so unrestricting a pawn")
                        unrestrict_first_pawn_from_palyers_pawns(cur_player)
                    elif len(cur_player.unrestricted_pawns) == 4:

                        print("you have no restricted pawns so choose a pawn to move")
                        pawn = select_pawn_to_move(cur_player)
                        move_pawn(pawn, num, board)
                    else:

                        what_to_do = input(
                            "Enter u to unrestrict a pawn, m to a move pawn already unrestricted: "
                        ).lower()
                        match what_to_do:
                            case "u":
                                unrestrict_first_pawn_from_palyers_pawns(cur_player)
                                print("Pawn unrestricted and start from your home")
                            case "m":
                                print("choose which pawn to move")
                                pawn = select_pawn_to_move(cur_player)
                                move_pawn(pawn, num, board)
                else:
                    if len(cur_player.unrestricted_pawns) != 0:
                        print("choose which pawn to move")
                        pawn = select_pawn_to_move(cur_player)
                        move_pawn(pawn, num, board)
                    else:
                        print("you have no pawn to move try again")
                    turn.append(cur_player)
            case _:
                print("Enter the letter again")
                continue

        pawns_pos_on_board = get_all_pawns_present_on_board(players)

        print("#" * 33)
        print_board(board, pawns_pos_on_board)
        print("#" * 33)


if __name__ == "__main__":
    main()
