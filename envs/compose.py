#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 17:49:35 2019

@author: molano
"""

from gym import spaces
import numpy as np
import itertools


class compose():
    """
    combines two different tasks
    """
    def __init__(self, env1, env2, delay=1, dt=100):
        self.t = 0
        self.delay = delay/dt
        self.delay_on = True
        self.env1 = env1
        self.env2 = env2
        self.num_act1 = self.env1.action_space.n
        self.num_act2 = self.env2.action_space.n
        self.action_space = spaces.Discrete(self.num_act1 *
                                            self.num_act2)
        self.observation_space = \
            spaces.Box(-np.inf, np.inf,
                       shape=(self.env1.observation_space.shape[0] +
                              self.env2.observation_space.shape[0], ),
                       dtype=np.float32)
        self.action_split = list(itertools.product(np.arange(self.num_act1),
                                                   np.arange(self.num_act2)))
        # start trials
        self.env1_on = True
        self.env2_on = True
        self._new_trial()
        print(self.action_split)

    def _new_trial(self):
        self.env1.trial = self.env1._new_trial()
        self.env2.trial = self.env2._new_trial()

    def reset(self):
        return np.concatenate((self.env1.reset(), self.env2.reset()), axis=0)

    def step(self, action):
        action1, action2 = self.action_split[action]
        if self.env1_on:
            #            print('env1 on')
            obs1, reward1, done1, info1, new_trial1 = self.env1._step(action1)
            self.env1_on = not new_trial1
        else:
            obs1, reward1, done1 = self.standby_step(1)
            new_trial1 = False

        if self.t > self.delay and self.env2_on:
            #            print('env2 on')
            obs2, reward2, done2, info2, new_trial2 = self.env2._step(action2)
            self.env2_on = not new_trial2
        else:
            obs2, reward2, done2 = self.standby_step(2)
            new_trial2 = False

        if not self.env1_on and not self.env2_on:
            #            print('new trial')
            self._new_trial()
            self.t = 0
            self.env1_on = True
            self.env2_on = True

        #        print(self.t)
        #        print(action1)
        #        print(reward1)
        #        print(reward2)
        #        print('--------')
        self.t += 1

        obs = np.concatenate((obs1, obs2), axis=0)
        reward = reward1 + reward2
        done = done1  # TODO: done whenever the primary task is done?

        # new trial information
        info = {}
        if new_trial1:
            gt1 = info1['gt']
            info = {'new_trial': True}
        else:
            gt1 = ''
        if new_trial2:
            gt2 = info2['gt']
            info = {'new_trial': True}
        else:
            gt2 = ''
        info['gt'] = [gt1, gt2]

        return obs, reward, done, info

    def standby_step(self, env):
        if env == 1:
            obs = np.zeros((self.env1.observation_space.shape[0], ))
        else:
            obs = np.zeros((self.env2.observation_space.shape[0], ))
        rew = 0
        done = False
        return obs, rew, done
