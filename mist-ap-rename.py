import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
import csv
import os
import re

class APRenamingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("AP Renaming Tool")
        self.root.geometry("700x600")
        
        # Variables
        self.global_instance = tk.StringVar(value="Global 01")
        self.org_id = tk.StringVar()
        self.api_token = tk.StringVar()
        self.csv_file_path = tk.StringVar()
        self.has_headers = tk.BooleanVar(value=True)
        self.base_url = tk.StringVar(value="https://api.mist.com")
        self.selected_site = tk.StringVar()
        self.site_data = []
        
        # Create UI
        self.create_ui()
        
        # Load config if exists
        self.load_config()

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Global Instance Selection
        ttk.Label(main_frame, text="Global Instance:  ").grid(row=0, column=0, sticky=tk.W, pady=5)
        global_options = ["Global 01", "Global 02", "Global 03", "Global 04"]
        global_dropdown = ttk.Combobox(main_frame, textvariable=self.global_instance, values=global_options, state="readonly")
        global_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        global_dropdown.bind("<<ComboboxSelected>>", self.update_base_url)
        
        # Organization ID
        ttk.Label(main_frame, text="Organization ID:  ").grid(row=1, column=0, sticky=tk.W, pady=5)
        org_entry = ttk.Entry(main_frame, textvariable=self.org_id, width=40)
        org_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # API Token
        ttk.Label(main_frame, text="API Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        api_entry = ttk.Entry(main_frame, textvariable=self.api_token, width=40, show="*")
        api_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Save Config Button
        save_button = ttk.Button(main_frame, text="Save Config", command=self.save_config)
        save_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # CSV File Selection
        ttk.Label(main_frame, text="CSV File:").grid(row=4, column=0, sticky=tk.W, pady=5)
        csv_frame = ttk.Frame(main_frame)
        csv_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(csv_frame, textvariable=self.csv_file_path, width=30).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(csv_frame, text="Browse", command=self.select_csv_file).pack(side=tk.RIGHT)
        
        # Headers checkbox
        ttk.Checkbutton(main_frame, text="CSV has headers", variable=self.has_headers).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Sites Retrieval
        retrieve_sites_button = ttk.Button(main_frame, text="Retrieve Sites", command=self.retrieve_sites)
        retrieve_sites_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Sites display area - MODIFIED TO BE SCROLLABLE
        sites_label_frame = ttk.LabelFrame(main_frame, text="Available Sites")
        sites_label_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        sites_label_frame.rowconfigure(0, weight=1)
        sites_label_frame.columnconfigure(0, weight=1)
        
        # Create a Canvas widget for scrolling
        self.sites_canvas = tk.Canvas(sites_label_frame, height=150)
        self.sites_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Add scrollbar to the canvas
        sites_scrollbar = ttk.Scrollbar(sites_label_frame, orient=tk.VERTICAL, command=self.sites_canvas.yview)
        sites_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.sites_canvas.configure(yscrollcommand=sites_scrollbar.set)
        
        # Create a frame inside the canvas to hold the radio buttons
        self.sites_frame = ttk.Frame(self.sites_canvas)
        self.sites_canvas.create_window((0, 0), window=self.sites_frame, anchor=tk.NW, tags="self.sites_frame")
        
        # Configure canvas scrolling
        self.sites_frame.bind("<Configure>", self.on_sites_frame_configure)
        self.sites_canvas.bind("<Configure>", self.on_sites_canvas_configure)
        
        # Process CSV Button
        self.process_button = ttk.Button(main_frame, text="Process CSV", command=self.process_csv, state=tk.DISABLED)
        self.process_button.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Results text area
        ttk.Label(main_frame, text="Results:").grid(row=9, column=0, sticky=tk.W)
        
        self.results_text = tk.Text(main_frame, height=10, width=70, wrap=tk.WORD)
        self.results_text.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar to results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=10, column=2, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)  # Make sites frame expand
        main_frame.rowconfigure(10, weight=1)

    # Canvas configuration methods for scrolling
    def on_sites_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.sites_canvas.configure(scrollregion=self.sites_canvas.bbox("all"))
        
    def on_sites_canvas_configure(self, event):
        """Resize the inner frame to match the canvas width"""
        self.sites_canvas.itemconfig("self.sites_frame", width=event.width)

    def update_base_url(self, event=None):
        # Update base URL based on selected global instance
        global_instance = self.global_instance.get()
        if global_instance == "Global 01":
            self.base_url.set("https://api.mist.com")
        elif global_instance == "Global 02":
            self.base_url.set("https://api.gc1.mist.com")
        elif global_instance == "Global 03":
            self.base_url.set("https://api.ac2.mist.com")
        elif global_instance == "Global 04":
            self.base_url.set("https://api.gc2.mist.com")
            
    def select_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            self.csv_file_path.set(file_path)
            
    def save_config(self):
        """Save org_id, api_token, and global instance to config file"""
        config = {
            "global_instance": self.global_instance.get(),
            "org_id": self.org_id.get(),
            "api_token": self.api_token.get()
        }
        
        try:
            with open("org.conf", "w") as f:
                json.dump(config, f)
            messagebox.showinfo("Success", "Configuration saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
    def load_config(self):
        """Load config from file if it exists"""
        if os.path.exists("org.conf"):
            try:
                with open("org.conf", "r") as f:
                    config = json.load(f)
                    
                self.global_instance.set(config.get("global_instance", "Global 01"))
                self.org_id.set(config.get("org_id", ""))
                self.api_token.set(config.get("api_token", ""))
                self.update_base_url()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
                
    def retrieve_sites(self):
        """Retrieve sites from API and display as radio buttons"""
        # Clear previous sites
        for widget in self.sites_frame.winfo_children():
            widget.destroy()
            
        org_id = self.org_id.get()
        api_token = self.api_token.get()
        base_url = self.base_url.get()
        
        if not org_id or not api_token:
            messagebox.showerror("Error", "Organization ID and API Token are required")
            return
            
        # API call to get sites
        url = f"{base_url}/api/v1/orgs/{org_id}/sites"
        headers = {"Authorization": f"Token {api_token}"}
        
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Retrieving sites...\n")
            self.root.update_idletasks()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            self.site_data = response.json()
            
            if not self.site_data:
                self.results_text.insert(tk.END, "No sites found.\n")
                return
                
            # Display sites as radio buttons
            for i, site in enumerate(self.site_data):
                # Using a grid layout with 2 columns for the radio buttons
                row = i // 2
                col = i % 2
                
                rb = ttk.Radiobutton(
                    self.sites_frame, 
                    text=site["name"], 
                    value=site["id"],
                    variable=self.selected_site
                )
                rb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
                
            # Update canvas scroll region
            self.sites_frame.update_idletasks()
            self.sites_canvas.configure(scrollregion=self.sites_canvas.bbox("all"))
            
            self.process_button.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, f"Retrieved {len(self.site_data)} sites.\n")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Failed to retrieve sites: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
            
    def normalize_mac(self, mac):
        """Normalize MAC address by removing colons and dashes and converting to lowercase"""
        # Remove colons and dashes and convert to lowercase
        return re.sub(r'[:-]', '', mac).lower()
        
    def process_csv(self):
        """Process CSV file and rename APs"""
        csv_file = self.csv_file_path.get()
        target_site = self.selected_site.get()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
            
        if not target_site:
            messagebox.showerror("Error", "Please select a target site")
            return
            
        # Get AP inventory
        org_id = self.org_id.get()
        api_token = self.api_token.get()
        base_url = self.base_url.get()
        
        url = f"{base_url}/api/v1/orgs/{org_id}/inventory?type=ap"
        headers = {"Authorization": f"Token {api_token}"}
        
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Retrieving AP inventory...\n")
            self.root.update_idletasks()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            ap_inventory = response.json()
            
            # Create a lookup dictionary for MAC addresses
            ap_dict = {}
            for ap in ap_inventory:
                mac = self.normalize_mac(ap.get("mac", ""))
                if mac:
                    ap_dict[mac] = {
                        "id": ap.get("id"),
                        "site_id": ap.get("site_id"),
                        "current_name": ap.get("name", "")
                    }
            
            self.results_text.insert(tk.END, f"Found {len(ap_dict)} APs in inventory.\n")
            self.results_text.insert(tk.END, "Processing CSV file...\n")
            self.root.update_idletasks()
            
            # Process CSV file
            results = []
            assigned_count = 0
            renamed_count = 0
            skipped_count = 0
            
            with open(csv_file, 'r', newline='') as f:
                csv_reader = csv.reader(f)
                
                # Skip header if needed
                if self.has_headers.get():
                    next(csv_reader, None)
                    
                for row in csv_reader:
                    if len(row) < 2:
                        continue
                        
                    ap_mac = self.normalize_mac(row[0])
                    ap_name = row[1].strip()
                    
                    if ap_mac in ap_dict:
                        ap_info = ap_dict[ap_mac]
                        ap_id = ap_info["id"]
                        site_id = ap_info["site_id"]
                        
                        # If site_id is null, assign to target site
                        if site_id is None:
                            assign_url = f"{base_url}/api/v1/orgs/{org_id}/inventory"
                            assign_payload = {
                                "op": "assign",
                                "site_id": target_site,
                                "macs": [ap_mac]
                            }
                            
                            try:
                                response = requests.put(
                                    assign_url, 
                                    headers=headers, 
                                    json=assign_payload
                                )
                                response.raise_for_status()
                                
                                # Update site_id to target_site since we just assigned it
                                site_id = target_site
                                assigned_count += 1
                                results.append(f"Assigned AP {ap_mac} to target site")
                            except requests.exceptions.RequestException as e:
                                results.append(f"Failed to assign AP {ap_mac}: {str(e)}")
                                continue
                        
                        # If AP belongs to target site, rename it
                        if site_id == target_site:
                            rename_url = f"{base_url}/api/v1/sites/{site_id}/devices/{ap_id}"
                            rename_payload = {"name": ap_name}
                            
                            try:
                                response = requests.put(
                                    rename_url, 
                                    headers=headers, 
                                    json=rename_payload
                                )
                                response.raise_for_status()
                                renamed_count += 1
                                results.append(f"Renamed AP {ap_mac} from '{ap_info['current_name']}' to '{ap_name}'")
                            except requests.exceptions.RequestException as e:
                                results.append(f"Failed to rename AP {ap_mac}: {str(e)}")
                        else:
                            skipped_count += 1
                            results.append(f"Skipped AP {ap_mac} - not in target site")
                    else:
                        skipped_count += 1
                        results.append(f"Skipped AP {ap_mac} - not found in inventory")
            
            # Display results
            summary = (
                f"Processing complete.\n"
                f"Total APs processed: {assigned_count + renamed_count + skipped_count}\n"
                f"APs assigned to target site: {assigned_count}\n"
                f"APs renamed: {renamed_count}\n"
                f"APs skipped: {skipped_count}\n\n"
                "Detailed results:\n"
            )
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, summary)
            
            for result in results:
                self.results_text.insert(tk.END, f"- {result}\n")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Failed to retrieve AP inventory: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = APRenamingTool(root)
    root.mainloop()
