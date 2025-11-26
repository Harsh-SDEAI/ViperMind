#!/usr/bin/env python3
"""
Script to manage progression configuration
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_user_token():
    """Get user token"""
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def show_current_config(headers):
    """Show current progression configuration"""
    response = requests.get(f"{BASE_URL}/progress/config", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get config: {response.text}")
        return None
    
    config = response.json()
    
    print("📋 Current Progression Configuration")
    print("=" * 50)
    
    print("\n🎯 Assessment Pass Thresholds:")
    thresholds = config["thresholds"]
    print(f"  Quiz Pass: {thresholds['quiz_pass_threshold']}%")
    print(f"  Section Test Pass: {thresholds['section_test_pass_threshold']}%")
    print(f"  Level Final Pass: {thresholds['level_final_pass_threshold']}%")
    
    print("\n📚 Section Requirements:")
    section_req = config["section_requirements"]
    print(f"  Section Average Required: {section_req['average_requirement']}%")
    print(f"  Section Test Required: {section_req['test_requirement']}%")
    print(f"  Topic Quiz Required: {section_req['topic_quiz_requirement']}%")
    
    print("\n🎓 Level Requirements:")
    level_req = config["level_requirements"]
    print(f"  Section Average Required: {level_req['section_average_requirement']}%")
    print(f"  Level Final Required: {level_req['final_requirement']}%")
    
    print("\n🔄 Attempt Limits:")
    print(f"  Quiz Max Attempts: {thresholds['quiz_max_attempts']}")
    print(f"  Section Test Max Attempts: {thresholds['section_test_max_attempts']}")
    print(f"  Level Final Max Attempts: {thresholds['level_final_max_attempts']}")
    
    return config

def update_config(headers):
    """Update progression configuration"""
    print("\n🔧 Update Progression Configuration")
    print("=" * 50)
    
    print("Choose what to update:")
    print("1. Section average requirement (for level advancement)")
    print("2. Level final requirement (for level advancement)")
    print("3. Quiz pass threshold")
    print("4. Section test pass threshold")
    print("5. Level final pass threshold")
    print("6. Make it easier (lower all thresholds)")
    print("7. Make it harder (raise all thresholds)")
    print("8. Custom update")
    
    choice = input("\nEnter choice (1-8): ").strip()
    
    updates = {}
    
    if choice == "1":
        new_value = float(input("Enter new section average requirement (current: varies): "))
        updates = {
            "section_average_requirement": new_value,
            "level_section_average_requirement": new_value
        }
    
    elif choice == "2":
        new_value = float(input("Enter new level final requirement (current: varies): "))
        updates = {
            "level_final_pass_threshold": new_value,
            "level_final_requirement": new_value
        }
    
    elif choice == "3":
        new_value = float(input("Enter new quiz pass threshold: "))
        updates = {"quiz_pass_threshold": new_value}
    
    elif choice == "4":
        new_value = float(input("Enter new section test pass threshold: "))
        updates = {"section_test_pass_threshold": new_value}
    
    elif choice == "5":
        new_value = float(input("Enter new level final pass threshold: "))
        updates = {"level_final_pass_threshold": new_value}
    
    elif choice == "6":
        # Make it easier
        updates = {
            "quiz_pass_threshold": 60.0,
            "section_test_pass_threshold": 65.0,
            "level_final_pass_threshold": 70.0,
            "section_average_requirement": 65.0,
            "level_section_average_requirement": 65.0,
            "level_final_requirement": 70.0,
            "topic_quiz_requirement": 60.0
        }
        print("Making all thresholds easier...")
    
    elif choice == "7":
        # Make it harder
        updates = {
            "quiz_pass_threshold": 80.0,
            "section_test_pass_threshold": 85.0,
            "level_final_pass_threshold": 90.0,
            "section_average_requirement": 85.0,
            "level_section_average_requirement": 85.0,
            "level_final_requirement": 90.0,
            "topic_quiz_requirement": 80.0
        }
        print("Making all thresholds harder...")
    
    elif choice == "8":
        print("Enter custom updates (key=value format, comma separated):")
        print("Available keys: quiz_pass_threshold, section_test_pass_threshold, level_final_pass_threshold,")
        print("                section_average_requirement, level_final_requirement, etc.")
        custom_input = input("Updates: ")
        
        for update in custom_input.split(","):
            if "=" in update:
                key, value = update.strip().split("=", 1)
                try:
                    updates[key.strip()] = float(value.strip())
                except ValueError:
                    updates[key.strip()] = value.strip()
    
    else:
        print("Invalid choice")
        return
    
    if not updates:
        print("No updates specified")
        return
    
    # Apply updates
    response = requests.post(f"{BASE_URL}/progress/config/update", 
                           json=updates, 
                           headers=headers)
    
    if response.status_code == 200:
        print("✅ Configuration updated successfully!")
        result = response.json()
        print(f"Updated: {list(updates.keys())}")
    else:
        print(f"❌ Failed to update config: {response.text}")

def main():
    """Main function"""
    try:
        token = get_user_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        while True:
            print("\n🎛️  Progression Configuration Manager")
            print("=" * 50)
            print("1. Show current configuration")
            print("2. Update configuration")
            print("3. Quick fix - Lower section requirements to 50%")
            print("4. Quick fix - Lower level final requirement to 60%")
            print("5. Reset to defaults")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == "1":
                show_current_config(headers)
            
            elif choice == "2":
                show_current_config(headers)
                update_config(headers)
            
            elif choice == "3":
                # Quick fix for section requirements
                updates = {
                    "section_average_requirement": 50.0,
                    "level_section_average_requirement": 50.0
                }
                response = requests.post(f"{BASE_URL}/progress/config/update", 
                                       json=updates, headers=headers)
                if response.status_code == 200:
                    print("✅ Section requirements lowered to 50%")
                else:
                    print(f"❌ Failed: {response.text}")
            
            elif choice == "4":
                # Quick fix for level final
                updates = {
                    "level_final_pass_threshold": 60.0,
                    "level_final_requirement": 60.0
                }
                response = requests.post(f"{BASE_URL}/progress/config/update", 
                                       json=updates, headers=headers)
                if response.status_code == 200:
                    print("✅ Level final requirement lowered to 60%")
                else:
                    print(f"❌ Failed: {response.text}")
            
            elif choice == "5":
                # Reset to defaults
                updates = {
                    "quiz_pass_threshold": 70.0,
                    "section_test_pass_threshold": 75.0,
                    "level_final_pass_threshold": 80.0,
                    "section_average_requirement": 75.0,
                    "level_final_requirement": 80.0,
                    "topic_quiz_requirement": 70.0
                }
                response = requests.post(f"{BASE_URL}/progress/config/update", 
                                       json=updates, headers=headers)
                if response.status_code == 200:
                    print("✅ Configuration reset to defaults")
                else:
                    print(f"❌ Failed: {response.text}")
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("Invalid choice")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()