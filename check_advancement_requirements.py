#!/usr/bin/env python3
"""
Simple script to check level advancement requirements
"""

import requests
import json

def check_requirements():
    """Check what's needed for level advancement"""
    
    # Get user credentials
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    # Login
    response = requests.post("http://localhost:8000/api/v1/auth/login", data={
        "username": email,
        "password": password
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Checking Level Advancement Requirements")
    print("=" * 50)
    
    # Use the new debug endpoint
    response = requests.get("http://localhost:8000/api/v1/progress/debug-advancement", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get debug info: {response.text}")
        return
    
    debug_info = response.json()
    
    print(f"Current Level: {debug_info['user_level']} ({debug_info['current_level_name']})")
    print(f"Can Advance: {'✅' if debug_info['can_advance'] else '❌'}")
    
    if not debug_info['can_advance']:
        print(f"Reason: {debug_info['advancement_reason']}")
    
    print("\nSection Requirements (need 75% average):")
    for section in debug_info['section_requirements']:
        status = "✅" if section['meets_requirement'] else "❌"
        print(f"  {status} {section['section_code']}: {section['average_score']:.1f}%")
    
    print("\nLevel Final Requirement (need 80%):")
    final = debug_info['level_final_requirement']
    if final['attempted']:
        status = "✅" if final['meets_requirement'] else "❌"
        print(f"  {status} Score: {final['score']:.1f}%")
    else:
        print("  ❌ Not attempted")
    
    print("\n" + "=" * 50)
    
    if not debug_info['can_advance']:
        print("To advance to the next level, you need to:")
        
        # Check what's missing
        missing_sections = [s for s in debug_info['section_requirements'] if not s['meets_requirement']]
        if missing_sections:
            print("\n📚 Complete section requirements:")
            for section in missing_sections:
                if section['average_score'] == 0:
                    print(f"  • Take quizzes for all topics in {section['section_code']} ({section['section_name']})")
                else:
                    print(f"  • Improve {section['section_code']} average from {section['average_score']:.1f}% to 75%")
        
        if not final['meets_requirement']:
            if not final['attempted']:
                print(f"\n🎯 Take the {debug_info['current_level_name']} Level Final exam")
            else:
                print(f"\n🎯 Retake the Level Final (current: {final['score']:.1f}%, need: 80%)")
    else:
        print("🎉 All requirements met! Level advancement should occur automatically.")
        print("If you're still not seeing the next level, try:")
        print("  • Refresh your browser")
        print("  • Log out and log back in")
        print("  • Clear browser cache")

if __name__ == "__main__":
    try:
        check_requirements()
    except Exception as e:
        print(f"❌ Error: {e}")