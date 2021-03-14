#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
from utils.socket_wrap import SocketWrapper
from .game_client import MatchmakerConnection
from .game_client import NetworkEnv
from envs.envs_list import all_environments

class test_agent:
    def __init__(self, latency = 0,  games = ["__all__"], port = 12345, direct = False, host = "localhost"):
        self.host = host
        self.port = port
        self.username = '' 
        self.password = ''
        self.latency = latency
        self.direct = direct
        self.games = games
        
    def connect(self, username, password):
        self.username = username
        self.password = password
        env = None
        mm_env = MatchmakerConnection(
                self.host, self.port, self.username, self.password, available_games=self.games
                )
        env = mm_env.start_new()        
        #return env            
            
            
    def run(self):
        for i in range(100000):
            if i % 100 == 0:
                print("Timestep {}".format(i))
            time.sleep(self.latency / 1000)  # Used to simulate network latency
            action = env.action_space.sample()  # Choose a random action
            obs, rew, done, info = env.step(action)  # Send action to game server
            if done:
                print("Done")
                break  # Episode ended

#    conenv.render()            