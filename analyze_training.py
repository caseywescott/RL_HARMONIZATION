#!/usr/bin/env python3
"""
Quick analysis of training progress
"""

import numpy as np

def analyze_training():
    """Analyze the training progress"""
    try:
        rewards = np.load('reward_history.npy')
        
        print("=== RL HARMONIZATION TRAINING ANALYSIS ===")
        print(f"Total episodes completed: {len(rewards)}")
        print(f"Reward range: {rewards.min():.3f} to {rewards.max():.3f}")
        print(f"Overall average reward: {rewards.mean():.3f}")
        print(f"Latest reward: {rewards[-1]:.3f}")
        
        # Analyze improvement
        if len(rewards) >= 100:
            first_100 = rewards[:100]
            last_100 = rewards[-100:]
            
            print(f"\nFirst 100 episodes average: {first_100.mean():.3f}")
            print(f"Last 100 episodes average: {last_100.mean():.3f}")
            improvement = last_100.mean() - first_100.mean()
            print(f"Improvement: {improvement:.3f}")
            
            if improvement > 0.5:
                print("✅ EXCELLENT: Training is showing significant improvement!")
            elif improvement > 0.1:
                print("📈 GOOD: Training is improving steadily")
            elif improvement > 0:
                print("➡️ SLOW: Training is improving slowly")
            elif improvement > -0.1:
                print("🔄 STABLE: Training has plateaued")
            else:
                print("📉 CONCERN: Training may need adjustment")
        
        # Check recent trend
        if len(rewards) >= 500:
            last_500 = rewards[-500:]
            last_100 = rewards[-100:]
            
            recent_trend = last_100.mean() - last_500.mean()
            print(f"\nRecent trend (last 100 vs last 500): {recent_trend:.3f}")
            
            if recent_trend > 0.1:
                print("🚀 Still improving recently!")
            elif recent_trend > -0.1:
                print("➡️ Recent performance is stable")
            else:
                print("⚠️ Recent performance may be declining")
        
        # Check convergence
        if len(rewards) >= 1000:
            last_1000 = rewards[-1000:]
            last_500 = rewards[-500:]
            last_100 = rewards[-100:]
            
            # Check if variance is decreasing (convergence indicator)
            early_var = np.var(rewards[:1000])
            recent_var = np.var(rewards[-1000:])
            
            print(f"\nVariance analysis:")
            print(f"Early episodes variance: {early_var:.3f}")
            print(f"Recent episodes variance: {recent_var:.3f}")
            
            if recent_var < early_var * 0.5:
                print("🔄 Training appears to be converging (reduced variance)")
            elif recent_var < early_var:
                print("📊 Training is becoming more consistent")
            else:
                print("📈 Training is still exploring (high variance)")
        
        # Performance milestones
        print(f"\n=== PERFORMANCE MILESTONES ===")
        milestones = [100, 500, 1000, 5000, 10000]
        for milestone in milestones:
            if len(rewards) >= milestone:
                milestone_avg = np.mean(rewards[:milestone])
                print(f"Episodes {milestone}: Average reward = {milestone_avg:.3f}")
        
        # Current status
        print(f"\n=== CURRENT STATUS ===")
        print(f"Training has completed {len(rewards)} episodes")
        print(f"Current average reward: {rewards.mean():.3f}")
        print(f"Best single episode: {rewards.max():.3f}")
        print(f"Worst single episode: {rewards.min():.3f}")
        
        # Recommendations
        print(f"\n=== RECOMMENDATIONS ===")
        if len(rewards) >= 10000:
            if rewards[-100:].mean() > rewards.mean():
                print("✅ Training is performing well! Consider:")
                print("   - Continue training for more episodes")
                print("   - Test the model on new melodies")
                print("   - Save the current model")
            else:
                print("⚠️ Training may have plateaued. Consider:")
                print("   - Adjusting learning rate")
                print("   - Modifying reward function weights")
                print("   - Testing current model performance")
        else:
            print("🔄 Training is still in progress. Continue training for better results.")
        
    except Exception as e:
        print(f"Error analyzing training: {e}")

if __name__ == "__main__":
    analyze_training() 