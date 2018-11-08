import marlo
import numpy as np
import pandas
import sklearn
import random
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.layers import MaxPooling2D,Flatten
from collections import deque
import pdb
import gym


# Notes:
# Observation only has text which is blank and vision under observation_n[0] dict
# env.action_space.sample() gives a random action from those available, applies to any env

def sendAgentToTrainingCamp(env, agent):
    goal_steps = 500
    initial_games = 10000
    batch_size = 16
    scores = deque(maxlen=50)
    for i in range(initial_games):
        reward = 0
        game_score = 0
        env.reset()
        state = env.last_image
        for j in range(goal_steps):
            print("Starting goal step: ", j, " of game: ", i, " avg score: ", np.mean(scores))
            action = agent.act(state)
            new_state, reward, done, info = env.step(action)
            agent.memory.append((state,action, reward, new_state, done))

            if done:
                print("Game: ",i ," complete, score: " , game_score," last 50 scores avg: ", np.mean(scores), " epsilon ", agent.epsilon)
                scores.append(game_score)
                break
            game_score += reward
            #env.render()
            state = new_state


            if len(agent.memory) > batch_size:
                randomBatch = random.sample(agent.memory, batch_size)
                agent.replay(randomBatch)
    return scores

class agent:
    def __init__(self, observation_shape, action_size):
        self.observation_shape = observation_shape
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9999
        self.learning_rate = 0.001
        self.model = self.create_model()

    def create_model(self):
        model = Sequential()
        # Need to check that this is processing the colour bands correctly <- have checked this and:
        # the default is channels last which is what we have
        # This max pooling layer is quite extreme because of memory limits on machine
        model.add(MaxPooling2D(pool_size=(8, 8), input_shape=(self.observation_shape)))
        model.add(Conv2D(8, (3, 3)))
        # Flatten needed to get a single vector as output otherwise get a matrix
        model.add(Flatten())
        model.add(Dense(128,activation='relu'))
        model.add(Dense(64,activation='relu'))
        model.add(Dense(self.action_size,activation='linear'))
        model.compile(loss='mse', optimizer='adam')
        return model

    def act(self, state):
        # Randomly choose to take a randomly chosen action to allow exploration
        # When epsilon is high, higher chance, therefore decrease it overtime
        # This then results in exploration early on with greater exploitation later
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state.reshape([-1, 600, 800, 3]))
        return np.argmax(act_values[0])

    def replay(self, batch):
        x_train = []
        y_train = []
        for state, action, reward, newState, done in batch:
            if done:
                # Set the reward for finishing the game
                target_q = reward
            else:
                #pdb.set_trace()
                #self.model.predict(newState.reshape([-1, 600, 800, 3]))
                target_q = reward + self.gamma * np.amax(self.model.predict(newState.reshape([-1, 600, 800, 3])))
            prediction = self.model.predict(newState.reshape([-1, 600, 800, 3]))
            prediction[0][action] = target_q
            x_train.append(state)
            y_train.append(prediction[0])
        self.model.fit(np.asarray(x_train),np.asarray(y_train),epochs=1,verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        else:
            self.epsilon = 0
        return

def main():
    client_pool = [('127.0.0.1', 10000)]
    join_tokens = marlo.make('MarLo-FindTheGoal-v0', params={"client_pool": client_pool})
    # As this is a single agent scenario,
    # there will just be a single token
    assert len(join_tokens) == 1
    join_token = join_tokens[0]

    env = marlo.init(join_token)

    # Get the number of available states and actions
    observation_shape = env.observation_space.shape
    action_size = env.action_space.n
    myagent = agent(observation_shape, action_size)
    scores = sendAgentToTrainingCamp(env, myagent)
    print (scores)
    return

if __name__ == "__main__":
    main()