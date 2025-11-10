#!/usr/bin/env python3
"""Test Salesforce login directly"""

from simple_salesforce import Salesforce

USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"
SECURITY_TOKEN = "yHuCHxO44Oaf8No7mJmgUxAP"

print("Testing Salesforce login...")
print(f"Username: {USERNAME}")
print(f"Password: {'*' * len(PASSWORD)}")
print(f"Token: {SECURITY_TOKEN[:10]}...")

try:
    print("\n1. Trying with security_token parameter...")
    sf = Salesforce(
        username=USERNAME,
        password=PASSWORD,
        security_token=SECURITY_TOKEN,
        domain='login'
    )
    print("✅ SUCCESS with security_token parameter!")
    print(f"   Instance: {sf.instance_url}")
except Exception as e:
    print(f"❌ Failed: {e}")
    
    try:
        print("\n2. Trying without token (IP whitelisted)...")
        sf = Salesforce(
            username=USERNAME,
            password=PASSWORD,
            domain='login'
        )
        print("✅ SUCCESS without token!")
        print(f"   Instance: {sf.instance_url}")
    except Exception as e2:
        print(f"❌ Failed: {e2}")
        
        try:
            print("\n3. Trying with concatenated password...")
            sf = Salesforce(
                username=USERNAME,
                password=PASSWORD + SECURITY_TOKEN,
                domain='login'
            )
            print("✅ SUCCESS with concatenated password!")
            print(f"   Instance: {sf.instance_url}")
        except Exception as e3:
            print(f"❌ Failed: {e3}")
            print("\n❌ ALL LOGIN METHODS FAILED")





