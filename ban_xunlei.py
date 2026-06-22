import json
import time
import argparse
from urllib import request, parse
from http import cookiejar

# =================================================================
# USER CONFIGURATION: Edit these variables to suit your environment
# =================================================================
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8090
DEFAULT_TORRENT_INTERVAL = 300  # Seconds to refresh torrent list
DEFAULT_PEER_INTERVAL = 10      # Seconds to refresh peers list
USERNAME = 'admin'              # Your qBittorrent Web UI username
PASSWORD = 'adminadmin'         # Your qBittorrent Web UI password

# Add new patterns here (case-insensitive check is performed)
LEECH_PATTERNS = ['XunLei', '-XL', 'Thunder', 'Xunlei', 'Xfplay'] 
# =================================================================

class XunleiBanner:
    def __init__(self, config):
        self.url = f"{'https' if config.s else 'http'}://{config.u}:{config.p}"
        self.torrent_interval = config.a
        self.peer_interval = config.b
        self.cj = cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))
        request.install_opener(self.opener)
        self.login()

    def login(self):
        data = parse.urlencode({'username': USERNAME, 'password': PASSWORD}).encode()
        req = request.Request(f"{self.url}/api/v2/auth/login", data=data)
        try:
            self.opener.open(req)
            print("✔ Successfully connected to qBittorrent")
        except Exception as e:
            print(f"✘ Login failed: {e}")

    def get_json(self, path):
        with self.opener.open(f"{self.url}{path}") as resp:
            return json.loads(resp.read().decode())

    def ban_ip_globally(self, ip_to_ban):
        """Adds an IP to the global qBittorrent banned_IPs list."""
        prefs = self.get_json("/api/v2/app/preferences")
        current_bans = prefs.get('banned_IPs', '')
        
        # Avoid duplicates and update
        ban_list = [ip.strip() for ip in current_bans.split('\n') if ip.strip()]
        if ip_to_ban not in ban_list:
            ban_list.append(ip_to_ban)
            new_bans = '\n'.join(ban_list)
            
            data = parse.urlencode({'json': json.dumps({'banned_IPs': new_bans})}).encode()
            req = request.Request(f"{self.url}/api/v2/app/setPreferences", data=data)
            self.opener.open(req)
            print(f"✔ Globally banned IP: {ip_to_ban}")

    def run(self):
        print(f"Monitoring started: Torrent refresh={self.torrent_interval}s, Peer filter={self.peer_interval}s")
        print("Press Ctrl+C to stop.")
        last_torrent_fetch = 0
        hashes = []
        
        while True:
            if time.time() - last_torrent_fetch >= self.torrent_interval:
                print("Refreshing torrent list...")
                torrents = self.get_json("/api/v2/sync/maindata").get('torrents', {})
                hashes = list(torrents.keys())
                last_torrent_fetch = time.time()

            for h in hashes:
                try:
                    peers_data = self.get_json(f"/api/v2/sync/torrentPeers?hash={h}").get('peers', {})
                    for ip_port, info in peers_data.items():
                        client = info.get('client', '')
                        ip = ip_port.split(':')[0]
                        
                        if any(pattern.lower() in client.lower() for pattern in LEECH_PATTERNS):
                            print(f"Detected leech: {ip} ({client}) -> Globally Banning...")
                            self.ban_ip_globally(ip)
                except Exception:
                    pass
                
                time.sleep(self.peer_interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Auto-ban Leech peers globally in qBittorrent.")
    parser.add_argument('-u', default=DEFAULT_HOST, help='Host address')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, help='Port number')
    parser.add_argument('-a', default=DEFAULT_TORRENT_INTERVAL, type=int, help='Torrent refresh interval')
    parser.add_argument('-b', default=DEFAULT_PEER_INTERVAL, type=int, help='Peer refresh interval')
    parser.add_argument('-s', action="store_true", help='Use HTTPS')
    
    config = parser.parse_args()
    banner = XunleiBanner(config)
    
    try:
        banner.run()
    except KeyboardInterrupt:
        print("\n✔ Monitoring stopped by user. Goodbye!")