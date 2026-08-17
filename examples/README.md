# Example Tasks for the Free Coding Agent

This directory contains example tasks you can give to the agent. Each example shows the prompt and the expected output.

---

## 1. Create a Flask API

```
Create a Flask web app with a /api/status endpoint that returns JSON with status, uptime, and version. Include requirements.txt and a README.
```

## 2. Build a CLI Tool

```
Create a Python CLI tool called "todo" that lets me add, list, and complete tasks. Use argparse. Store tasks in a JSON file.
```

## 3. Generate Tests

```
Read the main.py file and write comprehensive unit tests using pytest. Make sure to test edge cases.
```

## 4. Refactor Code

```
Read utils.py and refactor it to use dataclasses instead of dicts. Keep all existing functionality.
```

## 5. Create a Data Pipeline

```
Create a Python script that reads a CSV file, filters rows where age > 25, groups by department, and outputs summary statistics. Use pandas.
```

## 6. Build a Discord Bot

```
Create a Discord bot using discord.py that responds to !hello, !ping, and !joke commands. Include a config file for the bot token.
```

## 7. Create a Static Website

```
Create a simple HTML/CSS/JS portfolio page with a hero section, about section, and contact form. Make it responsive.
```

## 8. Write Documentation

```
Read all Python files in the src/ directory and generate a comprehensive API reference in Markdown.
```

---

> 💡 **Tip:** Run the agent in `--verbose` mode to see its thought process:
> ```bash
> python -m src.agent --verbose
> ```
