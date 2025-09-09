#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import threading
import json
import subprocess
import webbrowser
from datetime import datetime, timezone
import os
import time

class GitHubRepoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repository Manager - Philip S Wright")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        # Configuration
        self.github_token = self.get_github_token()
        self.github_user = "pdubbbbbs"
        self.repos_data = {}
        self.selected_repos = set()
        
        # Colors
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#0366d6',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'dark': '#343a40'
        }
        
        self.setup_ui()
        self.load_repositories()
        
    def get_github_token(self):
        """Get GitHub token from pass store"""
        try:
            result = subprocess.run(['pass', 'show', 'github/token'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to get GitHub token from pass store")
            return None
    
    def setup_ui(self):
        """Setup the user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="GitHub Repository Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Repository table
        self.setup_repository_table(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup control panel with buttons and filters"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Refresh button
        ttk.Button(control_frame, text="🔄 Refresh", 
                  command=self.refresh_repositories).pack(fill=tk.X, pady=2)
        
        # Repository actions
        ttk.Label(control_frame, text="Repository Actions:", 
                 font=('Arial', 9, 'bold')).pack(pady=(10, 2))
        
        ttk.Button(control_frame, text="📂 Open in Browser", 
                  command=self.open_selected_repos).pack(fill=tk.X, pady=1)
        
        ttk.Button(control_frame, text="📋 Clone Selected", 
                  command=self.clone_selected_repos).pack(fill=tk.X, pady=1)
        
        ttk.Button(control_frame, text="🏷️ Update License", 
                  command=self.update_selected_licenses).pack(fill=tk.X, pady=1)
        
        ttk.Button(control_frame, text="🔧 Bulk Settings", 
                  command=self.bulk_settings_dialog).pack(fill=tk.X, pady=1)
        
        # Filters
        ttk.Label(control_frame, text="Filters:", 
                 font=('Arial', 9, 'bold')).pack(pady=(10, 2))
        
        # Private/Public filter
        self.visibility_filter = tk.StringVar(value="All")
        ttk.Label(control_frame, text="Visibility:").pack()
        visibility_combo = ttk.Combobox(control_frame, textvariable=self.visibility_filter,
                                       values=["All", "Public", "Private"], state="readonly")
        visibility_combo.pack(fill=tk.X, pady=1)
        visibility_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Language filter
        self.language_filter = tk.StringVar(value="All")
        ttk.Label(control_frame, text="Language:").pack()
        self.language_combo = ttk.Combobox(control_frame, textvariable=self.language_filter,
                                          state="readonly")
        self.language_combo.pack(fill=tk.X, pady=1)
        self.language_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Search
        ttk.Label(control_frame, text="Search:").pack(pady=(10, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=1)
        search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Statistics
        self.setup_statistics(control_frame)
        
    def setup_statistics(self, parent):
        """Setup statistics panel"""
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Loading...", font=('Arial', 8))
        self.stats_label.pack()
        
    def setup_repository_table(self, parent):
        """Setup the main repository table"""
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), columnspan=2)
        
        # Define columns
        columns = (
            'select', 'name', 'visibility', 'language', 'stars', 'forks', 'issues',
            'license', 'size', 'updated', 'status', 'actions'
        )
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        column_configs = {
            'select': ('☐', 30, tk.CENTER),
            'name': ('Repository Name', 200, tk.W),
            'visibility': ('Visibility', 80, tk.CENTER),
            'language': ('Language', 100, tk.CENTER),
            'stars': ('⭐', 50, tk.CENTER),
            'forks': ('🍴', 50, tk.CENTER),
            'issues': ('📋', 50, tk.CENTER),
            'license': ('License', 100, tk.CENTER),
            'size': ('Size (KB)', 80, tk.E),
            'updated': ('Last Updated', 120, tk.CENTER),
            'status': ('Status', 100, tk.CENTER),
            'actions': ('Actions', 80, tk.CENTER)
        }
        
        for col, (heading, width, anchor) in column_configs.items():
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=width, anchor=anchor)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<Button-3>', self.on_tree_right_click)
        
        # Configure tags for row colors
        self.tree.tag_configure('private', background='#fff3cd')
        self.tree.tag_configure('archived', background='#f8d7da')
        self.tree.tag_configure('fork', background='#d4edda')
        self.tree.tag_configure('selected', background='#cce5ff')
        
    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        
    def load_repositories(self):
        """Load repositories from GitHub API"""
        if not self.github_token:
            return
            
        def load_thread():
            self.set_status("Loading repositories...")
            self.progress_var.set(10)
            
            try:
                headers = {
                    'Authorization': f'token {self.github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                # Get all repositories
                repos = []
                page = 1
                while True:
                    response = requests.get(
                        f'https://api.github.com/user/repos?per_page=100&page={page}',
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    page_repos = response.json()
                    if not page_repos:
                        break
                        
                    repos.extend(page_repos)
                    page += 1
                    self.progress_var.set(min(90, 10 + len(repos) * 2))
                
                # Process repository data
                self.repos_data = {}
                languages = set()
                
                for repo in repos:
                    repo_data = self.process_repo_data(repo)
                    self.repos_data[repo['name']] = repo_data
                    if repo_data['language']:
                        languages.add(repo_data['language'])
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_ui_with_repos(languages))
                
            except requests.exceptions.RequestException as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load repositories: {e}"))
            finally:
                self.root.after(0, lambda: self.progress_var.set(0))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def process_repo_data(self, repo):
        """Process repository data from API response"""
        updated_date = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        days_since_update = (datetime.now(timezone.utc) - updated_date).days
        
        # Determine status
        if repo['archived']:
            status = "🗄️ Archived"
        elif days_since_update > 365:
            status = "😴 Stale"
        elif days_since_update > 180:
            status = "⚠️ Inactive"
        elif days_since_update > 30:
            status = "📝 Active"
        else:
            status = "🔥 Hot"
        
        return {
            'name': repo['name'],
            'full_name': repo['full_name'],
            'private': repo['private'],
            'html_url': repo['html_url'],
            'clone_url': repo['clone_url'],
            'language': repo['language'] or 'None',
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'issues': repo['open_issues_count'],
            'size': repo['size'],
            'updated_at': updated_date.strftime('%Y-%m-%d'),
            'status': status,
            'archived': repo['archived'],
            'fork': repo['fork'],
            'license': repo['license']['name'] if repo['license'] else 'None',
            'description': repo['description'] or '',
            'topics': repo.get('topics', []),
            'default_branch': repo['default_branch']
        }
    
    def update_ui_with_repos(self, languages):
        """Update UI with loaded repository data"""
        # Update language filter
        language_values = ["All"] + sorted(list(languages))
        self.language_combo['values'] = language_values
        
        # Populate tree
        self.populate_tree()
        
        # Update statistics
        self.update_statistics()
        
        self.set_status(f"Loaded {len(self.repos_data)} repositories")
    
    def populate_tree(self):
        """Populate the tree with repository data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Apply filters
        filtered_repos = self.apply_current_filters()
        
        # Add repositories to tree
        for repo_name, repo_data in filtered_repos.items():
            # Determine row tags
            tags = []
            if repo_data['private']:
                tags.append('private')
            if repo_data['archived']:
                tags.append('archived')
            if repo_data['fork']:
                tags.append('fork')
            if repo_name in self.selected_repos:
                tags.append('selected')
            
            # Create row
            values = (
                '☑️' if repo_name in self.selected_repos else '☐',
                repo_data['name'],
                '🔒 Private' if repo_data['private'] else '🌐 Public',
                repo_data['language'],
                repo_data['stars'],
                repo_data['forks'],
                repo_data['issues'],
                repo_data['license'],
                f"{repo_data['size']:,}",
                repo_data['updated_at'],
                repo_data['status'],
                '⚙️'
            )
            
            item = self.tree.insert('', tk.END, values=values, tags=tags)
            # Store repo name in item for reference
            self.tree.set(item, '#0', repo_name)
    
    def apply_current_filters(self):
        """Apply current filters and return filtered repository data"""
        filtered = {}
        
        visibility_filter = self.visibility_filter.get()
        language_filter = self.language_filter.get()
        search_term = self.search_var.get().lower()
        
        for repo_name, repo_data in self.repos_data.items():
            # Visibility filter
            if visibility_filter == "Public" and repo_data['private']:
                continue
            elif visibility_filter == "Private" and not repo_data['private']:
                continue
            
            # Language filter
            if language_filter != "All" and repo_data['language'] != language_filter:
                continue
            
            # Search filter
            if search_term and search_term not in repo_name.lower():
                continue
            
            filtered[repo_name] = repo_data
        
        return filtered
    
    def apply_filters(self, event=None):
        """Apply filters and refresh tree"""
        self.populate_tree()
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.repos_data:
            return
        
        filtered_repos = self.apply_current_filters()
        total = len(filtered_repos)
        private_count = sum(1 for r in filtered_repos.values() if r['private'])
        public_count = total - private_count
        total_stars = sum(r['stars'] for r in filtered_repos.values())
        total_forks = sum(r['forks'] for r in filtered_repos.values())
        
        stats_text = f"Repos: {total} | Public: {public_count} | Private: {private_count} | ⭐ {total_stars} | 🍴 {total_forks}"
        self.stats_label.config(text=stats_text)
    
    def sort_column(self, col):
        """Sort tree by column"""
        # Implementation for column sorting
        pass
    
    def on_tree_click(self, event):
        """Handle tree click events"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x, event.y)
            if column == '#1':  # Select column
                item = self.tree.identify_row(event.y)
                if item:
                    repo_name = self.tree.item(item)['values'][1]
                    self.toggle_repo_selection(repo_name)
    
    def on_tree_double_click(self, event):
        """Handle double-click to open repository"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            repo_name = self.tree.item(item)['values'][1]
            if repo_name in self.repos_data:
                webbrowser.open(self.repos_data[repo_name]['html_url'])
    
    def on_tree_right_click(self, event):
        """Handle right-click context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            repo_name = self.tree.item(item)['values'][1]
            self.show_context_menu(event, repo_name)
    
    def show_context_menu(self, event, repo_name):
        """Show context menu for repository"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Open in Browser", 
                               command=lambda: webbrowser.open(self.repos_data[repo_name]['html_url']))
        context_menu.add_command(label="Clone Repository", 
                               command=lambda: self.clone_repository(repo_name))
        context_menu.add_separator()
        context_menu.add_command(label="Update License", 
                               command=lambda: self.update_repository_license(repo_name))
        context_menu.add_command(label="Repository Settings", 
                               command=lambda: self.show_repo_settings(repo_name))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def toggle_repo_selection(self, repo_name):
        """Toggle repository selection"""
        if repo_name in self.selected_repos:
            self.selected_repos.remove(repo_name)
        else:
            self.selected_repos.add(repo_name)
        
        self.populate_tree()  # Refresh to update checkboxes
    
    def refresh_repositories(self):
        """Refresh repository list"""
        self.load_repositories()
    
    def open_selected_repos(self):
        """Open selected repositories in browser"""
        if not self.selected_repos:
            messagebox.showwarning("Warning", "No repositories selected")
            return
        
        for repo_name in self.selected_repos:
            if repo_name in self.repos_data:
                webbrowser.open(self.repos_data[repo_name]['html_url'])
    
    def clone_selected_repos(self):
        """Clone selected repositories"""
        if not self.selected_repos:
            messagebox.showwarning("Warning", "No repositories selected")
            return
        
        clone_dir = simpledialog.askstring("Clone Directory", 
                                         "Enter directory to clone repositories:",
                                         initialvalue=os.path.expanduser("~/git"))
        if not clone_dir:
            return
        
        def clone_thread():
            for i, repo_name in enumerate(self.selected_repos):
                if repo_name in self.repos_data:
                    repo_data = self.repos_data[repo_name]
                    self.set_status(f"Cloning {repo_name}...")
                    self.progress_var.set(int((i + 1) / len(self.selected_repos) * 100))
                    
                    try:
                        subprocess.run(['git', 'clone', repo_data['clone_url']], 
                                     cwd=clone_dir, check=True)
                    except subprocess.CalledProcessError as e:
                        self.root.after(0, lambda r=repo_name: 
                                       messagebox.showerror("Error", f"Failed to clone {r}"))
            
            self.root.after(0, lambda: self.set_status("Cloning completed"))
            self.root.after(0, lambda: self.progress_var.set(0))
        
        threading.Thread(target=clone_thread, daemon=True).start()
    
    def update_selected_licenses(self):
        """Update licenses for selected repositories"""
        if not self.selected_repos:
            messagebox.showwarning("Warning", "No repositories selected")
            return
        
        # This would implement license updating logic
        messagebox.showinfo("Info", f"License update for {len(self.selected_repos)} repositories would be implemented here")
    
    def bulk_settings_dialog(self):
        """Show bulk settings dialog"""
        if not self.selected_repos:
            messagebox.showwarning("Warning", "No repositories selected")
            return
        
        # Create bulk settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Bulk Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings options
        ttk.Label(settings_window, text=f"Bulk settings for {len(self.selected_repos)} repositories", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Placeholder for bulk settings options
        ttk.Label(settings_window, text="Bulk settings interface would be implemented here").pack(pady=20)
    
    def clone_repository(self, repo_name):
        """Clone a single repository"""
        if repo_name not in self.repos_data:
            return
        
        clone_dir = simpledialog.askstring("Clone Directory", 
                                         "Enter directory to clone repository:",
                                         initialvalue=os.path.expanduser("~/git"))
        if not clone_dir:
            return
        
        repo_data = self.repos_data[repo_name]
        
        def clone_thread():
            self.set_status(f"Cloning {repo_name}...")
            try:
                subprocess.run(['git', 'clone', repo_data['clone_url']], 
                             cwd=clone_dir, check=True)
                self.root.after(0, lambda: self.set_status(f"Successfully cloned {repo_name}"))
            except subprocess.CalledProcessError:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to clone {repo_name}"))
        
        threading.Thread(target=clone_thread, daemon=True).start()
    
    def update_repository_license(self, repo_name):
        """Update license for a single repository"""
        messagebox.showinfo("Info", f"License update for {repo_name} would be implemented here")
    
    def show_repo_settings(self, repo_name):
        """Show repository settings dialog"""
        if repo_name not in self.repos_data:
            return
        
        repo_data = self.repos_data[repo_name]
        
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title(f"Settings - {repo_name}")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Repository info
        info_frame = ttk.LabelFrame(settings_window, text="Repository Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Name: {repo_data['name']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Language: {repo_data['language']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Stars: {repo_data['stars']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Forks: {repo_data['forks']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"License: {repo_data['license']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Last Updated: {repo_data['updated_at']}").pack(anchor=tk.W)
        
        if repo_data['description']:
            ttk.Label(info_frame, text=f"Description: {repo_data['description']}", 
                     wraplength=400).pack(anchor=tk.W)
    
    def set_status(self, message):
        """Set status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = GitHubRepoManager(root)
    
    # Handle window closing
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
