#!/usr/bin/env python3
import time
import threading
import requests
from datetime import datetime

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
        print("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                current_time = time.time()
                
                for job in self.jobs:
                    if current_time - job['last_run'] >= job['interval']:
                        self.ping_sites()
                        job['last_run'] = current_time
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
            self.running = False

# Usage example
if __name__ == "__main__":
    scheduler = SimpleCronScheduler()
    
    # Add sites to ping
    scheduler.add_site("google.com")
    scheduler.add_site("github.com")
    scheduler.add_site("stackoverflow.com")
    
    # Add job to ping every 60 seconds
    scheduler.add_job(60)
    
    # Start scheduler
    scheduler.run()
