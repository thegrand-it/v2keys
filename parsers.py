import base64
import json
import urllib.parse

def parse_ss_link(link):
    if not link.startswith('ss://'):
        raise ValueError("Invalid SS link")
    # Handle name after #
    if '#' in link:
        link, name_encoded = link.split('#', 1)
        name = urllib.parse.unquote(name_encoded)
    else:
        name = None
    # Remove ss://
    encoded_part = link[5:]
    # Find the last @ to separate encoded method:password from host:port
    at_index = encoded_part.rfind('@')
    if at_index == -1:
        raise ValueError("Invalid SS format")
    encoded = encoded_part[:at_index]
    host_port = encoded_part[at_index + 1:]
    # Decode base64 - handle padding issues
    # Add padding if necessary
    padding = len(encoded) % 4
    if padding:
        encoded += '=' * (4 - padding)
    decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
    # Format: method:password
    if ':' not in decoded:
        raise ValueError("Invalid method:password")
    method, password = decoded.split(':', 1)
    # host:port
    # Remove any query parameters (after ?) if present
    if '?' in host_port:
        host_port = host_port.split('?')[0]
    
    if ':' not in host_port:
        raise ValueError("Invalid host:port")
    host, port_str = host_port.split(':', 1)
    port = int(port_str)
    config = {
        'protocol': 'ss',
        'method': method,
        'password': password,
        'host': host,
        'port': port
    }
    if name:
        config['name'] = name
    return config

def parse_vmess_link(link):
    if not link.startswith('vmess://'):
        raise ValueError("Invalid VMess link")
    encoded = link[8:]
    decoded = base64.b64decode(encoded).decode('utf-8')
    config = json.loads(decoded)
    return {
        'protocol': 'vmess',
        'host': config.get('add'),
        'port': config.get('port'),
        'id': config.get('id'),
        'aid': config.get('aid'),
        'net': config.get('net'),
        'type': config.get('type'),
        'host_header': config.get('host'),
        'path': config.get('path'),
        'tls': config.get('tls')
    }

def parse_vless_link(link):
    if not link.startswith('vless://'):
        raise ValueError("Invalid VLess link")
    # vless://uuid@host:port?params
    parsed = urllib.parse.urlparse(link)
    uuid = parsed.netloc.split('@')[0]
    host_port = parsed.netloc.split('@')[1]
    host, port = host_port.split(':')
    port = int(port)
    params = urllib.parse.parse_qs(parsed.query)
    return {
        'protocol': 'vless',
        'uuid': uuid,
        'host': host,
        'port': port,
        'type': params.get('type', [''])[0],
        'security': params.get('security', [''])[0],
        'path': params.get('path', [''])[0],
        'host_header': params.get('host', [''])[0]
    }

def parse_link(link):
    if link.startswith('ss://'):
        return parse_ss_link(link)
    elif link.startswith('vmess://'):
        return parse_vmess_link(link)
    elif link.startswith('vless://'):
        return parse_vless_link(link)
    else:
        raise ValueError("Unsupported protocol")
