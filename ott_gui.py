import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import connect_db
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, timedelta

# ---------------- APP WINDOW ----------------
root = tb.Window(themename="darkly")
root.title("OTT Database Manager")
root.geometry("1200x750")
root.state('zoomed')  # Start maximized

# ---------------- DB CONNECTION ----------------
conn = connect_db()
cursor = conn.cursor()

# ---------------- UTILITY FUNCTIONS ----------------
def clear_entries(*entries):
    """Clear all entry widgets"""
    for entry in entries:
        entry.delete(0, tk.END)

def refresh_treeview(tree, query, columns):
    """Refresh a treeview with new data"""
    for item in tree.get_children():
        tree.delete(item)
    cursor.execute(query)
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

# ---------------- USER MANAGEMENT FUNCTIONS ----------------
def add_user():
    first = entry_first.get().strip()
    last = entry_last.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()

    if not all([first, last, email, phone]):
        messagebox.showerror("Error", "Please fill all fields.")
        return

    try:
        cursor.callproc("AddNewUser", [first, last, email, phone])
        conn.commit()
        messagebox.showinfo("Success", f"User {first} {last} added successfully!")
        clear_entries(entry_first, entry_last, entry_email, entry_phone)
        view_users()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def view_users():
    query = """SELECT u.user_id, u.first_name, u.last_name, ue.email, up.phone_number, u.registration_date
               FROM User u
               LEFT JOIN User_Email ue ON u.user_id = ue.user_id
               LEFT JOIN User_Phone up ON u.user_id = up.user_id
               ORDER BY u.user_id DESC"""
    refresh_treeview(tree_users, query, None)

def search_users():
    search_term = entry_user_search.get().strip()
    if not search_term:
        view_users()
        return
    
    query = f"""SELECT u.user_id, u.first_name, u.last_name, ue.email, up.phone_number, u.registration_date
               FROM User u
               LEFT JOIN User_Email ue ON u.user_id = ue.user_id
               LEFT JOIN User_Phone up ON u.user_id = up.user_id
               WHERE u.first_name LIKE '%{search_term}%' 
               OR u.last_name LIKE '%{search_term}%'
               OR ue.email LIKE '%{search_term}%'"""
    refresh_treeview(tree_users, query, None)

def delete_user():
    """Delete selected user from the database"""
    selected = tree_users.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a user to delete")
        return
    
    # Get user details
    item = tree_users.item(selected[0])
    user_data = item['values']
    user_id = user_data[0]
    user_name = f"{user_data[1]} {user_data[2]}"
    
    # Confirm deletion
    confirm = messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete user '{user_name}' (ID: {user_id})?\n\n"
        "This will also delete:\n"
        "• All user subscriptions\n"
        "• All user profiles\n"
        "• All watch history\n"
        "• All devices\n"
        "• Email and phone records\n\n"
        "This action cannot be undone!"
    )
    
    if confirm:
        try:
            cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
            conn.commit()
            messagebox.showinfo("Success", f"User '{user_name}' deleted successfully!")
            view_users()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            conn.rollback()

# ---------------- SUBSCRIPTION FUNCTIONS ----------------
def view_subscriptions():
    query = """SELECT us.subscription_id, u.first_name, u.last_name, sp.plan_name, 
               us.start_date, us.end_date, us.status, us.auto_renewal
               FROM User_Subscription us
               JOIN User u ON us.user_id = u.user_id
               JOIN Subscription_Plan sp ON us.plan_id = sp.plan_id
               ORDER BY us.subscription_id DESC"""
    refresh_treeview(tree_subscriptions, query, None)

def renew_subscription():
    try:
        sub_id = entry_sub_id.get().strip()
        if not sub_id:
            messagebox.showerror("Error", "Please enter Subscription ID")
            return
        
        cursor.callproc("RenewSubscription", [int(sub_id)])
        conn.commit()
        messagebox.showinfo("Success", f"Subscription {sub_id} renewed successfully!")
        entry_sub_id.delete(0, tk.END)
        view_subscriptions()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def check_days_left():
    try:
        sub_id = entry_days_check.get().strip()
        if not sub_id:
            messagebox.showerror("Error", "Please enter Subscription ID")
            return
        
        cursor.execute(f"SELECT DaysLeft({sub_id})")
        result = cursor.fetchone()
        if result:
            days = result[0]
            if days > 0:
                messagebox.showinfo("Days Remaining", f"Subscription has {days} days left")
            else:
                messagebox.showwarning("Expired", f"Subscription expired {abs(days)} days ago")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- CONTENT FUNCTIONS ----------------
def view_content():
    global content_cards
    
    # Clear existing content
    for widget in scrollable_frame_content.winfo_children():
        widget.destroy()
    content_cards = []
    
    query = """SELECT c.content_id, c.title, c.content_type, c.rating, c.language, 
               c.release_date, ROUND(AvgContentRating(c.content_id), 2) as avg_rating,
               c.description
               FROM Content c
               ORDER BY c.content_id DESC"""
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Group content by type
    movies = [row for row in rows if row[2] == 'movie']
    series = [row for row in rows if row[2] == 'series']
    
    # Display Movies Section
    if movies:
        movies_label = ttk.Label(scrollable_frame_content, text="🎬 Movies", 
                                font=("Helvetica", 18, "bold"), foreground="white", background="#141414")
        movies_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        movies_container = ttk.Frame(scrollable_frame_content)
        movies_container.pack(fill="x", padx=20, pady=(0, 20))
        
        for idx, movie in enumerate(movies):
            create_content_card(movies_container, movie, idx % 4)
    
    # Display Series Section
    if series:
        series_label = ttk.Label(scrollable_frame_content, text="📺 Series", 
                                font=("Helvetica", 18, "bold"), foreground="white", background="#141414")
        series_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        series_container = ttk.Frame(scrollable_frame_content)
        series_container.pack(fill="x", padx=20, pady=(0, 20))
        
        for idx, show in enumerate(series):
            create_content_card(series_container, show, idx % 4)

def create_content_card(parent, content_data, column):
    """Create a Netflix-style content card"""
    content_id, title, content_type, rating, language, release_date, avg_rating, description = content_data
    
    # Card frame
    card = ttk.Frame(parent, bootstyle="dark", relief="raised", borderwidth=2)
    card.grid(row=column//4, column=column%4, padx=10, pady=10, sticky="nsew")
    
    # Configure grid weights for responsiveness
    parent.columnconfigure(column%4, weight=1, minsize=250)
    
    # Color based on rating
    rating_colors = {
        'G': '#4CAF50',
        'PG': '#8BC34A', 
        'PG-13': '#FFC107',
        'R': '#FF9800',
        'NC-17': '#F44336'
    }
    rating_color = rating_colors.get(rating, '#9E9E9E')
    
    # Thumbnail placeholder (colored box with icon)
    thumbnail_frame = tk.Frame(card, bg=rating_color, height=140, width=240)
    thumbnail_frame.pack(fill="x", padx=5, pady=5)
    thumbnail_frame.pack_propagate(False)
    
    icon = "🎬" if content_type == "movie" else "📺"
    thumb_label = tk.Label(thumbnail_frame, text=icon, font=("Helvetica", 48), 
                          bg=rating_color, fg="white")
    thumb_label.place(relx=0.5, rely=0.5, anchor="center")
    
    # Rating badge
    rating_badge = tk.Label(thumbnail_frame, text=rating, font=("Helvetica", 10, "bold"),
                           bg="black", fg="white", padx=8, pady=2)
    rating_badge.place(x=5, y=5)
    
    # Info section
    info_frame = ttk.Frame(card, bootstyle="dark")
    info_frame.pack(fill="both", expand=True, padx=8, pady=5)
    
    # Title
    title_label = ttk.Label(info_frame, text=title[:30] + ("..." if len(title) > 30 else ""),
                           font=("Helvetica", 12, "bold"), foreground="white")
    title_label.pack(anchor="w", pady=(0, 5))
    
    # Metadata row
    meta_frame = ttk.Frame(info_frame)
    meta_frame.pack(fill="x", pady=2)
    
    # Language
    lang_label = ttk.Label(meta_frame, text=language, font=("Helvetica", 9),
                          foreground="#b3b3b3", background="#2a2a2a", padding=3)
    lang_label.pack(side="left", padx=(0, 5))
    
    # Year
    year = str(release_date).split('-')[0] if release_date else "N/A"
    year_label = ttk.Label(meta_frame, text=year, font=("Helvetica", 9),
                          foreground="#b3b3b3", background="#2a2a2a", padding=3)
    year_label.pack(side="left", padx=(0, 5))
    
    # Star rating
    if avg_rating and avg_rating > 0:
        stars = "⭐" * int(avg_rating)
        rating_text = f"{stars} {avg_rating}"
    else:
        rating_text = "☆ No ratings"
    
    star_label = ttk.Label(meta_frame, text=rating_text, font=("Helvetica", 9),
                          foreground="#FFD700")
    star_label.pack(side="left")
    
    # Description
    desc_text = description[:80] + "..." if description and len(description) > 80 else (description or "No description available")
    desc_label = ttk.Label(info_frame, text=desc_text, font=("Helvetica", 8),
                          foreground="#999999", wraplength=220)
    desc_label.pack(anchor="w", pady=(5, 5))
    
    # Hover effect
    def on_enter(e):
        card.configure(relief="solid", borderwidth=3)
        
    def on_leave(e):
        card.configure(relief="raised", borderwidth=2)
    
    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)
    
    # Store reference
    content_cards.append(card)

def search_content():
    global content_cards
    
    search_term = entry_content_search.get().strip()
    
    # Clear existing content
    for widget in scrollable_frame_content.winfo_children():
        widget.destroy()
    content_cards = []
    
    if not search_term:
        view_content()
        return
    
    query = f"""SELECT c.content_id, c.title, c.content_type, c.rating, c.language, 
               c.release_date, ROUND(AvgContentRating(c.content_id), 2) as avg_rating,
               c.description
               FROM Content c
               WHERE c.title LIKE '%{search_term}%' OR c.language LIKE '%{search_term}%'
               ORDER BY c.content_id DESC"""
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        no_results = ttk.Label(scrollable_frame_content, 
                              text=f"No results found for '{search_term}'",
                              font=("Helvetica", 16), foreground="#999999")
        no_results.pack(pady=50)
        return
    
    # Display search results
    results_label = ttk.Label(scrollable_frame_content, 
                             text=f"Search Results for '{search_term}' ({len(rows)} found)", 
                             font=("Helvetica", 18, "bold"), foreground="white", background="#141414")
    results_label.pack(anchor="w", padx=20, pady=(20, 10))
    
    results_container = ttk.Frame(scrollable_frame_content)
    results_container.pack(fill="x", padx=20, pady=(0, 20))
    
    for idx, content in enumerate(rows):
        create_content_card(results_container, content, idx % 4)

def view_top_rated():
    try:
        limit = entry_top_n.get().strip() or "10"
        cursor.callproc("TopRatedContent", [int(limit)])
        for result in cursor.stored_results():
            rows = result.fetchall()
        
        for item in tree_top_rated.get_children():
            tree_top_rated.delete(item)
        
        for row in rows:
            tree_top_rated.insert('', 'end', values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- ANALYTICS FUNCTIONS ----------------
def view_logs():
    query = "SELECT * FROM Payment_Log ORDER BY log_time DESC LIMIT 20"
    refresh_treeview(tree_logs, query, None)

def view_payment_summary():
    query = """SELECT DATE_FORMAT(payment_date, '%Y-%m') as month, 
               payment_method, COUNT(*) as transactions, SUM(amount) as total_amount
               FROM Payment
               WHERE status = 'success'
               GROUP BY DATE_FORMAT(payment_date, '%Y-%m'), payment_method
               ORDER BY month DESC"""
    refresh_treeview(tree_payment_summary, query, None)

def view_watch_stats():
    query = """SELECT c.title, COUNT(*) as views, 
               ROUND(AVG(wh.completion_percentage), 2) as avg_completion
               FROM Watch_History wh
               JOIN Content c ON wh.content_id = c.content_id
               GROUP BY c.title
               ORDER BY views DESC
               LIMIT 15"""
    refresh_treeview(tree_watch_stats, query, None)

# ---------------- DEVICE MANAGEMENT ----------------
def view_devices():
    query = """SELECT d.device_id, u.first_name, u.last_name, d.device_name, 
               d.device_type, d.last_used
               FROM Device d
               JOIN User u ON d.user_id = u.user_id
               ORDER BY d.last_used DESC"""
    refresh_treeview(tree_devices, query, None)

# ---------------- UI SETUP ----------------
# Header
header_frame = ttk.Frame(root, bootstyle="dark")
header_frame.pack(fill="x", padx=10, pady=10)

ttk.Label(header_frame, text="🎬 OTT Database Manager", 
          font=("Helvetica", 24, "bold")).pack(side="left", padx=10)

ttk.Label(header_frame, text=f"📅 {datetime.now().strftime('%B %d, %Y')}", 
          font=("Helvetica", 12)).pack(side="right", padx=10)

# Main Notebook
notebook = ttk.Notebook(root, bootstyle="dark")
notebook.pack(expand=True, fill='both', padx=10, pady=5)

# ============ TAB 1: USERS ============
tab_users = ttk.Frame(notebook)
notebook.add(tab_users, text="👤 Users")

# Add User Section
frame_add_user = ttk.LabelFrame(tab_users, text="➕ Add New User", padding=15, bootstyle="primary")
frame_add_user.pack(fill="x", padx=15, pady=10)

user_input_frame = ttk.Frame(frame_add_user)
user_input_frame.pack(fill="x")

# Row 1
ttk.Label(user_input_frame, text="First Name:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_first = ttk.Entry(user_input_frame, width=20, bootstyle="primary")
entry_first.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(user_input_frame, text="Last Name:", font=("Helvetica", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_last = ttk.Entry(user_input_frame, width=20, bootstyle="primary")
entry_last.grid(row=0, column=3, padx=5, pady=5)

# Row 2
ttk.Label(user_input_frame, text="Email:", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_email = ttk.Entry(user_input_frame, width=25, bootstyle="primary")
entry_email.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(user_input_frame, text="Phone:", font=("Helvetica", 10)).grid(row=1, column=2, padx=5, pady=5, sticky="w")
entry_phone = ttk.Entry(user_input_frame, width=20, bootstyle="primary")
entry_phone.grid(row=1, column=3, padx=5, pady=5)

ttk.Button(user_input_frame, text="✓ Add User", command=add_user, 
           bootstyle="success", width=15).grid(row=1, column=4, padx=10, pady=5)

# Search and View Users
frame_view_users = ttk.LabelFrame(tab_users, text="👥 All Users", padding=15, bootstyle="info")
frame_view_users.pack(fill="both", expand=True, padx=15, pady=10)

search_frame = ttk.Frame(frame_view_users)
search_frame.pack(fill="x", pady=(0, 10))

ttk.Label(search_frame, text="🔍 Search:", font=("Helvetica", 10)).pack(side="left", padx=5)
entry_user_search = ttk.Entry(search_frame, width=30, bootstyle="info")
entry_user_search.pack(side="left", padx=5)
ttk.Button(search_frame, text="Search", command=search_users, bootstyle="info").pack(side="left", padx=5)
ttk.Button(search_frame, text="🔄 Refresh All", command=view_users, bootstyle="secondary").pack(side="left", padx=5)
ttk.Button(search_frame, text="🗑️ Delete Selected", command=delete_user, bootstyle="danger").pack(side="left", padx=15)

# Users Treeview
tree_frame_users = ttk.Frame(frame_view_users)
tree_frame_users.pack(fill="both", expand=True)

scroll_users = ttk.Scrollbar(tree_frame_users)
scroll_users.pack(side="right", fill="y")

tree_users = ttk.Treeview(tree_frame_users, columns=("ID", "First", "Last", "Email", "Phone", "Reg Date"),
                          show="headings", height=12, yscrollcommand=scroll_users.set, bootstyle="info")
scroll_users.config(command=tree_users.yview)

tree_users.heading("ID", text="User ID")
tree_users.heading("First", text="First Name")
tree_users.heading("Last", text="Last Name")
tree_users.heading("Email", text="Email")
tree_users.heading("Phone", text="Phone")
tree_users.heading("Reg Date", text="Registration Date")

tree_users.column("ID", width=80, anchor="center")
tree_users.column("First", width=120)
tree_users.column("Last", width=120)
tree_users.column("Email", width=200)
tree_users.column("Phone", width=120)
tree_users.column("Reg Date", width=120, anchor="center")

tree_users.pack(fill="both", expand=True)

# ============ TAB 2: SUBSCRIPTIONS ============
tab_subscriptions = ttk.Frame(notebook)
notebook.add(tab_subscriptions, text="💳 Subscriptions")

# Subscription Management
frame_sub_manage = ttk.LabelFrame(tab_subscriptions, text="⚙️ Subscription Management", padding=15, bootstyle="warning")
frame_sub_manage.pack(fill="x", padx=15, pady=10)

sub_controls = ttk.Frame(frame_sub_manage)
sub_controls.pack(fill="x")

ttk.Label(sub_controls, text="Subscription ID:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_sub_id = ttk.Entry(sub_controls, width=15, bootstyle="warning")
entry_sub_id.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(sub_controls, text="🔄 Renew Subscription", command=renew_subscription, 
           bootstyle="success", width=20).grid(row=0, column=2, padx=10, pady=5)

ttk.Label(sub_controls, text="Check Days Left:", font=("Helvetica", 10)).grid(row=0, column=3, padx=15, pady=5, sticky="w")
entry_days_check = ttk.Entry(sub_controls, width=15, bootstyle="info")
entry_days_check.grid(row=0, column=4, padx=5, pady=5)
ttk.Button(sub_controls, text="📅 Check Days", command=check_days_left, 
           bootstyle="info", width=15).grid(row=0, column=5, padx=5, pady=5)

# View Subscriptions
frame_view_subs = ttk.LabelFrame(tab_subscriptions, text="📋 All Subscriptions", padding=15, bootstyle="primary")
frame_view_subs.pack(fill="both", expand=True, padx=15, pady=10)

ttk.Button(frame_view_subs, text="🔄 Refresh Subscriptions", command=view_subscriptions, 
           bootstyle="primary").pack(pady=(0, 10))

tree_frame_subs = ttk.Frame(frame_view_subs)
tree_frame_subs.pack(fill="both", expand=True)

scroll_subs = ttk.Scrollbar(tree_frame_subs)
scroll_subs.pack(side="right", fill="y")

tree_subscriptions = ttk.Treeview(tree_frame_subs, 
                                  columns=("ID", "First", "Last", "Plan", "Start", "End", "Status", "Auto-Renew"),
                                  show="headings", height=15, yscrollcommand=scroll_subs.set, bootstyle="primary")
scroll_subs.config(command=tree_subscriptions.yview)

for col in ["ID", "First", "Last", "Plan", "Start", "End", "Status", "Auto-Renew"]:
    tree_subscriptions.heading(col, text=col)
    tree_subscriptions.column(col, width=120, anchor="center")

tree_subscriptions.pack(fill="both", expand=True)

# ============ TAB 3: CONTENT ============
tab_content = ttk.Frame(notebook)
notebook.add(tab_content, text="🎬 Content")

# Search Content
frame_content_search = ttk.LabelFrame(tab_content, text="🔍 Search Content", padding=15, bootstyle="success")
frame_content_search.pack(fill="x", padx=15, pady=10)

content_search_frame = ttk.Frame(frame_content_search)
content_search_frame.pack(fill="x")

ttk.Label(content_search_frame, text="Title/Language:", font=("Helvetica", 10)).pack(side="left", padx=5)
entry_content_search = ttk.Entry(content_search_frame, width=30, bootstyle="success")
entry_content_search.pack(side="left", padx=5)
ttk.Button(content_search_frame, text="🔍 Search", command=search_content, 
           bootstyle="success").pack(side="left", padx=5)
ttk.Button(content_search_frame, text="🔄 View All", command=view_content, 
           bootstyle="secondary").pack(side="left", padx=5)

# Content Display - Netflix Style
frame_view_content = ttk.Frame(tab_content)
frame_view_content.pack(fill="both", expand=True, padx=15, pady=10)

# Canvas for scrolling
canvas_content = tk.Canvas(frame_view_content, bg="#141414", highlightthickness=0)
scrollbar_content = ttk.Scrollbar(frame_view_content, orient="vertical", command=canvas_content.yview)
scrollable_frame_content = ttk.Frame(canvas_content)

scrollable_frame_content.bind(
    "<Configure>",
    lambda e: canvas_content.configure(scrollregion=canvas_content.bbox("all"))
)

canvas_content.create_window((0, 0), window=scrollable_frame_content, anchor="nw")
canvas_content.configure(yscrollcommand=scrollbar_content.set)

canvas_content.pack(side="left", fill="both", expand=True)
scrollbar_content.pack(side="right", fill="y")

# Store content cards for updates
content_cards = []

# Top Rated Content
frame_top_rated = ttk.LabelFrame(tab_content, text="⭐ Top Rated Content", padding=15, bootstyle="warning")
frame_top_rated.pack(fill="x", padx=15, pady=10)

top_rated_controls = ttk.Frame(frame_top_rated)
top_rated_controls.pack(fill="x", pady=(0, 10))

ttk.Label(top_rated_controls, text="Top N:", font=("Helvetica", 10)).pack(side="left", padx=5)
entry_top_n = ttk.Entry(top_rated_controls, width=10, bootstyle="warning")
entry_top_n.insert(0, "10")
entry_top_n.pack(side="left", padx=5)
ttk.Button(top_rated_controls, text="📊 View Top Rated", command=view_top_rated, 
           bootstyle="warning").pack(side="left", padx=5)

tree_top_rated = ttk.Treeview(frame_top_rated, columns=("Title", "Avg Rating", "Reviews"),
                              show="headings", height=5, bootstyle="warning")
tree_top_rated.heading("Title", text="Content Title")
tree_top_rated.heading("Avg Rating", text="Average Rating")
tree_top_rated.heading("Reviews", text="Total Reviews")
tree_top_rated.column("Title", width=300)
tree_top_rated.column("Avg Rating", width=150, anchor="center")
tree_top_rated.column("Reviews", width=150, anchor="center")
tree_top_rated.pack(fill="x")

# ============ TAB 4: ANALYTICS ============
tab_analytics = ttk.Frame(notebook)
notebook.add(tab_analytics, text="📊 Analytics")

# Create main container with two columns
analytics_main = ttk.Frame(tab_analytics)
analytics_main.pack(fill="both", expand=True, padx=10, pady=10)

# Left Column
left_column = ttk.Frame(analytics_main)
left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))

# Right Column
right_column = ttk.Frame(analytics_main)
right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

# === LEFT COLUMN ===

# Revenue Summary Card
frame_revenue = ttk.LabelFrame(left_column, text="💰 Revenue Overview", padding=15, bootstyle="success")
frame_revenue.pack(fill="x", pady=(0, 10))

revenue_display = ttk.Frame(frame_revenue)
revenue_display.pack(fill="x")

# Revenue metrics
revenue_labels = {}
for i, (key, label) in enumerate([("total", "Total Revenue"), ("month", "This Month"), ("success", "Success Rate")]):
    metric_frame = ttk.Frame(revenue_display, bootstyle="dark")
    metric_frame.pack(side="left", fill="x", expand=True, padx=5)
    
    ttk.Label(metric_frame, text=label, font=("Helvetica", 9), foreground="#999").pack()
    revenue_labels[key] = ttk.Label(metric_frame, text="₹0.00", font=("Helvetica", 18, "bold"), foreground="#4CAF50")
    revenue_labels[key].pack()

def update_revenue_summary():
    try:
        # Total revenue
        cursor.execute("SELECT SUM(amount) FROM Payment WHERE status='success'")
        total = cursor.fetchone()[0] or 0
        revenue_labels["total"].config(text=f"₹{total:,.2f}")
        
        # This month revenue
        cursor.execute("""SELECT SUM(amount) FROM Payment 
                         WHERE status='success' AND MONTH(payment_date) = MONTH(CURDATE())
                         AND YEAR(payment_date) = YEAR(CURDATE())""")
        month_rev = cursor.fetchone()[0] or 0
        revenue_labels["month"].config(text=f"₹{month_rev:,.2f}")
        
        # Success rate
        cursor.execute("SELECT COUNT(*) FROM Payment WHERE status='success'")
        success = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM Payment")
        total_payments = cursor.fetchone()[0] or 1
        rate = (success / total_payments) * 100
        revenue_labels["success"].config(text=f"{rate:.1f}%")
    except Exception as e:
        print(f"Error updating revenue: {e}")

ttk.Button(frame_revenue, text="🔄 Refresh", command=update_revenue_summary, 
           bootstyle="success-outline", width=15).pack(pady=(10, 0))

# User Statistics Card
frame_user_stats = ttk.LabelFrame(left_column, text="👥 User Statistics", padding=15, bootstyle="primary")
frame_user_stats.pack(fill="x", pady=(0, 10))

user_stats_display = ttk.Frame(frame_user_stats)
user_stats_display.pack(fill="x")

user_stat_labels = {}
for key, label in [("total", "Total Users"), ("active", "Active Subs"), ("new", "New This Month")]:
    stat_frame = ttk.Frame(user_stats_display, bootstyle="dark")
    stat_frame.pack(side="left", fill="x", expand=True, padx=5)
    
    ttk.Label(stat_frame, text=label, font=("Helvetica", 9), foreground="#999").pack()
    user_stat_labels[key] = ttk.Label(stat_frame, text="0", font=("Helvetica", 18, "bold"), foreground="#2196F3")
    user_stat_labels[key].pack()

def update_user_stats():
    try:
        cursor.execute("SELECT COUNT(*) FROM User")
        user_stat_labels["total"].config(text=str(cursor.fetchone()[0]))
        
        cursor.execute("SELECT COUNT(*) FROM User_Subscription WHERE status='active'")
        user_stat_labels["active"].config(text=str(cursor.fetchone()[0]))
        
        cursor.execute("""SELECT COUNT(*) FROM User 
                         WHERE MONTH(registration_date) = MONTH(CURDATE())
                         AND YEAR(registration_date) = YEAR(CURDATE())""")
        user_stat_labels["new"].config(text=str(cursor.fetchone()[0]))
    except Exception as e:
        print(f"Error updating user stats: {e}")

ttk.Button(frame_user_stats, text="🔄 Refresh", command=update_user_stats, 
           bootstyle="primary-outline", width=15).pack(pady=(10, 0))

# Watch Statistics
frame_watch_stats = ttk.LabelFrame(left_column, text="📺 Top Content by Views", padding=15, bootstyle="info")
frame_watch_stats.pack(fill="both", expand=True, pady=(0, 10))

ttk.Button(frame_watch_stats, text="🔄 Refresh Stats", command=view_watch_stats, 
           bootstyle="info-outline", width=15).pack(pady=(0, 10))

tree_frame_watch = ttk.Frame(frame_watch_stats)
tree_frame_watch.pack(fill="both", expand=True)

scroll_watch = ttk.Scrollbar(tree_frame_watch)
scroll_watch.pack(side="right", fill="y")

tree_watch_stats = ttk.Treeview(tree_frame_watch, 
                                columns=("Title", "Views", "Avg Completion"),
                                show="headings", height=10, yscrollcommand=scroll_watch.set, bootstyle="info")
scroll_watch.config(command=tree_watch_stats.yview)

tree_watch_stats.heading("Title", text="Content Title")
tree_watch_stats.heading("Views", text="Views")
tree_watch_stats.heading("Avg Completion", text="Completion %")
tree_watch_stats.column("Title", width=200)
tree_watch_stats.column("Views", width=80, anchor="center")
tree_watch_stats.column("Avg Completion", width=100, anchor="center")
tree_watch_stats.pack(fill="both", expand=True)

# === RIGHT COLUMN ===

# Payment Method Distribution
frame_payment_methods = ttk.LabelFrame(right_column, text="💳 Payment Methods", padding=15, bootstyle="warning")
frame_payment_methods.pack(fill="x", pady=(0, 10))

payment_method_display = ttk.Frame(frame_payment_methods)
payment_method_display.pack(fill="both", expand=True)

payment_method_labels = {}

def update_payment_methods():
    try:
        cursor.execute("""SELECT payment_method, COUNT(*) as count, SUM(amount) as total
                         FROM Payment WHERE status='success'
                         GROUP BY payment_method""")
        results = cursor.fetchall()
        
        # Clear previous
        for widget in payment_method_display.winfo_children():
            widget.destroy()
        
        method_icons = {"card": "💳", "upi": "📱", "netbanking": "🏦", "wallet": "👛"}
        
        for method, count, total in results:
            method_frame = ttk.Frame(payment_method_display, bootstyle="dark", relief="solid", borderwidth=1)
            method_frame.pack(fill="x", pady=5, padx=5)
            
            icon_label = ttk.Label(method_frame, text=method_icons.get(method, "💰"), 
                                  font=("Helvetica", 24))
            icon_label.pack(side="left", padx=10, pady=10)
            
            info_frame = ttk.Frame(method_frame)
            info_frame.pack(side="left", fill="x", expand=True, pady=10)
            
            ttk.Label(info_frame, text=method.upper(), font=("Helvetica", 12, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"{count} transactions • ₹{total:,.2f}", 
                     font=("Helvetica", 9), foreground="#999").pack(anchor="w")
    except Exception as e:
        print(f"Error updating payment methods: {e}")

ttk.Button(frame_payment_methods, text="🔄 Refresh", command=update_payment_methods, 
           bootstyle="warning-outline", width=15).pack(pady=(10, 0))

# Subscription Plans Distribution
frame_plan_stats = ttk.LabelFrame(right_column, text="📊 Active Plans", padding=15, bootstyle="secondary")
frame_plan_stats.pack(fill="x", pady=(0, 10))

plan_stats_display = ttk.Frame(frame_plan_stats)
plan_stats_display.pack(fill="both", expand=True)

def update_plan_stats():
    try:
        cursor.execute("""SELECT sp.plan_name, COUNT(*) as subscribers, sp.price
                         FROM User_Subscription us
                         JOIN Subscription_Plan sp ON us.plan_id = sp.plan_id
                         WHERE us.status = 'active'
                         GROUP BY sp.plan_name, sp.price""")
        results = cursor.fetchall()
        
        # Clear previous
        for widget in plan_stats_display.winfo_children():
            widget.destroy()
        
        plan_colors = {"Basic": "#4CAF50", "Standard": "#2196F3", "Premium": "#FF9800"}
        
        for plan_name, subscribers, price in results:
            plan_frame = ttk.Frame(plan_stats_display, bootstyle="dark", relief="solid", borderwidth=1)
            plan_frame.pack(fill="x", pady=5, padx=5)
            
            # Color indicator
            color_bar = tk.Frame(plan_frame, bg=plan_colors.get(plan_name, "#999"), width=5)
            color_bar.pack(side="left", fill="y")
            
            info_frame = ttk.Frame(plan_frame)
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            ttk.Label(info_frame, text=plan_name, font=("Helvetica", 12, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"{subscribers} subscribers • ₹{price}/month", 
                     font=("Helvetica", 9), foreground="#999").pack(anchor="w")
    except Exception as e:
        print(f"Error updating plan stats: {e}")

ttk.Button(frame_plan_stats, text="🔄 Refresh", command=update_plan_stats, 
           bootstyle="secondary-outline", width=15).pack(pady=(10, 0))

# Payment Logs
frame_logs = ttk.LabelFrame(right_column, text="📜 Recent Payment Logs", padding=15, bootstyle="danger")
frame_logs.pack(fill="both", expand=True, pady=(0, 10))

ttk.Button(frame_logs, text="🔄 Refresh Logs", command=view_logs, 
           bootstyle="danger-outline", width=15).pack(pady=(0, 10))

tree_frame_logs = ttk.Frame(frame_logs)
tree_frame_logs.pack(fill="both", expand=True)

scroll_logs = ttk.Scrollbar(tree_frame_logs)
scroll_logs.pack(side="right", fill="y")

tree_logs = ttk.Treeview(tree_frame_logs, columns=("Log ID", "Payment ID", "Message", "Time"),
                         show="headings", height=10, yscrollcommand=scroll_logs.set, bootstyle="danger")
scroll_logs.config(command=tree_logs.yview)

tree_logs.heading("Log ID", text="ID")
tree_logs.heading("Payment ID", text="Pay ID")
tree_logs.heading("Message", text="Message")
tree_logs.heading("Time", text="Time")

tree_logs.column("Log ID", width=50, anchor="center")
tree_logs.column("Payment ID", width=60, anchor="center")
tree_logs.column("Message", width=250)
tree_logs.column("Time", width=120, anchor="center")
tree_logs.pack(fill="both", expand=True)

# Content Statistics
frame_content_stats = ttk.LabelFrame(right_column, text="🎬 Content Stats", padding=15, bootstyle="success")
frame_content_stats.pack(fill="x", pady=(0, 10))

content_stats_display = ttk.Frame(frame_content_stats)
content_stats_display.pack(fill="x")

content_stat_labels = {}
for key, label in [("total", "Total Content"), ("movies", "Movies"), ("series", "Series")]:
    stat_frame = ttk.Frame(content_stats_display, bootstyle="dark")
    stat_frame.pack(side="left", fill="x", expand=True, padx=5)
    
    ttk.Label(stat_frame, text=label, font=("Helvetica", 9), foreground="#999").pack()
    content_stat_labels[key] = ttk.Label(stat_frame, text="0", font=("Helvetica", 18, "bold"), foreground="#4CAF50")
    content_stat_labels[key].pack()

def update_content_stats():
    try:
        cursor.execute("SELECT COUNT(*) FROM Content")
        content_stat_labels["total"].config(text=str(cursor.fetchone()[0]))
        
        cursor.execute("SELECT COUNT(*) FROM Content WHERE content_type='movie'")
        content_stat_labels["movies"].config(text=str(cursor.fetchone()[0]))
        
        cursor.execute("SELECT COUNT(*) FROM Content WHERE content_type='series'")
        content_stat_labels["series"].config(text=str(cursor.fetchone()[0]))
    except Exception as e:
        print(f"Error updating content stats: {e}")

ttk.Button(frame_content_stats, text="🔄 Refresh", command=update_content_stats, 
           bootstyle="success-outline", width=15).pack(pady=(10, 0))

# ============ TAB 5: DEVICES ============
tab_devices = ttk.Frame(notebook)
notebook.add(tab_devices, text="📱 Devices")

# Device Statistics Cards
device_stats_frame = ttk.Frame(tab_devices)
device_stats_frame.pack(fill="x", padx=15, pady=10)

device_stat_labels = {}
device_stat_frames = {}

device_types_info = [
    ("TV", "📺", "primary"),
    ("Mobile", "📱", "success"),
    ("Laptop", "💻", "info"),
    ("Tablet", "📋", "warning"),
    ("Other", "🖥️", "secondary")
]

for device_type, icon, style in device_types_info:
    card = ttk.LabelFrame(device_stats_frame, text=f"{icon} {device_type}", 
                         padding=15, bootstyle=style)
    card.pack(side="left", fill="both", expand=True, padx=5)
    
    count_label = ttk.Label(card, text="0", font=("Helvetica", 32, "bold"))
    count_label.pack()
    
    desc_label = ttk.Label(card, text="devices", font=("Helvetica", 10), foreground="#999")
    desc_label.pack()
    
    device_stat_labels[device_type] = count_label
    device_stat_frames[device_type] = card

def update_device_stats():
    """Update device type statistics"""
    try:
        for device_type in device_stat_labels.keys():
            cursor.execute(f"SELECT COUNT(*) FROM Device WHERE device_type='{device_type}'")
            count = cursor.fetchone()[0]
            device_stat_labels[device_type].config(text=str(count))
    except Exception as e:
        print(f"Error updating device stats: {e}")

# Device Management Section
device_management_frame = ttk.Frame(tab_devices)
device_management_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

# Left side - Device List
left_device_panel = ttk.LabelFrame(device_management_frame, text="🖥️ All Devices", 
                                   padding=15, bootstyle="info")
left_device_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

# Search and filter controls
device_controls = ttk.Frame(left_device_panel)
device_controls.pack(fill="x", pady=(0, 10))

ttk.Label(device_controls, text="🔍 Search User:", font=("Helvetica", 10)).pack(side="left", padx=5)
entry_device_search = ttk.Entry(device_controls, width=25, bootstyle="info")
entry_device_search.pack(side="left", padx=5)

ttk.Label(device_controls, text="Filter Type:", font=("Helvetica", 10)).pack(side="left", padx=(15, 5))
device_type_filter = ttk.Combobox(device_controls, values=["All", "TV", "Mobile", "Laptop", "Tablet", "Other"], 
                                  width=12, state="readonly")
device_type_filter.set("All")
device_type_filter.pack(side="left", padx=5)

def search_devices():
    search_term = entry_device_search.get().strip()
    device_filter = device_type_filter.get()
    
    query = """SELECT d.device_id, u.first_name, u.last_name, d.device_name, 
               d.device_type, d.last_used
               FROM Device d
               JOIN User u ON d.user_id = u.user_id
               WHERE 1=1"""
    
    if search_term:
        query += f" AND (u.first_name LIKE '%{search_term}%' OR u.last_name LIKE '%{search_term}%' OR d.device_name LIKE '%{search_term}%')"
    
    if device_filter != "All":
        query += f" AND d.device_type = '{device_filter}'"
    
    query += " ORDER BY d.last_used DESC"
    refresh_treeview(tree_devices, query, None)

ttk.Button(device_controls, text="🔍 Search", command=search_devices, 
           bootstyle="info").pack(side="left", padx=5)
ttk.Button(device_controls, text="🔄 Show All", command=view_devices, 
           bootstyle="secondary").pack(side="left", padx=5)

# Device TreeView
tree_frame_devices = ttk.Frame(left_device_panel)
tree_frame_devices.pack(fill="both", expand=True)

scroll_devices = ttk.Scrollbar(tree_frame_devices)
scroll_devices.pack(side="right", fill="y")

tree_devices = ttk.Treeview(tree_frame_devices,
                            columns=("Device ID", "First Name", "Last Name", "Device", "Type", "Last Used"),
                            show="headings", height=18, yscrollcommand=scroll_devices.set, bootstyle="info")
scroll_devices.config(command=tree_devices.yview)

tree_devices.heading("Device ID", text="ID")
tree_devices.heading("First Name", text="First Name")
tree_devices.heading("Last Name", text="Last Name")
tree_devices.heading("Device", text="Device Name")
tree_devices.heading("Type", text="Type")
tree_devices.heading("Last Used", text="Last Used")

tree_devices.column("Device ID", width=60, anchor="center")
tree_devices.column("First Name", width=100)
tree_devices.column("Last Name", width=100)
tree_devices.column("Device", width=150)
tree_devices.column("Type", width=80, anchor="center")
tree_devices.column("Last Used", width=140, anchor="center")

tree_devices.pack(fill="both", expand=True)

# Right side - Device Details & Actions
right_device_panel = ttk.Frame(device_management_frame)
right_device_panel.pack(side="right", fill="y", padx=(5, 0))

# Device Details Card
device_details_frame = ttk.LabelFrame(right_device_panel, text="📋 Device Details", 
                                      padding=15, bootstyle="primary")
device_details_frame.pack(fill="x", pady=(0, 10))

device_detail_labels = {}
detail_fields = [
    ("device_id", "Device ID:"),
    ("user_name", "User:"),
    ("device_name", "Device Name:"),
    ("device_type", "Type:"),
    ("last_used", "Last Used:")
]

for key, label_text in detail_fields:
    frame = ttk.Frame(device_details_frame)
    frame.pack(fill="x", pady=5)
    
    ttk.Label(frame, text=label_text, font=("Helvetica", 9, "bold"), 
             foreground="#999").pack(anchor="w")
    device_detail_labels[key] = ttk.Label(frame, text="Select a device", 
                                         font=("Helvetica", 10), wraplength=200)
    device_detail_labels[key].pack(anchor="w", padx=(10, 0))

def on_device_select(event):
    """Show selected device details"""
    selected = tree_devices.selection()
    if selected:
        item = tree_devices.item(selected[0])
        values = item['values']
        
        device_detail_labels["device_id"].config(text=str(values[0]))
        device_detail_labels["user_name"].config(text=f"{values[1]} {values[2]}")
        device_detail_labels["device_name"].config(text=str(values[3]))
        device_detail_labels["device_type"].config(text=str(values[4]))
        device_detail_labels["last_used"].config(text=str(values[5]))

tree_devices.bind('<<TreeviewSelect>>', on_device_select)

# Device Actions
device_actions_frame = ttk.LabelFrame(right_device_panel, text="⚙️ Actions", 
                                      padding=15, bootstyle="warning")
device_actions_frame.pack(fill="x", pady=(0, 10))

def delete_device():
    """Delete selected device"""
    selected = tree_devices.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a device to delete")
        return
    
    item = tree_devices.item(selected[0])
    device_data = item['values']
    device_id = device_data[0]
    device_name = device_data[3]
    
    confirm = messagebox.askyesno(
        "Confirm Delete", 
        f"Delete device '{device_name}' (ID: {device_id})?\n\nThis action cannot be undone!"
    )
    
    if confirm:
        try:
            cursor.execute("DELETE FROM Device WHERE device_id = %s", (device_id,))
            conn.commit()
            messagebox.showinfo("Success", f"Device '{device_name}' deleted!")
            view_devices()
            update_device_stats()
            # Clear details
            for label in device_detail_labels.values():
                label.config(text="Select a device")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            conn.rollback()

ttk.Button(device_actions_frame, text="🗑️ Delete Device", command=delete_device, 
           bootstyle="danger", width=20).pack(fill="x", pady=5)
ttk.Button(device_actions_frame, text="🔄 Refresh List", command=lambda: [view_devices(), update_device_stats()], 
           bootstyle="secondary", width=20).pack(fill="x", pady=5)

# Most Active Users Card
active_users_frame = ttk.LabelFrame(right_device_panel, text="🏆 Most Active Users", 
                                    padding=15, bootstyle="success")
active_users_frame.pack(fill="both", expand=True)

tree_active_users = ttk.Treeview(active_users_frame, 
                                 columns=("User", "Devices"),
                                 show="headings", height=8, bootstyle="success")
tree_active_users.heading("User", text="User Name")
tree_active_users.heading("Devices", text="Device Count")
tree_active_users.column("User", width=140)
tree_active_users.column("Devices", width=80, anchor="center")
tree_active_users.pack(fill="both", expand=True)

def update_active_users():
    """Show users with most devices"""
    try:
        query = """SELECT CONCAT(u.first_name, ' ', u.last_name) as name, COUNT(d.device_id) as device_count
                   FROM User u
                   JOIN Device d ON u.user_id = d.user_id
                   GROUP BY u.user_id, name
                   ORDER BY device_count DESC
                   LIMIT 10"""
        refresh_treeview(tree_active_users, query, None)
    except Exception as e:
        print(f"Error updating active users: {e}")

ttk.Button(active_users_frame, text="🔄 Refresh", command=update_active_users, 
           bootstyle="success-outline", width=15).pack(pady=(10, 0))

# Footer
footer_frame = ttk.Frame(root, bootstyle="dark")
footer_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(footer_frame, text="© 2024 OTT Database Manager | Connected to MySQL Database", 
          font=("Helvetica", 9)).pack()

# Initial data load
view_users()
view_subscriptions()
view_content()
update_revenue_summary()
update_user_stats()
update_payment_methods()
update_plan_stats()
update_content_stats()
view_logs()
view_watch_stats()
view_devices()
update_device_stats()
update_active_users()

root.mainloop()