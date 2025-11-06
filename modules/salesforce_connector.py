"""
Salesforce Connection Manager
Handles authentication and connection to Salesforce
"""

from simple_salesforce import Salesforce
from datetime import datetime

class SalesforceManager:
    def __init__(self):
        self.sf = None
        self.username = None
        self.instance_url = None
        self.org_id = None
        self.connected_at = None
    
    def connect(self, username, password, security_token=''):
        """Connect to Salesforce"""
        # Try with security token first if provided
        if security_token and security_token.strip():
            try:
                self.sf = Salesforce(
                    username=username,
                    password=password,
                    security_token=security_token,
                    domain='login'
                )
            except Exception as e:
                # If that fails, try concatenating (some orgs need this)
                self.sf = Salesforce(
                    username=username,
                    password=password + security_token,
                    domain='login'
                )
        else:
            # No security token - IP must be whitelisted
            self.sf = Salesforce(
                username=username,
                password=password,
                domain='login'
            )
        
        self.username = username
        self.instance_url = self.sf.instance_url
        self.connected_at = datetime.now()
        
        # Get org info
        org_query = self.sf.query("SELECT Id, Name, OrganizationType FROM Organization LIMIT 1")
        if org_query['records']:
            self.org_id = org_query['records'][0]['Id']
        
        return True
    
    def is_connected(self):
        """Check if connected"""
        return self.sf is not None
    
    def get_org_info(self):
        """Get organization information"""
        if not self.is_connected():
            return None
        
        try:
            org_query = self.sf.query("SELECT Id, Name, OrganizationType, InstanceName FROM Organization LIMIT 1")
            org = org_query['records'][0] if org_query['records'] else {}
            
            return {
                'username': self.username,
                'instance_url': self.instance_url,
                'org_id': self.org_id,
                'org_name': org.get('Name', 'Unknown'),
                'org_type': org.get('OrganizationType', 'Unknown'),
                'instance': org.get('InstanceName', 'Unknown'),
                'connected_at': self.connected_at.isoformat() if self.connected_at else None
            }
        except Exception as e:
            return {
                'username': self.username,
                'instance_url': self.instance_url,
                'org_id': self.org_id,
                'error': str(e)
            }
    
    def disconnect(self):
        """Disconnect from Salesforce"""
        self.sf = None
        self.username = None
        self.instance_url = None
        self.org_id = None
        self.connected_at = None

