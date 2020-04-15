
"""
The template of the main script of the machine learning process
"""
import pickle
import numpy as np
import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import os.path as path


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """
    #放ml裡面
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    filename = path.join(path.dirname(__file__),'save','clf_KNN_BallAndDirection.pickle')
    with open(filename, 'rb') as file:
        clf = pickle.load(file)

    # 2. Inform the game process that ml process is ready before start the loop.

    s = [93, 93]

    def get_direction(ball_x, ball_y, ball_pre_x, ball_pre_y):
        VectorX = ball_x - ball_pre_x
        VectorY = ball_y - ball_pre_y
        if (VectorX >= 0 and VectorY >= 0):
            return 0
        elif (VectorX > 0 and VectorY < 0):
            return 1
        elif (VectorX < 0 and VectorY > 0):
            return 2
        elif (VectorX < 0 and VectorY < 0):
            return 3

    def get_direction_x(ball_x, ball_pre_x):
        VectorX = ball_x - ball_pre_x
        return VectorX

    def get_direction_y(ball_y, ball_pre_y):
        VectorY = ball_y - ball_pre_y
        return VectorY

    comm.ml_ready()
    

        

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        feature = [] #數量內容要一致
        feature.append(scene_info.ball[0])
        feature.append(scene_info.ball[1])
        platform_pos=scene_info.platform[0]+20
        feature.append(platform_pos)
        feature.append(get_direction_x(feature[0],s[0]))
        feature.append(get_direction_y(feature[1],s[1]))
        feature.append(get_direction(feature[0],feature[1],s[0],s[1]))
        s = [feature[0], feature[1]]
        feature = np.array(feature)
        feature = feature.reshape((-1,6))
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

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
                #訓練目標
            y = clf.predict(feature)
            
            if y == 0:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                print('NONE')
            elif y == 1:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                print('LEFT')
            elif y == 2:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                print('RIGHT')
