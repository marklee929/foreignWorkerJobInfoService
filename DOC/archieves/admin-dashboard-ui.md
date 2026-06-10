# Admin Dashboard UI Architecture

## Purpose

The admin dashboard is an internal operations screen for WorkConnect data collection, social news automation, local LLaMA validation, and CrewTeam bot control.

The first dashboard should focus on operational visibility rather than public user features.

## Core Sections

### 1. Overview KPI Cards

Show high-level status at the top.

Recommended cards:

- Collected News Today
- Published Posts
- Duplicate Skipped
- Life Info Collected
- Pending Review
- Failed Jobs
- Active Bots
- Local LLaMA Status

### 2. Local LLaMA Status Panel

The dashboard must show local LLaMA status as a first-class operational component.

Fields:

- Status: Online / Offline / Starting / Running / Timeout / Fallback Used
- Model name
- Endpoint
- Last check time
- Average response time
- Queue length
- Last error
- Current task: Summarizing / Duplicate Checking / Relevance Review / Idle

This status should also appear as a small indicator in the top bar.

Example:

```text
Local LLaMA: Online · llama3.1 · 820ms avg · 3 queued
```

If local LLaMA is unavailable, the dashboard should clearly show that deterministic fallback rules are being used.

### 3. CrewTeam Bot Operations Panel

The dashboard must show running bots and allow basic control.

Bot examples:

- News Collector Bot
- News Duplicate Guard Bot
- Facebook Publisher Bot
- Telegram Notifier Bot
- Life Info Research Bot
- Normalizer Bot
- Verifier Bot
- Local LLaMA Review Bot

Each bot row should show:

- Bot name
- Domain: social/news, research, storage, etc.
- Current status: Idle / Running / Paused / Stopped / Failed
- Current task
- Last started at
- Last completed at
- Last error
- Processed count
- Success count
- Failed count

Control buttons:

- Start
- Pause
- Stop
- Restart
- View Logs

Dangerous controls such as Stop/Restart should be visually distinct and may require confirmation later.

### 4. Bot Work Logs

Show recent bot work logs in the dashboard.

Recommended columns:

- Time
- Bot
- Level: INFO / WARN / ERROR
- Task
- Message
- Related entity ID
- Duration

Example logs:

```text
10:12:31 News Collector Bot INFO collected 10 candidates from Google News RSS
10:12:38 Duplicate Guard Bot WARN 3 candidates marked duplicate
10:12:42 Local LLaMA Review Bot INFO semantic duplicate check completed
10:12:44 Facebook Publisher Bot INFO dry-run publish completed
10:12:45 Telegram Notifier Bot INFO dry-run notification completed
```

### 5. All Collected Data Table

The dashboard must include an `All Collected Data` table.

Columns:

- Category
- Region
- Service / Task
- Name / Organization
- Contact
- Address
- Language
- Source
- Quality Score
- Duplicate Risk
- Verification Status
- Collected At
- Local LLaMA Status
- Processing Status

Category badge examples:

- Lifestyle
- Immigration
- Labor
- Housing
- Mobile
- Hospital
- Translation

Processing Status examples:

- Collected
- Normalizing
- Duplicate Checking
- LLaMA Reviewing
- Ready for Review
- Verified
- Skipped
- Failed

Local LLaMA Status examples:

- Not Used
- Pending
- Running
- Passed
- Warning
- Failed
- Timeout
- Fallback Used

Filters:

- Category filter
- Region filter
- Verification Status filter
- Processing Status filter
- Local LLaMA Status filter
- Quality Score range
- Duplicate Risk toggle
- Search input

Row click opens a right-side detail drawer.

Detail drawer fields:

- Raw collected text
- Source URL
- Evidence text
- Duplicate candidates
- Local LLaMA review result
- LLaMA confidence score
- LLaMA reasoning summary
- Processing history
- Edit history
- Last updated at

### 6. Social News Automation Panel

Show Facebook news automation status.

Fields:

- Latest collected news
- Selected candidate
- Evaluation score
- Duplicate score
- Korea relevance score
- Facebook publish status
- Telegram notification status
- Dry-run / Real mode indicator

### 7. Data Coverage Panel

For the first version, use tables and simple charts instead of a full national map.

Recommended charts:

- Regional collection count by sido/sigungu
- Category distribution
- Pending review by region
- Duplicate risk by category

A future Korea map can be added later.

## Layout Recommendation

Desktop-first admin layout:

```text
Sidebar
  Dashboard
  Social
    News Automation
    Facebook Posts
    Telegram Notifications
  Lifestyle
    Housing
    Appliances
    Mobile Service
  Immigration
    Immigration Law
    Lawyers
    Administrative Agents
  Labor
    Labor Lawyers
    Labor Attorneys
  Data Quality
    Duplicate Candidates
    Review Queue
    Source Reliability
  Bot Operations
  Settings

Main Dashboard
  KPI cards
  Local LLaMA Status + Bot Control summary
  Social News Automation Status
  All Collected Data Table
  Bot Work Logs
  Data Coverage Overview
```

## Stitch Prompt Base

Use this when generating or updating dashboard UI in Stitch.

```text
Create a clean SaaS-style internal admin dashboard for WorkConnect.

The dashboard manages foreign worker life information collection, social news automation, local LLaMA validation, and CrewTeam bot operations.

Include a left sidebar with:
- Dashboard
- Social
  - News Automation
  - Facebook Posts
  - Telegram Notifications
- Lifestyle
  - Housing
  - Appliances
  - Mobile Service
- Immigration
  - Immigration Law
  - Lawyers
  - Administrative Agents
- Labor
  - Labor Lawyers
  - Labor Attorneys
- Data Quality
  - Duplicate Candidates
  - Review Queue
  - Source Reliability
- Bot Operations
- Settings

Main dashboard sections:
1. KPI cards for collected news, published posts, duplicate skipped, life info collected, pending review, failed jobs, active bots, and local LLaMA status.
2. Local LLaMA Status panel showing online/offline, model name, endpoint, average response time, queue length, current task, last error, and fallback status.
3. CrewTeam Bot Operations panel showing bot status and controls: Start, Pause, Stop, Restart, View Logs.
4. Bot Work Logs table showing time, bot, level, task, message, related entity ID, and duration.
5. Social News Automation panel showing selected candidate, evaluation score, duplicate score, publish status, and Telegram notification status.
6. All Collected Data table with columns: Category, Region, Service / Task, Name / Organization, Contact, Address, Language, Source, Quality Score, Duplicate Risk, Verification Status, Collected At, Local LLaMA Status, Processing Status.
7. Data Coverage panel with regional/category distribution charts. Use placeholder for future Korea map.

All Collected Data table requirements:
- Category badges with different colors
- Filters for category, region, verification status, processing status, local LLaMA status, quality score range, duplicate risk, and search
- Row click opens right-side detail drawer
- Detail drawer includes raw collected text, source URL, evidence text, duplicate candidates, local LLaMA review result, LLaMA confidence score, LLaMA reasoning summary, processing history, edit history, and last updated time

Design:
- Desktop-first SaaS admin dashboard
- Light background
- Card-based layout
- Blue/purple accent colors
- Compact tables
- Clear status badges
- Use mock data
```
