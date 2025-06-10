# Enhanced EntraID MCP Server Setup Guide

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Azure AD tenant with administrative access
- Azure AD app registration with required permissions

### 1. Clone and Setup

```bash
# Clone your enhanced repository
git clone https://github.com/eait1200/entraid-mcp-server.git
cd entraid-mcp-server

# Install dependencies (using uv - recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Azure AD App Registration

#### Create App Registration
1. Go to Azure Portal → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: "EntraID MCP Server" 
4. Account types: "Accounts in this organizational directory only"
5. Redirect URI: Leave blank
6. Click "Register"

#### Configure API Permissions
Add these **Application permissions** (not Delegated):

| Permission | Type | Description |
|------------|------|-------------|
| `AuditLog.Read.All` | Application | Read all audit log data |
| `Directory.Read.All` | Application | Read directory data |
| `Group.ReadWrite.All` | Application | Full group management |
| `UserAuthenticationMethod.Read.All` | Application | Read user auth methods |
| **`User.ReadWrite.All`** | Application | **Complete user lifecycle management** |

#### Create Client Secret
1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Description: "MCP Server Secret"
4. Expires: Choose your preferred duration
5. Click "Add"
6. **Copy the secret value immediately** (you won't see it again)

#### Grant Admin Consent
1. Go back to "API permissions"
2. Click "Grant admin consent for [Your Organization]"
3. Click "Yes" to confirm

### 3. Configuration

Create your environment file:

```bash
# Copy the example configuration
cp config/.env.example config/.env

# Edit with your Azure AD details
nano config/.env
```

Add your credentials to `config/.env`:
```bash
TENANT_ID=your-tenant-id-here
CLIENT_ID=your-client-id-here
CLIENT_SECRET=your-client-secret-here
```

### 4. Testing

Test your setup:

```bash
# Development mode with FastMCP CLI
fastmcp dev 'src/msgraph_mcp_server/server.py'

# Or run directly
python src/msgraph_mcp_server/server.py
```

### 5. Claude Integration

Install for Claude:

```bash
fastmcp install 'src/msgraph_mcp_server/server.py' \\
  --with msgraph-sdk --with azure-identity --with azure-core --with msgraph-core \\
  -f config/.env
```

## 🎯 What You Can Do Now

### **User Lifecycle Management**
- *"Create a new user account for Sarah Wilson joining as HR Director"*
- *"Change John Doe's department to Finance and job title to Senior Analyst"*
- *"Disable all users who haven't signed in for 90 days"*
- *"Set Alice Johnson as Bob Smith's manager"*

### **Organizational Changes**
- *"Move all Marketing team members to Building B, Floor 3"*
- *"Update usage location to 'US' for all users without a location"*
- *"Show me all users in the Finance department and their managers"*

### **Security & Compliance**
- *"Check MFA status for all users in the Executives group"*
- *"Show sign-in logs for john.doe@company.com for the last 30 days"*
- *"List all privileged users and their roles"*

## 🔧 Development

### Project Structure
```
src/msgraph_mcp_server/
├── auth/                 # Authentication & credentials
├── resources/            # Resource modules (users, groups, etc.)
├── utils/               # Utilities (graph client, password generator)
└── server.py           # Main FastMCP server with all tools
```

### Adding New Features
1. Create new resource module in `resources/`
2. Add new MCP tools in `server.py`
3. Update README with new capabilities

### Testing
```bash
# Run tests (when available)
pytest

# Type checking
mypy src/

# Code formatting
black src/
```

## ⚠️ Security Considerations

### Credentials
- **Never commit secrets** to version control
- Use environment variables or secure vaults
- Rotate secrets regularly
- Use least privilege permissions

### Monitoring
- Monitor Azure AD audit logs for MCP server activities
- Set up alerts for sensitive operations (user creation/deletion)
- Review permission usage regularly

### Access Control
- Limit who has access to the MCP server credentials
- Consider implementing additional approval workflows for critical operations
- Use service accounts with limited scope when possible

## 🆘 Troubleshooting

### Common Issues

#### Authentication Failures
```
Error: Missing required credentials: client_secret
```
- Check that `config/.env` exists and contains all required values
- Verify the client secret hasn't expired

#### Permission Denied
```
Authorization_RequestDenied
```
- Verify all required API permissions are added
- Ensure admin consent has been granted
- Check that permissions are "Application" type, not "Delegated"

#### User Creation Fails
```
Error creating user: Property 'userPrincipalName' is invalid
```
- Ensure the UPN domain matches your tenant's verified domains
- Check that the user doesn't already exist

### Getting Help
1. Check the error logs for specific error messages
2. Verify your Azure AD app permissions
3. Test with a simple operation first (like `search_users`)
4. Check Microsoft Graph API documentation for specific requirements

## 📈 Next Steps

### Advanced Features
Consider adding support for:
- License management
- Device compliance policies
- Custom security attributes
- Application role assignments

### Integration
- Set up CI/CD for automated deployments
- Integrate with your ITSM system
- Create custom workflows for your organization

---

**🎉 You're ready to revolutionize your identity management with AI-powered automation!**
