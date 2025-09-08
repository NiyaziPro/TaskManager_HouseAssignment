#!/usr/bin/env python3
"""
TaskMeister - Worker Assignment System
=====================================

A comprehensive GUI application for managing worker assignments to houses
with email notifications and comprehensive tracking.

Author: Your Name
License: MIT
Version: 1.0.0
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple, Optional, Dict, Any

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


# =========================
# CONFIGURATION
# =========================
class Config:
    """Application configuration constants."""
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_USER = "your_email@gmail.com"  # Change this
    EMAIL_PASS = "your_app_password"  # Change this
    DB_PATH = "task_assignments.db"

    # UI Constants
    MAIN_WINDOW_SIZE = "900x700"
    DIALOG_WINDOW_SIZE = "350x150"
    WORKER_LIST_WIDTH = 30
    WORKER_LIST_HEIGHT = 20

# =========================
# DATABASE MANAGEMENT
# =========================
class DatabaseManager:
    """Handles all database operations."""

    def __init__(self, db_path: str = Config.DB_PATH):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self) -> None:
        """Create tables and migrate existing database if needed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            self._create_tables(cursor)
            self._migrate_database(cursor)
            conn.commit()
            print("Database initialized successfully.")
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _create_tables(self, cursor: sqlite3.Cursor) -> None:
        """Create database tables if they don't exist."""
        # Workers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)

        # Houses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS houses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        # Assignment history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER,
                house_id INTEGER,
                quantity INTEGER DEFAULT 1,
                note TEXT,
                date_assigned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(worker_id) REFERENCES workers(id),
                FOREIGN KEY(house_id) REFERENCES houses(id)
            )
        """)

    def _migrate_database(self, cursor: sqlite3.Cursor) -> None:
        """Add new columns to existing database if needed."""
        cursor.execute("PRAGMA table_info(assignment_history)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add assignment_date column if it doesn't exist
        if 'assignment_date' not in columns:
            cursor.execute("ALTER TABLE assignment_history ADD COLUMN assignment_date DATE")
            cursor.execute("""
                UPDATE assignment_history 
                SET assignment_date = DATE(date_assigned) 
                WHERE assignment_date IS NULL
            """)
            print("Added assignment_date column.")

        # Add email_sent column if it doesn't exist
        if 'email_sent' not in columns:
            cursor.execute("ALTER TABLE assignment_history ADD COLUMN email_sent BOOLEAN DEFAULT 1")
            cursor.execute("UPDATE assignment_history SET email_sent = 1 WHERE email_sent IS NULL")
            print("Added email_sent column.")

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SELECT query and return all results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute INSERT, UPDATE, or DELETE query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        finally:
            conn.close()

# =========================
# EMAIL SERVICE
# =========================
class EmailService:
    """Handles email sending functionality."""

    def __init__(self, smtp_server: str = Config.SMTP_SERVER,
                 smtp_port: int = Config.SMTP_PORT,
                 email_user: str = Config.EMAIL_USER,
                 email_pass: str = Config.EMAIL_PASS):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_pass = email_pass

    def send_assignment_email(self, to_email: str, worker_name: str,
                              assignments: List[Dict], assignment_date: str) -> None:
        """Send assignment email to worker."""
        subject = f"Work Assignment - {assignment_date}"
        body = self._create_email_body(worker_name, assignments, assignment_date)

        msg = MIMEMultipart()
        msg["From"] = self.email_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.send_message(msg)

    def _create_email_body(self, worker_name: str, assignments: List[Dict],
                           assignment_date: str) -> str:
        """Create email body content."""
        lines = []
        for assignment in assignments:
            line = f"- {assignment['house_name']} → {assignment['quantity']} bedding sets"
            if assignment['note']:
                line += f" | Note: {assignment['note']}"
            lines.append(line)

        body = f"Hello {worker_name},\n\n"
        body += f"Date: {assignment_date}\n"
        body += f"You have been assigned to the following houses:\n\n"
        body += "\n".join(lines)
        body += "\n\nGood luck with your work!"

        return body

# =========================
# DIALOG WINDOWS
# =========================
class WorkerDialog:
    """Dialog for adding/editing workers."""

    def __init__(self, parent: tk.Tk, worker_data: Optional[Tuple] = None):
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title("Add Worker" if worker_data is None else "Edit Worker")
        self.window.geometry("350x150")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_widgets(worker_data)

    def _create_widgets(self, worker_data: Optional[Tuple]) -> None:
        """Create dialog widgets."""
        ttk.Label(self.window, text="Name:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        ttk.Label(self.window, text="Email:").grid(row=1, column=0, padx=8, pady=6, sticky="e")

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()

        if worker_data:
            self.name_var.set(worker_data[1])
            self.email_var.set(worker_data[2])

        ttk.Entry(self.window, textvariable=self.name_var, width=30).grid(
            row=0, column=1, padx=8, pady=6)
        ttk.Entry(self.window, textvariable=self.email_var, width=30).grid(
            row=1, column=1, padx=8, pady=6)

        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=8)

        ttk.Button(button_frame, text="Save", command=self._save).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=1, padx=5)

    def _save(self) -> None:
        """Save worker data."""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()

        if not name or not email:
            messagebox.showerror("Error", "Name and email are required.")
            return

        self.result = (name, email)
        self.window.destroy()

    def _cancel(self) -> None:
        """Cancel dialog."""
        self.window.destroy()


class HouseDialog:
    """Dialog for adding/editing houses."""

    def __init__(self, parent: tk.Tk, house_data: Optional[Tuple] = None):
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title("Add House" if house_data is None else "Edit House")
        self.window.geometry("300x100")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_widgets(house_data)

    def _create_widgets(self, house_data: Optional[Tuple]) -> None:
        """Create dialog widgets."""
        ttk.Label(self.window, text="House Name:").grid(row=0, column=0, padx=8, pady=6, sticky="e")

        self.name_var = tk.StringVar()
        if house_data:
            self.name_var.set(house_data[1])

        ttk.Entry(self.window, textvariable=self.name_var, width=25).grid(
            row=0, column=1, padx=8, pady=6)

        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=1, column=0, columnspan=2, pady=8)

        ttk.Button(button_frame, text="Save", command=self._save).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).grid(row=0, column=1, padx=5)

    def _save(self) -> None:
        """Save house data."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "House name is required.")
            return

        self.result = name
        self.window.destroy()

    def _cancel(self) -> None:
        """Cancel dialog."""
        self.window.destroy()


class ListSelectionDialog:
    """Generic dialog for selecting items from a list."""

    def __init__(self, parent: tk.Tk, title: str, items: List[Tuple],
                 instruction: str, button_text: str):
        self.result = None
        self.items = items
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("300x400")
        self.window.grab_set()

        self._create_widgets(instruction, button_text)

    def _create_widgets(self, instruction: str, button_text: str) -> None:
        """Create dialog widgets."""
        ttk.Label(self.window, text=instruction).grid(row=0, column=0, padx=8, pady=6, sticky="w")

        self.listbox = tk.Listbox(self.window, height=15)
        self.listbox.grid(row=1, column=0, padx=8, pady=6, sticky="nsew")
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        for item in self.items:
            display_text = item[1] if len(item) > 1 else str(item[0])
            self.listbox.insert(tk.END, display_text)

        ttk.Button(self.window, text=button_text, command=self._select).grid(row=2, column=0, pady=8)

    def _select(self) -> None:
        """Handle item selection."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an item.")
            return

        self.result = self.items[selection[0]]
        self.window.destroy()


# =========================
# MAIN APPLICATION
# =========================
class TaskMeisterApp(tk.Tk):
    """Main application class."""

    def __init__(self):
        super().__init__()
        self.title("TaskMeister - Worker Assignment System")
        self.geometry(Config.MAIN_WINDOW_SIZE)

        # Initialize services
        self.db_manager = DatabaseManager()
        self.email_service = EmailService()

        # State variables
        self.house_vars: Dict[int, tk.IntVar] = {}
        self.house_qty: Dict[int, tk.IntVar] = {}
        self.house_notes: Dict[int, str] = {}
        self.comment_buttons: Dict[int, ttk.Button] = {}
        self.house_frames: Dict[int, ttk.Frame] = {}
        self.all_houses: List[Tuple] = []
        self.current_worker: Optional[Tuple] = None

        # Create UI
        self._setup_ui()
        self._load_initial_data()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Configure main grid
        self.grid_columnconfigure(0, weight=0)  # left panel fixed
        self.grid_columnconfigure(1, weight=1)  # right panel flexible
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._create_left_panel()
        self._create_right_panel()
        self._create_bottom_panel()

    def _create_left_panel(self) -> None:
        """Create the left panel with worker management."""
        self.left_frame = ttk.Frame(self, padding=10)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Title
        ttk.Label(self.left_frame, text="Workers",
                  font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))

        # Worker listbox with scrollbar
        listbox_frame = ttk.Frame(self.left_frame)
        listbox_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)

        self.worker_list = tk.Listbox(listbox_frame, height=Config.WORKER_LIST_HEIGHT,
                                      exportselection=False, width=Config.WORKER_LIST_WIDTH)
        self.worker_list.grid(row=0, column=0, sticky="nsew")
        self.worker_list.bind('<<ListboxSelect>>', self._on_worker_select)

        scrollbar_y = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.worker_list.yview)
        self.worker_list.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Worker management buttons
        self._create_worker_buttons()

    def _create_worker_buttons(self) -> None:
        """Create worker management buttons."""
        button_frame = ttk.Frame(self.left_frame)
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Button(button_frame, text="Add", command=self._add_worker).grid(
            row=0, column=0, padx=2, sticky="ew")
        ttk.Button(button_frame, text="Edit", command=self._edit_worker).grid(
            row=0, column=1, padx=2, sticky="ew")
        ttk.Button(button_frame, text="Delete", command=self._delete_worker).grid(
            row=0, column=2, padx=2, sticky="ew")
        ttk.Button(button_frame, text="Unselect", command=self._unselect_worker).grid(
            row=0, column=3, padx=2, sticky="ew")

    def _create_right_panel(self) -> None:
        """Create the right panel with house management."""
        self.right_frame = ttk.Frame(self, padding=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)

        self._create_house_header()
        self._create_search_box()
        self._create_house_list()

    def _create_house_header(self) -> None:
        """Create house management header with buttons."""
        title_frame = ttk.Frame(self.right_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        title_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(title_frame, text="Houses",
                  font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")

        house_btn_frame = ttk.Frame(title_frame)
        house_btn_frame.grid(row=0, column=1, sticky="e")

        ttk.Button(house_btn_frame, text="Add House", command=self._add_house).grid(
            row=0, column=0, padx=2)
        ttk.Button(house_btn_frame, text="Edit House", command=self._edit_house).grid(
            row=0, column=1, padx=2)
        ttk.Button(house_btn_frame, text="Delete House", command=self._delete_house).grid(
            row=0, column=2, padx=2)

    def _create_search_box(self) -> None:
        """Create search functionality for houses."""
        search_frame = ttk.Frame(self.right_frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        search_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._filter_houses)
        ttk.Entry(search_frame, textvariable=self.search_var).grid(row=0, column=1, sticky="ew")

    def _create_house_list(self) -> None:
        """Create scrollable house list."""
        self.houses_canvas = tk.Canvas(self.right_frame)
        self.houses_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical",
                                              command=self.houses_canvas.yview)
        self.houses_scrollable_frame = ttk.Frame(self.houses_canvas)

        self.houses_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.houses_canvas.configure(scrollregion=self.houses_canvas.bbox("all"))
        )

        self.houses_canvas.create_window((0, 0), window=self.houses_scrollable_frame, anchor="nw")
        self.houses_canvas.configure(yscrollcommand=self.houses_scrollbar.set)

        self.houses_canvas.grid(row=2, column=0, sticky="nsew")
        self.houses_scrollbar.grid(row=2, column=1, sticky="ns")

        # Bind mousewheel
        self.houses_canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _create_bottom_panel(self) -> None:
        """Create bottom panel with date selection and action buttons."""
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom_frame.grid_columnconfigure(1, weight=1)

        self._create_date_selector(bottom_frame)
        self._create_action_buttons(bottom_frame)

    def _create_date_selector(self, parent: ttk.Frame) -> None:
        """Create date selection widget."""
        date_frame = ttk.Frame(parent)
        date_frame.grid(row=0, column=0, sticky="w")

        ttk.Label(date_frame, text="Assignment Date:").grid(row=0, column=0, padx=(0, 5))

        if DateEntry:
            tomorrow = datetime.now().date() + timedelta(days=1)
            self.date_var = tk.StringVar()
            self.date_picker = DateEntry(date_frame, textvariable=self.date_var,
                                         date_pattern='dd.mm.yyyy',
                                         mindate=datetime.now().date(),
                                         width=12)
            self.date_picker.set_date(tomorrow)
            self.date_picker.grid(row=0, column=1)
            self.date_picker.bind('<<DateEntrySelected>>', lambda e: self._refresh_houses())
        else:
            ttk.Label(date_frame, text="Install tkcalendar for date picker").grid(row=0, column=1)

    def _create_action_buttons(self, parent: ttk.Frame) -> None:
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=0, column=2, sticky="e")

        ttk.Button(button_frame, text="Send Assignments",
                   command=self._send_assignments).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View History",
                   command=self._show_history).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Exit",
                   command=self._exit_application).grid(row=0, column=2, padx=5)

    def _load_initial_data(self) -> None:
        """Load initial data from database."""
        self._refresh_workers()
        self._refresh_houses()

    def _on_mousewheel(self, event) -> None:
        """Handle mousewheel scrolling."""
        self.houses_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Worker Management Methods
    def _refresh_workers(self) -> None:
        """Refresh the worker list."""
        self.worker_list.delete(0, tk.END)
        rows = self.db_manager.fetch_all("SELECT id, name, email FROM workers ORDER BY name ASC")
        self.workers_cache = rows

        for worker_id, name, email in rows:
            self.worker_list.insert(tk.END, f"{name} <{email}>")

    def _on_worker_select(self, event) -> None:
        """Handle worker selection."""
        selection = self.worker_list.curselection()
        if selection:
            self.current_worker = self.workers_cache[selection[0]]
            self._clear_house_selections()
            self._refresh_houses()

    def _unselect_worker(self) -> None:
        """Unselect current worker."""
        self.worker_list.selection_clear(0, tk.END)
        self.current_worker = None
        self._clear_house_selections()
        self._refresh_houses()

    def _clear_house_selections(self) -> None:
        """Clear all house selections and notes."""
        for var in self.house_vars.values():
            var.set(0)
        for var in self.house_qty.values():
            var.set(1)

        self.house_notes.clear()
        for btn in self.comment_buttons.values():
            btn.config(text="+")

    def _add_worker(self) -> None:
        """Add a new worker."""
        dialog = WorkerDialog(self)
        self.wait_window(dialog.window)

        if dialog.result:
            name, email = dialog.result
            self.db_manager.execute("INSERT INTO workers(name, email) VALUES(?, ?)", (name, email))
            self._refresh_workers()

    def _edit_worker(self) -> None:
        """Edit selected worker."""
        selection = self.worker_list.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a worker to edit.")
            return

        worker_data = self.workers_cache[selection[0]]
        dialog = WorkerDialog(self, worker_data)
        self.wait_window(dialog.window)

        if dialog.result:
            name, email = dialog.result
            self.db_manager.execute("UPDATE workers SET name=?, email=? WHERE id=?",
                                    (name, email, worker_data[0]))
            self._refresh_workers()

    def _delete_worker(self) -> None:
        """Delete selected worker."""
        selection = self.worker_list.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a worker to delete.")
            return

        worker_data = self.workers_cache[selection[0]]
        if messagebox.askyesno("Confirm", f"Delete worker '{worker_data[1]}'?"):
            self.db_manager.execute("DELETE FROM workers WHERE id=?", (worker_data[0],))
            self.current_worker = None
            self._refresh_workers()
            self._refresh_houses()

    # House Management Methods
    def _get_assigned_houses_for_date(self, date_str: str) -> List[int]:
        """Get houses already assigned for the given date."""
        rows = self.db_manager.fetch_all("""
            SELECT DISTINCT house_id FROM assignment_history 
            WHERE assignment_date = ? AND email_sent = 1
        """, (date_str,))
        return [row[0] for row in rows]

    def _refresh_houses(self) -> None:
        """Refresh the house list."""
        # Clear existing frames
        for child in self.houses_scrollable_frame.winfo_children():
            child.destroy()

        self.house_vars.clear()
        self.house_qty.clear()
        self.comment_buttons.clear()
        self.house_frames.clear()

        # Get all houses
        rows = self.db_manager.fetch_all("SELECT id, name FROM houses ORDER BY name ASC")
        self.all_houses = rows

        # Get assigned houses for selected date
        assigned_houses = []
        try:
            if hasattr(self, 'date_picker') and DateEntry:
                selected_date = self.date_picker.get_date().strftime('%Y-%m-%d')
                assigned_houses = self._get_assigned_houses_for_date(selected_date)
        except:
            pass

        # Filter available houses
        available_houses = [(hid, name) for hid, name in rows if hid not in assigned_houses]

        self._create_house_header_row()
        self._create_house_rows(available_houses)

    def _create_house_header_row(self) -> None:
        """Create header row for house list."""
        header_frame = ttk.Frame(self.houses_scrollable_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(header_frame, text="Select", width=6).grid(row=0, column=0, padx=2)
        ttk.Label(header_frame, text="House Name", width=30).grid(row=0, column=1, padx=2, sticky="w")
        ttk.Label(header_frame, text="Quantity", width=8).grid(row=0, column=2, padx=2)
        ttk.Label(header_frame, text="Comment", width=8).grid(row=0, column=3, padx=2)

    def _create_house_rows(self, available_houses: List[Tuple]) -> None:
        """Create individual house rows."""
        for row_num, (house_id, house_name) in enumerate(available_houses, start=1):
            house_frame = ttk.Frame(self.houses_scrollable_frame)
            house_frame.grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
            house_frame.grid_columnconfigure(1, weight=1)

            self.house_frames[house_id] = house_frame

            # Selection checkbox
            sel_var = tk.IntVar(value=0)
            ttk.Checkbutton(house_frame, variable=sel_var, width=6).grid(
                row=0, column=0, padx=2, sticky="w")

            # House name
            ttk.Label(house_frame, text=house_name, width=30).grid(
                row=0, column=1, padx=2, sticky="w")

            # Quantity spinbox
            qty_var = tk.IntVar(value=1)
            ttk.Spinbox(house_frame, from_=1, to=999, textvariable=qty_var,
                        width=8, justify="center").grid(row=0, column=2, padx=2)

            # Comment button
            comment_btn = ttk.Button(house_frame, text="+", width=3,
                                     command=lambda x=house_id: self._open_comment_window(x))
            comment_btn.grid(row=0, column=3, padx=2)

            # Store references
            self.house_vars[house_id] = sel_var
            self.house_qty[house_id] = qty_var
            self.comment_buttons[house_id] = comment_btn

        # Configure scrollable frame
        self.houses_scrollable_frame.grid_columnconfigure(0, weight=1)

    def _filter_houses(self, *args) -> None:
        """Filter houses based on search term."""
        search_term = self.search_var.get().lower()

        for house_id, house_frame in self.house_frames.items():
            # Find house name
            house_name = ""
            for hid, hname in self.all_houses:
                if hid == house_id:
                    house_name = hname.lower()
                    break

            # Show/hide based on search
            if search_term in house_name:
                house_frame.grid()
            else:
                house_frame.grid_remove()

    def _add_house(self) -> None:
        """Add a new house."""
        dialog = HouseDialog(self)
        self.wait_window(dialog.window)

        if dialog.result:
            self.db_manager.execute("INSERT INTO houses(name) VALUES(?)", (dialog.result,))
            self._refresh_houses()

    def _edit_house(self) -> None:
        """Edit selected house."""
        houses = self.db_manager.fetch_all("SELECT id, name FROM houses ORDER BY name ASC")
        if not houses:
            messagebox.showinfo("Info", "No houses found to edit.")
            return

        dialog = ListSelectionDialog(self, "Edit House", houses,
                                     "Select house to edit:", "Edit")
        self.wait_window(dialog.window)

        if dialog.result:
            house_data = dialog.result
            edit_dialog = HouseDialog(self, house_data)
            self.wait_window(edit_dialog.window)

            if edit_dialog.result:
                self.db_manager.execute("UPDATE houses SET name=? WHERE id=?",
                                        (edit_dialog.result, house_data[0]))
                self._refresh_houses()

    def _delete_house(self) -> None:
        """Delete selected house."""
        houses = self.db_manager.fetch_all("SELECT id, name FROM houses ORDER BY name ASC")
        if not houses:
            messagebox.showinfo("Info", "No houses found to delete.")
            return

        dialog = ListSelectionDialog(self, "Delete House", houses,
                                     "Select house to delete:", "Delete")
        self.wait_window(dialog.window)

        if dialog.result:
            house_data = dialog.result
            if messagebox.askyesno("Confirm", f"Delete house '{house_data[1]}'?"):
                self.db_manager.execute("DELETE FROM houses WHERE id=?", (house_data[0],))
                self._refresh_houses()

    def _open_comment_window(self, house_id: int) -> None:
        """Open comment window for specific house."""
        window = tk.Toplevel(self)
        window.title("Add/Edit Comment")
        window.geometry("400x200")
        window.grab_set()

        ttk.Label(window, text="Comment (house-specific):").grid(
            row=0, column=0, padx=8, pady=6, sticky="w")

        text_widget = tk.Text(window, width=45, height=6)
        text_widget.grid(row=1, column=0, padx=8, pady=6, sticky="nsew")
        window.grid_rowconfigure(1, weight=1)
        window.grid_columnconfigure(0, weight=1)

        # Load existing comment
        text_widget.insert("1.0", self.house_notes.get(house_id, ""))

        def save_comment():
            comment = text_widget.get("1.0", "end").strip()
            self.house_notes[house_id] = comment

            # Update button icon
            btn = self.comment_buttons.get(house_id)
            if btn:
                btn.config(text="✎" if comment else "+")
            window.destroy()

        ttk.Button(window, text="Save", command=save_comment).grid(row=2, column=0, pady=8)

    # Assignment Methods
    def _send_assignments(self) -> None:
        """Send assignments to selected worker."""
        if not self.current_worker:
            messagebox.showerror("Error", "Please select a worker.")
            return

        # Get selected houses
        selected_houses = []
        for house_id, var in self.house_vars.items():
            if var.get():
                qty = self.house_qty[house_id].get()
                note = self.house_notes.get(house_id, "")
                selected_houses.append((house_id, qty, note))

        if not selected_houses:
            messagebox.showerror("Error", "Please select at least one house.")
            return

        # Get assignment date
        if not hasattr(self, 'date_picker') or not DateEntry:
            messagebox.showerror("Error", "Date picker not available. Please install tkcalendar.")
            return

        assignment_date = self.date_picker.get_date().strftime('%Y-%m-%d')
        date_formatted = self.date_picker.get_date().strftime('%d.%m.%Y')

        # Prepare assignment data
        worker_id, worker_name, worker_email = self.current_worker
        assignments = self._prepare_assignment_data(selected_houses)

        try:
            # Save to database
            self._save_assignments_to_db(worker_id, selected_houses, assignment_date)

            # Send email
            self.email_service.send_assignment_email(
                worker_email, worker_name, assignments, date_formatted)

            messagebox.showinfo("Success",
                                f"Assignments sent successfully!\n"
                                f"Recipient: {worker_name} <{worker_email}>\n"
                                f"Date: {date_formatted}")

            # Clear selections and refresh
            self._clear_house_selections()
            self._refresh_houses()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send assignments: {e}")

    def _prepare_assignment_data(self, selected_houses: List[Tuple]) -> List[Dict]:
        """Prepare assignment data for email."""
        house_names = {house_id: house_name for house_id, house_name in self.all_houses}

        assignments = []
        for house_id, qty, note in selected_houses:
            assignments.append({
                'house_name': house_names.get(house_id, f"House-{house_id}"),
                'quantity': qty,
                'note': note
            })

        return assignments

    def _save_assignments_to_db(self, worker_id: int, selected_houses: List[Tuple],
                                assignment_date: str) -> None:
        """Save assignments to database."""
        for house_id, qty, note in selected_houses:
            self.db_manager.execute("""
                INSERT INTO assignment_history(worker_id, house_id, quantity, note, assignment_date, email_sent)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (worker_id, house_id, qty, note, assignment_date))

    # History Methods
    def _show_history(self) -> None:
        """Show assignment history window."""
        window = tk.Toplevel(self)
        window.title("Assignment History")
        window.geometry("900x500")

        # Create treeview with scrollbars
        tree_frame = ttk.Frame(window)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("worker", "house", "qty", "note", "assignment_date", "date_assigned", "status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Configure columns
        column_config = {
            "worker": ("Worker", 120),
            "house": ("House", 150),
            "qty": ("Quantity", 60),
            "note": ("Note", 200),
            "assignment_date": ("Assignment Date", 100),
            "date_assigned": ("Record Date", 120),
            "status": ("Status", 80)
        }

        for col, (heading, width) in column_config.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width)

        tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Load and display data
        self._load_history_data(tree)

        # Create filter and export controls
        self._create_history_controls(window, tree)

    def _load_history_data(self, tree: ttk.Treeview) -> List[Tuple]:
        """Load history data into treeview."""
        rows = self.db_manager.fetch_all("""
            SELECT w.name, h.name, a.quantity, a.note, a.assignment_date, 
                   a.date_assigned, a.email_sent
            FROM assignment_history a
            JOIN workers w ON a.worker_id = w.id
            JOIN houses h ON a.house_id = h.id
            ORDER BY a.date_assigned DESC
        """)

        for worker_name, house_name, qty, note, assignment_date, date_assigned, email_sent in rows:
            status = "Sent" if email_sent else "Pending"

            # Format dates
            try:
                assignment_formatted = datetime.strptime(assignment_date, '%Y-%m-%d').strftime('%d.%m.%Y')
            except:
                assignment_formatted = assignment_date or ""

            try:
                assigned_formatted = datetime.strptime(date_assigned, '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
            except:
                assigned_formatted = date_assigned or ""

            tree.insert("", tk.END, values=(
                worker_name, house_name, qty, note or "",
                assignment_formatted, assigned_formatted, status
            ))

        return rows

    def _create_history_controls(self, parent: tk.Toplevel, tree: ttk.Treeview) -> None:
        """Create filter and export controls for history window."""
        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, padx=(0, 5))

        filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=filter_var)
        filter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        def apply_filter(*args):
            self._apply_history_filter(tree, filter_var.get())

        filter_var.trace('w', apply_filter)

        ttk.Button(filter_frame, text="Export to CSV",
                   command=lambda: self._export_history()).grid(row=0, column=2)

    def _apply_history_filter(self, tree: ttk.Treeview, filter_text: str) -> None:
        """Apply filter to history data."""
        filter_text = filter_text.lower()

        # Clear current items
        for item in tree.get_children():
            tree.delete(item)

        # Reload filtered data
        rows = self.db_manager.fetch_all("""
            SELECT w.name, h.name, a.quantity, a.note, a.assignment_date, 
                   a.date_assigned, a.email_sent
            FROM assignment_history a
            JOIN workers w ON a.worker_id = w.id
            JOIN houses h ON a.house_id = h.id
            ORDER BY a.date_assigned DESC
        """)

        for worker_name, house_name, qty, note, assignment_date, date_assigned, email_sent in rows:
            if (filter_text in worker_name.lower() or
                    filter_text in house_name.lower() or
                    filter_text in (note or "").lower()):

                status = "Sent" if email_sent else "Pending"

                try:
                    assignment_formatted = datetime.strptime(assignment_date, '%Y-%m-%d').strftime('%d.%m.%Y')
                except:
                    assignment_formatted = assignment_date or ""

                try:
                    assigned_formatted = datetime.strptime(date_assigned, '%Y-%m-%d %H:%M:%S').strftime(
                        '%d.%m.%Y %H:%M')
                except:
                    assigned_formatted = date_assigned or ""

                tree.insert("", tk.END, values=(
                    worker_name, house_name, qty, note or "",
                    assignment_formatted, assigned_formatted, status
                ))

    def _export_history(self) -> None:
        """Export history data to CSV file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export History"
            )

            if not filename:
                return

            rows = self.db_manager.fetch_all("""
                SELECT w.name, h.name, a.quantity, a.note, a.assignment_date, 
                       a.date_assigned, a.email_sent
                FROM assignment_history a
                JOIN workers w ON a.worker_id = w.id
                JOIN houses h ON a.house_id = h.id
                ORDER BY a.date_assigned DESC
            """)

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Worker", "House", "Quantity", "Note",
                                 "Assignment Date", "Record Date", "Status"])

                for worker_name, house_name, qty, note, assignment_date, date_assigned, email_sent in rows:
                    status = "Sent" if email_sent else "Pending"

                    try:
                        assignment_formatted = datetime.strptime(assignment_date, '%Y-%m-%d').strftime('%d.%m.%Y')
                    except:
                        assignment_formatted = assignment_date or ""

                    try:
                        assigned_formatted = datetime.strptime(date_assigned, '%Y-%m-%d %H:%M:%S').strftime(
                            '%d.%m.%Y %H:%M')
                    except:
                        assigned_formatted = date_assigned or ""

                    writer.writerow([
                        worker_name, house_name, qty, note or "",
                        assignment_formatted, assigned_formatted, status
                    ])

            messagebox.showinfo("Success", f"Data exported successfully to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def _exit_application(self) -> None:
        """Safely exit the application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.quit()
            self.destroy()


# =========================
# APPLICATION ENTRY POINT
# =========================
def main():
    """Main entry point for the application."""
    # Check for required dependencies
    if DateEntry is None:
        print("Warning: tkcalendar module not found.")
        print("Install it with: pip install tkcalendar")
        print("Date picker functionality will be limited.")

    try:
        app = TaskMeisterApp()
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start: {e}")


if __name__ == "__main__":
    main()