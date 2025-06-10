# EntraID MCP Server (Enhanced with User Lifecycle Management)

This project provides a comprehensive, modular FastMCP server for interacting with Microsoft Graph API. It is designed for extensibility, maintainability, and security, supporting advanced queries for users, sign-in logs, MFA status, privileged users, and **complete user lifecycle management**.

## ✨ Enhanced Features

### 🆕 **Complete User Lifecycle Management**
- **Create, update, and delete users**
- **Enable/disable user accounts**
- **Manage user properties** (department, job title, office location, manager, etc.)
- **Set manager relationships**
- **Bulk user operations**

### 📊 **Comprehensive Identity Operations**
- **Modular Resource Structure:** Each resource (users, groups, applications, etc.) is implemented in its own module under `src/msgraph_mcp_server/resources/`
- **Centralized Graph Client:** Handles authentication and client initialization, shared by all resource modules
- **Full Group Lifecycle & Membership Management:** Create, read, update, delete groups; manage members and owners
- **Application & Service Principal Management:** Complete CRUD operations for app registrations and service principals
- **Sign-in Log Operations:** Query and analyze user sign-in patterns
- **MFA Operations:** Monitor and assess multi-factor authentication status
- **Password Management:** Reset passwords with secure generation options
- **Permissions Helper:** Get Microsoft Graph permission recommendations
- **Error Handling & Logging:** Consistent error handling and progress reporting via FastMCP context

## Project Structure

```
src/msgraph_mcp_server/
├── auth/                     # Authentication logic (GraphAuthManager)
├── resources/                # Resource modules
│   ├── users.py             # ✨ Enhanced: Complete user lifecycle management
│   ├── groups.py            # Group operations and membership management
│   ├── applications.py      # Application (app registration) operations
│   ├── service_principals.py # Service principal operations
│   ├── signin_logs.py       # Sign-in log operations
│   ├── mfa.py              # MFA status operations
│   ├── managed_devices.py   # Device management operations
│   ├── conditional_access.py # Conditional access policy operations
│   ├── audit_logs.py        # Directory audit log operations
│   ├── password_auth.py     # Password authentication methods
│   └── permissions_helper.py # Graph permissions utilities
├── utils/                   # Core GraphClient and utilities
│   ├── graph_client.py      # Microsoft Graph client wrapper
│   └── password_generator.py # Secure password generation
├── server.py               # ✨ Enhanced: FastMCP server with new user management tools
└── __init__.py             # Package marker
```

## 🚀 Getting Started

### 1. Setup
1. Clone this enhanced repository
2. Create a `config/.env` file with your Azure AD credentials:
   ```
   TENANT_ID=your-tenant-id
   CLIENT_ID=your-client-id
   CLIENT_SECRET=your-client-secret
   ```
3. Install dependencies: `uv sync` or `pip install -e .`

### 2. Azure AD App Permissions

**Required Microsoft Graph API Permissions:**

| Permission | Type | Description |
|------------|------|-------------|
| `AuditLog.Read.All` | Application | Read all audit log data |
| `AuthenticationContext.Read.All` | Application | Read authentication context |
| `DeviceManagementManagedDevices.Read.All` | Application | Read Intune devices |
| `Directory.Read.All` | Application | Read directory data |
| `Group.ReadWrite.All` | Application | Full group management |
| `Policy.Read.All` | Application | Read policies |
| `RoleManagement.Read.Directory` | Application | Read directory RBAC |
| `UserAuthenticationMethod.Read.All` | Application | Read user auth methods |
| `Application.ReadWrite.All` | Application | Manage applications and service principals |
| **🆕 `User.ReadWrite.All`** | Application | **Complete user lifecycle management** |

### 3. Testing & Development

Test your enhanced MCP server directly using the FastMCP CLI:

```bash
fastmcp dev '/path/to/src/msgraph_mcp_server/server.py'
```

## 🛠️ Available Tools

### 🆕 **Enhanced User Management Tools**
- `search_users(query, ctx, limit=10)` — Search users by name/email
- `get_user_by_id(user_id, ctx)` — Get user details by ID
- `get_privileged_users(ctx)` — List all users in privileged directory roles
- `get_user_roles(user_id, ctx)` — Get all directory roles assigned to a user
- `get_user_groups(user_id, ctx)` — Get all groups for a user
- **🆕 `update_user(user_id, ctx, user_data)`** — **Update user properties (department, job title, etc.)**
- **🆕 `enable_user(user_id, ctx)`** — **Enable a user account**
- **🆕 `disable_user(user_id, ctx)`** — **Disable a user account**
- **🆕 `create_user(ctx, user_data)`** — **Create a new user**
- **🆕 `delete_user(user_id, ctx)`** — **Delete a user**
- **🆕 `set_user_manager(user_id, manager_id, ctx)`** — **Set a user's manager**
- **🆕 `remove_user_manager(user_id, ctx)`** — **Remove a user's manager**

### Group Management Tools
- `get_all_groups(ctx, limit=100)` — Get all groups
- `get_group_by_id(group_id, ctx)` — Get specific group details
- `search_groups_by_name(name, ctx, limit=50)` — Search groups by name
- `get_group_members(group_id, ctx, limit=100)` — Get group members
- `create_group(ctx, group_data)` — Create new groups
- `update_group(group_id, ctx, group_data)` — Update existing groups
- `delete_group(group_id, ctx)` — Delete groups
- `add_group_member(group_id, member_id, ctx)` — Add members to groups
- `remove_group_member(group_id, member_id, ctx)` — Remove members from groups

### Security & Compliance Tools
- `get_user_sign_ins(user_id, ctx, days=7)` — Get sign-in logs
- `get_user_mfa_status(user_id, ctx)` — Get MFA status for users
- `get_group_mfa_status(group_id, ctx)` — Get MFA status for group members
- `get_conditional_access_policies(ctx)` — Get conditional access policies
- `get_user_audit_logs(user_id, days=30)` — Get audit logs for users
- `reset_user_password_direct(user_id, password, ctx)` — Reset user passwords

### Application Management Tools
- `list_applications(ctx, limit=100)` — List app registrations
- `get_application_by_id(app_id, ctx)` — Get application details
- `create_application(ctx, app_data)` — Create applications
- `update_application(app_id, ctx, app_data)` — Update applications
- `delete_application(app_id, ctx)` — Delete applications

### Device Management Tools
- `get_all_managed_devices(ctx, filter_os=None)` — Get managed devices
- `get_managed_devices_by_user(user_id, ctx)` — Get devices for specific users

## 🎯 Usage Examples with Claude

With the enhanced user management capabilities, you can now ask Claude to perform comprehensive HR and IT administration tasks:

### **User Onboarding:**
- *"Create a new user account for Sarah Wilson joining as HR Director in the Seattle office"*
- *"Set up accounts for these 5 new hires in the Engineering department"*

### **User Management:**
- *"Change John Doe's department to Finance and set Alice Johnson as his manager"*
- *"Update all Marketing team members to work from Building B, Floor 3"*
- *"Move the entire Sales team to the new Dallas office location"*

### **User Offboarding:**
- *"Disable Mike Davis's account and remove his manager assignment"*
- *"Show me all disabled users from the last 30 days"*
- *"Disable all users in the Marketing department who haven't signed in for 90 days"*

### **Bulk Operations:**
- *"Update job titles for all users in the Finance department"*
- *"Set usage location to 'US' for all users without a location"*
- *"Enable all previously disabled intern accounts"*

### **Organizational Changes:**
- *"Show me all users reporting to John Smith and reassign them to Jane Doe"*
- *"Find all users in the IT department and update their office location"*

## 🔧 Using with Claude or Cursor

### Using with Claude (Anthropic)
```bash
fastmcp install '/path/to/src/msgraph_mcp_server/server.py' \\
  --with msgraph-sdk --with azure-identity --with azure-core --with msgraph-core \\
  -f /path/to/.env
```

### Using with Cursor
Add to your `.cursor/mcp.json`:
```json
{
  "EntraID MCP Server": {
    "command": "uv",
    "args": [
      "run",
      "--with", "azure-core",
      "--with", "azure-identity", 
      "--with", "fastmcp",
      "--with", "msgraph-core",
      "--with", "msgraph-sdk",
      "fastmcp",
      "run",
      "/path/to/src/msgraph_mcp_server/server.py"
    ],
    "env": {
      "TENANT_ID": "<your-tenant-id>",
      "CLIENT_ID": "<your-client-id>",
      "CLIENT_SECRET": "<your-client-secret>"
    }
  }
}
```

## 🔐 Security & Best Practices

- **Never commit secrets:** `.env` files are gitignored
- **Use least privilege:** Grant only necessary Microsoft Graph permissions
- **Audit & monitor:** All operations are logged in Azure AD audit logs
- **Input validation:** All user inputs are validated and sanitized
- **Error handling:** Comprehensive error handling with proper user feedback

## 📈 What's New in This Enhanced Version

### ✅ **Complete User Lifecycle Management**
- Create users with full profile information
- Update any user property (department, job title, contact info, etc.)
- Enable/disable accounts for onboarding/offboarding
- Manage manager relationships and organizational hierarchy
- Delete users when necessary

### ✅ **Enterprise-Ready Operations**
- Bulk user operations for organizational changes
- Comprehensive error handling and validation
- Audit trail support for compliance
- Integration with existing group and role management

### ✅ **Claude AI Integration**
- Natural language user management through conversational AI
- Intelligent bulk operations based on criteria
- Automated workflow suggestions
- Context-aware user administration

## 🤝 Contributing

This enhanced version builds on the excellent foundation of the original EntraID MCP Server. Contributions are welcome! Please ensure:

1. All new features include proper error handling
2. User management operations are thoroughly tested
3. Security best practices are followed
4. Documentation is updated for new capabilities

## 📄 License

MIT

---

**⚡ Ready to transform your identity management with AI-powered automation!**
