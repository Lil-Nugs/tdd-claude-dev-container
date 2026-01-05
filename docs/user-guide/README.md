# User Guide

A guide to using TDD Claude Dev Container for AI-assisted development.

## Getting Started

### Prerequisites

Before using the application, ensure you have:

- Docker running on your system
- Web browser (Chrome, Firefox, Safari, Edge)
- Network access to the application (default: http://localhost:5173)

### Accessing the Application

1. Open your web browser
2. Navigate to http://localhost:5173
3. You'll see the dashboard with project overview

## Dashboard

The dashboard provides an overview of your development environment:

- **Project Count** - Total number of projects
- **Active Containers** - Running Docker containers
- **Recent Projects** - Quick access to your latest projects
- **Navigation** - Links to projects list and other features

## Projects

### Creating a Project

1. Click **"Projects"** in the navigation or dashboard
2. Click **"New Project"** button
3. Enter a project name
4. (Optional) Enter a description
5. Click **"Create"**

Your project is now created and ready for use.

### Viewing Projects

The projects page shows all your projects in a grid layout:

- **Project Name** - Click to open project details
- **Creation Date** - When the project was created
- **Container Status** - Shows if a container is running

### Project Details

Click on a project to see its details:

- **Project ID** - Unique identifier
- **Path** - File system location (if set)
- **Created** - Creation timestamp
- **Container Status** - Current state (created/running/exited/error)

### Deleting a Project

1. Open the project details page
2. Click **"Delete Project"**
3. Confirm the deletion in the dialog

**Warning:** This action cannot be undone.

## Containers

### Starting a Container

1. Open a project's detail page
2. Click **"Start Container"**
3. Wait for the container to initialize
4. Status will change to "running"

### Stopping a Container

1. Open the project detail page
2. Click **"Stop Container"**
3. Wait for the container to stop
4. Status will change to "exited"

### Container States

| State | Description |
|-------|-------------|
| created | Container exists but not started |
| running | Container is active |
| exited | Container stopped normally |
| error | Container encountered an error |

## Terminal

### Opening the Terminal

1. Ensure the project's container is running
2. Click **"Open Terminal"** on the project page
3. The terminal opens in a new view

### Using the Terminal

The terminal provides full interactive access:

- Type commands and press **Enter** to execute
- Use **arrow keys** to navigate command history
- Standard shell features work (tab completion, etc.)

### Terminal Features

- **Full Color Support** - 256 color terminal
- **Cursor Movement** - Works with vim, nano, etc.
- **Interactive Programs** - Supports full-screen apps
- **Resize** - Automatically adjusts to window size

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+C | Send interrupt (SIGINT) |
| Ctrl+D | Send EOF / Exit shell |
| Ctrl+L | Clear terminal screen |
| Ctrl+Z | Suspend process (SIGTSTP) |
| Ctrl+\ | Send quit (SIGQUIT) |
| Tab | Command/path completion |
| Up/Down | Navigate command history |

### Interrupt Button

Click the **"Interrupt"** button to send Ctrl+C to the running process. Useful when:

- A command is stuck
- You want to stop a long-running process
- The program is waiting for input you can't provide

### Reconnecting

If the terminal disconnects:

1. Click the **"Reconnect"** button
2. Wait for connection to establish
3. You may need to restart your command

### Terminal Security

The terminal enforces security restrictions:

**Allowed commands:**
- bash, sh
- python, python3
- node, npm, npx
- bd, claude
- git, make
- pytest, ruff, mypy
- pip, uv

**Allowed directories:**
- /home
- /tmp
- /projects
- /workspace

Attempting to run unauthorized commands will result in an error.

## Workflow Tips

### Typical Development Session

1. **Create Project** - Name it descriptively
2. **Start Container** - Wait for initialization
3. **Open Terminal** - Begin interactive session
4. **Work with Claude** - Run claude commands
5. **Stop Container** - When finished

### Working with Claude CLI

Once in the terminal:

```bash
# Start Claude conversation
claude

# Ask Claude to help with code
claude "Help me create a Python function"

# Review and edit files
vim myfile.py

# Run your code
python myfile.py
```

### Best Practices

1. **One Project per Task** - Keep projects focused
2. **Stop Unused Containers** - Free up resources
3. **Check Container Status** - Ensure running before terminal
4. **Use Meaningful Names** - Easy to identify projects later

## Troubleshooting

### Terminal Not Connecting

**Symptoms:** Terminal shows "Connecting..." indefinitely

**Solutions:**
1. Verify the container is running (check status)
2. Refresh the browser page
3. Stop and restart the container
4. Check Docker is running on the host

### Container Won't Start

**Symptoms:** Start button doesn't change status

**Solutions:**
1. Check Docker is running: `docker ps`
2. Verify Docker has enough resources
3. Check Docker logs: `docker logs <container-id>`
4. Restart Docker daemon

### Commands Not Working

**Symptoms:** Commands fail or aren't recognized

**Solutions:**
1. Verify you're using an allowed command
2. Check you're in an allowed directory
3. Use full paths if needed

### Slow Performance

**Symptoms:** Terminal lag, delayed responses

**Solutions:**
1. Check network connectivity
2. Reduce terminal window size
3. Avoid commands with massive output
4. Consider increasing Docker resources

### Lost Connection

**Symptoms:** Terminal shows "Disconnected"

**Solutions:**
1. Click "Reconnect" button
2. Check network connection
3. Verify container still running
4. Refresh browser and reopen terminal

### Process Stuck

**Symptoms:** Can't type, no response

**Solutions:**
1. Click "Interrupt" button
2. Wait a few seconds
3. Try Ctrl+C in terminal
4. If persistent, stop container and restart

## Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | Full Support | Recommended |
| Firefox | Full Support | |
| Safari | Full Support | |
| Edge | Full Support | |

### WebSocket Requirements

The terminal requires WebSocket support. Ensure:
- WebSocket connections are allowed (firewall/proxy)
- Upgrade headers are not stripped
- Connection is to the correct port

## Getting Help

### Application Logs

For debugging, check:

- **Browser Console** - Press F12, go to Console tab
- **Network Tab** - Check WebSocket connections
- **Backend Logs** - `docker logs backend`

### Reporting Issues

When reporting issues, include:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and version
5. Any error messages (console, network)

## Keyboard Reference

### General

| Key | Action |
|-----|--------|
| Ctrl+C | Interrupt/Cancel |
| Ctrl+D | Exit/EOF |
| Ctrl+L | Clear screen |

### Navigation

| Key | Action |
|-----|--------|
| Up | Previous command |
| Down | Next command |
| Left/Right | Move cursor |
| Home | Start of line |
| End | End of line |

### Editing

| Key | Action |
|-----|--------|
| Backspace | Delete before cursor |
| Delete | Delete at cursor |
| Ctrl+W | Delete word before |
| Ctrl+U | Delete to start of line |
| Ctrl+K | Delete to end of line |

### Shell-Specific

| Key | Action |
|-----|--------|
| Tab | Auto-complete |
| Ctrl+R | Search history |
| Ctrl+A | Move to start |
| Ctrl+E | Move to end |
