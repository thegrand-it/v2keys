import tkinter as tk
from tkinter import messagebox, filedialog, ttk, font
import requests
import json
import os
import subprocess
import threading
import ctypes
import socket
import time
import platform
from parsers import parse_link
import math

# Import winreg only on Windows
if platform.system() == "Windows":
    import winreg
else:
    winreg = None

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects and animations"""
    def __init__(self, parent, text="", command=None, bg="#5e72e4", hover_bg="#4c63d2",
                 fg="white", width=150, height=40, corner_radius=8, icon="", **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)

        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.text = text
        self.icon = icon
        self.width = width
        self.height = height
        self.corner_radius = corner_radius

        self.draw_button()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def draw_button(self, color=None):
        if color is None:
            color = self.bg

        self.delete("all")
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, self.corner_radius,
                                 fill=color, outline="")

        # Draw text with icon
        text_display = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(self.width//2, self.height//2, text=text_display,
                         fill=self.fg, font=("Segoe UI", 10, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        self.draw_button(self.hover_bg)
        self.config(cursor="hand2")

    def on_leave(self, event):
        self.draw_button(self.bg)

    def on_click(self, event):
        self.move("all", 1, 1)

    def on_release(self, event):
        self.move("all", -1, -1)
        if self.command:
            self.command()

class AnimatedLabel(tk.Label):
    """Label with fade-in animation"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.alpha = 0
        self.fade_in()

    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.1
            self.configure(fg=self.hex_with_alpha(self.cget("fg"), self.alpha))
            self.after(50, self.fade_in)

    def hex_with_alpha(self, hex_color, alpha):
        # Simple fade simulation by adjusting color brightness
        return hex_color

class VPNGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VPN Client Pro")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # Modern color scheme - improved contrast and aesthetics
        self.colors = {
            'bg': '#0a0a0a',           # Pure black background
            'sidebar': '#1a1a1a',      # Dark gray sidebar
            'card': '#242424',         # Card background
            'primary': '#6366f1',      # Indigo primary
            'success': '#10b981',      # Emerald green
            'danger': '#ef4444',       # Red
            'warning': '#f59e0b',      # Amber
            'info': '#0ea5e9',         # Sky blue
            'text': '#f8fafc',         # Bright white text
            'text_secondary': '#94a3b8', # Slate gray secondary text
            'border': '#334155'        # Slate border
        }

        self.root.configure(bg=self.colors['bg'])

        # Configure ttk styles
        self.setup_styles()

        # Create main layout
        self.create_layout()

        # Store configs and state
        self.current_configs = []
        self.server_status = {}
        self.v2ray_process = None

        # Animation variables
        self.animation_running = False

        # Auto-load subscription on startup
        self.root.after(100, self.load_subscription)

        # Handle application exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_exit)

    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()

        # Try to use a modern theme
        try:
            style.theme_use('clam')
        except:
            pass

        # Configure custom styles
        style.configure("Sidebar.TFrame", background=self.colors['sidebar'])
        style.configure("Card.TFrame", background=self.colors['card'], relief="flat", borderwidth=1)
        style.configure("Main.TFrame", background=self.colors['bg'])

        # Custom Treeview style
        style.configure("Custom.Treeview",
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['card'],
                       borderwidth=0,
                       font=("Segoe UI", 10))

        style.configure("Custom.Treeview.Heading",
                       background=self.colors['sidebar'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       font=("Segoe UI", 10, "bold"))

        style.map("Custom.Treeview",
                 background=[("selected", self.colors['primary'])],
                 foreground=[("selected", "white")])

        # Scrollbar style
        style.configure("Custom.Vertical.TScrollbar",
                       background=self.colors['sidebar'],
                       bordercolor=self.colors['sidebar'],
                       darkcolor=self.colors['card'],
                       lightcolor=self.colors['card'],
                       troughcolor=self.colors['card'],
                       arrowcolor=self.colors['text_secondary'])

    def create_layout(self):
        """Create the main layout with sidebar and content area"""

        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg=self.colors['sidebar'], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo/Title area
        logo_frame = tk.Frame(sidebar, bg=self.colors['sidebar'], height=100)
        logo_frame.pack(fill="x", pady=(30, 20))
        logo_frame.pack_propagate(False)

        # App title with gradient effect (simulated)
        title = tk.Label(logo_frame, text="⚡", font=("Segoe UI", 32),
                        bg=self.colors['sidebar'], fg=self.colors['primary'])
        title.pack()

        app_name = tk.Label(logo_frame, text="VPN Client Pro", font=("Segoe UI", 18, "bold"),
                           bg=self.colors['sidebar'], fg=self.colors['text'])
        app_name.pack()

        # Connection status card
        self.create_status_card(sidebar)

        # Navigation buttons
        nav_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        nav_frame.pack(fill="x", pady=20, padx=20)

        self.reload_btn = ModernButton(nav_frame, text="Refresh Servers", icon="🔄",
                                      command=self.load_subscription,
                                      bg=self.colors['info'], hover_bg="#0284c7",
                                      width=240, height=45)
        self.reload_btn.pack(pady=5)

        self.sort_btn = ModernButton(nav_frame, text="Sort by Speed", icon="📊",
                                    command=self.sort_servers_by_latency,
                                    bg=self.colors['warning'], hover_bg="#d97706",
                                    width=240, height=45)
        self.sort_btn.pack(pady=5)

        self.test_btn = ModernButton(nav_frame, text="Test All Servers", icon="🔍",
                                    command=self.test_all_servers,
                                    bg=self.colors['primary'], hover_bg="#4f46e5",
                                    width=240, height=45)
        self.test_btn.pack(pady=5)

        # Settings section
        settings_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        settings_frame.pack(fill="x", pady=20, padx=20)

        self.system_proxy_var = tk.BooleanVar()
        proxy_check = tk.Checkbutton(settings_frame, text="Auto-configure System Proxy",
                                     variable=self.system_proxy_var,
                                     command=self.update_system_proxy,
                                     bg=self.colors['sidebar'], fg=self.colors['text'],
                                     activebackground=self.colors['sidebar'],
                                     activeforeground=self.colors['text'],
                                     selectcolor=self.colors['card'],
                                     font=("Segoe UI", 10))
        proxy_check.pack(anchor="w")

        # Content area
        content_area = tk.Frame(main_container, bg=self.colors['bg'])
        content_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(content_area, bg=self.colors['bg'])
        header_frame.pack(fill="x", pady=(0, 20))

        header_label = tk.Label(header_frame, text="Available Servers",
                               font=("Segoe UI", 24, "bold"),
                               bg=self.colors['bg'], fg=self.colors['text'])
        header_label.pack(side="left")

        self.server_count_label = tk.Label(header_frame, text="",
                                          font=("Segoe UI", 12),
                                          bg=self.colors['bg'],
                                          fg=self.colors['text_secondary'])
        self.server_count_label.pack(side="left", padx=(15, 0))

        # Search bar
        search_frame = tk.Frame(content_area, bg=self.colors['card'], height=50)
        search_frame.pack(fill="x", pady=(0, 20))
        search_frame.pack_propagate(False)

        search_icon = tk.Label(search_frame, text="🔍", font=("Segoe UI", 14),
                              bg=self.colors['card'], fg=self.colors['text_secondary'])
        search_icon.pack(side="left", padx=(15, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_servers)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               bg=self.colors['card'], fg=self.colors['text'],
                               insertbackground=self.colors['text'],
                               relief="flat", font=("Segoe UI", 11),
                               highlightthickness=0)
        search_entry.pack(side="left", fill="x", expand=True, pady=12)

        # Create placeholder text
        self.search_placeholder = "Search servers..."
        search_entry.insert(0, self.search_placeholder)
        search_entry.config(fg=self.colors['text_secondary'])

        def on_entry_click(event):
            if search_entry.get() == self.search_placeholder:
                search_entry.delete(0, "end")
                search_entry.config(fg=self.colors['text'])

        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, self.search_placeholder)
                search_entry.config(fg=self.colors['text_secondary'])

        search_entry.bind('<FocusIn>', on_entry_click)
        search_entry.bind('<FocusOut>', on_focus_out)

        # Server list card
        list_card = tk.Frame(content_area, bg=self.colors['card'])
        list_card.pack(fill="both", expand=True)

        # Create Treeview with custom style
        columns = ("server", "protocol", "status", "latency")
        self.server_tree = ttk.Treeview(list_card, columns=columns, show="headings",
                                        height=15, style="Custom.Treeview")

        # Configure columns
        self.server_tree.heading("server", text="Server Name")
        self.server_tree.heading("protocol", text="Protocol")
        self.server_tree.heading("status", text="Status")
        self.server_tree.heading("latency", text="Latency")

        self.server_tree.column("server", width=350, minwidth=200)
        self.server_tree.column("protocol", width=100, minwidth=80)
        self.server_tree.column("status", width=120, minwidth=100)
        self.server_tree.column("latency", width=100, minwidth=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_card, orient="vertical",
                                 command=self.server_tree.yview,
                                 style="Custom.Vertical.TScrollbar")
        self.server_tree.configure(yscrollcommand=scrollbar.set)

        self.server_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind double-click to connect
        self.server_tree.bind("<Double-Button-1>", lambda e: self.connect_vpn())

        # Create context menu
        self.create_context_menu()
        self.server_tree.bind("<Button-3>", self.show_context_menu)

        # Control buttons at bottom
        control_frame = tk.Frame(content_area, bg=self.colors['bg'])
        control_frame.pack(fill="x", pady=(20, 0))

        self.connect_btn = ModernButton(control_frame, text="Connect", icon="🔗",
                                       command=self.connect_vpn,
                                       bg=self.colors['success'], hover_bg="#0d966d",
                                       width=180, height=50)
        self.connect_btn.pack(side="left", padx=(0, 10))

        self.disconnect_btn = ModernButton(control_frame, text="Disconnect", icon="⛔",
                                          command=self.disconnect_vpn,
                                          bg=self.colors['danger'], hover_bg="#dc2626",
                                          width=180, height=50)
        self.disconnect_btn.pack(side="left")
        self.disconnect_btn.config(state="disabled")

    def create_status_card(self, parent):
        """Create connection status card"""
        status_card = tk.Frame(parent, bg=self.colors['card'], height=150)
        status_card.pack(fill="x", padx=20, pady=10)
        status_card.pack_propagate(False)

        # Status indicator
        self.status_indicator = tk.Canvas(status_card, width=12, height=12,
                                         bg=self.colors['card'], highlightthickness=0)
        self.status_indicator.pack(pady=(20, 5))
        self.draw_status_indicator("disconnected")

        # Status text
        self.status_label = tk.Label(status_card, text="Disconnected",
                                    font=("Segoe UI", 14, "bold"),
                                    bg=self.colors['card'], fg=self.colors['text'])
        self.status_label.pack()

        # Status details
        self.status_details = tk.Label(status_card, text="Ready to connect",
                                      font=("Segoe UI", 10),
                                      bg=self.colors['card'],
                                      fg=self.colors['text_secondary'])
        self.status_details.pack(pady=(5, 0))

        # Connection time
        self.connection_time = tk.Label(status_card, text="",
                                       font=("Segoe UI", 9),
                                       bg=self.colors['card'],
                                       fg=self.colors['text_secondary'])
        self.connection_time.pack()

    def draw_status_indicator(self, status):
        """Draw animated status indicator"""
        self.status_indicator.delete("all")

        if status == "connected":
            color = self.colors['success']
            self.animate_pulse(color)
        elif status == "connecting":
            color = self.colors['warning']
            self.animate_spin()
        else:
            color = self.colors['text_secondary']
            self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline="")

    def animate_pulse(self, color):
        """Pulse animation for connected status"""
        if not self.animation_running:
            return

        def pulse(size=6):
            if not self.animation_running:
                return
            self.status_indicator.delete("all")
            offset = 6 - size
            self.status_indicator.create_oval(offset, offset, 12-offset, 12-offset,
                                             fill=color, outline="")
            next_size = size - 1 if size > 2 else 6
            self.root.after(200, lambda: pulse(next_size))

        pulse()

    def animate_spin(self):
        """Spinning animation for connecting status"""
        if not self.animation_running:
            return

        def spin(angle=0):
            if not self.animation_running:
                return
            self.status_indicator.delete("all")
            start = angle
            extent = 270
            self.status_indicator.create_arc(2, 2, 10, 10, start=start, extent=extent,
                                            outline=self.colors['warning'], width=2, style="arc")
            self.root.after(50, lambda: spin((angle + 10) % 360))

        spin()

    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0,
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   activebackground=self.colors['primary'],
                                   activeforeground="white",
                                   relief="flat", bd=0)
        self.context_menu.add_command(label="🔗 Connect to Server",
                                      command=self.connect_vpn)
        self.context_menu.add_command(label="🔍 Test Server",
                                      command=self.test_selected_server)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy Server Info",
                                      command=self.copy_server_info)

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            item = self.server_tree.identify_row(event.y)
            if item:
                self.server_tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def filter_servers(self, *args):
        """Filter servers based on search input"""
        # Check if server_tree is initialized to avoid AttributeError
        if not hasattr(self, 'server_tree'):
            return
            
        search_text = self.search_var.get().lower()
        if search_text == self.search_placeholder.lower():
            search_text = ""

        # Clear and repopulate based on filter
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)

        for i, config in enumerate(self.current_configs):
            name = config.get('name', f"{config['protocol'].upper()}-{config['host']}:{config['port']}")

            if search_text and search_text not in name.lower():
                continue

            # Get status info
            status_info = self.server_status.get(i, {})
            available = status_info.get('available', None)
            latency = status_info.get('latency', None)

            # Format display
            protocol = config['protocol'].upper()

            if available is None:
                status_text = "⚫ Untested"
                latency_text = "-"
            elif available:
                status_text = "🟢 Online"
                latency_text = f"{latency}ms" if latency else "-"
            else:
                status_text = "🔴 Offline"
                latency_text = "-"

            self.server_tree.insert("", "end", values=(name, protocol, status_text, latency_text))

    def load_subscription(self):
        """Load VPN subscription"""
        sub_url = "https://raw.githubusercontent.com/thegrand-it/v2keys/refs/heads/main/ss.txt"

        self.status_label.config(text="Loading...")
        self.status_details.config(text="Fetching subscription...")
        self.animation_running = True
        self.draw_status_indicator("connecting")

        def load_worker():
            try:
                response = requests.get(sub_url, timeout=10)
                response.raise_for_status()
                content = response.text.strip()

                links = [line.strip() for line in content.split('\n') if line.strip()]
                configs = []

                for link in links:
                    try:
                        config = parse_link(link)
                        configs.append(config)
                    except:
                        continue

                self.current_configs = configs

                # Update UI in main thread
                self.root.after(0, self.update_after_load, len(configs))

            except Exception as e:
                self.root.after(0, self.show_load_error, str(e))

        threading.Thread(target=load_worker, daemon=True).start()

    def update_after_load(self, count):
        """Update UI after loading servers"""
        self.animation_running = False
        self.draw_status_indicator("disconnected")
        self.status_label.config(text="Disconnected")
        self.status_details.config(text=f"Loaded {count} servers")
        self.server_count_label.config(text=f"({count} servers)")

        # Populate server list
        self.filter_servers()

        # Auto-test servers
        if self.current_configs:
            self.root.after(500, self.test_all_servers)

    def show_load_error(self, error):
        """Show loading error"""
        self.animation_running = False
        self.draw_status_indicator("disconnected")
        self.status_label.config(text="Error")
        self.status_details.config(text="Failed to load servers")
        messagebox.showerror("Error", f"Failed to load subscription: {error}")

    def test_selected_server(self):
        """Test selected server"""
        selection = self.server_tree.selection()
        if not selection:
            return

        index = self.server_tree.index(selection[0])
        if index < len(self.current_configs):
            threading.Thread(target=lambda: self.test_single_server(self.current_configs[index], index),
                           daemon=True).start()

    def test_single_server(self, config, index):
        """Test a single server"""
        host = config['host']
        port = int(config['port'])

        is_available, latency = self.test_server_connectivity(host, port)

        self.server_status[index] = {
            'available': is_available,
            'latency': latency,
            'last_tested': time.time()
        }

        self.root.after(0, self.filter_servers)

    def test_server_connectivity(self, host, port, timeout=5):
        """Test server connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            start_time = time.time()
            result = sock.connect_ex((host, port))
            end_time = time.time()
            sock.close()

            if result == 0:
                latency = round((end_time - start_time) * 1000)
                return True, latency
            return False, None
        except:
            return False, None

    def test_all_servers(self):
        """Test all servers"""
        if not self.current_configs:
            return

        self.status_details.config(text="Testing all servers...")

        def test_worker():
            total = len(self.current_configs)
            for i, config in enumerate(self.current_configs):
                self.root.after(0, lambda n=i+1, t=total:
                              self.status_details.config(text=f"Testing server {n}/{t}..."))

                host = config['host']
                port = int(config['port'])

                is_available, latency = self.test_server_connectivity(host, port)

                self.server_status[i] = {
                    'available': is_available,
                    'latency': latency,
                    'last_tested': time.time()
                }

                self.root.after(0, self.filter_servers)

            self.root.after(0, lambda: self.status_details.config(text=f"All servers tested"))

        threading.Thread(target=test_worker, daemon=True).start()

    def sort_servers_by_latency(self):
        """Sort servers by latency"""
        if not self.current_configs:
            return

        server_latencies = []
        for i, config in enumerate(self.current_configs):
            status = self.server_status.get(i, {})
            latency = status.get('latency', float('inf'))
            available = status.get('available', False)
            server_latencies.append((i, latency, available))

        server_latencies.sort(key=lambda x: (not x[2], x[1]))

        sorted_configs = []
        sorted_status = {}

        for new_index, (old_index, _, _) in enumerate(server_latencies):
            sorted_configs.append(self.current_configs[old_index])
            if old_index in self.server_status:
                sorted_status[new_index] = self.server_status[old_index]

        self.current_configs = sorted_configs
        self.server_status = sorted_status

        self.filter_servers()
        self.status_details.config(text="Servers sorted by speed")

    def connect_vpn(self):
        """Connect to selected VPN server"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a server first")
            return

        index = self.server_tree.index(selection[0])
        if index >= len(self.current_configs):
            return

        selected_config = self.current_configs[index]

        self.animation_running = True
        self.draw_status_indicator("connecting")
        self.status_label.config(text="Connecting...")
        self.status_details.config(text=f"Connecting to {selected_config.get('name', selected_config['host'])}")

        # Generate config
        v2ray_config = self.generate_v2ray_config(selected_config)

        config_path = os.path.join(os.getcwd(), "temp_config.json")
        with open(config_path, 'w') as f:
            json.dump(v2ray_config, f, indent=2)

        def run_v2ray():
            try:
                v2ray_path = os.path.join(os.getcwd(), "v2ray", "v2ray.exe")
                if not os.path.exists(v2ray_path):
                    v2ray_path = "v2ray"

                self.v2ray_process = subprocess.Popen([v2ray_path, "-config", config_path],
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE)

                self.root.after(0, self.on_connected, selected_config)

            except Exception as e:
                self.root.after(0, self.on_connect_error, str(e))

        threading.Thread(target=run_v2ray, daemon=True).start()

    def on_connected(self, config):
        """Handle successful connection"""
        self.animation_running = True
        self.draw_status_indicator("connected")
        self.status_label.config(text="Connected")
        self.status_details.config(text=f"Connected to {config.get('name', config['host'])}")
        self.connection_start_time = time.time()

        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="normal")

        self.update_connection_time()
        self.update_system_proxy()

        messagebox.showinfo("Connected", "VPN connected successfully!\nProxy: 127.0.0.1:8080")

    def on_connect_error(self, error):
        """Handle connection error"""
        self.animation_running = False
        self.draw_status_indicator("disconnected")
        self.status_label.config(text="Disconnected")
        self.status_details.config(text="Connection failed")
        messagebox.showerror("Connection Error", f"Failed to connect: {error}")

    def update_connection_time(self):
        """Update connection time display"""
        if hasattr(self, 'connection_start_time') and self.v2ray_process:
            elapsed = int(time.time() - self.connection_start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60

            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.connection_time.config(text=f"Duration: {time_str}")

            self.root.after(1000, self.update_connection_time)

    def disconnect_vpn(self):
        """Disconnect VPN"""
        if self.v2ray_process:
            self.v2ray_process.terminate()
            self.v2ray_process = None

            self.animation_running = False
            self.draw_status_indicator("disconnected")
            self.status_label.config(text="Disconnected")
            self.status_details.config(text="Ready to connect")
            self.connection_time.config(text="")

            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")

            self.update_system_proxy()
            messagebox.showinfo("Disconnected", "VPN disconnected successfully")

    def generate_v2ray_config(self, config):
        """Generate v2ray configuration"""
        v2ray_config = {
            "inbounds": [
                {
                    "port": 8080,
                    "listen": "127.0.0.1",
                    "protocol": "http",
                    "settings": {"auth": "noauth"},
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    }
                }
            ],
            "outbounds": []
        }

        if config['protocol'] == 'ss':
            outbound = {
                "protocol": "shadowsocks",
                "settings": {
                    "servers": [{
                        "address": config['host'],
                        "port": int(config['port']),
                        "password": config['password'],
                        "method": config['method']
                    }]
                }
            }
        elif config['protocol'] == 'vmess':
            outbound = {
                "protocol": "vmess",
                "settings": {
                    "vnext": [{
                        "address": config['host'],
                        "port": int(config['port']),
                        "users": [{
                            "id": config['id'],
                            "alterId": int(config.get('aid', 0)),
                            "security": "auto"
                        }]
                    }]
                },
                "streamSettings": {
                    "network": config.get('net', 'tcp'),
                    "security": "tls" if config.get('tls') == 'tls' else "none"
                }
            }
        elif config['protocol'] == 'vless':
            outbound = {
                "protocol": "vless",
                "settings": {
                    "vnext": [{
                        "address": config['host'],
                        "port": int(config['port']),
                        "users": [{
                            "id": config['uuid'],
                            "encryption": "none"
                        }]
                    }]
                },
                "streamSettings": {
                    "network": config.get('type', 'tcp'),
                    "security": config.get('security', 'none')
                }
            }
        else:
            raise ValueError(f"Unsupported protocol: {config['protocol']}")

        v2ray_config["outbounds"].append(outbound)
        v2ray_config["outbounds"].append({"protocol": "freedom", "tag": "direct"})

        return v2ray_config

    def update_system_proxy(self):
        """Update system proxy settings"""
        if self.system_proxy_var.get() and self.v2ray_process:
            self.set_system_proxy()
        else:
            self.unset_system_proxy()

    def set_system_proxy(self):
        """Enable system proxy"""
        if winreg is None:
            return

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8080")
            winreg.CloseKey(key)

            # Notify system
            if platform.system() == "Windows":
                ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
                ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
        except:
            pass

    def unset_system_proxy(self):
        """Disable system proxy"""
        if winreg is None:
            return

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)

            # Notify system
            if platform.system() == "Windows":
                ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
                ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
        except:
            pass

    def copy_server_info(self):
        """Copy server information to clipboard"""
        selection = self.server_tree.selection()
        if not selection:
            return

        index = self.server_tree.index(selection[0])
        if index < len(self.current_configs):
            config = self.current_configs[index]
            info = f"Server: {config['host']}:{config['port']}\nProtocol: {config['protocol']}"

            self.root.clipboard_clear()
            self.root.clipboard_append(info)

            # Show brief notification
            self.status_details.config(text="Server info copied to clipboard")
            self.root.after(2000, lambda: self.status_details.config(text="Ready to connect"
                                                                    if not self.v2ray_process
                                                                    else "Connected"))

    def on_app_exit(self):
        """Handle application exit - ensure proxy is removed and processes are terminated"""
        try:
            # Terminate V2Ray process if running
            if self.v2ray_process:
                self.v2ray_process.terminate()
                self.v2ray_process.wait(timeout=5)  # Wait up to 5 seconds
                self.v2ray_process = None

            # Always unset system proxy on exit
            self.unset_system_proxy()

        except Exception as e:
            # Log error but don't prevent exit
            print(f"Error during cleanup: {e}")
        finally:
            # Destroy the window to exit
            self.root.destroy()


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Set DPI awareness for Windows
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    # Create and run application
    app = VPNGUI(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
