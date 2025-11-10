#!/usr/bin/env python3
"""Test with the exact method that worked before"""

from simple_salesforce import Salesforce

USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"

print("Testing with NO security token (IP should be whitelisted)...")
print(f"Username: {USERNAME}")
print(f"Password: {PASSWORD}")

try:
    sf = Salesforce(
        username=USERNAME,
        password=PASSWORD,
        domain='login'
    )
    print(f"\n✅ SUCCESS!")
    print(f"Instance URL: {sf.instance_url}")
    print(f"Session ID: {sf.session_id[:20]}...")
    
    # Try a simple query
    result = sf.query("SELECT Id, Name FROM Organization LIMIT 1")
    if result['records']:
        print(f"Org Name: {result['records'][0]['Name']}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    print(f"\nError type: {type(e).__name__}")
    print(f"\nFull error: {repr(e)}")





