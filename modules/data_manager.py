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
            
            # Count Individuals
            try:
                ind_count = sf.query("SELECT COUNT() FROM Individual")
                stats['individuals'] = ind_count['totalSize']
            except:
                stats['individuals'] = 0
            
            # Count Contacts
            try:
                contact_count = sf.query("SELECT COUNT() FROM Contact")
                stats['contacts'] = contact_count['totalSize']
            except:
                stats['contacts'] = 0
            
            # Count Campaigns
            try:
                campaign_count = sf.query("SELECT COUNT() FROM Campaign")
                stats['campaigns'] = campaign_count['totalSize']
            except:
                stats['campaigns'] = 0
            
            # Count Opportunities
            try:
                opp_count = sf.query("SELECT COUNT() FROM Opportunity")
                stats['opportunities'] = opp_count['totalSize']
            except:
                stats['opportunities'] = 0
            
            return stats
        except Exception as e:
            return {'error': str(e)}


