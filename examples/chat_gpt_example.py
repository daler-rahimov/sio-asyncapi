import pathlib
from typing import List, Union, Optional

from flask import Flask
from flask_socketio import emit
from pydantic import BaseModel, Field
from loguru import logger

from sio_asyncapi import AsyncAPISocketIO as SocketIO
from sio_asyncapi import (EmitValidationError, RequestValidationError,
                          ResponseValidationError)

app = Flask(__name__)

socketio = SocketIO(
    app,
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="Tick-Tack-Toe API",
    description="Tick-Tack-Toe Game API",
    server_url="http://localhost:5000",
    server_name="TICK_TACK_TOE_BACKEND",
)

games: dict[int, 'Game'] = {}


class Game(BaseModel):
    board: List[List[str]] = Field(..., description='The game board', example=[
                                   ['X', 'O', ''], ['', 'X', ''], ['', '', 'O']])
    turn: str = Field(..., description='The current turn', example='X')


class MakeMoveData(BaseModel):
    game_id: int = Field(..., description='The game id', example=1)
    x: int = Field(..., description='The x coordinate', example=0)
    y: int = Field(..., description='The y coordinate', example=0)


class GameCreatedData(BaseModel):
    game_id: int = Field(..., description='The game id', example=1)


class GameWonData(BaseModel):
    winner: str = Field(..., description='The winner', example='X')


class GameDrawnData(BaseModel):
    pass


class MoveMadeData(BaseModel):
    board: List[List[str]] = Field(..., description='The game board', example=[
                                   ['X', 'O', ''], ['', 'X', ''], ['', '', 'O']])
    turn: str = Field(..., description='The current turn', example='X')

class MakeMoveAckData(BaseModel):
    error: Optional[str] = Field(None, description='The error message', example='Invalid move')

@socketio.doc_emit('game_created', GameCreatedData)
@socketio.on('create_game')
def create_game():
    # Create a new game and add it to the list of games
    game_id = len(games) + 1
    games[game_id] = Game(board=[['' for _ in range(3)] for _ in range(3)], turn='X')

    # Send the game id to the client
    emit('game_created', {'game_id': game_id})

@socketio.doc_emit('game_won', GameWonData)
@socketio.doc_emit('game_drawn', GameDrawnData)
@socketio.doc_emit('move_made', MoveMadeData)
@socketio.on('make_move', get_from_typehint=True)
def make_move(data: MakeMoveData) -> MakeMoveAckData:
    # Get the game and make the move
    logger.info(f'Making move {data}')
    game = games[data.game_id]
    board = game.board
    turn = game.turn
    board[data.x][data.y] = turn

    # Check for a win or draw
    result = check_game_status(board)

    logger.info(f'Game result: {result}')
    # Update the game state and send it to the client
    if result == 'X':
        emit('game_won', {'winner': 'X'})
    elif result == 'O':
        emit('game_won', {'winner': 'O'})
    elif result == 'draw':
        emit('game_drawn', {})
    else:
        games[data.game_id] = Game(board=board, turn='O' if turn == 'X' else 'X')
        emit('move_made', {'board': board, 'turn': game.turn})

def check_game_status(board: List[List[str]]) -> Union[str, None]:
    # Check for a win or draw
    for i in range(3):
        if board[i] == ['X', 'X', 'X']:
            return 'X'
        if board[i] == ['O', 'O', 'O']:
            return 'O'
    if all(board[i][i] == 'X' for i in range(3)):
        return 'X'
    if all(board[i][i] == 'O' for i in range(3)):
        return 'O'
    if all(board[i][j] != '' for i in range(3) for j in range(3)):
        return 'draw'
    return None

@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    default error handler. it called if no other error handler defined.
    handles requestvalidationerror, emitvalidationerror and responsevalidationerror errors.
    """
    if isinstance(e, RequestValidationError):
        logger.error(f"request validation error: {e}")
        return {'error': str(e)}
    elif isinstance(e, ResponseValidationError):
        logger.critical(f"response validation error: {e}")
        raise e
    if isinstance(e, EmitValidationError):
        logger.critical(f"emit validation error: {e}")
        raise e
    else:
        logger.critical(f"unknown error: {e}")
        raise e

if __name__ == '__main__':
    # generate the asyncapi doc
    path = pathlib.Path(__file__).parent / "chat_gpt_asyncapi.yaml"
    doc_str = socketio.asyncapi_doc.get_yaml()
    with open(path, "w") as f:
        # doc_str = spec.get_json_str_doc()
        f.write(doc_str)
    # run the app
    socketio.run(app, debug=True)
