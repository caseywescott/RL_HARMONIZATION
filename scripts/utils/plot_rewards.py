#!/usr/bin/env python3
"""
Plot reward curve from training history
"""

import numpy as np
import matplotlib.pyplot as plt

def plot_reward_curve():
    """Load and plot the reward curve from training"""
    try:
        # Load reward history
        rewards = np.load('reward_history.npy')
        
        print(f"Loaded {len(rewards)} reward points")
        print(f"Reward range: {rewards.min():.3f} to {rewards.max():.3f}")
        print(f"Average reward: {rewards.mean():.3f}")
        print(f"Latest reward: {rewards[-1]:.3f}")
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Plot raw rewards
        plt.subplot(1, 2, 1)
        plt.plot(rewards, alpha=0.6, color='blue', linewidth=0.5)
        plt.title('Raw Reward History')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.grid(True, alpha=0.3)
        
        # Plot moving average for trend
        window_size = min(100, len(rewards) // 10)  # Adaptive window size
        if window_size > 1:
            moving_avg = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
            plt.plot(range(window_size-1, len(rewards)), moving_avg, 
                    color='red', linewidth=2, label=f'{window_size}-episode moving average')
            plt.legend()
        
        # Plot smoothed trend
        plt.subplot(1, 2, 2)
        
        # Calculate statistics
        episode_groups = 20  # Group episodes for statistics
        group_size = len(rewards) // episode_groups
        if group_size > 0:
            group_means = []
            group_stds = []
            episode_numbers = []
            
            for i in range(episode_groups):
                start_idx = i * group_size
                end_idx = start_idx + group_size
                if end_idx <= len(rewards):
                    group_rewards = rewards[start_idx:end_idx]
                    group_means.append(np.mean(group_rewards))
                    group_stds.append(np.std(group_rewards))
                    episode_numbers.append(end_idx)
            
            plt.errorbar(episode_numbers, group_means, yerr=group_stds, 
                        fmt='o-', capsize=5, capthick=2, linewidth=2, markersize=6)
            plt.title('Reward Statistics by Episode Groups')
            plt.xlabel('Episode')
            plt.ylabel('Average Reward')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('reward_curve.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print analysis
        print("\n=== TRAINING ANALYSIS ===")
        if len(rewards) >= 2:
            recent_avg = np.mean(rewards[-100:]) if len(rewards) >= 100 else np.mean(rewards[-len(rewards)//4:])
            early_avg = np.mean(rewards[:100]) if len(rewards) >= 100 else np.mean(rewards[:len(rewards)//4])
            
            improvement = recent_avg - early_avg
            print(f"Early episodes average: {early_avg:.3f}")
            print(f"Recent episodes average: {recent_avg:.3f}")
            print(f"Improvement: {improvement:.3f}")
            
            if improvement > 0.1:
                print("✅ Training is showing clear improvement!")
            elif improvement > 0:
                print("📈 Training is improving slowly")
            elif improvement > -0.1:
                print("➡️ Training is stable")
            else:
                print("📉 Training may need adjustment")
        
        # Check for convergence
        if len(rewards) >= 200:
            last_200 = rewards[-200:]
            last_100 = rewards[-100:]
            last_50 = rewards[-50:]
            
            recent_trend = np.mean(last_50) - np.mean(last_100)
            overall_trend = np.mean(last_100) - np.mean(last_200)
            
            print(f"\nRecent trend (last 50 vs 100): {recent_trend:.3f}")
            print(f"Overall trend (last 100 vs 200): {overall_trend:.3f}")
            
            if abs(recent_trend) < 0.05 and abs(overall_trend) < 0.05:
                print("🔄 Training appears to be converging")
        
    except Exception as e:
        print(f"Error plotting rewards: {e}")
        return False
    
    return True

if __name__ == "__main__":
    plot_reward_curve() 