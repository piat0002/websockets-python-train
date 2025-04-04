#!/usr/bin/env python

import asyncio

from websockets.asyncio.server import serve


import json

from connect4 import PLAYER1, PLAYER2, Connect4

async def handler(websocket):
    # Initialize Connect game.
    game = Connect4()

    # player on the same browser
    PLAYERS = [PLAYER1, PLAYER2]
    currentPLAYERIndex = 0
    currentPLAYER = PLAYERS[currentPLAYERIndex]

    async for message in websocket:
        # parse the message claimed
        event = json.loads(message)

        assert event["type"] == "play", print("error unknow event received")
        column = event["column"]

        # Try to play and manage error if there is error
        try:
            row = game.play(currentPLAYER, column)
        except ValueError as exc:
            # Send an "error" event if the move was illegal.
            event = {
                "type": "error",
                "message": str(exc),
            }
            await websocket.send(json.dumps(event))
            continue
        

        # send message win if the player has win else send the legal move 
        if game.winner is not None:
            event = {
                "type": "win",
                "player": currentPLAYER,
            }
            await websocket.send(json.dumps(event))
        else:
            event = {
                "type": "play",
                "player": currentPLAYER,
                "column": column,
                "row": row,
            }
            await websocket.send(json.dumps(event))

            # change turn
            currentPLAYERIndex = (currentPLAYERIndex + 1) % 2
            currentPLAYER = PLAYERS[currentPLAYERIndex]

async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())