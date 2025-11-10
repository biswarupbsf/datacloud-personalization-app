"""
OAuth-based Salesforce Connection
Uses browser-based authentication - no security token needed!
"""

from simple_salesforce import Salesforce
import webbrowser
import http.server
import socketserver
import urllib.parse
from datetime import datetime
import threading

class OAuthConnector:
    def __init__(self):
        self.sf = None
        self.username = None
        self.instance_url = None
        self.org_id = None
        self.connected_at = None
        self.access_token = None
        self.instance = None
        
        # OAuth settings - using Salesforce CLI Connected App (public)
        self.client_id = "PlatformCLI"  # Salesforce CLI public client
        self.redirect_uri = "http://localhost:8888/oauth/callback"
        self.auth_code = None
        self.server = None
    
    def connect_with_browser(self, domain='login'):
        """
        Connect using browser-based OAuth flow
        Opens browser for user to authenticate
        """
        # Start local server to receive callback
        handler = self._create_handler()
        self.server = socketserver.TCPServer(("", 8888), handler)
        
        # Start server in background thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Build OAuth URL
        auth_url = f"https://{domain}.salesforce.com/services/oauth2/authorize"
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'prompt': 'login'
        }
        
        full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
        
        print(f"\n🌐 Opening browser for authentication...")
        print(f"📍 If browser doesn't open, visit: {full_auth_url}\n")
        
        # Open browser
        webbrowser.open(full_auth_url)
        
        # Wait for callback (timeout after 120 seconds)
        import time
        timeout = 120
        elapsed = 0
        
        while self.auth_code is None and elapsed < timeout:
            time.sleep(1)
            elapsed += 1
        
        # Stop server
        self.server.shutdown()
        
        if self.auth_code is None:
            raise Exception("Authentication timeout - no response from browser")
        
        # Exchange code for token
        token_url = f"https://{domain}.salesforce.com/services/oauth2/token"
        token_data = {
            'grant_type': 'authorization_code',
            'code': self.auth_code,
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        
        import requests
        response = requests.post(token_url, data=token_data)
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        token_info = response.json()
        
        self.access_token = token_info['access_token']
        self.instance_url = token_info['instance_url']
        self.instance = urllib.parse.urlparse(self.instance_url).hostname
        
        # Create Salesforce connection with token
        self.sf = Salesforce(
            instance_url=self.instance_url,
            session_id=self.access_token
        )
        
        self.connected_at = datetime.now()
        
        # Get user info
        try:
            user_info = self.sf.query("SELECT Id, Username FROM User WHERE Id = '{}'".format(token_info.get('id', '').split('/')[-1]))
            if user_info['records']:
                self.username = user_info['records'][0]['Username']
        except:
            self.username = "authenticated_user"
        
        # Get org info
        try:
            org_query = self.sf.query("SELECT Id, Name FROM Organization LIMIT 1")
            if org_query['records']:
                self.org_id = org_query['records'][0]['Id']
        except:
            pass
        
        return True
    
    def _create_handler(self):
        """Create HTTP request handler for OAuth callback"""
        parent = self
        
        class OAuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                # Parse the callback URL
                parsed = urllib.parse.urlparse(self.path)
                
                if parsed.path == '/oauth/callback':
                    # Extract auth code
                    params = urllib.parse.parse_qs(parsed.query)
                    
                    if 'code' in params:
                        parent.auth_code = params['code'][0]
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        success_html = """
                        <html>
                        <head><title>Authentication Successful</title></head>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1 style="color: #667eea;">✅ Authentication Successful!</h1>
                            <p>You can close this window and return to the application.</p>
                            <script>
                                setTimeout(function() { window.close(); }, 3000);
                            </script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                    else:
                        # Error in callback
                        error = params.get('error', ['Unknown error'])[0]
                        parent.auth_code = None
                        
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        error_html = f"""
                        <html>
                        <head><title>Authentication Failed</title></head>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1 style="color: #ef4444;">❌ Authentication Failed</h1>
                            <p>Error: {error}</p>
                            <p>Please try again.</p>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode())
            
            def log_message(self, format, *args):
                # Suppress log messages
                pass
        
        return OAuthHandler
    
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





