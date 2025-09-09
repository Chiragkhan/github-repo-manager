# GitHub Repository Manager

A comprehensive desktop application for managing all your GitHub repositories in one place. Built with Python and Tkinter, this tool provides a powerful interface to view, filter, and manage your entire GitHub portfolio.

![GitHub Repository Manager](https://img.shields.io/badge/python-3.7%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

## Features

### 📊 **Repository Overview**
- **Complete Repository List** - View all your repositories in a sortable table
- **Real-time Statistics** - See totals for repos, stars, forks, and more
- **Status Indicators** - Visual status showing activity level (🔥 Hot, 📝 Active, ⚠️ Inactive, 😴 Stale, 🗄️ Archived)
- **Visual Repository Types** - Color-coded rows for private, archived, and forked repositories

### 🔍 **Advanced Filtering & Search**
- **Visibility Filter** - Show All, Public only, or Private only repositories
- **Language Filter** - Filter by programming language
- **Text Search** - Real-time search across repository names
- **Smart Sorting** - Click column headers to sort by any attribute

### ⚙️ **Repository Management**
- **Bulk Operations** - Select multiple repositories for batch actions
- **Quick Access** - Double-click to open repositories in browser
- **Clone Management** - Clone single or multiple repositories locally
- **License Updates** - Update licenses across multiple repositories
- **Bulk Settings** - Apply settings to multiple repositories at once

### 🖱️ **Intuitive Interface**
- **Context Menus** - Right-click for repository-specific actions
- **Keyboard Shortcuts** - Efficient navigation and selection
- **Progress Tracking** - Visual progress bars for long-running operations
- **Status Updates** - Real-time status messages and feedback

## Installation

### Prerequisites

- Python 3.7 or higher
- `pass` password manager (for GitHub token storage)
- Git (for cloning functionality)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Setup GitHub Token

Store your GitHub personal access token in pass:

```bash
pass insert github/token
```

Enter your GitHub personal access token when prompted. You can create one at:
https://github.com/settings/tokens

**Required token permissions:**
- `repo` - Full repository access
- `admin:org` - Organization access (if managing org repos)

## Usage

### Starting the Application

```bash
python3 github_repo_manager.py
```

Or make it executable:

```bash
chmod +x github_repo_manager.py
./github_repo_manager.py
```

### Main Interface

The application window consists of several key areas:

1. **Control Panel (Left)** - Buttons, filters, and statistics
2. **Repository Table (Center)** - Main data display with sortable columns
3. **Status Bar (Bottom)** - Progress and status information

### Repository Table Columns

| Column | Description |
|--------|-------------|
| ☐ | Selection checkbox |
| Repository Name | Name and link to repository |
| Visibility | 🔒 Private or 🌐 Public |
| Language | Primary programming language |
| ⭐ | Star count |
| 🍴 | Fork count |
| 📋 | Open issues count |
| License | Repository license type |
| Size (KB) | Repository size |
| Last Updated | Date of last commit |
| Status | Activity status indicator |
| Actions | Quick action menu |

### Key Operations

#### Selecting Repositories
- **Single Selection**: Click the checkbox in the first column
- **Multiple Selection**: Click multiple checkboxes
- **Select All**: (Feature to be implemented)

#### Repository Actions
- **Open in Browser**: Double-click or use "Open in Browser" button
- **Clone Repository**: Right-click → Clone or use "Clone Selected" button
- **View Settings**: Right-click → Repository Settings

#### Filtering & Search
- **Visibility**: Use dropdown to show All/Public/Private repositories
- **Language**: Filter by specific programming language
- **Search**: Type in search box to filter by repository name

#### Bulk Operations
- Select multiple repositories using checkboxes
- Use bulk action buttons: Open, Clone, Update License, Bulk Settings

## Configuration

### GitHub Token Permissions

Your GitHub token needs the following scopes:
- `repo` - Access to repositories
- `admin:org` - Organization access (optional)

### Default Settings

- **Clone Directory**: `~/git` (customizable per operation)
- **Refresh Interval**: Manual refresh only
- **GitHub API**: Uses GitHub REST API v3

## Features in Detail

### Repository Status Indicators

- **🔥 Hot** - Updated within 30 days
- **📝 Active** - Updated 30-180 days ago  
- **⚠️ Inactive** - Updated 180-365 days ago
- **😴 Stale** - Updated over 365 days ago
- **🗄️ Archived** - Repository is archived

### Row Color Coding

- **Yellow Background** - Private repositories
- **Red Background** - Archived repositories  
- **Green Background** - Forked repositories
- **Blue Background** - Selected repositories

### Statistics Panel

Real-time statistics showing:
- Total repositories (filtered)
- Public/Private count
- Total stars across all repos
- Total forks across all repos

## Troubleshooting

### Common Issues

**"Failed to get GitHub token from pass store"**
- Ensure `pass` is installed and configured
- Store your GitHub token: `pass insert github/token`

**"Failed to load repositories"**
- Check your internet connection
- Verify your GitHub token has correct permissions
- Check if you've hit GitHub API rate limits

**Repositories not loading**
- Click the "🔄 Refresh" button to reload
- Check the status bar for error messages

### GitHub API Rate Limits

- **Authenticated requests**: 5,000 per hour
- **Search API**: 30 requests per minute
- The app shows progress bars for rate limit awareness

## Development

### Project Structure

```
github-repo-manager/
├── github_repo_manager.py    # Main application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
└── .gitignore              # Git ignore rules
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Future Enhancements

- [ ] Repository creation and deletion
- [ ] Issue and pull request management
- [ ] Branch management interface
- [ ] Repository templates
- [ ] Export/import repository lists
- [ ] Automated license updates
- [ ] Repository health scoring
- [ ] Integration with other Git providers

## Security Considerations

- GitHub token is stored securely in pass
- No tokens are logged or displayed in the UI
- All API calls use HTTPS
- Local repository data is cached in memory only

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Philip S Wright** - [GitHub Profile](https://github.com/pdubbbbbs)

## Acknowledgments

- GitHub REST API for repository data
- Python Tkinter for the GUI framework
- Pass password manager for secure token storage
