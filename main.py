import pygame
import numpy as np
from game import *

# CONSTANTS

EPISODES = 100000
DISCOUNT = 0.95
LEARNING_RATE = 0.05

epsilon = 0.6
START_DECAYING = 1
END_DECAYING = EPISODES
epsilon_decay = epsilon / (END_DECAYING - START_DECAYING)

INPUT_COUNT = 6
ACTIONS = 4

# observation space is 5 sensor inputs and velocity
OS_MIN = np.array([0, 0, 0, 0, 0, 0])
OS_MAX = np.array([101, 101, 101, 101, 101, 6])
DISCRETE_OS_SIZE = [16] * len(OS_MIN)
discrete_os_win_size = (OS_MAX - OS_MIN) / DISCRETE_OS_SIZE

def get_discrete_state(state):
    discrete_state = (state - OS_MIN) / discrete_os_win_size
    return tuple(discrete_state.astype(int))

def main():

    # q-learning initialization
    q_table = np.random.uniform(low = -100, high = -100, size=(DISCRETE_OS_SIZE + [ACTIONS]))

    # start training
    for episode in range(EPISODES):
        render = (episode % 200 == 0)
        total_reward = 0

        # pygame initialization
        fps = 100000
        pygame.init()
        clock = pygame.time.Clock()
        if render:
            screen = pygame.display.set_mode((SWIDTH, SHEIGHT))
            pygame.display.set_caption("QCar")
            fps = 60

        frame_counter = 0
        global epsilon
        running = True

        # initialize the environment
        start_x, start_y = 660, 160
        player = Car(start_x, start_y)
        track = Track("assets/track1.txt")
        reward_gates = RewardGates("assets/gates1.txt")
        sensors = [pygame.math.Vector2] * 5
        update_sensors(player, sensors)

        state = get_current_state(player, sensors, track)
        discrete_state = get_discrete_state(state)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 1. make optimal action from current q-table
            if np.random.random() > epsilon:
                action = np.argmax(q_table[discrete_state])
            else:
                action = np.random.randint(0, 4)
            
            x0, y0 = player.origin
            update_car(player, action)
            update_sensors(player, sensors)
            x1, y1 = player.origin

            # 2. get new state, reward and check for collision or end
            reward = math.sqrt((x0 - x1) * (x0 - x1) + (y0 - y1) * (y0 - y1)) / 5
            new_state = get_current_state(player, sensors, track)
            new_discrete_state = get_discrete_state(new_state)
            
            if check_car_reward(player, reward_gates):
                reward += 10

            if check_collision_car_track(player, track):
                reward -= 200
                running = False

            if frame_counter > 60 * 60:
                running = False

            if total_reward > 2000:
                running = False

            total_reward += reward

            # 3. perform updates to q-table
            if running:
                max_future_q = np.max(q_table[new_discrete_state])
                current_q = q_table[discrete_state + (action, )]
                new_q = (1.0 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
                q_table[discrete_state + (action,)] = new_q
            
            state = new_state
            discrete_state = new_discrete_state

            frame_counter += 1

            # draw

            if render:
                screen.fill(BLACK)
                
                draw_track(screen, track)
                draw_car(screen, player)
                draw_sensors(screen, player, sensors, track)
                draw_reward_gates(screen, reward_gates)

                pygame.display.flip()
            
            clock.tick(fps)
        
        if START_DECAYING <= episode <= END_DECAYING:
            epsilon = max(0.02, epsilon - epsilon_decay)

        if episode % 5000 == 0:
            np.save(f"qtables/{episode}-qtable.npy", q_table)
        
        if episode % 10 == 0:
            print(episode, total_reward)
            
        pygame.quit()

if __name__ == "__main__":
    main()