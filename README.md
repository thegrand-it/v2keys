# v2keys

A Windows GUI VPN client with a modern blue and white theme for connecting to SS, VMess, and VLess servers.

## Features
- Parse VPN links from URLs or direct input
- Support for Shadowsocks (SS), VMess, and VLess protocols
- Export parsed configs to v2ray-compatible JSON format
- Hard-coded subscription URL for easy loading

## Usage
1. Run `python main.py` (subscription loads automatically)
2. Select a server from the list
3. Check "Auto-set System Proxy" to automatically configure Windows proxy settings
4. Click "Connect" to start the VPN
5. Monitor status in the status bar
6. Click "Disconnect" to stop the VPN
7. Use "Reload Subscription" to refresh the server list

## Requirements
- Python 3.x
- Install dependencies: `pip install requests`
- v2ray-core in the `v2ray` folder (download from https://github.com/v2fly/v2ray-core/releases)

## Connecting to Server
The app provides direct connection:
1. Load servers from the subscription
2. Select a server
3. Click Connect - v2ray starts with HTTP proxy at 127.0.0.1:8080
4. Configure your applications to use the HTTP proxy
5. Disconnect when done