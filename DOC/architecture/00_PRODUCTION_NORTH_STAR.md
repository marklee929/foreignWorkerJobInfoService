# Product North Star

## Core Mission

WorkConnect is an information platform for people who move to another country to work, live, study, or settle.

The service helps them understand the practical information they need before and after arrival.

WorkConnect starts with Korea, but the product direction is not limited to Korea.

The long-term goal is to become a trusted information layer for living and working abroad.

## Product Direction

People who move to another country face scattered, unclear, and often language-heavy information.

WorkConnect collects, organizes, explains, and delivers that information in a form that is easier to understand and act on.

The service should cover not only jobs, but the full settlement journey.

Core areas include:

- work
- visa
- immigration
- housing
- healthcare
- banking
- insurance
- transportation
- language
- local support
- public services
- rights and risks
- daily life

## First Market

The first target market is Korea.

Korea is the first implementation case because the initial data, admin UI, collectors, and publishing workflow are being built around Korea.

However, the architecture should avoid hardcoding the product identity as Korea-only.

Country-specific logic should be separated from the global product model whenever possible.

## Target Users

WorkConnect serves people who are trying to understand life and work in a foreign country.

Primary users include:

- foreign workers
- job seekers abroad
- international students
- immigrants
- marriage migrants
- long-term residents
- people preparing to move overseas
- people already living abroad who need local guidance

The user may not understand the local language, local institutions, administrative terms, labor rules, or daily-life systems.

## Core User Need

The user is usually not looking for random information.

They are trying to answer practical questions such as:

- Can I work there?
- What visa or permit do I need?
- What should I prepare?
- What rights and risks should I know?
- Where can I get help?
- How do I handle daily life after arrival?
- Which information is official, reliable, or only reference?

WorkConnect should prioritize information that helps users make decisions or reduce uncertainty.

## Product Identity

WorkConnect should be understood as:

- a settlement information platform
- a work-and-life abroad guide
- a source-backed explainer
- a practical information hub
- a bridge between official information and everyday understanding

WorkConnect should not become:

- a random news repost bot
- a generic travel blog
- a sensational issue feed
- an unverified immigration advice site
- a job guarantee service
- a replacement for official institutions

## Data Philosophy

WorkConnect collects data to make life abroad more understandable.

Data is valuable when it is:

- useful
- source-backed
- understandable
- relevant to foreign residents or movers
- connected to a real user problem
- reusable for guides, alerts, search, or future GPT answers

Data is not valuable just because it was collected.

Low-quality, irrelevant, unclear, or unsafe data should not be forced into public content.

## Content Philosophy

Public content should help users understand what matters and why.

A good content item should answer:

```text
What happened or what information exists?
Why does it matter to someone living or working abroad?
What should the user check or do next?
Where is the original source?
````

Content should be clear, calm, practical, and source-aware.

It should avoid clickbait, fear-based framing, overclaiming, or pretending to provide legal certainty.

## Automation Philosophy

Automation should support trust, not replace judgment.

The system may automate:

* collection
* normalization
* translation
* summarization
* duplicate detection
* relevance scoring
* content drafting
* publishing queue preparation

The system should be careful with:

* legal or visa interpretation
* sensitive incidents
* official policy changes
* weak or unclear sources
* automatically publishing unverified content

Automation should make the operator faster, but not make the product careless.

## Architecture Implication

Because WorkConnect is a global work-and-settlement information platform, the system should separate:

```text
global product model
→ country-specific sources
→ domain data
→ normalized information
→ publishable content
→ user-facing delivery
```

The first implementation is Korea, but the structure should allow other countries to be added later.

Korea-specific collectors, keywords, sources, and rules should not define the whole product identity.

## Success Criteria

WorkConnect is moving in the right direction if:

* users can understand foreign work and settlement information more easily
* important information is collected from reliable sources
* public content is practical and source-backed
* country-specific systems can be added without rewriting the whole product
* collected data can support social posts, admin review, guides, APIs, and future GPT answers
* the system separates raw data, normalized data, content candidates, and published content
* automation improves consistency without damaging trust
