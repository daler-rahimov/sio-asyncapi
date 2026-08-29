import logging
import pathlib
from typing import List, Optional, Union

from flask import Flask
from pydantic import BaseModel, Field

from sio_asyncapi import (
    AsyncAPISocketIO as SocketIO,
    EmitValidationError,
    RequestValidationError,
    ResponseValidationError,
    emit,
)
from sio_asyncapi._compat import field_schema_extra

logger = logging.getLogger(__name__)

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

games: dict[int, "Game"] = {}


class Game(BaseModel):
    board: List[List[str]] = Field(
        ...,
        description="The game board",
        **field_schema_extra(example=[["X", "O", ""], ["", "X", ""], ["", "", "O"]]),
    )
    turn: str = Field(
        ...,
        description="The current turn",
        **field_schema_extra(example="X"),
    )


class MakeMoveData(BaseModel):
    game_id: int = Field(..., description="The game id", **field_schema_extra(example=1))
    x: int = Field(..., description="The x coordinate", **field_schema_extra(example=0))
    y: int = Field(..., description="The y coordinate", **field_schema_extra(example=0))


class GameCreatedData(BaseModel):
    game_id: int = Field(..., description="The game id", **field_schema_extra(example=1))


class GameWonData(BaseModel):
    winner: str = Field(..., description="The winner", **field_schema_extra(example="X"))


class GameDrawnData(BaseModel):
    pass


class MoveMadeData(BaseModel):
    board: List[List[str]] = Field(
        ...,
        description="The game board",
        **field_schema_extra(example=[["X", "O", ""], ["", "X", ""], ["", "", "O"]]),
    )
    turn: str = Field(
        ...,
        description="The current turn",
        **field_schema_extra(example="X"),
    )


class MakeMoveAckData(BaseModel):
    error: Optional[str] = Field(
        None,
        description="The error message",
        **field_schema_extra(example="Invalid move"),
    )


@socketio.doc_emit("game_created", GameCreatedData)
@socketio.on("create_game")
def create_game():
    game_id = len(games) + 1
    games[game_id] = Game(board=[["" for _ in range(3)] for _ in range(3)], turn="X")
    emit("game_created", {"game_id": game_id})


@socketio.doc_emit("game_won", GameWonData)
@socketio.doc_emit("game_drawn", GameDrawnData)
@socketio.doc_emit("move_made", MoveMadeData)
@socketio.on("make_move", get_from_typehint=True)
def make_move(data: MakeMoveData) -> MakeMoveAckData:
    logger.info("Making move %s", data)
    game = games[data.game_id]
    board = game.board
    turn = game.turn
    board[data.x][data.y] = turn

    result = check_game_status(board)
    logger.info("Game result: %s", result)
    if result == "X":
        emit("game_won", {"winner": "X"})
    elif result == "O":
        emit("game_won", {"winner": "O"})
    elif result == "draw":
        emit("game_drawn", {})
    else:
        games[data.game_id] = Game(board=board, turn="O" if turn == "X" else "X")
        emit("move_made", {"board": board, "turn": game.turn})


def check_game_status(board: List[List[str]]) -> Union[str, None]:
    for i in range(3):
        if board[i] == ["X", "X", "X"]:
            return "X"
        if board[i] == ["O", "O", "O"]:
            return "O"
    if all(board[i][i] == "X" for i in range(3)):
        return "X"
    if all(board[i][i] == "O" for i in range(3)):
        return "O"
    if all(board[i][j] != "" for i in range(3) for j in range(3)):
        return "draw"
    return None


@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It is called if no other error handler is defined.
    """
    if isinstance(e, RequestValidationError):
        logger.error("Request validation error: %s", e)
        return {"error": str(e)}
    if isinstance(e, ResponseValidationError):
        logger.critical("Response validation error: %s", e)
        raise e
    if isinstance(e, EmitValidationError):
        logger.critical("Emit validation error: %s", e)
        raise e
    logger.critical("Unknown error: %s", e)
    raise e


if __name__ == "__main__":
    path = pathlib.Path(__file__).parent / "chat_gpt_asyncapi.yaml"
    path.write_text(socketio.asyncapi_doc.get_yaml())
    socketio.run(app, debug=True)
