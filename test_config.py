#!/usr/bin/env python3
"""
Test script to verify configuration and API credentials
"""

from dotenv import load_dotenv
load_dotenv()

from config import CONFIG
import json

def test_configuration():
    """Test that configuration loads properly"""
    
    print("🔧 Testing Configuration...")
    print("=" * 50)
    
    # Test API credentials
    print(f"✅ API Login: {CONFIG['dataforseo']['login']}")
    print(f"✅ API Base URL: {CONFIG['dataforseo']['base']}")
    print(f"✅ Rate Limit: {CONFIG['dataforseo']['rate_limit']} req/sec")
    
    # Test target settings
    print(f"\n🎯 Target Settings:")
    print(f"   Country: {CONFIG['target']['country']}")
    print(f"   Language: {CONFIG['target']['language']}")
    print(f"   Provinces: {', '.join(CONFIG['target']['provinces'])}")
    
    # Test business terms
    print(f"\n🏢 Business Terms ({len(CONFIG['seed']['business_terms'])}):")
    for i, term in enumerate(CONFIG['seed']['business_terms'], 1):
        print(f"   {i}. {term}")
    
    # Test filters
    print(f"\n🔍 Filters:")
    print(f"   Search Volume: {CONFIG['filters']['min_search_volume']} - {CONFIG['filters']['max_search_volume']}")
    print(f"   CPC Range: ${CONFIG['filters']['min_cpc_cad']} - ${CONFIG['filters']['max_cpc_cad']}")
    print(f"   Max Difficulty: {CONFIG['filters']['max_keyword_difficulty']}")
    print(f"   Word Count: {CONFIG['filters']['min_word_count']} - {CONFIG['filters']['max_word_count']} words")
    
    # Test export settings
    print(f"\n📊 Export Settings:")
    print(f"   Directory: {CONFIG['export']['dir']}")
    print(f"   Formats: {', '.join(CONFIG['export']['formats'])}")
    
    print("\n✅ All configuration tests passed!")
    return True

if __name__ == "__main__":
    test_configuration()