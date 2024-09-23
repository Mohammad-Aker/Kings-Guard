import modelInference
from stockfish import Stockfish

def update_fen_square(fen: str, square: str, piece: str) -> str:
    piece_map = {
        'pawn': 'P',
        'queen': 'Q',
        'king': 'K',
        'rook': 'R',
        'bishop': 'B',
        'knight': 'N',
        'blank-piece': '1'
    }

    piece = piece_map[piece.lower()]
    rows = fen.split(' ')[0].split('/')
    col_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    rank_map = {'8': 0, '7': 1, '6': 2, '5': 3, '4': 4, '3': 5, '2': 6, '1': 7}

    col = col_map[square[0]]
    rank = rank_map[square[1]]

    rank_list = []
    for ch in rows[rank]:
        if ch.isdigit():
            rank_list.extend(['1'] * int(ch))
        else:
            rank_list.append(ch)

    rank_list[col] = piece

    new_rank = []
    empty_count = 0
    for ch in rank_list:
        if ch == '1':
            empty_count += 1
        else:
            if empty_count > 0:
                new_rank.append(str(empty_count))
                empty_count = 0
            new_rank.append(ch)
    if empty_count > 0:
        new_rank.append(str(empty_count))

    rows[rank] = ''.join(new_rank)

    updated_fen = '/'.join(rows) + ' ' + ' '.join(fen.split(' ')[1:])
    return updated_fen



def extract_move_from_fens(current_fen, new_fen):
    # Initialize Stockfish instances
    stockfish_current = Stockfish()
    stockfish_new = Stockfish()

    stockfish_current.set_fen_position(current_fen)
    stockfish_new.set_fen_position(new_fen)

    move_from = None
    move_to = None

    for file in 'abcdefgh':
        for rank in '12345678':
            square = file + rank

            piece_current = stockfish_current.get_what_is_on_square(square)
            piece_new = stockfish_new.get_what_is_on_square(square)

            if piece_current is not None and piece_new is None:
                move_from = square

            elif piece_current is None and piece_new is not None:
                move_to = square

            elif piece_current is not None and piece_new is not None and piece_current != piece_new:
               # move_from = square
                move_to = square

    if move_from and move_to:
        return move_from + move_to
    else:
        raise ValueError("Could not extract a move from the FEN comparison.")



def expand_fen_row(fen_row):
    """Expands a compressed FEN row into its full representation."""
    expanded_row = ""
    for char in fen_row:
        if char.isdigit():
            expanded_row += '1' * int(char)
        else:
            expanded_row += char
    return expanded_row

def generate_fen(current_fen):
    fen_parts = current_fen.strip().split()
    board_part = fen_parts[0]
    turn = 'b'  # Ensure it's Black's turn
    castling_availability = fen_parts[2]
    en_passant_target = fen_parts[3]
    halfmove_clock = fen_parts[4]
    fullmove_number = fen_parts[5]

    file_names = [
        'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8',
        'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8',
        'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8',
        'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8',
        'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8',
        'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'
    ]

    detections = modelInference.process_images_detections('divided_output')

    original_board_part = board_part
    changes = 0

    for i, detection in enumerate(detections):
        detected_class = detection['detected_class']
        square = file_names[i]

        if detected_class == 'black':
            continue
        elif detected_class == 'blank-piece':
            updated_fen = update_fen_square(board_part, square, 'blank-piece')
        else:
            updated_fen = update_fen_square(board_part, square, detected_class)

        updated_board_part = updated_fen.split(' ')[0]

        if original_board_part != updated_board_part:
            changes += 1
            board_part = updated_fen
            original_board_part = updated_board_part

    new_fen = ' '.join([board_part, turn, castling_availability, en_passant_target, halfmove_clock, fullmove_number])

    # Extract the move from the FEN comparison
    try:
        move = extract_move_from_fens(current_fen, new_fen)

    except ValueError as e:

        move = None


    stockfish = Stockfish()
    stockfish.set_fen_position(current_fen)

    is_legal = stockfish.is_move_correct(move) if move else False

    return new_fen, changes, move, is_legal


def update_fen_after_move(fen, move):
    board_part, turn, castling, en_passant, halfmove_clock, fullmove_number = fen.split()


    board_rows = [list(row.replace('8', '1' * 8).replace('7', '1' * 7).replace('6', '1' * 6)
                       .replace('5', '1' * 5).replace('4', '1' * 4).replace('3', '1' * 3)
                       .replace('2', '1' * 2)) for row in board_part.split('/')]


    start_square = move[:2]
    end_square = move[2:]

    start_rank = 8 - int(start_square[1])
    start_file = ord(start_square[0]) - ord('a')

    end_rank = 8 - int(end_square[1])
    end_file = ord(end_square[0]) - ord('a')

    piece = board_rows[start_rank][start_file]
    board_rows[start_rank][start_file] = '1'
    board_rows[end_rank][end_file] = piece

    new_board_part = '/'.join([''.join(row).replace('11111111', '8').replace('1111111', '7')
                              .replace('111111', '6').replace('11111', '5').replace('1111', '4')
                              .replace('111', '3').replace('11', '2').replace('1', '1')
                               for row in board_rows])

    new_turn = 'w' if turn == 'b' else 'b'


    if piece.lower() == 'p' or board_rows[end_rank][end_file] != '1':  # pawn move or capture
        new_halfmove_clock = '0'
    else:
        new_halfmove_clock = str(int(halfmove_clock) + 1)

    if turn == 'b':
        new_fullmove_number = str(int(fullmove_number) + 1)
    else:
        new_fullmove_number = fullmove_number

    # new Fen construction
    new_fen = f"{new_board_part} {new_turn} {castling} {en_passant} {new_halfmove_clock} {new_fullmove_number}"

    return new_fen


def generate_move_and_update_fen(fen):
    # Initialize Stockfish
    stockfish = Stockfish()

    stockfish.set_fen_position(fen)
    print(f"Generating move for FEN: {fen}")

    move = stockfish.get_best_move()
    if not move:
        raise ValueError("No valid move could be generated.")

    print(f"Generated move: {move}")

    try:

        board_part, turn, castling, en_passant, halfmove_clock, fullmove_number = fen.split()
    except ValueError as e:
        print(f"Error parsing FEN: {e}")
        print(f"Received FEN: {fen}")
        raise

    board_rows = [list(row.replace('8', '1'*8).replace('7', '1'*7).replace('6', '1'*6)
                      .replace('5', '1'*5).replace('4', '1'*4).replace('3', '1'*3)
                      .replace('2', '1'*2)) for row in board_part.split('/')]

    start_square = move[:2]
    end_square = move[2:]

    start_rank = 8 - int(start_square[1])
    start_file = ord(start_square[0]) - ord('a')

    end_rank = 8 - int(end_square[1])
    end_file = ord(end_square[0]) - ord('a')

    destination_occupied = board_rows[end_rank][end_file] != '1'

    updated_fen = update_fen_after_move(fen, move)
    print(f"Updated FEN after move: {updated_fen}")

    move_type = 'm'
    if len(move) == 5:
        move_type = 'r'
        move = move[:4]  # Castling
    elif destination_occupied:
        move_type = 'c'  # Capture

    # Check if the move results in checkmate
    stockfish.set_fen_position(updated_fen)
    evaluation_after_move = stockfish.get_evaluation()
    is_checkmate = evaluation_after_move['type'] == 'mate'

    return updated_fen, move, move_type, is_checkmate


#
# current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# new_fen, changes, move, is_legal = generate_fen(current_fen)
#
# print(f"New FEN: {new_fen}")
# print(f"Changes: {changes}")
# print(f"Extracted Move: {move}")
# print(f"Is Move Legal: {is_legal}")
#print(extract_move_from_fens('rnbqk1nr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 3','rnbqk1nr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 0 3'))
