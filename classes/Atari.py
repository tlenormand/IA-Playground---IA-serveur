#!/usr/bin/env python3

import gym
import numpy as np
import tensorflow as tf

from classes._Logs import _log
from classes.MasterClass import MasterClass
from classes.Memory import Memory
from classes.Model import Model
from classes.Games import Games
from classes.Logs import Logs
from classes.Docker import Docker


class Atari(MasterClass):
    def __init__(self, data):
        super().__init__({ 'user_id': data.get('user_id'), 'model_name': data.get('model_name') })

        self.config = {
            **data.get('atari_config', {}),
            'path': 'ALE',
            'frameskip': 4,
            'repeat_action_probability': 0.25,
            'full_action_space': True,
            'render_mode': None,  # None, human, rgb_array, single_rgb_array...
            'seed': 42,
            'gamma': 0.99,  # Discount factor for past rewards
            'epsilon_max': 1.0,  # Maximum epsilon greedy parameter
            'max_steps_per_episode': 10000,
            'epsilon_random_frames': 20,
            'epsilon_greedy_frames': 1000000,
            'epsilon_interval': 0,
            'batch_size': 32,
            'update_target_network': 1000,
            'update_after_actions': 4,
            'state': None,
            'can_render': False,
            'frame_count_training': 0,
            'can_train': True,
        }
        self.config['epsilon_interval'] = self.config.get('epsilon_max', 0) - self.config.get('epsilon_min', 0)
        self.env = self.build_env()

        # self.Memory_instance = Memory()
        self.Model_instance = Model({
            'user_id': data.get('user_id'),
            'model_name': data.get('model_name'),
            'model_config': data.get('model_config', {}),
            'model_layers': data.get('model_layers', {})
        })
        self.Memory_instance = Memory()
        self.Game_instance = Games(self.config.get('game'))
        self.Logs_instance = Logs({ 'logs_config': data.get('logs_config') })
        self.Docker_instance = Docker(data)

    def quit(self):
        _log.write("Quitting the program...")
        _log.write("Collet the model on the api server...")
        is_sent = self.Docker_instance.send_model()

        _log.write("Stopping the program...")
        _log.write("Saving the model...")
        self.Model.save_model()
        # _log.write("Saving the logs...")
        # self.Logs_instance.save()
        _log.write("Quitting the program...")
        # self.Model.send_model()

    def build_env(self):
        try:
            return gym.make(f"ALE/{self.config['game']}")
        except Exception as e:
            _log.write(f"Erreur lors de la création de l'environnement : {e}")

    def train(self):
        _log.write("Starting the training...")

        while True:
            state, info = np.array(self.env.reset(), dtype=object)

            for timestep in range(1, self.config.get('max_steps_per_episode')):
                if self.config.get('can_render') == True:
                    self.env.render()  # Adding this line would show the attempts of the agent in a pop up window but it slows down the training

                # Use epsilon-greedy for exploration
                if self.config.get('frame_count_training') < self.config.get('epsilon_random_frames') or self.config.get('epsilon') > np.random.rand(1)[0]:
                    # Take random action
                    action = self.Game_instance.get_random_action()
                    self.Logs_instance.log['action_type'] = 'random'
                else:
                    # Predict action Q-values from environment state
                    try:
                        state_tensor = tf.convert_to_tensor(state)
                        state_tensor = tf.expand_dims(state_tensor, 0)
                        action_probs = self.Model_instance.model(state_tensor, training=False)
                        # Take best action
                        action = tf.argmax(action_probs[0]).numpy()
                        self.Logs_instance.log['action_type'] = 'predicted'
                    except Exception as e:
                        # self.Logs.error("While predicting action", e)
                        action = self.Game_instance.get_random_action()
                        self.Logs_instance.log['action_type'] = 'random'

                self.Logs_instance.log['action'] = action

                # Decay probability of taking random action
                self.config['epsilon'] -= self.config.get('epsilon_interval') / self.config.get('epsilon_greedy_frames')
                self.config['epsilon'] = max(self.config.get('epsilon'), self.config.get('epsilon_min'))
                self.Logs_instance.log['epsilon'] = self.config.get('epsilon')

                # Apply the sampled action in our environment
                # self.Game_instance.output_to_actions(action)
                state_next, reward, done, _, _ = self.env.step(action)
                state_next = np.array(state_next)

                self.Logs_instance.log['reward'] = reward
                self.Logs_instance.log['reward_game'] += reward
                self.Logs_instance.log['reward_training'] += reward
                self.Logs_instance.log['done'] = bool(done)

                # Save actions and states in replay buffer
                self.Memory_instance.action_history.append(action)
                self.Memory_instance.state_history.append(state)
                self.Memory_instance.state_next_history.append(state_next)
                self.Memory_instance.done_history.append(done)
                self.Memory_instance.rewards_history.append(reward)
                state = state_next

                # Update every fourth frame and once batch size is over 32
                if self.config['frame_count_training'] % self.config.get('update_after_actions') == 0 and len(self.Memory_instance.done_history) > self.config.get('batch_size'):

                    # Get indices of samples for replay buffers
                    indices = np.random.choice(range(len(self.Memory_instance.done_history)), size=self.config.get('batch_size'))

                    # Using list comprehension to sample from replay buffer
                    state_sample = np.array([self.Memory_instance.state_history[i] for i in indices], dtype=object)
                    state_next_sample = np.array([self.Memory_instance.state_next_history[i] for i in indices])
                    rewards_sample = [self.Memory_instance.rewards_history[i] for i in indices]
                    action_sample = [self.Memory_instance.action_history[i] for i in indices]
                    done_sample = tf.convert_to_tensor([float(self.Memory_instance.done_history[i]) for i in indices])

                    # Build the updated Q-values for the sampled future states
                    # Use the target model for stability
                    future_rewards = self.Model_instance.model_target.predict(state_next_sample, verbose=0)

                    if self.config.get('can_train') == True:
                        # Q value = reward + discount factor * expected future reward
                        updated_q_values = rewards_sample + self.config.get('gamma') * tf.reduce_max(future_rewards, axis=1)

                        # If final frame set the last value to -1
                        updated_q_values = updated_q_values * (1 - done_sample) - done_sample

                        # Create a mask so we only calculate loss on the updated Q-values
                        masks = tf.one_hot(action_sample, len(self.Game_instance.get_inputs_for_game()))

                        with tf.GradientTape() as tape:
                            # Train the model on the states and updated Q-values
                            for i in range(len(state_sample)):
                                if state_sample[i].shape != self.Model_instance.config.get('input_shape'):
                                    state_sample[i] = np.zeros(self.Model_instance.config.get('input_shape'))
                            state_sample = tf.convert_to_tensor(state_sample, dtype=tf.float32)
                            q_values = self.Model_instance.model(state_sample)

                            # Apply the masks to the Q-values to get the Q-value for action taken
                            q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                            # Calculate loss between new Q-value and old Q-value
                            loss = self.Model_instance.loss_function(updated_q_values, q_action)

                        # Backpropagation
                        grads = tape.gradient(loss, self.Model_instance.model.trainable_variables)
                        self.Model_instance.optimizer.apply_gradients(zip(grads, self.Model_instance.model.trainable_variables))

                if self.config.get('frame_count_training') % self.config.get('update_target_network') == 0:
                    # update the the target network with new weights
                    self.Model_instance.update()
                    self.Model_instance.save_model()
                self.config['frame_count_training'] += 1

                # Limit the state and reward history
                if len(self.Memory_instance.rewards_history) > self.Memory_instance.max_memory_length:
                    del self.Memory_instance.rewards_history[:1]
                    del self.Memory_instance.state_history[:1]
                    del self.Memory_instance.state_next_history[:1]
                    del self.Memory_instance.action_history[:1]
                    del self.Memory_instance.done_history[:1]

                # Appel de la fonction pour enregistrer les logs dans le fichier CSV
                self.Logs_instance.push()

                # if self.can_save_logs:
                #     self.Logs_instance.save()

                if self.Logs_instance.config.get('can_send_logs'):
                    self.Logs_instance.send()

                # reset unique values
                self.Logs_instance.log['new_model'] = False
                self.Logs_instance.log['done'] = False

                if done:
                    break

            self.Logs_instance.log['game_number_total'] += 1
            self.Logs_instance.log['game_number_training'] += 1
            self.Logs_instance.log['frame_count_game'] = 0
            self.Logs_instance.log['executed_time_game'] = 0
            self.Logs_instance.log['reward_game'] = 0

            # Update running reward to check condition for solving
            self.Memory_instance.episode_reward_history.append(self.Logs_instance.log['reward_game'])
            if len(self.Memory_instance.episode_reward_history) > 100:
                del self.Memory_instance.episode_reward_history[:1]
            running_reward = np.mean(self.Memory_instance.episode_reward_history)

            if running_reward > 40:  # Condition to consider the task solved
                _log.write(f"Solved at episode {self.Logs_instance.log['game_number_training']}!")
                break

    def reset(self):
        return self.env.reset()

    def player_step(self, action):
        self.Logs_instance.log['action'] = action
        state_next, reward, done, _, info = self.env.step(action)
        self.state = np.array(state_next)
        self.Logs_instance.log['reward'] = reward

        self.Logs_instance.log['reward'] = reward
        self.Logs_instance.log['done'] = bool(done)

        return self._rgb_to_grayscale(self.state), reward, done, info

    def ia_step(self):
        if self.Logs_instance.log['frame_count_training'] < self.config.get('epsilon_random_frames') or self.config['hyperparameters']['epsilon'] > np.random.rand(1)[0]:
            # Take random action
            action = self.Game_instance.get_random_action()
            # action = np.random.choice(list(GAMES[self.config['env']['game']]['inputs'].keys()))
            self.Logs_instance.log['action_type'] = 'random'
        else:
            # Predict action Q-values from environment state
            try:
                state_tensor = tf.convert_to_tensor(self.state)
                state_tensor = tf.expand_dims(state_tensor, 0)
                action_probs = self.Model_instance.model(state_tensor, training=False)
                # Take best action
                action = tf.argmax(action_probs[0]).numpy()
                self.Logs_instance.log['action_type'] = 'predicted'
            except Exception as e:
                # _log.error("While predicting action", e)
                action = self.Game_instance.get_random_action()
                # action = np.random.choice(list(GAMES[self.config['env']['game']]['inputs'].keys()))
                self.Logs_instance.log['action_type'] = 'random'

        self.config['epsilon'] -= self.config.get('epsilon_interval') / self.config.get('epsilon_greedy_frames')
        self.config['epsilon'] = max(self.config.get('epsilon'), self.config.get('epsilon_min'))

        self.Logs_instance.log['action'] = action
        state_next, reward, done, _, info = self.env.step((action))
        state_next = np.array(state_next)
        self.Logs_instance.log['reward'] = reward
        self.Logs_instance.log['done'] = bool(done)

        # Save actions and states in replay buffer
        self.state = np.array(state_next)
        self.Memory_instance.action_history.append(action)
        self.Memory_instance.state_history.append(self.state)
        self.Memory_instance.state_next_history.append(state_next)
        self.Memory_instance.done_history.append(done)
        self.Memory_instance.rewards_history.append(reward)

        # Limit the state and reward history
        if len(self.Memory_instance.rewards_history) > self.Memory_instance.max_memory_length:
            del self.Memory_instance.rewards_history[:1]
            del self.Memory_instance.state_history[:1]
            del self.Memory_instance.state_next_history[:1]
            del self.Memory_instance.action_history[:1]
            del self.Memory_instance.done_history[:1]

        return self._rgb_to_grayscale(self.state), reward, done, info

    def _rgb_to_grayscale(self, img):
        return np.dot(img, [0.299, 0.587, 0.114]).astype(np.uint8)
