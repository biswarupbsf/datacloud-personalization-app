#!/usr/bin/env python3
"""Test using requests session for auth"""

import requests
from simple_salesforce import Salesforce

USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"
SECURITY_TOKEN = "yHuCHxO44Oaf8No7mJmgUxAP"

# Try manual SOAP login first
print("Attempting manual SOAP authentication...")

soap_url = 'https://login.salesforce.com/services/Soap/u/59.0'
headers = {
    'content-type': 'text/xml',
    'SOAPAction': 'login'
}

body = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:enterprise.soap.sforce.com">
  <soapenv:Body>
    <urn:login>
      <urn:username>{USERNAME}</urn:username>
      <urn:password>{PASSWORD}{SECURITY_TOKEN}</urn:password>
    </urn:login>
  </soapenv:Body>
</soapenv:Envelope>"""

try:
    response = requests.post(soap_url, data=body, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ SOAP Auth successful!")
        print(response.text[:500])
    else:
        print(f"❌ SOAP Auth failed")
        print(response.text[:1000])
except Exception as e:
    print(f"❌ Error: {e}")


