import random
import copy


def display_state(s, *, clear=False):
    """
    Display the state s

    If 'clear' is set to True, erase previous displayed states
   """

    def colored(r, g, b, text):
        rb, gb, bb = (r + 2) / 3, (g + 2) / 3, (b + 2) / 3
        rd, gd, bd = (r) / 1.5, (g) / 1.5, (b) / 1.5
        return f"\033[38;2;{int(rb*255)};{int(gb*255)};{int(bb*255)}m\033[48;2;{int(rd*255)};{int(gd*255)};{int(bd*255)}m{text}\033[0m"

    def inverse(text):
        rb, gb, bb = .2, .2, .2
        rd, gd, bd = .8, .8, .8
        return f"\033[38;2;{int(rb*255)};{int(gb*255)};{int(bb*255)}m\033[48;2;{int(rd*255)};{int(gd*255)};{int(bd*255)}m{text}\033[0m"

    colours = [(1.0, 0.349, 0.369), (1.0, 0.573, 0.298), (1.0, 0.792, 0.227),
               (0.773, 0.792, 0.188), (0.541, 0.788, 0.149),
               (0.322, 0.651, 0.459), (0.098, 0.509, 0.769),
               (0.259, 0.404, 0.675), (0.416, 0.298, 0.576)]

    n_columns = len(s['stacks'])
    if clear:
        print(chr(27) + "[2J")

    print('\n')
    row = 0
    numrows = max(len(stack) for stack in s['stacks'])
    for row in range(numrows - 1, -1, -1):
        for i in range(n_columns):
            num_in_col = len(s['stacks'][i])
            if num_in_col > row:
                val = s['stacks'][i][row]
                if num_in_col == row + 1 and s['blocked'][i]:
                    print(inverse(' ' + str(val) + ' '), end=' ')
                else:
                    if s['complete'][i]:
                        print(colored(*colours[val - 1], '   '), end=' ')
                    else:
                        print(colored(*colours[val - 1], ' ' + str(val) + ' '),
                              end=' ')
            else:
                print('    ', end='')
        print()
    print(' A   B   C   D   E   F')


# Q1
def initial_state():
    #36 cards in play
    deck = [i for i in range(1, 10)] * 4
    random.shuffle(deck)

    #divide into 6 stacks
    stacks = [deck[i * 6:(i + 1) * 6] for i in range(6)]

    blocked = [False] * 6  #not blocked by any card
    complete = [False] * 6  #no column is completed
    state = {'stacks': stacks, 'blocked': blocked, 'complete': complete}
    return state


# Q2
def parse_move(input_str):
    #undo the move(s)
    if input_str.strip().upper() == "U":
        return -1

    #reset the game
    if input_str.strip().upper() == "R":
        return 0

    stack_labels = ['A', 'B', 'C', 'D', 'E', 'F']  #for A-F stacks
    source_stack = stack_labels.index(input_str[0].upper())
    destination_stack = stack_labels.index(input_str[1].upper())

    #identify the number of cards
    if len(input_str) > 2:
        number_of_cards = int(input_str[2])
    else:
        number_of_cards = 1

    #error if string not of the form of 2 letters
    #error if the 2 letters are outside range A-F
    #optionally followed by positive integer
    if len(input_str) < 2:
        raise ValueError("Input must have at least 2 letters")
    elif len(input_str) == 2:
        number_of_cards = 1
    elif len(input_str) == 3:
        number_of_cards = int(input_str[2])
    elif len(input_str) > 3:
        raise ValueError("Input must only have length of max 3")

    source = input_str[0].upper()
    destination = input_str[1].upper()
    if source not in stack_labels or destination not in stack_labels:
        raise ValueError("Source and destination must in the range of A-F")

    if len(input_str) == 3:
        if not 1 <= int(input_str[2]) <= 9:
            raise ValueError("Number of cards must be valid")
        number_of_cards = int(input_str[2])
    else:
        number_of_cards = 1

    m = (source_stack, destination_stack, number_of_cards)
    return m


# Q3
def validate_move(state, move):
    source_stack, destination_stack, number_of_cards = move
    stacks = state['stacks']
    blocked = state['blocked']
    complete = state['complete']

    #check source stack and destination stack
    if source_stack == destination_stack:
        return False
    if not (0 <= source_stack < len(stacks)) or not (0 <= destination_stack <
                                                     len(stacks)):
        return False
    if len(stacks[source_stack]) == 0:
        return False
    if complete[destination_stack]:
        return False

    #check number of cards
    if number_of_cards <= 0 or number_of_cards > len(stacks[source_stack]):
        return False

    #moving card(s)
    cards_to_move = stacks[source_stack][-number_of_cards:]

    if blocked[destination_stack]:
        return False

    #rule: moving single cards
    if blocked[source_stack]:
        if number_of_cards > 1:
            return False
        elif number_of_cards == 1:
            if len(stacks[destination_stack]) == 0:
                return True
            else:
                top_card = stacks[destination_stack][-1]
                if cards_to_move[0] == top_card - 1:
                    if not blocked[destination_stack]:
                        return True
                return False

    # not blocked source
    if number_of_cards == 1:
        if len(stacks[destination_stack]) == 0:
            return True
        else:
            top_card = stacks[destination_stack][-1]
            if cards_to_move[0] == top_card - 1:
                return True

            if not blocked[destination_stack]:
                return True
            return False

    #rule: moving multiple cards
    if number_of_cards > 1:
        for i in range(len(cards_to_move) - 1):
            if cards_to_move[i] != cards_to_move[i + 1] + 1:
                return False
        if len(stacks[destination_stack]) == 0:
            return True

        top_card = stacks[destination_stack][-1]
        if cards_to_move[0] == top_card - 1:
            return True

        return False

    #rule: blocking moves
    if len(stacks[destination_stack]) > 0 and blocked[destination_stack]:
        return False

    return True


# Q4
def apply_move(state, move):
    source_stack, destination_stack, number_of_cards = move
    stacks = state['stacks']
    blocked = state['blocked']
    complete = state['complete']

    #selection of cards that need to be taken out
    cards_to_move = stacks[source_stack][-number_of_cards:]

    #taking out the selected cards
    stacks[source_stack] = stacks[source_stack][:-number_of_cards]

    #add cards from source stack to destination stack
    stacks[destination_stack].extend(cards_to_move)

    #if the destination stack's status is blocked
    if len(stacks[destination_stack]) > 1:
        top_card = stacks[destination_stack][-1]
        below_top_card = stacks[destination_stack][-2]
        if top_card != below_top_card - 1:
            blocked[destination_stack] = True
        else:
            blocked[destination_stack] = False
    else:
        blocked[destination_stack] = False

    #if source is blocked, after move a card, source stack becomes unblock
    if blocked[source_stack]:
        blocked[source_stack] = False

    #if the status is complete
    if len(stacks[destination_stack]
           ) == 9 and stacks[destination_stack] == list(range(9, 0, -1)):
        complete[destination_stack] = True
    else:
        complete[destination_stack] = False


# Q5
def game_won(state):
    stacks = state['stacks']
    complete = state['complete']

    completed_stacks = 0
    for i in range(len(stacks)):
        if complete[i]:
            completed_stacks += 1
    return completed_stacks == 4


# For questions 1-5, DO NOT edit the play_game function.
# For the tasks in questions 1-5 initial_state, parse_move,
# validate_move, apply_move, and game_won must work with the
# the unmodified play_game function.

# For questions 6, 7 and 8, you should modify the play_game
# function


def play_game():
    # When we start the game,
    board = initial_state()
    history = [copy.deepcopy(board)]
    try:
        while True:
            display_state(board, clear=False)
            try:
                # Read input from the user.
                # (Do not alter this line, even in questions 6, 7, 8.)
                move_str = input()

                # Parse the text typed by the user and convert it to a move
                move = parse_move(move_str)

                #reset
                if move == 0:
                    board = initial_state()
                    history = [copy.deepcopy(board)]
                    print("Game reset. You may start now!")
                    continue

                # undo
                elif move == -1:
                    if len(history) > 1:
                        history.pop()
                        board = dict(history[-1])
                        print("Undo successful!")
                    else:
                        print("No undo found.")
                    continue

                # If the move was valid...
                else:
                    if validate_move(board, move):
                        apply_move(board, move)  # ... alter the board
                        history.append(copy.deepcopy(board))
                    else:
                        print("Move is invalid. Try again!")

            except ValueError as e:
                print("Invalid input. Try again!")

            finally:
                if game_won(board):
                    print("Congratulations my dear! You won!")
                    display_state(board, clear=False)
                    break

    except KeyboardInterrupt:  # If the user presses Ctrl-C, quit
        pass


play_game()
