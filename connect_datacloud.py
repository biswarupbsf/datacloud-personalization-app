#!/usr/bin/env python3
"""
Connect to Salesforce Data Cloud org (sftutor)
"""

import sys
import os
import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.simple_auth import SimpleAuthConnector

def connect_to_datacloud():
    """Connect to Data Cloud org"""
    print("=" * 80)
    print("🌩️  SALESFORCE DATA CLOUD CONNECTION")
    print("=" * 80)
    print("\nOrg: SFtutor")
    print("Using SOAP Authentication (no security token required)")
    print()
    
    # Get credentials
    username = input("Enter username (email): ").strip()
    password = getpass.getpass("Enter password: ")
    
    if not username or not password:
        print("❌ Username and password are required!")
        return None
    
    print("\n🔄 Connecting to Salesforce...")
    
    # Create connector
    connector = SimpleAuthConnector()
    
    try:
        # Connect using SOAP
        connector.connect_soap(username, password)
        
        print("✅ Connection successful!")
        print()
        
        # Get org info
        org_info = connector.get_org_info()
        
        print("📊 Organization Information:")
        print("-" * 80)
        print(f"Org Name: {org_info.get('org_name', 'N/A')}")
        print(f"Org Type: {org_info.get('org_type', 'N/A')}")
        print(f"Instance: {org_info.get('instance', 'N/A')}")
        print(f"Org ID: {org_info.get('org_id', 'N/A')}")
        print(f"Instance URL: {org_info.get('instance_url', 'N/A')}")
        print(f"Username: {org_info.get('username', 'N/A')}")
        print(f"Connected at: {org_info.get('connected_at', 'N/A')}")
        print("-" * 80)
        print()
        
        return connector
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print()
        print("Possible issues:")
        print("  • Wrong username or password")
        print("  • Account locked or suspended")
        print("  • IP not whitelisted (security token may be required)")
        print("  • Network connectivity issues")
        return None

def query_data_cloud_objects(connector):
    """Query Data Cloud objects"""
    if not connector or not connector.is_connected():
        print("❌ Not connected to Salesforce")
        return
    
    print("\n🔍 QUERYING DATA CLOUD OBJECTS")
    print("=" * 80)
    
    try:
        # Query Data Lake Model objects (DLM)
        print("\n📊 Searching for Data Lake Model (DLM) objects...")
        
        # This will list custom objects that end with __dlm
        sobjects_response = connector.sf.describe()
        dlm_objects = [obj for obj in sobjects_response['sobjects'] 
                      if obj['name'].endswith('__dlm')]
        
        if dlm_objects:
            print(f"\n✅ Found {len(dlm_objects)} Data Lake Model objects:")
            print("-" * 80)
            for obj in dlm_objects:
                print(f"  • {obj['label']} ({obj['name']})")
            print("-" * 80)
        else:
            print("\n⚠️  No Data Lake Model objects found")
        
        # Query Individual object
        print("\n📊 Querying Individual object...")
        try:
            individual_query = connector.sf.query("SELECT COUNT() FROM Individual")
            count = individual_query['totalSize']
            print(f"✅ Found {count} Individual records")
        except Exception as e:
            print(f"⚠️  Could not query Individual: {str(e)}")
        
        # Query Data Model Objects (DMO)
        print("\n📊 Searching for Data Model Objects (DMO)...")
        dmo_objects = [obj for obj in sobjects_response['sobjects'] 
                      if '__dmo' in obj['name'].lower() or 'DataModel' in obj['name']]
        
        if dmo_objects:
            print(f"\n✅ Found {len(dmo_objects)} Data Model Objects:")
            print("-" * 80)
            for obj in dmo_objects:
                print(f"  • {obj['label']} ({obj['name']})")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error querying objects: {str(e)}")

def main():
    """Main function"""
    # Connect
    connector = connect_to_datacloud()
    
    if connector:
        # Query objects
        query_data_cloud_objects(connector)
        
        print("\n" + "=" * 80)
        print("✅ CONNECTION ESTABLISHED AND READY")
        print("=" * 80)
        print("\nYou can now use this connector to query and manage Data Cloud objects.")
        print()
        
        # Save connection info
        connection_file = 'data/datacloud_connection.json'
        import json
        with open(connection_file, 'w') as f:
            json.dump({
                'connected': True,
                'org_info': connector.get_org_info()
            }, f, indent=2)
        print(f"💾 Connection info saved to: {connection_file}")
        print()
        
        return connector
    else:
        print("\n❌ Failed to establish connection")
        return None

if __name__ == '__main__':
    main()





