#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 13:48:19 2019

@author: molano


Perceptual decision-making task, based on

  Bounded integration in parietal cortex underlies decisions even when viewing
  duration is dictated by the environment.
  R Kiani, TD Hanks, & MN Shadlen, JNS 2008.

  http://dx.doi.org/10.1523/JNEUROSCI.4761-07.2008

"""
from __future__ import division

import numpy as np
from gym import spaces
from neurogym.ops import tasktools
from neurogym.envs import ngym


class RDM(ngym.ngym):
    def __init__(self, dt=100, timing=[500, 80, 330, 1500, 500], stimEv=1.,
                 **kwargs):
        super().__init__(dt=dt)
        # Actions (fixate, left, right)
        self.actions = [0, -1, 1]
        # trial conditions
        self.choices = [-1, 1]
        # cohs specifies the amount of evidence (which is modulated by stimEv)
        self.cohs = np.array([0, 6.4, 12.8, 25.6, 51.2])*stimEv
        # Input noise
        self.sigma = np.sqrt(2*100*0.01)
        # Durations (stimulus duration will be drawn from an exponential)
        self.fixation = timing[0]
        self.stimulus_min = timing[1]
        self.stimulus_mean = timing[2]
        self.stimulus_max = timing[3]
        self.decision = timing[4]
        self.mean_trial_duration = self.fixation + self.stimulus_mean +\
            self.decision
        if self.fixation == 0 or self.decision == 0 or self.stimulus_mean == 0:
            print('XXXXXXXXXXXXXXXXXXXXXX')
            print('the duration of all periods must be larger than 0')
            print('XXXXXXXXXXXXXXXXXXXXXX')
        print('mean trial duration: ' + str(self.mean_trial_duration) +
              ' (max num. steps: ' +
              str(self.mean_trial_duration/self.dt) + ')')
        # Rewards
        self.R_ABORTED = -0.1
        self.R_CORRECT = +1.
        self.R_FAIL = 0.
        self.R_MISS = 0.
        self.abort = False
        # action and observation spaces
        self.stimulus_min = np.max([self.stimulus_min, dt])
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(3,),
                                            dtype=np.float32)
        # seeding
        self.seed()
        self.viewer = None

        # start new trial
        self.trial = self._new_trial()

    def _new_trial(self):
        # ---------------------------------------------------------------------
        # Epochs
        # ---------------------------------------------------------------------
        stimulus = tasktools.truncated_exponential(self.rng, self.dt,
                                                   self.stimulus_mean,
                                                   xmin=self.stimulus_min,
                                                   xmax=self.stimulus_max)
        # maximum length of current trial
        self.tmax = self.fixation + stimulus + self.decision
        durations = {
            'fixation': (0, self.fixation),
            'stimulus': (self.fixation, self.fixation + stimulus),
            'decision': (self.fixation + stimulus,
                         self.fixation + stimulus + self.decision),
            }

        # ---------------------------------------------------------------------
        # Trial
        # ---------------------------------------------------------------------
        ground_truth = tasktools.choice(self.rng, self.choices)
        coh = tasktools.choice(self.rng, self.cohs)

        return {
            'durations': durations,
            'ground_truth': ground_truth,
            'coh': coh
            }

    # Input scaling
    def scale(self, coh):
        return (1 + coh/100)/2

    def _step(self, action):
        # ---------------------------------------------------------------------
        # Reward and observations
        # ---------------------------------------------------------------------
        trial = self.trial
        info = {'new_trial': False}
        # rewards
        reward = 0
        # observations
        obs = np.zeros((3,))
        if self.in_epoch(self.t, 'fixation'):
            obs[0] = 1
            if self.actions[action] != 0:
                info['new_trial'] = self.abort
                reward = self.R_ABORTED
        elif self.in_epoch(self.t, 'decision'):
            gt_sign = np.sign(trial['ground_truth'])
            action_sign = np.sign(self.actions[action])
            if gt_sign == action_sign:
                reward = self.R_CORRECT
            elif gt_sign == -action_sign:
                reward = self.R_FAIL
            info['new_trial'] = self.actions[action] != 0

        # this is an 'if' to allow the stimulus and fixation periods to overlap
        if self.in_epoch(self.t, 'stimulus'):
            obs[0] = 1
            high = (trial['ground_truth'] > 0) + 1
            low = (trial['ground_truth'] < 0) + 1
            obs[high] = self.scale(trial['coh']) +\
                self.rng.gauss(mu=0, sigma=self.sigma)/np.sqrt(self.dt)
            obs[low] = self.scale(-trial['coh']) +\
                self.rng.gauss(mu=0, sigma=self.sigma)/np.sqrt(self.dt)

        # ---------------------------------------------------------------------
        # new trial?
        reward, new_trial = tasktools.new_trial(self.t, self.tmax, self.dt,
                                                info['new_trial'],
                                                self.R_MISS, reward)
        info['gt'] = np.zeros((3,))
        if new_trial:
            info['new_trial'] = True
            info['gt'][int((trial['ground_truth']/2+1.5))] = 1
            self.t = 0
            self.num_tr += 1
        else:
            self.t += self.dt
            info['gt'][0] = 1

        done = self.num_tr > self.num_tr_exp
        return obs, reward, done, info, new_trial

    def step(self, action):
        obs, reward, done, info, new_trial = self._step(action)
        if new_trial:
            self.trial = self._new_trial()
        return obs, reward, done, info


if __name__ == '__main__':
    env = RDM(timing=[100, 200, 200, 200, 100])
    for ind in range(100):
        action = 1  # env.action_space.sample()
        obs, reward, done, info = env.step(action)
        print(action)
        print(obs)
        print(reward)
        if info['new_trial']:
            print(info['gt'])
            print('xxxxxxxxxxxxxxxx')
        else:
            print('----------------')
