import time
import threading
import schedule
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Callable
from dataclasses import dataclass
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PingResult:
    url: str
    status: str
    response_time: float
    status_code: int = None
    error: str = None
    timestamp: datetime = None

class SitePinger:
    """Handles pinging multiple sites and collecting results"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        
    def ping_site(self, url: str) -> PingResult:
        """Ping a single site and return result"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return PingResult(
                url=url,
                status="success",
                response_time=round(response_time, 2),
                status_code=response.status_code,
                timestamp=datetime.now()
            )
            
        except requests.exceptions.RequestException as e:
            return PingResult(
                url=url,
                status="failed",
                response_time=0,
                error=str(e),
                timestamp=datetime.now()
            )
    
    def ping_multiple_sites(self, urls: List[str]) -> List[PingResult]:
        """Ping multiple sites concurrently"""
        results = []
        threads = []
        
        def ping_worker(url):
            result = self.ping_site(url)
            results.append(result)
            
        for url in urls:
            thread = threading.Thread(target=ping_worker, args=(url,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        return results

class CronJob:
    """Represents a single cron job"""
    
    def __init__(self, name: str, func: Callable, schedule_time: str, args=None, kwargs=None):
        self.name = name
        self.func = func
        self.schedule_time = schedule_time
        self.args = args or []
        self.kwargs = kwargs or {}
        self.last_run = None
        self.run_count = 0
        self.is_active = True
        
    def execute(self):
        """Execute the job function"""
        if not self.is_active:
            return
            
        try:
            logger.info(f"Executing job: {self.name}")
            self.func(*self.args, **self.kwargs)
            self.last_run = datetime.now()
            self.run_count += 1
            logger.info(f"Job {self.name} completed successfully")
        except Exception as e:
            logger.error(f"Job {self.name} failed: {str(e)}")

class CronScheduler:
    """Custom cron job scheduler"""
    
    def __init__(self):
        self.jobs = {}
        self.pinger = SitePinger()
        self.running = False
        self.scheduler_thread = None
        self.sites_to_ping = []
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping scheduler...")
        self.stop()
        sys.exit(0)
        
    def add_site(self, url: str):
        """Add a site to ping list"""
        if url not in self.sites_to_ping:
            self.sites_to_ping.append(url)
            logger.info(f"Added site: {url}")
        else:
            logger.warning(f"Site {url} already in ping list")
            
    def remove_site(self, url: str):
        """Remove a site from ping list"""
        if url in self.sites_to_ping:
            self.sites_to_ping.remove(url)
            logger.info(f"Removed site: {url}")
        else:
            logger.warning(f"Site {url} not found in ping list")
            
    def ping_all_sites(self):
        """Ping all sites in the list"""
        if not self.sites_to_ping:
            logger.warning("No sites configured for pinging")
            return
            
        logger.info(f"Pinging {len(self.sites_to_ping)} sites...")
        results = self.pinger.ping_multiple_sites(self.sites_to_ping)
        
        # Log results
        for result in results:
            if result.status == "success":
                logger.info(f"✓ {result.url} - {result.status_code} - {result.response_time}ms")
            else:
                logger.error(f"✗ {result.url} - {result.error}")
                
        return results
        
    def add_job(self, name: str, func: Callable, schedule_time: str, args=None, kwargs=None):
        """Add a new cron job"""
        job = CronJob(name, func, schedule_time, args, kwargs)
        self.jobs[name] = job
        
        # Parse schedule and add to scheduler
        self._schedule_job(job)
        logger.info(f"Added job: {name} scheduled for {schedule_time}")
        
    def _schedule_job(self, job: CronJob):
        """Parse schedule time and add job to scheduler"""
        schedule_str = job.schedule_time.lower()
        
        if schedule_str == "every minute":
            schedule.every().minute.do(job.execute)
        elif schedule_str.startswith("every ") and schedule_str.endswith(" minutes"):
            minutes = int(schedule_str.split()[1])
            schedule.every(minutes).minutes.do(job.execute)
        elif schedule_str.startswith("every ") and schedule_str.endswith(" seconds"):
            seconds = int(schedule_str.split()[1])
            schedule.every(seconds).seconds.do(job.execute)
        elif schedule_str == "hourly":
            schedule.every().hour.do(job.execute)
        elif schedule_str == "daily":
            schedule.every().day.do(job.execute)
        elif ":" in schedule_str:  # Time format like "14:30"
            schedule.every().day.at(schedule_str).do(job.execute)
        else:
            raise ValueError(f"Invalid schedule format: {schedule_str}")
            
    def remove_job(self, name: str):
        """Remove a job from scheduler"""
        if name in self.jobs:
            job = self.jobs[name]
            job.is_active = False
            del self.jobs[name]
            logger.info(f"Removed job: {name}")
        else:
            logger.warning(f"Job {name} not found")
            
    def list_jobs(self):
        """List all jobs and their status"""
        if not self.jobs:
            print("No jobs scheduled")
            return
            
        print("\n=== Scheduled Jobs ===")
        for name, job in self.jobs.items():
            status = "Active" if job.is_active else "Inactive"
            last_run = job.last_run.strftime("%Y-%m-%d %H:%M:%S") if job.last_run else "Never"
            print(f"Name: {name}")
            print(f"  Schedule: {job.schedule_time}")
            print(f"  Status: {status}")
            print(f"  Run Count: {job.run_count}")
            print(f"  Last Run: {last_run}")
            print()
            
    def list_sites(self):
        """List all sites configured for pinging"""
        if not self.sites_to_ping:
            print("No sites configured for pinging")
            return
            
        print("\n=== Sites to Ping ===")
        for i, site in enumerate(self.sites_to_ping, 1):
            print(f"{i}. {site}")
        print()
        
    def start(self):
        """Start the scheduler"""
        self.running = True
        logger.info("Starting cron scheduler...")
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
                
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started successfully")
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")
        
    def run_interactive(self):
        """Run interactive mode"""
        print("=== Custom Cron Job Scheduler ===")
        print("Type 'help' for available commands")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "help":
                    self._show_help()
                elif command == "start":
                    self.start()
                elif command == "stop":
                    self.stop()
                elif command == "status":
                    print(f"Scheduler is {'running' if self.running else 'stopped'}")
                elif command == "jobs":
                    self.list_jobs()
                elif command == "sites":
                    self.list_sites()
                elif command.startswith("add-site "):
                    url = command.split(" ", 1)[1]
                    self.add_site(url)
                elif command.startswith("remove-site "):
                    url = command.split(" ", 1)[1]
                    self.remove_site(url)
                elif command == "ping-now":
                    self.ping_all_sites()
                elif command.startswith("add-job "):
                    self._add_job_interactive(command)
                elif command.startswith("remove-job "):
                    job_name = command.split(" ", 1)[1]
                    self.remove_job(job_name)
                elif command in ["quit", "exit"]:
                    self.stop()
                    print("Goodbye!")
                    break
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nReceived interrupt signal")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error processing command: {str(e)}")
                
    def _show_help(self):
        """Show help information"""
        print("""
Available commands:
  help                    - Show this help message
  start                   - Start the scheduler
  stop                    - Stop the scheduler  
  status                  - Show scheduler status
  jobs                    - List all scheduled jobs
  sites                   - List all sites to ping
  add-site <url>          - Add a site to ping list
  remove-site <url>       - Remove a site from ping list
  ping-now                - Ping all sites immediately
  add-job <name> <schedule> - Add a ping job (e.g., "every 5 minutes")
  remove-job <name>       - Remove a job
  quit/exit               - Exit the program

Example schedule formats:
  "every minute"          - Run every minute
  "every 5 minutes"       - Run every 5 minutes
  "every 30 seconds"      - Run every 30 seconds
  "hourly"                - Run every hour
  "daily"                 - Run once per day
  "14:30"                 - Run daily at 2:30 PM
        """)
        
    def _add_job_interactive(self, command):
        """Add a job interactively"""
        try:
            parts = command.split(" ", 2)
            if len(parts) < 3:
                print("Usage: add-job <name> <schedule>")
                return
                
            name = parts[1]
            schedule_time = parts[2]
            
            # Create a ping job
            self.add_job(name, self.ping_all_sites, schedule_time)
            
        except Exception as e:
            print(f"Error adding job: {str(e)}")

def main():
    """Main function"""
    scheduler = CronScheduler()
    
    # Add some example sites
    scheduler.add_site("google.com")
    scheduler.add_site("github.com")
    scheduler.add_site("stackoverflow.com")
    
    # Add a default ping job
    scheduler.add_job("ping_sites", scheduler.ping_all_sites, "every 5 minutes")
    
    # Start interactive mode
    scheduler.run_interactive()

if __name__ == "__main__":
    main()
