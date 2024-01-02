#!/usr/bin/env python3

class Memory:
    def __init__(self):
        self.max_memory_length = 100000
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []
