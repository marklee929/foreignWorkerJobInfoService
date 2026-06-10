# System Architecture

## Purpose

This document defines the high-level system architecture of WorkConnect.

WorkConnect is a practical information platform for people who move to another country to work, live, study, or settle.

The first implementation target is Korea, but the system should be designed as a reusable country-based information platform.

This document focuses on the major system components and how information flows between them.

## High-Level Architecture

WorkConnect is composed of five major layers.

```text
External Sources
→ Backend + Local LLM
→ Database / Content Management
→ Admin Frontend
→ Facebook Page

Current first channel:

Facebook Page: WorkConnect Korea

Current admin channel:

Local admin web UI

Current runtime:

Local PC before production deployment
Main Components
1. Facebook Page

The Facebook Page is the first public delivery channel.

Current page:

WorkConnect Korea

Role:

publish selected content
test public reaction
collect early audience signals
expose useful work/life/settlement information
drive future subscription or service conversion

Important:

Facebook is a delivery channel, not the core product.

The core product is the structured information system behind it.

2. Admin Frontend

The admin frontend is the operator control screen.

Role:

show collected data
show content candidates
show publishing status
show Facebook token/status
show bot and scheduler status
show Local LLM status
allow manual review, editing, and additional publishing
make the whole workflow visible and controllable

The admin UI should prioritize intuitive data inspection.

An operator should be able to quickly understand:

what was collected
what was normalized
what became content
what was skipped
what was published
what failed
what needs review
3. Backend

The backend connects the admin UI, database, collectors, Local LLM, and publishing channels.

Role:

expose admin APIs
run collection pipelines
normalize sources
validate data quality
manage content candidates
control publishing
store logs
check Facebook token/page status
communicate with Local LLM when needed
send Telegram operation summaries if enabled

The backend should protect the system from unsafe automation.

It should not publish low-quality, broken, duplicated, or irrelevant data only because it was collected.

4. Local LLM

Local LLM is an optional helper.

Role:

semantic duplicate check
relevance check
summary quality check
sensitive topic detection
content drafting support

Local LLM must not be required for the system to run.

If Local LLM is unavailable, the backend should fall back to deterministic rules.

Local LLM should support the workflow, not control final publishing by itself.

5. External Data Sources

WorkConnect collects information from multiple source types.

Examples:

government APIs
country information APIs
immigration and visa websites
employment and occupation APIs
Naver
Google
RSS feeds
official public agency pages
trusted media
local support organizations

Each source may have a different format, language, reliability level, and content depth.

Therefore, every source must pass through normalization and quality checks before it becomes content.

Basic Data Flow

The system should follow this flow.

source discovery
→ raw collection
→ source normalization
→ duplicate/source normalization
→ domain classification
→ quality evaluation
→ content candidate
→ admin review or automatic publishing
→ Facebook publishing
→ operation/performance logging

This flow should apply to all major information domains:

news
living information
immigration information
occupation information
employment/job information
Source Normalization

Sources are not trusted as-is.

The backend should normalize:

source URL
canonical URL
title
body text
language
country
category
source trust level
published date
collected date
hash key
similarity key

The system should distinguish:

discovery URL
source URL
canonical URL
publishable link URL

For example, Google News RSS may help discover a topic, but it should not automatically become the final publishable link.

Content Management Layer

All publishable information should flow into the content management layer.

The content management layer is responsible for:

listing content candidates
showing source reference
showing quality status
showing publishing readiness
allowing admin edits
allowing manual publish
supporting automatic publish
storing publish results

First stage:

automatic publishing for safe, high-confidence content

Second stage:

admin intervention for review, editing, additional publishing, or republishing

The goal is not only to automate posting, but to give the operator clear control over the full content pipeline.

Facebook Token and Publishing Status

Because Facebook is the first public delivery channel, token and page status must be visible and validated.

The system should track:

token type
token validity
page match
required permissions
expiration status
token fingerprint
last validation time
last publish error
Meta error code/subcode/fbtrace_id when available

The system must not collapse all Facebook failures into a generic token error.

Facebook publishing should be blocked or reviewed when token status is unsafe or unknown.

Admin Visibility Principle

The admin frontend should not hide the workflow.

Each data item should clearly show its current stage:

collected
normalized
classified
evaluated
content candidate created
ready to review
ready to publish
published
skipped
failed
archived

The admin should also see why an item was accepted, blocked, skipped, or promoted.

Examples:

Blocked: no usable article body
Blocked: Google RSS link only
Skipped: low user relevance
Review: immigration/legal sensitivity
Ready: high actionability and valid source
Published: Facebook post created
Automation Control

Automation should be controllable.

The system should support:

automatic collection
automatic normalization
automatic candidate creation
automatic publishing for safe items
manual review for uncertain items
manual republish or edit
bot status visibility
scheduler visibility
stop or pause controls

Automation must not silently cross system boundaries.

If publishing, token, scheduler, auth, or protected areas fail, the system should stop or report clearly rather than continue blindly.

Current Runtime Boundary

Before production deployment, WorkConnect runs locally.

This means:

local frontend
local backend
local PostgreSQL
local automation scheduler
optional local LLM
external Facebook/Telegram APIs

Even though the admin system is local, Facebook publishing is external and public.

Therefore, local development changes can affect real public output.

Target Architecture Direction

The system should evolve toward this structure.

country-specific sources
→ normalized domain data
→ content management
→ public/social publishing
→ feedback/performance
→ reusable knowledge base
→ future GPT/API/subscription layer

The first implementation is Korea, but the architecture should keep country-specific rules separate from the global product model.

Key Architecture Principles
Facebook is a channel, not the product.
Admin frontend is the operator cockpit.
Backend owns validation, normalization, and workflow control.
Local LLM is optional and advisory.
External sources must be normalized before use.
Source data and publishable content must stay separated.
Content management is the bridge between data and public output.
Automation must be visible and controllable.
Facebook token and publish errors must be explicit.
The system should remain expandable beyond Korea.