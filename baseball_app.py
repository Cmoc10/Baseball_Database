import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import mysql.connector

class BaseballLeagueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Baseball League Management")
        self.root.geometry("800x600")

        # Database connection parameters
        self.db_config = {
            'host': 'localhost',
            'user': 'baseball_user',
            'password': 'your_password',
            'database': 'baseball_league'
        }

        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.create_player_search_tab()
        self.create_team_search_tab()
        self.create_player_management_tab()
        self.create_stat_management_tab()
        self.create_manager_management_tab()

    def create_connection(self):
        """Create a database connection"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            return connection
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
            return None

    def create_player_search_tab(self):
        """Create tab for searching player information"""
        player_search_frame = ttk.Frame(self.notebook)
        self.notebook.add(player_search_frame, text="Player Search")

        # Search entry and button
        search_label = ttk.Label(player_search_frame, text="Search Player:")
        search_label.pack(pady=10)
        
        self.player_search_var = tk.StringVar()
        search_entry = ttk.Entry(player_search_frame, textvariable=self.player_search_var, width=50)
        search_entry.pack(pady=5)

        search_button = ttk.Button(player_search_frame, text="Search", command=self.search_player)
        search_button.pack(pady=5)

        # Results treeview
        self.player_results_tree = ttk.Treeview(player_search_frame, columns=(
            "Name", "Team", "Position", "Salary", "Jersey", "Active"
        ), show='headings')
        
        for col in self.player_results_tree['columns']:
            self.player_results_tree.heading(col, text=col)
            self.player_results_tree.column(col, width=100)
        
        self.player_results_tree.pack(padx=10, pady=10, expand=True, fill='both')

    def search_player(self):
        """Search for players based on name or partial name"""
        search_term = self.player_search_var.get()
        
        # Clear previous results
        for i in self.player_results_tree.get_children():
            self.player_results_tree.delete(i)
        
        connection = self.create_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        query = """
        SELECT 
            p.player_name, 
            t.team_name, 
            pl.position_name, 
            p.salary, 
            p.jersey_number, 
            p.is_active
        FROM player p
        JOIN team t ON p.team_id = t.team_id
        JOIN place pl ON p.position_id = pl.position_id
        WHERE p.player_name LIKE %s
        """
        
        cursor.execute(query, (f'%{search_term}%',))
        
        for row in cursor.fetchall():
            self.player_results_tree.insert('', 'end', values=row)
        
        cursor.close()
        connection.close()

    def create_team_search_tab(self):
        """Create tab for searching team information"""
        team_search_frame = ttk.Frame(self.notebook)
        self.notebook.add(team_search_frame, text="Team Search")

        # Search entry and button
        search_label = ttk.Label(team_search_frame, text="Search Team:")
        search_label.pack(pady=10)
        
        self.team_search_var = tk.StringVar()
        search_entry = ttk.Entry(team_search_frame, textvariable=self.team_search_var, width=50)
        search_entry.pack(pady=5)

        search_button = ttk.Button(team_search_frame, text="Search", command=self.search_team)
        search_button.pack(pady=5)

        # Results treeview
        self.team_results_tree = ttk.Treeview(team_search_frame, columns=(
            "Name", "City", "League", "Division", "Founded", "Total Salary"
        ), show='headings')
        
        for col in self.team_results_tree['columns']:
            self.team_results_tree.heading(col, text=col)
            self.team_results_tree.column(col, width=100)
        
        self.team_results_tree.pack(padx=10, pady=10, expand=True, fill='both')

    def search_team(self):
        """Search for teams based on name or partial name"""
        search_term = self.team_search_var.get()
        
        # Clear previous results
        for i in self.team_results_tree.get_children():
            self.team_results_tree.delete(i)
        
        connection = self.create_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        query = """
        SELECT 
            team_name, 
            city, 
            league_name, 
            division_name, 
            founded_year, 
            total_salary
        FROM team
        JOIN league ON team.league_id = league.league_id
        WHERE team_name LIKE %s
        """
        
        cursor.execute(query, (f'%{search_term}%',))
        
        for row in cursor.fetchall():
            self.team_results_tree.insert('', 'end', values=row)
        
        cursor.close()
        connection.close()

    def create_player_management_tab(self):
        """Create tab for adding, updating, and retiring players"""
        player_mgmt_frame = ttk.Frame(self.notebook)
        self.notebook.add(player_mgmt_frame, text="Player Management")

        # Add New Player section
        add_player_frame = ttk.LabelFrame(player_mgmt_frame, text="Add New Player")
        add_player_frame.pack(padx=10, pady=10, fill='x')

        # Name
        ttk.Label(add_player_frame, text="Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.new_player_name = tk.StringVar()
        ttk.Entry(add_player_frame, textvariable=self.new_player_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Team
        ttk.Label(add_player_frame, text="Team:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.new_player_team = tk.StringVar()
        teams = self.get_team_names()
        ttk.Combobox(add_player_frame, textvariable=self.new_player_team, values=teams, width=27).grid(row=0, column=3, padx=5, pady=5)

        # Position
        ttk.Label(add_player_frame, text="Position:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.new_player_position = tk.StringVar()
        positions = self.get_positions()
        ttk.Combobox(add_player_frame, textvariable=self.new_player_position, values=positions, width=27).grid(row=1, column=1, padx=5, pady=5)

        # Salary
        ttk.Label(add_player_frame, text="Salary:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.new_player_salary = tk.StringVar()
        ttk.Entry(add_player_frame, textvariable=self.new_player_salary, width=30).grid(row=1, column=3, padx=5, pady=5)

        # Add Player Button
        ttk.Button(add_player_frame, text="Add Player", command=self.add_new_player).grid(row=2, column=1, columnspan=2, pady=10)

        # Manage Player section (renamed from Retire/Update)
        manage_player_frame = ttk.LabelFrame(player_mgmt_frame, text="Manage Player")
        manage_player_frame.pack(padx=10, pady=10, fill='x')

        # Player to Manage
        ttk.Label(manage_player_frame, text="Player Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.update_player_name = tk.StringVar()
        ttk.Entry(manage_player_frame, textvariable=self.update_player_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Management buttons
        ttk.Button(manage_player_frame, text="Update Salary", command=self.update_player_salary).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(manage_player_frame, text="Retire Player", command=self.retire_player).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(manage_player_frame, text="Delete Player", command=self.delete_player).grid(row=1, column=2, padx=5, pady=5)

        # Add Trade Players section
        trade_frame = ttk.LabelFrame(player_mgmt_frame, text="Trade Players")
        trade_frame.pack(padx=10, pady=10, fill='x')

        # Player to trade
        ttk.Label(trade_frame, text="Player Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.trade_player_name = tk.StringVar()
        ttk.Entry(trade_frame, textvariable=self.trade_player_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        # New team
        ttk.Label(trade_frame, text="New Team:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.trade_new_team = tk.StringVar()
        teams = self.get_team_names()
        ttk.Combobox(trade_frame, textvariable=self.trade_new_team, values=teams, width=27).grid(row=0, column=3, padx=5, pady=5)

        # Trade button
        ttk.Button(trade_frame, text="Execute Trade", command=self.execute_trade).grid(row=1, column=1, columnspan=2, pady=10)
        trade_frame = ttk.LabelFrame(player_mgmt_frame, text="Trade Players")
        trade_frame.pack(padx=10, pady=10, fill='x')

        # First Player
        ttk.Label(trade_frame, text="Player 1 Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.trade_player1_name = tk.StringVar()
        ttk.Entry(trade_frame, textvariable=self.trade_player1_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Second Player
        ttk.Label(trade_frame, text="Player 2 Name:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.trade_player2_name = tk.StringVar()
        ttk.Entry(trade_frame, textvariable=self.trade_player2_name, width=30).grid(row=1, column=1, padx=5, pady=5)

        # Execute Trade Button
        ttk.Button(trade_frame, text="Trade Players", command=self.trade_two_players).grid(row=2, column=0, columnspan=2, pady=10)



    def get_team_names(self):
        """Retrieve team names for dropdown"""
        connection = self.create_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        cursor.execute("SELECT team_name FROM team")
        teams = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return teams

    def get_positions(self):
        """Retrieve positions for dropdown"""
        connection = self.create_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        cursor.execute("SELECT position_name FROM place")
        positions = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return positions

    def add_new_player(self):
        """Add a new player to the database"""
        name = self.new_player_name.get()
        team = self.new_player_team.get()
        position = self.new_player_position.get()
        salary = self.new_player_salary.get()

        if not all([name, team, position, salary]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # Get team_id
            cursor.execute("SELECT team_id FROM team WHERE team_name = %s", (team,))
            team_id = cursor.fetchone()[0]

            # Get position_id
            cursor.execute("SELECT position_id FROM place WHERE position_name = %s", (position,))
            position_id = cursor.fetchone()[0]

            # Insert new player
            query = """
            INSERT INTO player 
            (player_name, team_id, position_id, salary, is_active, bats, throws, jersey_number) 
            VALUES (%s, %s, %s, %s, TRUE, 'R', 'R', 99)
            """
            
            cursor.execute(query, (name, team_id, position_id, float(salary)))
            connection.commit()

            messagebox.showinfo("Success", f"Player {name} added successfully!")

            # Clear fields
            self.new_player_name.set('')
            self.new_player_team.set('')
            self.new_player_position.set('')
            self.new_player_salary.set('')

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not add player: {err}")
        
        finally:
            cursor.close()
            connection.close()

    def update_player_salary(self):
        """Update a player's salary"""
        name = self.update_player_name.get()
        if not name:
            messagebox.showerror("Error", "Please enter a player name")
            return

        new_salary = simpledialog.askfloat("Update Salary", f"Enter new salary for {name}:")
        if new_salary is None:
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            query = "UPDATE player SET salary = %s WHERE player_name = %s"
            cursor.execute(query, (new_salary, name))
            
            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No player found with name {name}")
            else:
                connection.commit()
                messagebox.showinfo("Success", f"Salary updated for {name}")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not update salary: {err}")
        
        finally:
            cursor.close()
            connection.close()

    def retire_player(self):
        """Retire a player by setting is_active to False"""
        name = self.update_player_name.get()
        if not name:
            messagebox.showerror("Error", "Please enter a player name")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            query = "UPDATE player SET is_active = FALSE, salary = 0 WHERE player_name = %s"
            cursor.execute(query, (name,))
            
            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No player found with name {name}")
            else:
                connection.commit()
                messagebox.showinfo("Success", f"{name} has been retired")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not retire player: {err}")
        
        finally:
            cursor.close()
            connection.close()

    def delete_player(self):
        """Delete a player from the database"""
        name = self.update_player_name.get()
        if not name:
            messagebox.showerror("Error", "Please enter a player name")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}? This cannot be undone."):
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
        
            # First delete from player_stats (due to foreign key constraint)
            cursor.execute("""
                DELETE ps FROM player_stats ps
                INNER JOIN player p ON ps.player_id = p.player_id
                WHERE p.player_name = %s
            """, (name,))
        
            # Then delete the player
            cursor.execute("DELETE FROM player WHERE player_name = %s", (name,))
        
            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No player found with name {name}")
            else:
                connection.commit()
                messagebox.showinfo("Success", f"{name} has been deleted from the database")
                self.update_player_name.set('')  # Clear the entry field

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not delete player: {err}")
    
        finally:
            cursor.close()
        connection.close()

    def execute_trade(self):
        """Execute a player trade to a new team"""
        player_name = self.trade_player_name.get()
        new_team = self.trade_new_team.get()

        if not all([player_name, new_team]):
            messagebox.showerror("Error", "Please enter both player name and new team")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # First check if player exists and get current team
            cursor.execute("""
                SELECT p.player_name, t.team_name, p.is_active
                FROM player p
                JOIN team t ON p.team_id = t.team_id
                WHERE p.player_name = %s
            """, (player_name,))
        
            player_info = cursor.fetchone()
            if not player_info:
                messagebox.showerror("Error", f"Player {player_name} not found")
                return
        
            if not player_info[2]:  # Check is_active
                messagebox.showerror("Error", f"Cannot trade retired player {player_name}")
                return

            current_team = player_info[1]
            if current_team == new_team:
                messagebox.showerror("Error", f"Player {player_name} is already on {new_team}")
                return

            # Get new team ID
            cursor.execute("SELECT team_id FROM team WHERE team_name = %s", (new_team,))
            new_team_id = cursor.fetchone()
            if not new_team_id:
                messagebox.showerror("Error", f"Team {new_team} not found")
                return

            # Execute the trade
            cursor.execute("""
                UPDATE player 
                SET team_id = %s
                WHERE player_name = %s
            """, (new_team_id[0], player_name))

            connection.commit()
            messagebox.showinfo("Success", f"Traded {player_name} from {current_team} to {new_team}")

            # Clear fields
            self.trade_player_name.set('')
            self.trade_new_team.set('')

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not execute trade: {err}")
        
        finally:
            cursor.close()
            connection.close()
    def trade_two_players(self):
        player1_name = self.trade_player1_name.get()
        player2_name = self.trade_player2_name.get()

        if not all([player1_name, player2_name]):
            messagebox.showerror("Error", "Please enter both player names for the trade")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # Get player IDs and team IDs
            cursor.execute("SELECT player_id, team_id FROM player WHERE player_name = %s", (player1_name,))
            player1 = cursor.fetchone()
            cursor.execute("SELECT player_id, team_id FROM player WHERE player_name = %s", (player2_name,))
            player2 = cursor.fetchone()

            if not player1 or not player2:
                messagebox.showerror("Error", "One or both players not found")
                return

            # Swap teams
            cursor.execute("""
                UPDATE player AS p1
                JOIN player AS p2 ON p1.player_id = %s AND p2.player_id = %s
                SET p1.team_id = p2.team_id, p2.team_id = p1.team_id
            """, (player1[0], player2[0]))
            
            connection.commit()
            messagebox.showinfo("Success", f"{player1_name} and {player2_name} have swapped teams")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not trade players: {err}")
        finally:
            cursor.close()
            connection.close()

    def create_manager_management_tab(self):
        """Create tab for managing managers"""
        manager_mgmt_frame = ttk.Frame(self.notebook)
        self.notebook.add(manager_mgmt_frame, text="Manager Management")

        # Add New Manager
        add_manager_frame = ttk.LabelFrame(manager_mgmt_frame, text="Add Manager")
        add_manager_frame.pack(padx=10, pady=10, fill='x')

        # Manager Details
        manager_fields = [("Name", "new_manager_name"),
                        ("Birth Date (YYYY-MM-DD)", "new_manager_birth_date"),
                        ("Hire Date (YYYY-MM-DD)", "new_manager_hire_date"),
                        ("Salary", "new_manager_salary"),
                        ("Team", "new_manager_team")]

        for i, (label, var_name) in enumerate(manager_fields):
            ttk.Label(add_manager_frame, text=f"{label}:").grid(row=i, column=0, sticky='w', padx=5, pady=5)
            setattr(self, var_name, tk.StringVar())
            if var_name == "new_manager_team":
                ttk.Combobox(add_manager_frame, textvariable=getattr(self, var_name), values=self.get_team_names(), width=27).grid(row=i, column=1, padx=5, pady=5)
            else:
                ttk.Entry(add_manager_frame, textvariable=getattr(self, var_name), width=30).grid(row=i, column=1, padx=5, pady=5)

        # Hire Manager Button
        ttk.Button(add_manager_frame, text="Hire Manager", command=self.hire_manager).grid(row=len(manager_fields), column=0, columnspan=2, pady=10)

        # Fire Manager
        fire_manager_frame = ttk.LabelFrame(manager_mgmt_frame, text="Fire Manager")
        fire_manager_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(fire_manager_frame, text="Manager Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.manager_name_to_fire = tk.StringVar()
        ttk.Entry(fire_manager_frame, textvariable=self.manager_name_to_fire, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(fire_manager_frame, text="Fire Manager", command=self.fire_manager).grid(row=1, column=0, columnspan=2, pady=10)

    def fire_manager(self):
        manager_name = self.manager_name_to_fire.get()
        if not manager_name:
            messagebox.showerror("Error", "Please enter the manager's name")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM manager WHERE manager_name = %s", (manager_name,))
            
            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No manager found with name {manager_name}")
            else:
                connection.commit()
                messagebox.showinfo("Success", f"Manager {manager_name} has been fired")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not fire manager: {err}")
        finally:
            cursor.close()
            connection.close()

    def hire_manager(self):
        name = self.new_manager_name.get()
        birth_date = self.new_manager_birth_date.get()
        hire_date = self.new_manager_hire_date.get()
        salary = self.new_manager_salary.get()
        team_name = self.new_manager_team.get()

        if not all([name, birth_date, hire_date, salary, team_name]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT team_id FROM team WHERE team_name = %s", (team_name,))
            team_id = cursor.fetchone()

            if not team_id:
                messagebox.showerror("Error", f"Team {team_name} not found")
                return

            cursor.execute("""
                INSERT INTO manager (manager_name, birth_date, hire_date, salary, team_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, birth_date, hire_date, salary, team_id[0]))
            
            connection.commit()
            messagebox.showinfo("Success", f"Manager {name} has been hired for {team_name}")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not hire manager: {err}")
        finally:
            cursor.close()
            connection.close()

    def create_stat_management_tab(self):
        """Create tab for managing player statistics"""
        stat_mgmt_frame = ttk.Frame(self.notebook)
        self.notebook.add(stat_mgmt_frame, text="Stat Management")

        # Player Selection
        ttk.Label(stat_mgmt_frame, text="Player Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.stats_player_name = tk.StringVar()
        ttk.Entry(stat_mgmt_frame, textvariable=self.stats_player_name, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Season Year
        ttk.Label(stat_mgmt_frame, text="Season Year:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.stats_season_year = tk.StringVar()
        ttk.Entry(stat_mgmt_frame, textvariable=self.stats_season_year, width=30).grid(row=1, column=1, padx=5, pady=5)

        # Stat Fields
        stat_fields = [("Games Played", "stats_games_played"),
                    ("Runs", "stats_runs"),
                    ("Hits", "stats_hits")]

        for i, (label, var_name) in enumerate(stat_fields):
            ttk.Label(stat_mgmt_frame, text=f"{label}:").grid(row=i + 2, column=0, sticky='w', padx=5, pady=5)
            setattr(self, var_name, tk.StringVar())
            ttk.Entry(stat_mgmt_frame, textvariable=getattr(self, var_name), width=30).grid(row=i + 2, column=1, padx=5, pady=5)

        # Update Stats Button
        ttk.Button(stat_mgmt_frame, text="Update Stats", command=self.update_player_stats).grid(row=5, column=0, columnspan=2, pady=10)


    def update_player_stats(self):
        player_name = self.stats_player_name.get()
        season_year = self.stats_season_year.get()
        games_played = self.stats_games_played.get()
        runs = self.stats_runs.get()
        hits = self.stats_hits.get()

        if not all([player_name, season_year, games_played, runs, hits]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        connection = self.create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT player_id FROM player WHERE player_name = %s", (player_name,))
            player_id = cursor.fetchone()

            if not player_id:
                messagebox.showerror("Error", f"Player {player_name} not found")
                return

            cursor.execute("""
                UPDATE player_stats
                SET games_played = %s, runs = %s, hits = %s
                WHERE player_id = %s AND season_year = %s
            """, (games_played, runs, hits, player_id[0], season_year))
            
            connection.commit()
            messagebox.showinfo("Success", f"Stats updated for {player_name} in {season_year}")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not update stats: {err}")
        finally:
            cursor.close()
            connection.close()





def main():
    root = tk.Tk()
    app = BaseballLeagueApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()