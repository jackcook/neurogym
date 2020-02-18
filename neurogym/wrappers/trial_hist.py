#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 11:48:59 2019

@author: molano
"""

import neurogym as ngym


class TrialHistory(ngym.TrialWrapper):
    metadata = {
        'description': 'Change ground truth probability ' +
        'based on previous outcome.',
        'paper_link': 'https://www.biorxiv.org/content/10.1101/433409v3',
        'paper_name': 'Response outcomes gate the impact of expectations ' +
        'on perceptual decisions'
    }

    def __init__(self, env, probs=None, block_dur=200,
                 blk_ch_prob=None):
        """
        Change ground truth probability based on previous outcome.
        probs: matrix of probabilities of the current choice conditioned
        on the previous for each block. (def: None, np.array)
        block_dur: Number of trials per block. (def: 200 (int))
        blk_ch_prob: If not None, specifies the probability of changing block
        (randomly). (def: None, float)
        """
        super().__init__(env)
        try:
            self.choices = self.task.choices
        except AttributeError:
            raise AttributeError('''SideBias requires task
                                 to have attribute choices''')
        assert isinstance(self.task, ngym.TrialEnv), 'Task has to be TrialEnv'
        assert probs is not None, 'Please provide choices probabilities'
        assert probs.shape[1] == len(self.choices),\
            'The number of choices {:d}'.format(probs.shape[1]) +\
            ' inferred from prob mismatchs {:d}'.format(len(self.choices)) +\
            ' inferred from choices'

        self.n_block = self.choice_prob.shape[0]
        self.curr_block = self.task.rng.choice(range(self.n_block))
        self.probs = probs
        self.block_dur = block_dur
        self.prev_trial = -1
        self.blk_ch_prob = blk_ch_prob

    def new_trial(self, **kwargs):
        # ---------------------------------------------------------------------
        # Periods
        # ---------------------------------------------------------------------
        # change rep. prob. every self.block_dur trials
        if self.blk_ch_prob is None:
            if self.task.num_tr % self.block_dur == 0:
                self.curr_block = (self.curr_block + 1) % len(self.rep_prob)
        else:
            if self.task.rng.random() < self.blk_ch_prob:
                self.curr_block = (self.curr_block + 1) % len(self.rep_prob)

        ground_truth = self.task.rng.choice(self.task.choices,
                                            p=self.probs[self.prev_trial, :])
        self.prev_trial = ground_truth
        kwargs.update({'ground_truth': ground_truth})
        self.env.new_trial(**kwargs)
