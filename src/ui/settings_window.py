"""
Settings window for user and machine management
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                            QLabel, QLineEdit, QTextEdit, QComboBox, QGroupBox,
                            QFormLayout, QMessageBox, QHeaderView, QDialog,
                            QDialogButtonBox, QSpacerItem, QSizePolicy, QCheckBox,
                            QScrollArea, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Use try/except to handle both relative and absolute imports
try:
    from ..database.operations import db_ops
    from ..utils.auth import auth_manager
    from ..utils.constants import *
    from .styles import get_application_style
except ImportError:
    # Fallback to absolute imports when running directly
    from database.operations import db_ops
    from utils.auth import auth_manager
    from utils.constants import *
    from ui.styles import get_application_style

logger = logging.getLogger(__name__)

class UserDialog(QDialog):
    """Dialog for adding/editing users"""
    
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_editing = user_data is not None
        
        self.setWindowTitle("Edit User" if self.is_editing else "Add User")
        self.setFixedSize(400, 350)
        
        self.setup_ui()
        
        if self.is_editing:
            self.populate_fields()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setStyleSheet(f"QDialog {{ background-color: {BACKGROUND_COLOR}; }}")
        
        layout = QVBoxLayout()
        
        # Form fields
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        form_layout.addRow("Username:", self.username_edit)
        
        self.full_name_edit = QLineEdit()
        form_layout.addRow("Full Name:", self.full_name_edit)
        
        self.email_edit = QLineEdit()
        form_layout.addRow("Email:", self.email_edit)
        
        self.role_combo = QComboBox()
        # Only show roles that current user can manage
        current_role = auth_manager.get_user_role()
        if current_role == 'admin':
            self.role_combo.addItems(['admin', 'manager', 'engineer'])
        elif current_role == 'manager':
            self.role_combo.addItems(['engineer'])
        
        form_layout.addRow("Role:", self.role_combo)
        
        if not self.is_editing:
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow("Password:", self.password_edit)
            
            self.confirm_password_edit = QLineEdit()
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow("Confirm Password:", self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_changes)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields when editing"""
        if self.user_data:
            self.username_edit.setText(self.user_data['username'])
            self.full_name_edit.setText(self.user_data['full_name'])
            self.email_edit.setText(self.user_data.get('email', ''))
            
            # Set role if it's allowed
            role_index = self.role_combo.findText(self.user_data['role'])
            if role_index >= 0:
                self.role_combo.setCurrentIndex(role_index)
    
    def accept_changes(self):
        """Validate and accept changes"""
        username = self.username_edit.text().strip()
        full_name = self.full_name_edit.text().strip()
        email = self.email_edit.text().strip()
        role = self.role_combo.currentText()
        
        if not username or not full_name:
            QMessageBox.warning(self, "Validation Error", "Username and Full Name are required.")
            return
        
        if not self.is_editing:
            password = self.password_edit.text()
            confirm_password = self.confirm_password_edit.text()
            
            if not password:
                QMessageBox.warning(self, "Validation Error", "Password is required.")
                return
            
            if password != confirm_password:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                return
        
        # Check if current user can manage this role
        if not auth_manager.can_manage_user_role(role):
            QMessageBox.warning(self, "Permission Error", f"You don't have permission to manage {role} users.")
            return
        
        self.accept()
    
    def get_user_data(self):
        """Get user data from form"""
        data = {
            'username': self.username_edit.text().strip(),
            'full_name': self.full_name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'role': self.role_combo.currentText()
        }
        
        if not self.is_editing:
            data['password'] = self.password_edit.text()
        
        return data

class MachineAssignmentDialog(QDialog):
    """Dialog for assigning machines to users"""
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.machine_checkboxes = {}
        
        self.setWindowTitle(f"Assign Machines - {user_data['full_name']}")
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        self.load_machines()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setStyleSheet(f"""
            QDialog {{ 
                background-color: {BACKGROUND_COLOR}; 
                color: {TEXT_COLOR};
            }}
            QCheckBox {{
                color: {TEXT_COLOR};
                font-size: 12px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {SECONDARY_COLOR};
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {SECONDARY_COLOR};
                background-color: {ACCENT_COLOR};
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {SECONDARY_COLOR};
            }}
            QScrollArea {{
                border: 1px solid {SECONDARY_COLOR};
                border-radius: 4px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f"Assign machines to {self.user_data['full_name']} ({self.user_data['role']})")
        header_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 10px;
            background-color: {CARD_COLOR};
            border-radius: 4px;
            margin-bottom: 10px;
        """)
        layout.addWidget(header_label)
        
        # Scroll area for machines
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet(f"background-color: {CARD_COLOR};")
        self.machines_layout = QVBoxLayout(scroll_widget)
        self.machines_layout.setSpacing(5)
        self.machines_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_machines)
        button_layout.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(self.clear_all_machines)
        button_layout.addWidget(clear_all_btn)
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_assignments)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_machines(self):
        """Load available machines"""
        try:
            # Get machines based on current user's permissions
            current_role = auth_manager.get_user_role()
            current_user = auth_manager.get_current_user()
            
            logger.info(f"Loading machines for user role: {current_role}")
            logger.info(f"Current user: {current_user}")
            
            if current_role == 'admin':
                # Admin can assign all machines - use same call as config window
                machines = db_ops.get_machines(current_user['id'], current_user['role'])
                logger.info(f"Admin user - fetching all machines")
            elif current_role == 'manager':
                # Manager can assign from all machines - use same call as config window
                machines = db_ops.get_machines(current_user['id'], current_user['role'])
                logger.info(f"Manager user - fetching all machines")
            else:
                machines = []
                logger.info(f"Other role ({current_role}) - no machines allowed")
            
            logger.info(f"Found {len(machines)} machines from database")
            
            # Remove the duplicate debug call since we're now using the correct method
            
            # Get currently assigned machines
            assigned_machines = db_ops.get_user_machines(self.user_data['id'])
            assigned_machine_ids = [m['id'] for m in assigned_machines]
            
            logger.info(f"User {self.user_data['id']} has {len(assigned_machine_ids)} assigned machines")
            
            # Clear existing checkboxes
            for i in reversed(range(self.machines_layout.count())):
                child = self.machines_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # Create checkboxes for each machine
            for machine in machines:
                checkbox = QCheckBox(f"{machine['name']} - {machine['location']}")
                checkbox.setChecked(machine['id'] in assigned_machine_ids)
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        color: black;
                        font-size: 12px;
                        padding: 8px;
                        background-color: white;
                    }}
                """)
                
                # Store machine info
                self.machine_checkboxes[machine['id']] = {
                    'checkbox': checkbox,
                    'machine': machine
                }
                
                self.machines_layout.addWidget(checkbox)
                logger.info(f"Added checkbox for machine: {machine['name']}")
            
            # Add some debug info to see if machines are loading
            if not machines:
                no_machines_label = QLabel("No machines available to assign.")
                no_machines_label.setStyleSheet("color: red; font-style: italic; padding: 20px; font-size: 14px;")
                self.machines_layout.addWidget(no_machines_label)
                logger.warning("No machines found to display")
                
                # Add debug info
                debug_label = QLabel(f"Debug: Current role is '{current_role}', User: {current_user}")
                debug_label.setStyleSheet("color: blue; padding: 10px; font-size: 12px;")
                self.machines_layout.addWidget(debug_label)
            
        except Exception as e:
            logger.error(f"Error loading machines: {e}")
            error_label = QLabel(f"Error loading machines: {str(e)}")
            error_label.setStyleSheet("color: red; padding: 20px; font-size: 14px;")
            self.machines_layout.addWidget(error_label)
    
    def select_all_machines(self):
        """Select all machines"""
        for machine_info in self.machine_checkboxes.values():
            machine_info['checkbox'].setChecked(True)
    
    def clear_all_machines(self):
        """Clear all machine selections"""
        for machine_info in self.machine_checkboxes.values():
            machine_info['checkbox'].setChecked(False)
    
    def save_assignments(self):
        """Save machine assignments"""
        selected_machine_ids = []
        
        for machine_id, machine_info in self.machine_checkboxes.items():
            if machine_info['checkbox'].isChecked():
                selected_machine_ids.append(machine_id)
        
        try:
            if db_ops.set_user_machine_access(self.user_data['id'], selected_machine_ids):
                QMessageBox.information(self, "Success", "Machine assignments updated successfully.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update machine assignments.")
        except Exception as e:
            logger.error(f"Error saving machine assignments: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

class SettingsWindow(QMainWindow):
    """Settings window for user and machine management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - NextCare2")
        self.setMinimumSize(900, 700)
        
        # Check permissions
        if not auth_manager.can_access_settings():
            QMessageBox.warning(self, "Access Denied", "You don't have permission to access settings.")
            self.close()
            return
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setStyleSheet(get_application_style())
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Settings")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            padding: 10px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # User Management Tab
        if auth_manager.can_manage_users() or auth_manager.can_manage_engineers():
            self.create_user_management_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_user_management_tab(self):
        """Create user management tab"""
        user_widget = QWidget()
        layout = QVBoxLayout(user_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(self.add_user)
        controls_layout.addWidget(add_user_btn)
        
        edit_user_btn = QPushButton("Edit User")
        edit_user_btn.clicked.connect(self.edit_user)
        controls_layout.addWidget(edit_user_btn)
        
        delete_user_btn = QPushButton("Delete User")
        delete_user_btn.clicked.connect(self.delete_user)
        controls_layout.addWidget(delete_user_btn)
        
        controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        assign_machines_btn = QPushButton("Assign Machines")
        assign_machines_btn.clicked.connect(self.assign_machines)
        controls_layout.addWidget(assign_machines_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_users)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Set columns
        columns = ['ID', 'Username', 'Full Name', 'Email', 'Role', 'Created']
        self.users_table.setColumnCount(len(columns))
        self.users_table.setHorizontalHeaderLabels(columns)
        
        # Set column widths
        header = self.users_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Username
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Full Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Role
        
        layout.addWidget(self.users_table)
        
        self.tab_widget.addTab(user_widget, "User Management")
    
    def load_data(self):
        """Load all data"""
        self.load_users()
    
    def load_users(self):
        """Load users into the table"""
        try:
            # Get users based on current user's permissions
            current_role = auth_manager.get_user_role()
            
            if current_role == 'admin':
                # Admin can see all users
                users = db_ops.get_users()
            elif current_role == 'manager':
                # Manager can see only engineers
                users = db_ops.get_users(role='engineer')
            else:
                users = []
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['full_name']))
                self.users_table.setItem(row, 3, QTableWidgetItem(user.get('email', '')))
                self.users_table.setItem(row, 4, QTableWidgetItem(user['role']))
                self.users_table.setItem(row, 5, QTableWidgetItem(str(user['created_at'])))
                
                # Store user data in the first column for easy access
                self.users_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, user)
        
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    
    def get_selected_user(self):
        """Get currently selected user"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            item = self.users_table.item(current_row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def add_user(self):
        """Add new user"""
        dialog = UserDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_user_data()
            
            try:
                if db_ops.create_user(
                    user_data['username'],
                    user_data['password'],
                    user_data['role'],
                    user_data['full_name'],
                    user_data['email']
                ):
                    QMessageBox.information(self, "Success", "User created successfully.")
                    self.load_users()
                else:
                    QMessageBox.critical(self, "Error", "Failed to create user.")
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def edit_user(self):
        """Edit selected user"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
            return
        
        # Check if current user can manage this user's role
        if not auth_manager.can_manage_user_role(user['role']):
            QMessageBox.warning(self, "Permission Error", f"You don't have permission to edit {user['role']} users.")
            return
        
        dialog = UserDialog(user_data=user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_user_data()
            
            try:
                if db_ops.update_user(
                    user['id'],
                    user_data['username'],
                    user_data['role'],
                    user_data['full_name'],
                    user_data['email']
                ):
                    QMessageBox.information(self, "Success", "User updated successfully.")
                    self.load_users()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update user.")
            except Exception as e:
                logger.error(f"Error updating user: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def delete_user(self):
        """Delete selected user"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return
        
        # Check if current user can manage this user's role
        if not auth_manager.can_manage_user_role(user['role']):
            QMessageBox.warning(self, "Permission Error", f"You don't have permission to delete {user['role']} users.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete user '{user['full_name']}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db_ops.delete_user(user['id']):
                    QMessageBox.information(self, "Success", "User deleted successfully.")
                    self.load_users()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete user.")
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def assign_machines(self):
        """Assign machines to selected user"""
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "No Selection", "Please select a user to assign machines to.")
            return
        
        # Check permissions
        if not auth_manager.can_assign_machines():
            QMessageBox.warning(self, "Permission Error", "You don't have permission to assign machines.")
            return
        
        dialog = MachineAssignmentDialog(user_data=user, parent=self)
        dialog.exec()