# # #!/usr/bin/env python3
# # import time
# # import threading
# # import requests
# # import os
# # from datetime import datetime

# # class SimpleCronScheduler:
# #     def __init__(self):
# #         self.sites = []
# #         self.jobs = []
# #         self.running = False
    
# #     def load_sites_from_env(self):
# #         """Load sites from .env file"""
# #         if os.path.exists('.env'):
# #             with open('.env', 'r') as f:
# #                 for line in f:
# #                     line = line.strip()
# #                     if line and not line.startswith('#'):
# #                         if '=' in line:
# #                             key, value = line.split('=', 1)
# #                             if key.startswith('SITE'):
# #                                 self.add_site(value)
# #         else:
# #             print("No .env file found. Create one with SITE1=url, SITE2=url, etc.")
# #         """Add a site to ping"""
# #         if not url.startswith('http'):
# #             url = 'https://' + url
# #         self.sites.append(url)
# #         print(f"Added: {url}")
    
# #     def ping_sites(self):
# #         """Ping all sites"""
# #         print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pinging {len(self.sites)} sites...")
        
# #         for url in self.sites:
# #             try:
# #                 start = time.time()
# #                 response = requests.get(url, timeout=5)
# #                 duration = round((time.time() - start) * 1000)
# #                 print(f"✓ {url} - {response.status_code} - {duration}ms")
# #             except Exception as e:
# #                 print(f"✗ {url} - Error: {str(e)}")
    
# #     def add_job(self, interval_seconds):
# #         """Add a ping job with interval in seconds"""
# #         job = {'interval': interval_seconds, 'last_run': 0}
# #         self.jobs.append(job)
# #         print(f"Added job: ping every {interval_seconds} seconds")
    
# #     def run(self):
# #         """Start the scheduler"""
# #         self.running = True
# #         print("Scheduler started. Press Ctrl+C to stop.")
        
# #         try:
# #             while self.running:
# #                 current_time = time.time()
                
# #                 for job in self.jobs:
# #                     if current_time - job['last_run'] >= job['interval']:
# #                         self.ping_sites()
# #                         job['last_run'] = current_time
                
# #                 time.sleep(1)
# #         except KeyboardInterrupt:
# #             print("\nScheduler stopped.")
# #             self.running = False

# # # Usage example
# # if __name__ == "__main__":
# #     scheduler = SimpleCronScheduler()
# #     # Load sites from .env file
# #     scheduler.load_sites_from_env()
# #     # Add job to ping every 10 minutes (600 seconds)
# #     scheduler.add_job(600)
# #     scheduler.run()

# #!/usr/bin/env python3
# import time
# import threading
# import requests
# import os
# from datetime import datetime

# class SimpleCronScheduler:
#     def __init__(self):
#         self.sites = []
#         self.jobs = []
#         self.running = False
    
#     def add_site(self, url):
#         """Add a site to ping"""
#         if not url.startswith('http'):
#             url = 'https://' + url
#         self.sites.append(url)
#         print(f"Added: {url}")
    
#     def load_sites_from_env(self):
#         """Load sites from .env file"""
#         if os.path.exists('.env'):
#             with open('.env', 'r') as f:
#                 for line in f:
#                     line = line.strip()
#                     if line and not line.startswith('#'):
#                         if '=' in line:
#                             key, value = line.split('=', 1)
#                             if key.startswith('SITE'):
#                                 self.add_site(value)
#         else:
#             print("No .env file found. Create one with SITE1=url, SITE2=url, etc.")
    
#     def ping_sites(self):
#         """Ping all sites"""
#         print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pinging {len(self.sites)} sites...")
        
#         for url in self.sites:
#             try:
#                 start = time.time()
#                 response = requests.get(url, timeout=5)
#                 duration = round((time.time() - start) * 1000)
#                 print(f"✓ {url} - {response.status_code} - {duration}ms")
#             except Exception as e:
#                 print(f"✗ {url} - Error: {str(e)}")
    
#     def add_job(self, interval_seconds):
#         """Add a ping job with interval in seconds"""
#         job = {'interval': interval_seconds, 'last_run': 0}
#         self.jobs.append(job)
#         print(f"Added job: ping every {interval_seconds} seconds")
    
#     def run(self):
#         """Start the scheduler"""
#         self.running = True
#         print("Scheduler started. Press Ctrl+C to stop.")
        
#         try:
#             while self.running:
#                 current_time = time.time()
                
#                 for job in self.jobs:
#                     if current_time - job['last_run'] >= job['interval']:
#                         self.ping_sites()
#                         job['last_run'] = current_time
                
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print("\nScheduler stopped.")
#             self.running = False

# # Usage example
# if __name__ == "__main__":
#     scheduler = SimpleCronScheduler()
    
#     # Load sites from .env file
#     scheduler.load_sites_from_env()
    
#     # Add job to ping every 10 minutes (600 seconds)
#     scheduler.add_job(600)
    
#     # Start the scheduler
#     scheduler.run()


#!/usr/bin/env python3
import time
import threading
import requests
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleCronScheduler:
    def __init__(self):
        self.sites = []
        self.jobs = []
        self.running = False
    
    def add_site(self, url):
        """Add a site to ping"""
        if not url.startswith('http'):
            url = 'https://' + url
        self.sites.append(url)
        print(f"Added: {url}")
    
    def load_sites_from_env(self):
        """Load sites from .env file"""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key.startswith('SITE'):
                                self.add_site(value)
        else:
            # Load from environment variables
            for key, value in os.environ.items():
                if key.startswith('SITE'):
                    self.add_site(value)
    
    def ping_sites(self):
        """Ping all sites"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pinging {len(self.sites)} sites...")
        
        for url in self.sites:
            try:
                start = time.time()
                response = requests.get(url, timeout=5)
                duration = round((time.time() - start) * 1000)
                print(f"✓ {url} - {response.status_code} - {duration}ms")
            except Exception as e:
                print(f"✗ {url} - Error: {str(e)}")
    
    def add_job(self, interval_seconds):
        """Add a ping job with interval in seconds"""
        job = {'interval': interval_seconds, 'last_run': 0}
        self.jobs.append(job)
        print(f"Added job: ping every {interval_seconds} seconds")
    
    def run(self):
        """Start the scheduler"""
        self.running = True
        print("Scheduler started.")
        
        while self.running:
            current_time = time.time()
            
            for job in self.jobs:
                if current_time - job['last_run'] >= job['interval']:
                    self.ping_sites()
                    job['last_run'] = current_time
            
            time.sleep(10)

# Simple web handler
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Cron scheduler is running!')

if __name__ == "__main__":
    scheduler = SimpleCronScheduler()
    scheduler.load_sites_from_env()
    scheduler.add_job(600)
    
    # Start scheduler in background
    threading.Thread(target=scheduler.run, daemon=True).start()
    
    # Start simple web server
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Web server starting on port {port}")
    server.serve_forever()
