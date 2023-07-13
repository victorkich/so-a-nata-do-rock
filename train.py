import numpy as np
from collections import deque
import torch
import wandb
import argparse
from buffer import ReplayBuffer
from utils import save
from environment import Environment
import random
from agent import SAC


def get_config():
    parser = argparse.ArgumentParser(description='RL')
    parser.add_argument("--run_name", type=str, default="SAC", help="Run name, default: SAC")
    parser.add_argument("--episodes", type=int, default=10000, help="Number of episodes, default: 100")
    parser.add_argument("--buffer_size", type=int, default=100_000, help="Maximal training dataset size, default: 100_000")
    parser.add_argument("--seed", type=int, default=1, help="Seed, default: 1")
    parser.add_argument("--log_video", type=int, default=0, help="Log agent behaviour to wanbd when set to 1, default: 0")
    parser.add_argument("--save_every", type=int, default=100, help="Saves the network every x epochs, default: 25")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size, default: 256")
    
    args = parser.parse_args()
    return args


def train(config):
    np.random.seed(config.seed)
    random.seed(config.seed)
    torch.manual_seed(config.seed)
    env = Environment()

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    steps = 0
    a1_average10 = deque(maxlen=10)
    a2_average10 = deque(maxlen=10)
    total_steps = 0
    
    with wandb.init(project="SAC_Discrete", name=config.run_name, config=config):
        a1 = SAC(state_size=53, action_size=4, device=device)
        a2 = SAC(state_size=53, action_size=4, device=device)

        a1_buffer = ReplayBuffer(buffer_size=config.buffer_size, batch_size=config.batch_size, device=device)
        a2_buffer = ReplayBuffer(buffer_size=config.buffer_size, batch_size=config.batch_size, device=device)
        
        # if config.log_video:
        #    env = gym.wrappers.Monitor(env, './video', video_callable=lambda x: x%10==0, force=True)

        for i in range(1, config.episodes+1):
            env.reset()

            episode_steps = 0
            a1_rewards = 0
            a2_rewards = 0
            for _ in range(1000):
                a1_state = env.get_state(robot_id=1)
                a1_action = a1.get_action(a1_state)
                steps += 1
                a1_next_state, a1_reward, a1_done = env.step(a1_action, robot_id=1)
                a1_buffer.add(a1_state, a1_action, a1_reward, a1_next_state, a1_done)
                if a1_buffer.__len__() >= 25000:
                    a1_policy_loss, a1_alpha_loss, a1_bellmann_error1, a1_bellmann_error2, a1_current_alpha = a1.learn(
                        steps, a1_buffer.sample(), gamma=0.99)

                if a1_done:
                    break

                a2_state = env.get_state(robot_id=2)
                a2_action = a2.get_action(a2_state)
                a2_next_state, a2_reward, a2_done = env.step(a2_action, robot_id=2)
                a2_buffer.add(a2_state, a2_action, a2_reward, a2_next_state, a2_done)
                if a2_buffer.__len__() >= 25000:
                    a2_policy_loss, a2_alpha_loss, a2_bellmann_error1, a2_bellmann_error2, a2_current_alpha = a2.learn(
                        steps, a2_buffer.sample(), gamma=0.99)

                a1_rewards += a1_reward
                a2_rewards += a2_reward
                episode_steps += 1

                if a2_done:
                    break

            a1_average10.append(a1_rewards)
            a2_average10.append(a2_rewards)
            total_steps += episode_steps

            if a1_buffer.__len__() >= 25000:
                print("Agent 1 -- Episode: {} | Reward: {} | Policy Loss: {} | Steps: {}".format(i, a1_rewards,
                                                                                                 a1_policy_loss, steps))
                wandb.log({"Agent 1 Reward": a1_rewards,
                       "Agent 1 Average10": np.mean(a1_average10),
                       "Agent 1 Steps": total_steps,
                       "Agent 1 Policy Loss": a1_policy_loss,
                       "Agent 1 Alpha Loss": a1_alpha_loss,
                       "Agent 1 Bellmann error 1": a1_bellmann_error1,
                       "Agent 1 Bellmann error 2": a1_bellmann_error2,
                       "Agent 1 Alpha": a1_current_alpha,
                       "Agent 1 Steps": steps,
                       "Agent 1 Episode": i,
                       "Agent 1 Buffer size": a1_buffer.__len__()})

            if a2_buffer.__len__() >= 25000:
                print("Agent 2 -- Episode: {} | Reward: {} | Policy Loss: {} | Steps: {}".format(i, a2_rewards,
                                                                                                 a2_policy_loss, steps))
                wandb.log({"Agent 2 Reward": a2_rewards,
                       "Agent 2 Average10": np.mean(a2_average10),
                       "Agent 2 Steps": total_steps,
                       "Agent 2 Policy Loss": a2_policy_loss,
                       "Agent 2 Alpha Loss": a2_alpha_loss,
                       "Agent 2 Bellmann error 1": a2_bellmann_error1,
                       "Agent 2 Bellmann error 2": a2_bellmann_error2,
                       "Agent 2 Alpha": a2_current_alpha,
                       "Agent 2 Steps": steps,
                       "Agent 2 Episode": i,
                       "Agent 2 Buffer size": a2_buffer.__len__()})

            # if (i % 10 == 0) and config.log_video:
            #    mp4list = glob.glob('video/*.mp4')
            #    if len(mp4list) > 1:
            #        mp4 = mp4list[-2]
            #        wandb.log({"gameplays": wandb.Video(mp4, caption='episode:
            #        '+str(i-10), fps=4, format="gif"), "Episode": i})

            if i % config.save_every == 0:
                save(config, save_name="a1_SAC_discrete", model=a1.actor_local, wandb=wandb, ep=0)
                save(config, save_name="a2_SAC_discrete", model=a2.actor_local, wandb=wandb, ep=0)


if __name__ == "__main__":
    config = get_config()
    train(config)
