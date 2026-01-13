import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import threading
import time
import re
import queue
import os
import sys

class LinkScraper:
    def __init__(self, root):
        self.root = root
        self.scrape_stop_event = threading.Event()
        
        # For right-click menu
        self.right_click_menu = None
        self.root.title("Web Link Collector 1000 by Reactorcore Games")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # Set up variables
        self.scrape_mode = tk.StringVar(value="single")
        self.domain_only = tk.BooleanVar(value=False)
        self.links_found = set()
        self.visited = set()
        self.queue = queue.Queue()
        self.is_scraping = False
        self.scrape_thread = None
        
        # Create UI elements
        self.create_widgets()
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TRadiobutton', font=('Arial', 10))
        style.configure('TCheckbutton', font=('Arial', 10))
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.pack(fill=tk.X, pady=5)
        
        instructions_text = (
            "1. Enter a name for your link list file\n"
            "2. Select scraping mode\n"
            "3. Enter the URL to scrape\n"
            "4. Click 'Collect Links' to start"
        )
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # File name section
        file_frame = ttk.Frame(main_frame, padding="5")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="Link List File Name:").pack(side=tk.LEFT, padx=5)
        self.filename_entry = ttk.Entry(file_frame, width=30)
        self.filename_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.add_right_click_menu(self.filename_entry)
        ttk.Label(file_frame, text=".txt").pack(side=tk.LEFT)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Scraping Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            mode_frame, 
            text="Single Page: Get links from one specific page only", 
            variable=self.scrape_mode, 
            value="single"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            mode_frame, 
            text="Domain Crawl: Find all links across the entire domain", 
            variable=self.scrape_mode, 
            value="domain"
        ).pack(anchor=tk.W, pady=2)
        
        # Filter options
        filter_frame = ttk.LabelFrame(main_frame, text="Filter Options", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            filter_frame, 
            text="Only save links that belong to the same domain", 
            variable=self.domain_only
        ).pack(anchor=tk.W)
        
        # URL input
        url_frame = ttk.Frame(main_frame, padding="5")
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.add_right_click_menu(self.url_entry)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.pack(fill=tk.X, pady=5)
        
        self.collect_button = ttk.Button(
            button_frame, 
            text="Collect Links", 
            command=self.start_scraping
        )
        self.collect_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_scraping, 
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status and progress
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.progress_var).pack(anchor=tk.W, pady=2)
        
        self.links_count_var = tk.StringVar(value="Links found: 0")
        ttk.Label(status_frame, textvariable=self.links_count_var).pack(anchor=tk.W, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
    
    def validate_inputs(self):
        """Validate user inputs before starting the scraping process."""
        filename = self.filename_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not filename:
            messagebox.showerror("Error", "Please enter a file name.")
            return False
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return False
        
        # Check if URL has a scheme, add http:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                messagebox.showerror("Error", "Invalid URL format.")
                return False
        except Exception:
            messagebox.showerror("Error", "Invalid URL format.")
            return False
            
        return True
    
    def start_scraping(self):
        """Start the scraping process in a separate thread."""
        if not self.validate_inputs():
            return
        
        if self.is_scraping:
            return
        
        self.is_scraping = True
        self.links_found.clear()
        self.visited.clear()
        self.scrape_stop_event.clear()
        
        self.collect_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        
        url = self.url_entry.get().strip()
        
        # Start scraping in a separate thread
        self.scrape_thread = threading.Thread(
            target=self.scrape_links,
            args=(url,)
        )
        self.scrape_thread.daemon = True
        self.scrape_thread.start()
        
        # Update UI periodically
        self.root.after(100, self.update_progress)
    
    def stop_scraping(self):
        """Stop the scraping process."""
        if self.is_scraping:
            self.is_scraping = False
            self.scrape_stop_event.set()
            self.progress_var.set("Stopping... Please wait.")
            self.root.update_idletasks()
            
            # Force stop the thread if it doesn't respond quickly
            self.root.after(2000, self.force_stop_thread)
    
    def update_progress(self):
        """Update UI with current progress."""
        if self.is_scraping and self.scrape_thread and self.scrape_thread.is_alive():
            self.links_count_var.set(f"Links found: {len(self.links_found)}")
            self.root.after(100, self.update_progress)
        else:
            self.is_scraping = False
            self.collect_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress.stop()
    
    def normalize_url(self, url):
        """Normalize URL for comparison to avoid duplicates."""
        # Remove trailing slashes, fragment identifiers, etc.
        parsed = urlparse(url)
        
        # Reconstruct without fragments
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Add query parameters if they exist
        if parsed.query:
            normalized += f"?{parsed.query}"
            
        return normalized.rstrip('/')
    
    def get_domain(self, url):
        """Extract the domain from a URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def scrape_page(self, url):
        """Scrape links from a single page."""
        if url in self.visited or self.scrape_stop_event.is_set() or not self.is_scraping:
            return
        
        self.visited.add(url)
        
        try:
            self.progress_var.set(f"Scraping: {url}")
            self.root.update_idletasks()
            
            if self.scrape_stop_event.is_set() or not self.is_scraping:
                return
                
            # Respect websites by using proper headers and delays
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if self.scrape_stop_event.is_set() or not self.is_scraping:
                return
                
            # Only process text/html content
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            base_domain = self.get_domain(url)
            
            # Find all links
            for a_tag in soup.find_all('a', href=True):
                if self.scrape_stop_event.is_set() or not self.is_scraping:
                    return
                    
                href = a_tag['href'].strip()
                
                # Skip empty links, javascript, mailto, tel
                if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                # Normalize URL
                normalized_url = self.normalize_url(absolute_url)
                
                # Check domain filter
                if self.domain_only.get():
                    link_domain = self.get_domain(normalized_url)
                    if link_domain != base_domain:
                        continue
                
                # Add to found links if not already there
                if normalized_url not in self.links_found:
                    self.links_found.add(normalized_url)
                    
                    # For domain crawl, add new URLs to the queue
                    if self.scrape_mode.get() == "domain":
                        link_domain = self.get_domain(normalized_url)
                        if link_domain == base_domain and normalized_url not in self.visited:
                            self.queue.put(normalized_url)
            
            # Be gentle on the server
            if not self.scrape_stop_event.is_set() and self.is_scraping:
                time.sleep(1)
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    def scrape_links(self, start_url):
        """Main scraping function that handles single page or domain crawl."""
        try:
            # Clear queue and add starting URL
            while not self.queue.empty():
                self.queue.get()
            
            self.queue.put(start_url)
            
            if self.scrape_mode.get() == "single":
                # Single page mode
                self.scrape_page(start_url)
            else:
                # Domain crawl mode
                while not self.queue.empty() and self.is_scraping and not self.scrape_stop_event.is_set():
                    current_url = self.queue.get()
                    self.scrape_page(current_url)
            
            # Save results if any links were found
            if self.links_found and self.is_scraping and not self.scrape_stop_event.is_set():
                self.save_links()
                self.progress_var.set(f"Completed! Saved {len(self.links_found)} links.")
            else:
                if not self.is_scraping or self.scrape_stop_event.is_set():
                    self.progress_var.set("Scraping stopped by user.")
                else:
                    self.progress_var.set("No links found.")
        
        except Exception as e:
            self.progress_var.set(f"Error: {str(e)}")
        
        finally:
            self.is_scraping = False
            self.filename_entry.delete(0, tk.END)  # Clear filename input field
    
    def save_links(self):
        """Save collected links to a text file."""
        filename = self.filename_entry.get().strip()
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for link in sorted(self.links_found):
                    f.write(f"{link}\n")
            
            messagebox.showinfo("Success", f"Saved {len(self.links_found)} links to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            
    def add_right_click_menu(self, entry_widget):
        """Add right-click context menu to text fields."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Cut", command=lambda: self.right_click_action(entry_widget, "cut"))
        menu.add_command(label="Copy", command=lambda: self.right_click_action(entry_widget, "copy"))
        menu.add_command(label="Paste", command=lambda: self.right_click_action(entry_widget, "paste"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self.right_click_action(entry_widget, "select_all"))
        
        # Bind the menu
        if isinstance(entry_widget, ttk.Entry) or isinstance(entry_widget, tk.Entry):
            entry_widget.bind("<Button-3>", lambda e: self.show_menu(e, menu))
            
    def show_menu(self, event, menu):
        """Show the right-click menu."""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
            
    def right_click_action(self, widget, action):
        """Execute the selected right-click action."""
        if action == "cut":
            widget.event_generate("<<Cut>>")
        elif action == "copy":
            widget.event_generate("<<Copy>>")
        elif action == "paste":
            widget.event_generate("<<Paste>>")
        elif action == "select_all":
            widget.select_range(0, tk.END)
            
    def force_stop_thread(self):
        """Force stop the scraping thread if it's still running after the stop command."""
        if self.is_scraping and self.scrape_thread and self.scrape_thread.is_alive():
            self.is_scraping = False
            self.progress.stop()
            self.collect_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_var.set("Scraping forcefully stopped.")

def main():
    root = tk.Tk()
    app = LinkScraper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
