# Role-Based Access Control (RBAC) Implementation

## Overview

This document describes the comprehensive role-based access control system implemented in NextCare2. The system provides granular permissions for three user roles: Admin, Manager, and Engineer.

## User Roles and Permissions

### Admin Role
- **Full system access** - complete control over all features
- **User Management**: Add, edit, delete all users (admins, managers, engineers)
- **Machine Management**: Add, edit, delete all machines
- **Parameter Management**: Add, edit, delete parameters for all machines
- **Settings Access**: Full access to all settings tabs
- **Machine Assignment**: Assign any machine to any user
- **Dashboard**: View all machines and their data

### Manager Role
- **Limited administrative access** - focused on operational management
- **User Management**: Add, edit, delete engineers only (cannot manage admins or other managers)
- **Machine Management**: View all machines, but cannot add/edit/delete machines
- **Parameter Management**: Add, edit, delete parameters for all machines
- **Settings Access**: Access to engineer management tab only
- **Machine Assignment**: Assign machines to engineers (from all available machines)
- **Dashboard**: View all machines and their data

### Engineer Role
- **Read-only operational access** - monitoring and dashboard only
- **User Management**: No access
- **Machine Management**: No access to configuration page
- **Parameter Management**: No access
- **Settings Access**: No access
- **Machine Assignment**: No access
- **Dashboard**: View only assigned machines and their data

## Access Control Matrix

| Feature | Admin | Manager | Engineer |
|---------|-------|---------|----------|
| Configuration Page | Full Access | Assigned Machines Only | No Access |
| Add/Delete Machines | Yes | No | No |
| Add/Edit Parameters | Yes | Yes (all machines) | No |
| Settings Page | Full Access | Engineer Management Only | No Access |
| User Management | All Users | Engineers Only | No |
| Machine Assignment | Yes | Yes (to engineers) | No |
| Dashboard | All Machines | All Machines | Assigned Machines Only |

## Implementation Details

### Database Schema
The system leverages existing database tables:
- `users`: Stores user information with role field
- `machines`: Stores machine information
- `parameters`: Stores parameter definitions
- `user_machine_access`: Manages machine assignments to users

### Authentication System (`src/utils/auth.py`)
Enhanced with granular permission checks:
- `can_manage_machines()`: Admin only
- `can_manage_users()`: Admin only
- `can_manage_engineers()`: Admin and Manager
- `can_access_settings()`: Admin and Manager
- `can_assign_machines()`: Admin and Manager
- `can_edit_machine_parameters()`: Admin and Manager
- `get_accessible_machines()`: Role-based machine list

### Database Operations (`src/database/operations.py`)
Extended with user management functions:
- `get_users(role=None)`: Filter users by role
- `update_user()`: Update user information
- `delete_user()`: Soft delete users
- `change_user_password()`: Password management
- `get_machine_users()`: Users assigned to machines
- `set_user_machine_access()`: Bulk machine assignment

### User Interface

#### Settings Window (`src/ui/settings_window.py`)
- **New comprehensive settings interface**
- **Tabbed design** for different management sections
- **Role-based tab visibility**
- **User CRUD operations** with proper validation
- **Machine assignment interface** with bulk selection
- **Responsive design** consistent with application theme

#### Dashboard Window (`src/ui/dashboard_window.py`)
- **Settings button** added to header (role-based visibility)
- **Role-based machine filtering** for engineers
- **User information display** in header

#### Configuration Window (`src/ui/config_window.py`)
- **Role-based operation restrictions**
- **Permission checks** for all machine/parameter operations
- **UI element visibility** based on user role
- **Access control enforcement** for all CRUD operations

### Application Flow (`src/main.py`)
- **Role-based window routing**: Engineers bypass configuration, go directly to dashboard
- **Proper session management** and cleanup
- **Error handling** for unauthorized access attempts

## Security Features

1. **Server-side validation**: All operations validated on database level
2. **UI restrictions**: Interface elements hidden/disabled based on permissions
3. **Session management**: Proper authentication state handling
4. **Input validation**: Comprehensive validation for all user inputs
5. **Error handling**: Graceful handling of unauthorized operations

## Usage Examples

### Admin Workflow
1. Login → Configuration Window
2. Access Settings → Manage all users and machine assignments
3. Add/edit machines and parameters
4. View dashboard with all machines

### Manager Workflow
1. Login → Configuration Window
2. Access Settings → Manage engineers only
3. Edit parameters for all machines
4. Assign machines to engineers
5. View dashboard with all machines

### Engineer Workflow
1. Login → Dashboard (direct)
2. View assigned machines only
3. No access to settings or configuration

## Testing

Run the test script to verify role-based functionality:

```bash
python test_rbac.py
```

This will test:
- User authentication for all roles
- Permission validation
- Database operations
- Access control enforcement

## Configuration

Default users are created during database initialization:
- **admin/admin** (Admin role)
- **manager1/manager1** (Manager role)
- **engineer1/engineer1** (Engineer role)

Change these passwords in production environments.

## Error Handling

The system provides user-friendly error messages for:
- Unauthorized access attempts
- Invalid operations
- Database connection issues
- Validation failures

All errors are logged for debugging purposes while showing appropriate messages to users.