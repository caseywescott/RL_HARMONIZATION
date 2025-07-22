#!/usr/bin/env python3
"""
Generate example MIDI demonstration using the hybrid harmonization system.
Uses the existing realms2 melody as a starting point.
"""

import requests
import time
import os

def test_hybrid_harmonization():
    """Test the hybrid harmonization system with the realms2 melody."""
    
    print("🎵 Hybrid Harmonization System - Example Generation")
    print("=" * 60)
    
    # Check if the realms2 file exists
    input_file = "realms2_harmonized.mid"
    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found!")
        return
    
    print(f"📁 Using input melody: {input_file}")
    
    # Create output directory if it doesn't exist
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test different methods
    methods = [
        ("rl", "RL-Only Harmonization"),
        ("coconet", "Coconet-Only Harmonization"), 
        ("hybrid", "Hybrid (Coconet → RL Optimization)")
    ]
    
    results = []
    
    for method, description in methods:
        print(f"\n🎼 Testing {description}...")
        
        output_file = os.path.join(output_dir, f"example_{method}_output.mid")
        
        try:
            # Make API request
            with open(input_file, 'rb') as f:
                files = {'file': f}
                params = {
                    'method': method,
                    'temperature': 0.8
                }
                
                response = requests.post(
                    'http://localhost:8000/harmonize',
                    files=files,
                    params=params
                )
            
            if response.status_code == 200:
                # Save the output
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                print(f"   ✅ Success! Saved to: {output_file}")
                print(f"   📊 File size: {file_size} bytes")
                
                results.append({
                    'method': method,
                    'description': description,
                    'output_file': output_file,
                    'file_size': file_size,
                    'status': 'success'
                })
            else:
                print(f"   ❌ Failed with status code: {response.status_code}")
                results.append({
                    'method': method,
                    'description': description,
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'method': method,
                'description': description,
                'status': 'error',
                'error': str(e)
            })
    
    # Summary
    print(f"\n📊 Generation Summary:")
    print("-" * 40)
    
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['description']}")
            print(f"   Output: {result['output_file']}")
            print(f"   Size: {result['file_size']} bytes")
        else:
            print(f"❌ {result['description']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Create a comparison analysis
    print(f"\n🔍 File Comparison:")
    print("-" * 40)
    
    successful_results = [r for r in results if r['status'] == 'success']
    if successful_results:
        print(f"Input melody: {input_file}")
        for result in successful_results:
            print(f"{result['method'].upper()}: {result['file_size']} bytes")
    
    print(f"\n🎵 Example generation complete!")
    print(f"Files created in {output_dir}/")

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get('http://localhost:8000/status', timeout=5)
        if response.status_code == 200:
            print("✅ Hybrid harmonization server is running")
            test_hybrid_harmonization()
        else:
            print("❌ Server responded with error status")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to harmonization server")
        print("   Make sure the server is running on http://localhost:8000")
        print("   Run: docker run -d -p 8000:8000 hybrid-harmonization-server")
    except Exception as e:
        print(f"❌ Error checking server: {e}") 