"""
Data Manager
Handles CRUD operations on Salesforce objects
"""

import random
from datetime import datetime

class DataManager:
    
    def get_available_objects(self, sf):
        """Get list of available Salesforce objects"""
        try:
            # Get commonly used objects
            common_objects = [
                'Individual', 'Contact', 'Account', 'Lead', 'Opportunity',
                'Campaign', 'CampaignMember', 'ContactPointEmail',
                'Order', 'Product2', 'Asset'
            ]
            
            objects_info = []
            for obj_name in common_objects:
                try:
                    desc = sf.__getattr__(obj_name).describe()
                    objects_info.append({
                        'name': obj_name,
                        'label': desc['label'],
                        'labelPlural': desc['labelPlural'],
                        'createable': desc['createable'],
                        'updateable': desc['updateable'],
                        'deletable': desc['deletable']
                    })
                except:
                    pass
            
            return objects_info
        except Exception as e:
            return []
    
    def get_object_fields(self, sf, object_name):
        """Get fields for a specific object"""
        try:
            desc = sf.__getattr__(object_name).describe()
            fields = []
            
            for field in desc['fields']:
                fields.append({
                    'name': field['name'],
                    'label': field['label'],
                    'type': field['type'],
                    'length': field.get('length'),
                    'required': not field['nillable'] and not field.get('defaultedOnCreate', False),
                    'createable': field['createable'],
                    'updateable': field['updateable'],
                    'picklistValues': field.get('picklistValues', [])
                })
            
            return fields
        except Exception as e:
            raise Exception(f"Failed to get fields for {object_name}: {str(e)}")
    
    def get_records(self, sf, object_name, limit=100, offset=0):
        """Get records for an object"""
        try:
            # Get object fields
            desc = sf.__getattr__(object_name).describe()
            field_names = [f['name'] for f in desc['fields'] if f['type'] != 'address'][:20]  # Limit fields
            
            fields_str = ', '.join(field_names)
            query = f"SELECT {fields_str} FROM {object_name} LIMIT {limit} OFFSET {offset}"
            
            results = sf.query(query)
            
            return {
                'records': results['records'],
                'totalSize': results['totalSize'],
                'done': results['done']
            }
        except Exception as e:
            raise Exception(f"Failed to get records: {str(e)}")
    
    def create_record(self, sf, object_name, data):
        """Create a single record"""
        try:
            result = sf.__getattr__(object_name).create(data)
            return result
        except Exception as e:
            raise Exception(f"Failed to create record: {str(e)}")
    
    def bulk_create_records(self, sf, object_name, count, template):
        """Bulk create records"""
        results = []
        
        try:
            for i in range(count):
                record_data = template.copy()
                
                # Add auto-incrementing fields
                for key, value in record_data.items():
                    if isinstance(value, str) and '{i}' in value:
                        record_data[key] = value.replace('{i}', str(i + 1))
                
                result = self.create_record(sf, object_name, record_data)
                results.append(result)
            
            return results
        except Exception as e:
            raise Exception(f"Bulk create failed: {str(e)}")
    
    def update_record(self, sf, object_name, record_id, data):
        """Update a record"""
        try:
            result = sf.__getattr__(object_name).update(record_id, data)
            return result
        except Exception as e:
            raise Exception(f"Failed to update record: {str(e)}")
    
    def delete_record(self, sf, object_name, record_id):
        """Delete a record"""
        try:
            result = sf.__getattr__(object_name).delete(record_id)
            return result
        except Exception as e:
            raise Exception(f"Failed to delete record: {str(e)}")
    
    def get_dashboard_stats(self, sf):
        """Get dashboard statistics"""
        if not sf:
            return {}
        
        try:
            stats = {}
            
            # Count Accounts
            try:
                account_count = sf.query("SELECT COUNT() FROM Account")
                stats['accounts'] = account_count['totalSize']
            except Exception as e:
                print(f"Error counting Accounts: {e}")
                stats['accounts'] = 0
            
            # Count Cases
            try:
                case_count = sf.query("SELECT COUNT() FROM Case")
                stats['cases'] = case_count['totalSize']
            except Exception as e:
                print(f"Error counting Cases: {e}")
                stats['cases'] = 0
            
            # Count AccountContactRelation
            try:
                acr_count = sf.query("SELECT COUNT() FROM AccountContactRelation")
                stats['account_contacts'] = acr_count['totalSize']
            except Exception as e:
                print(f"Error counting AccountContactRelation: {e}")
                stats['account_contacts'] = 0
            
            # Count Opportunities
            try:
                opp_count = sf.query("SELECT COUNT() FROM Opportunity")
                stats['opportunities'] = opp_count['totalSize']
            except:
                stats['opportunities'] = 0
            
            # Count Individuals
            try:
                individual_count = sf.query("SELECT COUNT() FROM Individual")
                stats['individuals'] = individual_count['totalSize']
            except Exception as e:
                print(f"Error counting Individuals: {e}")
                stats['individuals'] = 0
            
            # Count UnifiedIndividuals
            try:
                unified_count = sf.query("SELECT COUNT() FROM UnifiedIndividual__dlm")
                stats['unified_individuals'] = unified_count['totalSize']
            except Exception as e:
                print(f"Error counting UnifiedIndividuals: {e}")
                stats['unified_individuals'] = 0
            
            # Count Synthetic Profiles (from our app's data file)
            try:
                import json
                import os
                data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic_engagement.json')
                if os.path.exists(data_file):
                    with open(data_file, 'r') as f:
                        synthetic_data = json.load(f)
                        stats['synthetic_profiles'] = len(synthetic_data)
                else:
                    stats['synthetic_profiles'] = 0
            except Exception as e:
                print(f"Error counting Synthetic Profiles: {e}")
                stats['synthetic_profiles'] = 0
            
            return stats
        except Exception as e:
            return {'error': str(e)}



