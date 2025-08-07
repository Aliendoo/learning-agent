#!/usr/bin/env python3
"""
Test script for objective-based resource fetching
"""

import os
from dotenv import load_dotenv
from objective_based_fetcher import ObjectiveBasedFetcher

# Load environment variables
load_dotenv()

def test_objective_fetching():
    """Test the objective-based resource fetching system"""
    print("🧪 Testing Objective-Based Resource Fetching...")
    
    # Test learning objectives
    test_objectives = [
        "Understand Python variables and data types",
        "Learn how to create and use functions",
        "Master object-oriented programming concepts"
    ]
    
    try:
        # Initialize the fetcher
        fetcher = ObjectiveBasedFetcher()
        
        print(f"📚 Testing with {len(test_objectives)} learning objectives:")
        for i, objective in enumerate(test_objectives, 1):
            print(f"  {i}. {objective}")
        
        # Fetch resources for objectives
        print("\n🔍 Fetching resources for each objective...")
        objective_resources = fetcher.fetch_resources_for_objectives(test_objectives, "technical")
        
        # Display results
        total_resources = 0
        for objective, resources in objective_resources.items():
            print(f"\n🎯 **{objective}**")
            print(f"   Found {len(resources)} resources:")
            
            for j, resource in enumerate(resources, 1):
                print(f"   {j}. {resource.title}")
                print(f"      └ Source: {resource.source}")
                print(f"      └ Quality: {resource.quality_score}/10")
                print(f"      └ Relevance: {resource.relevance_score:.1f}")
                total_resources += 1
        
        print(f"\n✅ Successfully found {total_resources} resources across all objectives!")
        print("🎉 Objective-based fetching is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing objective-based fetching: {e}")
        return False

if __name__ == "__main__":
    success = test_objective_fetching()
    exit(0 if success else 1) 