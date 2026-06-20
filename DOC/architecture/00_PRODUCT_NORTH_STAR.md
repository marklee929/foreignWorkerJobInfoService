# Product Constitution

## Core Mission

WorkConnect is a practical, source-backed work-and-settlement information platform for people who move to another country to work, live, study, immigrate, or settle.

The service helps users understand what to check, prepare, avoid, and do next before and after arrival.

## Purpose Function

WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty and make practical decisions through reliable information about work, visa, immigration, housing, healthcare, banking, insurance, transportation, labor rights, public services, safety, and daily life.

This purpose function comes before data schema, source availability, social reach, automation convenience, or implementation shortcuts.

## Current WorkConnect Korea Scope

Korea is the current active market and public channel target.

WorkConnect Korea may use Korea-specific collectors, sources, admin views, categories, and public delivery channels. Those implementation details must not redefine the global product identity.

Generic global or non-Korea content may be stored as a future/global reference signal when useful, but it must not enter WorkConnect Korea public review or publishing by default.

## Global Product Direction

WorkConnect must remain expandable beyond Korea.

Country-specific logic should be separated from the global product model:

```text
global product purpose
-> target country scope
-> domain source data
-> normalized information
-> content candidate
-> public delivery
```

Future countries should be added by extending sources, categories, rules, and delivery channels, not by rewriting the product purpose.

## Target Users

Primary users include:

- foreign workers
- job seekers abroad
- international students
- immigrants
- marriage migrants
- long-term residents
- people preparing to move overseas
- people already living abroad who need local guidance

These users may not understand the local language, institutions, legal terms, labor rules, public-service systems, or everyday settlement processes.

## Classification Principle

A topic is WorkConnect-relevant only when it helps the target user:

- make a practical decision
- reduce uncertainty
- understand what to check next
- access source-backed support or guidance
- understand a work, visa, housing, healthcare, banking, labor, public-service, safety, or daily-life issue

A topic is not relevant merely because it mentions Korea, foreigners, travel, international affairs, or news.

Source availability or social reach must not override product purpose.

## Product Identity

WorkConnect should be understood as:

- a settlement information platform
- a work-and-life abroad guide
- a source-backed explainer
- a practical information hub
- a bridge between official information and everyday understanding
- a future knowledge layer for guides, search, APIs, alerts, and GPT-assisted answers

## What WorkConnect Must Not Become

WorkConnect must not become:

- a random news repost bot
- a generic Korea news feed
- a generic travel blog
- a sensational issue feed
- an unverified visa or legal advice site
- a job guarantee service
- a social-posting automation project
- a replacement for official institutions

## Content Constitution

Public or reviewable content should answer:

```text
What information exists?
Why does it matter to the target user?
What should the user check or do next?
What source supports this?
```

Content should be calm, practical, source-aware, and clear about uncertainty.

It must avoid clickbait, fear-based framing, legal overclaiming, and public use of internal diagnostic text.

## Automation Constitution

Automation may support:

- collection
- normalization
- translation
- summarization
- duplicate detection
- relevance scoring
- content drafting
- review queue preparation

Automation must not replace judgment for:

- legal or visa interpretation
- sensitive incidents
- official policy changes
- weak or unclear sources
- public publishing decisions that cross protected boundaries

Automation should make the operator faster without making the product careless.

## Success Criteria

WorkConnect is on course when:

- users understand foreign work and settlement information more easily
- important information is collected from reliable sources
- public content is practical and source-backed
- country-specific systems can be added without changing the product constitution
- raw data, normalized data, content candidates, and published output remain separated
- low-value news, generic politics, travel rankings, economy noise, crypto, and generic lifestyle items are blocked unless they pass user-need and actionability gates
- automation improves consistency without damaging trust
