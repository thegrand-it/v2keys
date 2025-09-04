import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import requests
import json
import os
import subprocess
import threading
import ctypes
import winreg
from parsers import parse_link

class VPNGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VPN Client - v2keys")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#2b2b2b")  # Modern dark background

        # Style - Modern Dark Theme
        style = ttk.Style()

        # Try to use a modern theme if available
        try:
            style.theme_use('vista')  # Modern Windows theme
        except:
            pass

        # Button styling with modern colors
        style.configure("TButton",
                        padding=10,
                        relief="flat",
                        background="#4CAF50",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("TButton",
                  background=[("active", "#45a049"),
                            ("pressed", "#3d8b40"),
                            ("disabled", "#cccccc")],
                  foreground=[("disabled", "#999999")],
                  relief=[("pressed", "sunken"), ("!pressed", "flat")])

        # Label styling
        style.configure("TLabel", font=("Segoe UI", 10), background="#2b2b2b", foreground="#e0e0e0")

        # Checkbutton styling
        style.configure("TCheckbutton", font=("Segoe UI", 10), background="#2b2b2b", foreground="#e0e0e0")

        # Frame styling
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TLabelframe", background="#363636", foreground="#2196F3", font=("Segoe UI", 12, "bold"))
        style.configure("TLabelframe.Label", background="#363636", foreground="#2196F3", font=("Segoe UI", 12, "bold"))

        # Listbox styling
        style.configure("TListbox", background="#363636", foreground="#e0e0e0", font=("Segoe UI", 9))

        # Main container
        main_frame = ttk.Frame(root, padding="30")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="🚀 VPN Client - v2keys", font=("Segoe UI", 20, "bold"), foreground="#4CAF50")
        title_label.pack(pady=(0, 30))

        # Subscription frame
        sub_frame = ttk.LabelFrame(main_frame, text="📡 Subscription Management", padding="15")
        sub_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(sub_frame, text="🔗 Default subscription loaded automatically", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 10))
        self.reload_button = tk.Button(sub_frame, text="🔄 Reload Subscription", command=self.load_subscription,
                                      bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
                                      relief="flat", bd=0, padx=15, pady=8,
                                      activebackground="#1976D2", activeforeground="white")
        self.reload_button.pack(anchor="w", pady=(0, 0))

        # Server selection frame
        server_frame = ttk.LabelFrame(main_frame, text="🌐 Server Selection", padding="15")
        server_frame.pack(fill="both", expand=True, pady=(0, 20))

        ttk.Label(server_frame, text="📋 Available Servers:", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 10))

        # Listbox with scrollbar
        listbox_frame = ttk.Frame(server_frame)
        listbox_frame.pack(fill="both", expand=True)

        self.server_listbox = tk.Listbox(listbox_frame, height=10, font=("Segoe UI", 9), selectbackground="#2196F3", selectforeground="white", bg="#363636", fg="#e0e0e0", relief="flat", bd=0)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.server_listbox.yview)
        self.server_listbox.configure(yscrollcommand=scrollbar.set)

        self.server_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Control frame
        control_frame = ttk.Frame(server_frame)
        control_frame.pack(fill="x", pady=(15, 0))

        self.connect_button = tk.Button(control_frame, text="🔗 Connect", command=self.connect_vpn,
                                       bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
                                       relief="flat", bd=0, padx=20, pady=10,
                                       activebackground="#45a049", activeforeground="white")
        self.connect_button.pack(side="left", padx=(0, 15))

        self.disconnect_button = tk.Button(control_frame, text="❌ Disconnect", command=self.disconnect_vpn, state="disabled",
                                          bg="#f44336", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                                          relief="flat", bd=0, padx=20, pady=10,
                                          activebackground="#d32f2f", activeforeground="#ffffff")
        self.disconnect_button.pack(side="left", padx=(0, 30))

        self.system_proxy_var = tk.BooleanVar()
        self.system_proxy_check = ttk.Checkbutton(control_frame, text="🔧 Auto-set System Proxy", variable=self.system_proxy_var, command=self.update_system_proxy)
        self.system_proxy_check.pack(side="left")

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(20, 0))

        self.status_label = ttk.Label(status_frame, text="📊 Status: Ready", font=("Segoe UI", 10, "italic"), foreground="#4CAF50")
        self.status_label.pack(anchor="w")

        # Store configs
        self.current_configs = []
        self.v2ray_process = None

        # Auto-load subscription on startup
        self.root.after(100, self.load_subscription)

    def fetch_and_parse_url(self, url):
        try:
            # Fetch from URL
            response = requests.get(url)
            response.raise_for_status()
            content = response.text.strip()
            # Split by lines, each line is a link
            links = [line.strip() for line in content.split('\n') if line.strip()]
            configs = []
            for link in links:
                try:
                    config = parse_link(link)
                    configs.append(config)
                except ValueError as e:
                    # Skip invalid links
                    pass

            # Store configs
            self.current_configs = configs

            # Populate server list
            self.server_listbox.delete(0, tk.END)
            for i, config in enumerate(configs):
                name = config.get('name', f"{config['protocol'].upper()}-{config['host']}:{config['port']}")
                self.server_listbox.insert(tk.END, f"{i+1}. {name}")
            self.status_label.config(text=f"📊 Status: Loaded {len(configs)} servers", foreground="#4CAF50")

        except Exception as e:
            self.status_label.config(text="❌ Status: Failed to load subscription", foreground="#f44336")
            messagebox.showerror("❌ Error", f"Failed to fetch or parse: {str(e)}")

    def load_subscription(self):
        sub_url = "https://raw.githubusercontent.com/thegrand-it/v2keys/refs/heads/main/ss.txt"
        self.status_label.config(text="⏳ Status: Loading subscription...", foreground="#ff9800")
        self.fetch_and_parse_url(sub_url)

    def export_config(self):
        if not self.current_configs:
            messagebox.showerror("❌ Error", "No configs to export")
            return

        configs = self.current_configs

        # Generate v2ray config
        v2ray_config = {
            "inbounds": [
                {
                    "port": 1080,
                    "listen": "127.0.0.1",
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": True
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    }
                }
            ],
            "outbounds": []
        }

        for config in configs:
            if config['protocol'] == 'ss':
                outbound = {
                    "protocol": "shadowsocks",
                    "settings": {
                        "servers": [
                            {
                                "address": config['host'],
                                "port": int(config['port']),
                                "password": config['password'],
                                "method": config['method']
                            }
                        ]
                    },
                    "tag": config.get('name', f"ss-{config['host']}")
                }
            elif config['protocol'] == 'vmess':
                outbound = {
                    "protocol": "vmess",
                    "settings": {
                        "vnext": [
                            {
                                "address": config['host'],
                                "port": int(config['port']),
                                "users": [
                                    {
                                        "id": config['id'],
                                        "alterId": int(config['aid']) if config['aid'] else 0,
                                        "security": "auto"
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": config['net'],
                        "security": "tls" if config['tls'] == 'tls' else "none",
                        "tlsSettings": {} if config['tls'] == 'tls' else None,
                        "wsSettings": {
                            "path": config['path'],
                            "headers": {
                                "Host": config['host_header']
                            }
                        } if config['net'] == 'ws' else None
                    },
                    "tag": config.get('name', f"vmess-{config['host']}")
                }
            elif config['protocol'] == 'vless':
                outbound = {
                    "protocol": "vless",
                    "settings": {
                        "vnext": [
                            {
                                "address": config['host'],
                                "port": int(config['port']),
                                "users": [
                                    {
                                        "id": config['uuid'],
                                        "encryption": "none"
                                    }
                                ]
                            }
                        ]
                    },
                    "streamSettings": {
                        "network": config['type'],
                        "security": config['security'],
                        "tlsSettings": {} if config['security'] == 'tls' else None,
                        "wsSettings": {
                            "path": config['path'],
                            "headers": {
                                "Host": config['host_header']
                            }
                        } if config['type'] == 'ws' else None
                    },
                    "tag": config.get('name', f"vless-{config['host']}")
                }
            else:
                continue
            v2ray_config["outbounds"].append(outbound)

        # Default outbound
        v2ray_config["outbounds"].append({
            "protocol": "freedom",
            "tag": "direct"
        })

        # Routing
        v2ray_config["routing"] = {
            "rules": [
                {
                    "type": "field",
                    "outboundTag": "direct",
                    "domain": ["geosite:cn"]
                },
                {
                    "type": "field",
                    "outboundTag": "direct",
                    "ip": ["geoip:cn"]
                }
            ]
        }

        # Save to file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(v2ray_config, f, indent=2)
            messagebox.showinfo("✅ Success", f"📁 Config exported to {file_path}\n\n🔗 To connect, import this file into v2rayN or similar client.")

    def connect_vpn(self):
        if not self.current_configs:
            messagebox.showerror("❌ Error", "No configs available")
            return

        selection = self.server_listbox.curselection()
        if not selection:
            messagebox.showerror("❌ Error", "Please select a server")
            return

        selected_index = selection[0]
        selected_config = self.current_configs[selected_index]

        # Generate config with only selected server
        v2ray_config = {
            "inbounds": [
                {
                    "port": 8080,
                    "listen": "127.0.0.1",
                    "protocol": "http",
                    "settings": {
                        "auth": "noauth"
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    }
                }
            ],
            "outbounds": []
        }

        if selected_config['protocol'] == 'ss':
            outbound = {
                "protocol": "shadowsocks",
                "settings": {
                    "servers": [
                        {
                            "address": selected_config['host'],
                            "port": int(selected_config['port']),
                            "password": selected_config['password'],
                            "method": selected_config['method']
                        }
                    ]
                },
                "tag": selected_config.get('name', f"ss-{selected_config['host']}")
            }
        elif selected_config['protocol'] == 'vmess':
            outbound = {
                "protocol": "vmess",
                "settings": {
                    "vnext": [
                        {
                            "address": selected_config['host'],
                            "port": int(selected_config['port']),
                            "users": [
                                {
                                    "id": selected_config['id'],
                                    "alterId": int(selected_config['aid']) if selected_config['aid'] else 0,
                                    "security": "auto"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": selected_config['net'],
                    "security": "tls" if selected_config['tls'] == 'tls' else "none",
                    "tlsSettings": {} if selected_config['tls'] == 'tls' else None,
                    "wsSettings": {
                        "path": selected_config['path'],
                        "headers": {
                            "Host": selected_config['host_header']
                        }
                    } if selected_config['net'] == 'ws' else None
                },
                "tag": selected_config.get('name', f"vmess-{selected_config['host']}")
            }
        elif selected_config['protocol'] == 'vless':
            outbound = {
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": selected_config['host'],
                            "port": int(selected_config['port']),
                            "users": [
                                {
                                    "id": selected_config['uuid'],
                                    "encryption": "none"
                                }
                            ]
                        }
                    ]
                },
                "streamSettings": {
                    "network": selected_config['type'],
                    "security": selected_config['security'],
                    "tlsSettings": {} if selected_config['security'] == 'tls' else None,
                    "wsSettings": {
                        "path": selected_config['path'],
                        "headers": {
                            "Host": selected_config['host_header']
                        }
                    } if selected_config['type'] == 'ws' else None
                },
                "tag": selected_config.get('name', f"vless-{selected_config['host']}")
            }
        else:
            messagebox.showerror("❌ Error", "Unsupported protocol")
            return

        v2ray_config["outbounds"].append(outbound)

        # Default outbound
        v2ray_config["outbounds"].append({
            "protocol": "freedom",
            "tag": "direct"
        })

        # Routing
        v2ray_config["routing"] = {
            "rules": [
                {
                    "type": "field",
                    "outboundTag": "direct",
                    "domain": ["geosite:cn"]
                },
                {
                    "type": "field",
                    "outboundTag": "direct",
                    "ip": ["geoip:cn"]
                }
            ]
        }

        # Save temp config
        config_path = os.path.join(os.getcwd(), "temp_config.json")
        with open(config_path, 'w') as f:
            json.dump(v2ray_config, f, indent=2)

        # Run v2ray
        def run_v2ray():
            try:
                v2ray_path = os.path.join(os.getcwd(), "v2ray", "v2ray.exe")
                if not os.path.exists(v2ray_path):
                    v2ray_path = "v2ray"  # fallback to PATH
                self.v2ray_process = subprocess.Popen([v2ray_path, "-config", config_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.connect_button.config(state="disabled")
                self.disconnect_button.config(state="normal")
                self.status_label.config(text="✅ Status: Connected - VPN active", foreground="#4CAF50")
                self.update_system_proxy()
                messagebox.showinfo("🎉 Connected", "VPN connected successfully!\n🌐 HTTP proxy: 127.0.0.1:8080")
            except FileNotFoundError:
                messagebox.showerror("❌ Error", "v2ray.exe not found. Please ensure v2ray folder is in the script directory or v2ray is in PATH.")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to start VPN: {str(e)}")

        threading.Thread(target=run_v2ray).start()

    def disconnect_vpn(self):
        if self.v2ray_process:
            self.v2ray_process.terminate()
            self.v2ray_process = None
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.status_label.config(text="🔌 Status: Disconnected", foreground="#9e9e9e")
            self.update_system_proxy()
            messagebox.showinfo("🔌 Disconnected", "VPN disconnected successfully.")

    def set_system_proxy(self):
        try:
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_SET_VALUE)
            # Set proxy enable
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            # Set proxy server
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8080")
            winreg.CloseKey(key)
            # Notify system of proxy change
            INTERNET_OPTION_REFRESH = 37
            INTERNET_OPTION_SETTINGS_CHANGED = 39
            ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to set system proxy: {str(e)}")

    def unset_system_proxy(self):
        try:
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_SET_VALUE)
            # Disable proxy
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            # Notify system of proxy change
            INTERNET_OPTION_REFRESH = 37
            INTERNET_OPTION_SETTINGS_CHANGED = 39
            ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to unset system proxy: {str(e)}")

    def update_system_proxy(self):
        if self.system_proxy_var.get():
            self.set_system_proxy()
        else:
            self.unset_system_proxy()
