#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
"""
import sys
from pathlib import Path

def test_imports():
    """Test all module imports"""
    try:
        # Test utils
        from utils.data_loader import discover_campaigns, load_campaign_data
        print("✅ Data loader imports working")
        
        from utils.clustering_engine import prepare_text_features
        print("✅ Clustering engine imports working")
        
        from utils.export_utils import export_to_google_ads
        print("✅ Export utils imports working")
        
        # Test components
        from components.sidebar import render_sidebar
        from components.metrics import render_metrics_row
        from components.visualizations import create_opportunity_scatter
        print("✅ Component imports working")
        
        # Test pages
        from pages import overview, actionable, clustering
        print("✅ Page imports working")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_discovery():
    """Test campaign data discovery"""
    try:
        from utils.data_loader import discover_campaigns
        
        campaigns = discover_campaigns()
        if campaigns:
            print(f"✅ Found {len(campaigns)} campaigns:")
            for name in campaigns.keys():
                print(f"  - {name}")
            return True
        else:
            print("⚠️  No campaigns found")
            return False
    except Exception as e:
        print(f"❌ Data discovery error: {e}")
        return False

def test_data_loading():
    """Test loading campaign data"""
    try:
        from utils.data_loader import discover_campaigns, load_campaign_data
        
        campaigns = discover_campaigns()
        if not campaigns:
            print("❌ No campaigns to test loading")
            return False
        
        # Test loading first campaign
        first_campaign = list(campaigns.keys())[0]
        campaign_path = campaigns[first_campaign]['path']
        
        print(f"Testing data loading for: {first_campaign}")
        data = load_campaign_data(campaign_path)
        
        print(f"✅ Loaded data with keys: {list(data.keys())}")
        
        if 'keywords' in data:
            print(f"✅ Keywords data: {len(data['keywords'])} rows")
        
        if 'competitor_keywords' in data:
            print(f"✅ Competitor data: {len(data['competitor_keywords'])} rows")
        
        return True
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Dashboard Components")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("Data Discovery", test_data_discovery),
        ("Data Loading", test_data_loading),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 20)
        result = test_func()
        results.append((name, result))
    
    print("\n🎯 Test Summary")
    print("=" * 40)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🚀 All tests passed! Dashboard is ready to launch.")
        print("\nTo start the dashboard:")
        print("cd dashboard && streamlit run dashboard.py")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)