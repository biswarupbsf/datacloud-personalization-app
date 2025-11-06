"""
Simple SOAP-based Authentication
Works with just username and password - no security token needed!
"""

from simple_salesforce import Salesforce
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

class SimpleAuthConnector:
    def __init__(self):
        self.sf = None
        self.username = None
        self.instance_url = None
        self.org_id = None
        self.connected_at = None
    
    def connect_soap(self, username, password, security_token=''):
        """
        Connect using SOAP API with username, password, and optional security token
        Security token is appended to password if provided
        """
        
        # Append security token to password if provided (Salesforce standard)
        full_password = password + security_token if security_token else password
        
        # SOAP endpoint
        soap_url = 'https://login.salesforce.com/services/Soap/u/59.0'
        
        # SOAP request body
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                  xmlns:urn="urn:partner.soap.sforce.com">
  <soapenv:Body>
    <urn:login>
      <urn:username>{username}</urn:username>
      <urn:password>{full_password}</urn:password>
    </urn:login>
  </soapenv:Body>
</soapenv:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'login'
        }
        
        # Make SOAP request
        response = requests.post(soap_url, data=soap_body, headers=headers)
        
        if response.status_code != 200:
            # Parse error
            try:
                root = ET.fromstring(response.text)
                # Find fault message
                fault = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body/{http://schemas.xmlsoap.org/soap/envelope/}Fault')
                if fault is not None:
                    faultstring = fault.find('faultstring')
                    if faultstring is not None:
                        raise Exception(f"Login failed: {faultstring.text}")
            except:
                pass
            raise Exception(f"Login failed with status {response.status_code}")
        
        # Parse response
        try:
            root = ET.fromstring(response.text)
            
            # Extract session ID
            ns = {
                'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                'urn': 'urn:partner.soap.sforce.com'
            }
            
            session_id = root.find('.//urn:sessionId', ns).text
            server_url = root.find('.//urn:serverUrl', ns).text
            
            # Extract instance URL from server URL
            # serverUrl looks like: https://instancename.salesforce.com/services/Soap/u/59.0/orgId
            instance_url = '/'.join(server_url.split('/')[:3])  # Gets https://instancename.salesforce.com
            
            # Create Salesforce connection with session
            self.sf = Salesforce(
                instance_url=instance_url,
                session_id=session_id
            )
            
            self.username = username
            self.instance_url = instance_url
            self.connected_at = datetime.now()
            
            # Get org info
            try:
                org_query = self.sf.query("SELECT Id, Name FROM Organization LIMIT 1")
                if org_query['records']:
                    self.org_id = org_query['records'][0]['Id']
            except:
                pass
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to parse login response: {str(e)}")
    
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


