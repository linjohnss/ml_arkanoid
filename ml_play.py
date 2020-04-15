"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
import random
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    ballpos=[]
    #記錄球的位置去解算斜率

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()  #讀取遊戲資料
        ballpos.append(scene_info.ball)     #
        platform_center_x = scene_info.platform[0]+20

        if(scene_info.frame<150):
            n = random.randint(0, 2)
            if n == 0:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            if n == 1:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif n == 2:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)

        if(len(ballpos))==1:
            ball_going_down = 0
        elif ballpos[-1][1]-ballpos[-2][1] > 0:
            ball_going_down = 1
            vy=ballpos[-1][1]-ballpos[-2][1]
            vx=ballpos[-1][0]-ballpos[-2][0]
        else:
            ball_going_down = 0

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if ball_going_down == 1 :
            ball_destination = int(ballpos[-1][0] + ((395 - ballpos[-1][1])/vy)*vx)
            if ball_destination >= 195:
                ball_destination = 195 - (ball_destination - 195)
            elif ball_destination <= 0:
                ball_destination = - ball_destination
        else:
            ball_destination = platform_center_x

        # 3.4. Send the instruction for this frame to the game process

        if ball_going_down == 1:
            if platform_center_x - ball_destination <20 and platform_center_x - ball_destination >-20:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            else:
                if platform_center_x - ball_destination>0:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                elif platform_center_x - ball_destination<0:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)

        #if not ball_served:
        #    comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
        #    ball_served = True
        #else:
        #    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)

        #if load_model.predict(input)==1:
            #comm.send_instruction(scene_info.frame, GameInstruction.CMD_RIGHT)
        #elif load_model.predict(input)==-1:
            #comm.send_instruction(scene_info.frame, GameInstruction.CMD_LEFT)
        #else:
            #comm.send_instruction(scene_info.frame, GameInstruction.CMD_NONE)