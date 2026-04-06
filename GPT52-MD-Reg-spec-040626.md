WOW Agentic Regulatory Studio (Enhanced) — Comprehensive Technical Specification (Streamlit on Hugging Face Spaces)
Scope & constraints
This specification upgrades the previously described Streamlit-based “Agentic Medical Device Reviewer” without removing any original features. It adds new “WOW UI”, multi-agent stepwise execution with editable handoffs, richer dashboards/status, safer API-key handling, expanded AI Note Keeper, and a new Guidance Reviewer & Regulatory Research workflow that can ingest published guidance (txt/markdown/pdf) and generate (1) a grounded 2000–3000 word regulatory research report, (2) a template-based report, and (3) a generated skill.md for creating a new agent skill.
No code is created or modified here—this is a functional + technical design specification only.

1. Product Goals
1.1 Primary goals
Regulatory productivity: accelerate review of medical device submissions and guidance (FDA/TFDA + international alignment).
Controlled agentic workflow: users can run agents one-by-one, choose models per step, edit prompts and intermediate outputs, and download artifacts.
Grounded reporting: the system must synthesize uploaded guidance with externally retrieved FDA-related sources (e.g., 510(k) summaries, FDA guidance, recognized standards) and extend to international regulations/standards.
WOW usability: visual “status indicators”, interactive dashboards, theme/style personalization, and “magical” AI helpers.
1.2 Non-goals
Building a full validated eQMS or regulatory submission system.
Guaranteeing legal compliance decisions; the system supports drafting and research, not final determinations.
2. Preserved Original Features (Must Remain)
The enhanced system retains all previously specified components, including:

Streamlit multi-tab app on Hugging Face Spaces
Providers: OpenAI API, Gemini API, Anthropic API, Grok API
agents.yaml driven agent catalog (upload/edit/download)
Tabs and features:
Dashboard (usage charts, history)
TW Premarket (TFDA application data entry, import/export JSON/CSV, completeness indicator, pre-screening agent, document helper agent)
510(k) Intelligence
PDF → Markdown
510(k) Review Pipeline (structuring + checklist/review memo)
Note Keeper & Magics
Agents Config Studio
Editable outputs in text/markdown views and session persistence (via st.session_state)
3. Enhanced WOW UI/UX Requirements
3.1 Theme, language, painter-style personalization (WOW UI v2)
User-selectable global UI settings (persisted in session):

Theme: Light / Dark
UI language: English / 繁體中文
Painter styles (20) inspired by famous painters, applied as background + component accents:
Example set: Monet, Van Gogh, Klimt, Picasso, Hokusai, Turner, Vermeer, Renoir, Matisse, Kandinsky, Dalí, Rembrandt, Frida Kahlo, Georgia O’Keeffe, Edward Hopper, Cézanne, Gauguin, Caravaggio, Magritte, Rothko
Jackpot style: one-click random style selection (with an animated “reveal” interaction).
Localization rules

UI labels and help text follow selected UI language.
Output language for generated documents is controlled per workflow (see §8), independent from UI language.
3.2 WOW status indicators (cross-tab)
A unified status system appears in the header and per-agent panels:

Statuses

Idle, Ready, Running, Blocked (Missing input), Done, Error, Needs review, Downloaded
Indicators

Color-coded chips + tooltips
Step progress bars for multi-step workflows
“Last run” metadata: model, tokens estimate, duration, timestamp, provider
3.3 Awesome interactive dashboard (WOW Dashboard v2)
Dashboard expands to include:

Run analytics (original + richer)
Runs by tab, model, provider
Token estimate trend over time
Agent pipeline explorer
Sankey/flow visualization: agent → next agent usage paths
Quality signals
“Edits after generation” rate (how often user modifies output)
“Download rate” by artifact type (md/txt/pdf/skill.md)
Cost-awareness panel (optional)
Approximate token-to-cost conversion configured by admin (no billing integration required)
4. API Key Handling (Secure UX Requirement)
4.1 Key sources & precedence
For each provider key (OpenAI/Gemini/Anthropic/Grok):

Prefer environment variable (e.g., OPENAI_API_KEY)
Else allow user input on webpage (password-type field)
Store user-provided key only in session state for the current session.
4.2 Display rules
If key is sourced from environment: do not show it; show only a badge like “Loaded from environment”.
If key is user-entered: mask it (password input), allow “Clear key” action.
4.3 Operational safety
Never write keys to disk.
Never include keys in logs, downloads, or LLM prompts.
5. Agent Execution Studio (Stepwise, Editable Handoffs)
5.1 Models supported (global selection list)
User can choose per step:

OpenAI: gpt-4o-mini, gpt-4.1-mini
Gemini: gemini-2.5-flash, gemini-3-flash-preview, gemini-2.5-flash-lite, gemini-3.1-flash-lite-preview
Anthropic models (configurable in agents.yaml)
Grok: grok-4-fast-reasoning, grok-3-mini
5.2 Step-by-step execution contract
For every LLM-related feature in the system:

User can:
Modify the prompt before running
Select the model before running
Select generation parameters (max tokens, temperature) if allowed
View output in Text or Markdown
Edit the output and pass the edited version to the next agent step
5.3 Multi-agent chaining UX
A “Pipeline Runner” panel supports:

Ordered list of steps (agents)
Each step shows:
Input source selector: manual paste / previous step output / uploaded file
Prompt editor and model selector
Output editor
“Use as next input” button
Pipeline can be saved as a named preset (stored in session; optionally exportable JSON).
6. AI Note Keeper v2 (Enhanced + 6 AI Magics)
6.1 Note ingestion
User can paste text or markdown notes.
A “Note Organizer Agent” transforms it into:

Organized markdown with headings, bullet points, and action items
Keywords highlighted in coral color (default)
Output language follows UI language unless overridden
User can edit:

Prompt
Model (any supported)
Output in Markdown/Text view
6.2 “Keep prompt with the note”
Each note stores:

The prompt used
The model used
Timestamp and optional tags So a note can be “re-run” with the same prompt later.
6.3 6 AI Magics (created features)
AI Keywords (custom color)
User inputs keyword list + selects highlight color(s)
Applies consistent highlighting across the note
AI Action Extractor
Generates an “Action Items” table: task, owner, due date, priority, evidence excerpt
AI Risk Flags
Detects regulatory risk language and marks with severity (Low/Med/High) and rationale
AI Meeting Minutes Converter
Converts messy notes into formal minutes: attendees, agenda, decisions, next steps
AI Compliance Crosswalk
Maps note content to selected frameworks (e.g., ISO 13485, ISO 14971) with gaps
AI Diff & Improve
Compares “original note” vs “edited note” and suggests clarity improvements while preserving meaning
All magics support prompt + model selection and editable results.

7. New Feature: Guidance Reviewer & Regulatory Research Workspace
This is a new top-level workflow/tab: “Guidance Reviewer & Research (FDA + International)”.

7.1 Inputs
User may:

Paste guidance text (txt/markdown)
Upload published guidance (txt, md, pdf)
Provide optional metadata:
Device type / intended use
Product code (if known)
Regulation area (sterility, biocompatibility, software, cybersecurity, etc.)
PDF handling requirement:

Extract text, preserve page boundaries, and store page index markers to support later citations like “(Uploaded Guidance p. 12)”.
7.2 Output language selector
User selects Output Language:

繁體中文 (default)
English
All generated artifacts in this workspace must be fully written in the selected output language.

8. External Search & Grounding Requirements (FDA + International)
8.1 Retrieval objective
Given uploaded/pasted guidance, the system must:

Analyze the document’s topic, device category, and claims.
Retrieve FDA-related information:
510(k) summaries (when device type/product code suggests relevant predicates)
FDA guidance documents
FDA recognized consensus standards (and/or standards referenced by FDA)
Extend research to international regulations, industry standards, and official guidance:
Examples: EU MDR/IVDR, IMDRF guidances, ISO/IEC standards, UKCA/MHRA guidance, Health Canada, TGA, PMDA/MHLW as applicable.
8.2 Search architecture (implementation-agnostic specification)
Because Hugging Face Spaces may have varying network constraints, retrieval is specified as a pluggable “Retrieval Connectors” layer:

Connector types

Online connectors (preferred when permitted)
FDA guidance repository pages / RSS
FDA 510(k) database pages (public)
openFDA endpoints (where applicable)
FDA recognized standards database exports (or official listings)
Offline/curated connectors (fallback)
Preloaded snapshot datasets (periodically updated by admin)
User-uploaded zip of references (pdf/md/txt)
Manual citation mode
User supplies URLs or reference text; system incorporates them with citations
8.3 Grounding & citation rules (hard requirement)
Every major claim in the generated report must be backed by at least one:

Uploaded guidance citation (page-based when PDF)
Retrieved source citation (URL + title + publication date when available)
Required citation block per source:

Title
Publisher (FDA/ISO/IMDRF/etc.)
Document number (if available)
URL (if online)
Date accessed
Relevance note (1–2 lines)
If the system cannot retrieve sources (offline mode), the report must explicitly state:

“External retrieval unavailable; analysis grounded only on uploaded content and general regulatory knowledge,” and provide a “To verify” checklist.
9. Report Generation: Comprehensive Research Report (2000–3000 words)
9.1 Step A — Analysis + Retrieval + Synthesis Agent
User selects model (only):

gemini-2.5-flash
gemini-3-flash-preview
gemini-3.1-flash-lite-preview
User can modify the prompt and run.

Agent output: a single markdown report of 2000–3000 words grounded in:

The provided guidance content
Retrieved FDA + international sources
Mandatory report structure (default template for Step A)

Title + document metadata (input filename, date, output language)
Executive summary (5–10 bullets)
Document synopsis (what the uploaded guidance says; include key excerpts)
FDA landscape
Relevant guidance documents (with citations)
510(k) pathway considerations (when applicable)
FDA recognized consensus standards relevant to the topic
International regulatory alignment
EU MDR/IVDR relevance
IMDRF guidance mapping
Other jurisdictions (conditional; only if relevant)
Standards & testing implications
Biocompatibility (ISO 10993), sterilization (ISO 11135/11137/17665), risk (ISO 14971), software (IEC 62304), cybersecurity (as applicable), usability (IEC 62366), etc.
Compliance checklist (actionable)
A table: requirement → evidence expected → source citation → status (Unknown/Provided/Needs work)
Gaps, ambiguities, and questions for the sponsor
Appendices
Source library (full citations)
Terminology glossary (optional)
9.2 User editing and downloads
After generation:

User may edit results in Markdown or Text view.
Download options:
.md (primary)
.txt (plain text)
10. Template-Based Report Transformation (Second Report)
10.1 Template selection
User can:

Upload a regulation report template (markdown/txt)
Or select a default report template (provided by the system)
The system must include a default template option similar in spirit to the sample “審查指引與審查清單” format (e.g., sections + checklist table), adaptable to device categories.

10.2 Step B — Template-Fitting Agent
User selects model:

gemini-2.5-flash
gemini-3-flash-preview
User can modify prompt.

Inputs

Step A comprehensive report (edited or original)
Selected template (uploaded or default)
Output

A comprehensive template-conformant report in the output language
Must preserve traceability: key claims should retain citations or reference IDs carried over from Step A.
User can edit and download .md / .txt.

11. Skill.md Generator (Third Artifact)
11.1 Purpose
Generate a skill.md file defining a new agent skill designed to generate comprehensive medical device guidance based on the structure and information found in the uploaded/pasted guidance input and the generated reports.

11.2 Step C — Skill Creator Agent (content generation)
User selects model:

gemini-2.5-flash
gemini-3-flash-preview
User can modify prompt.

Output language

Entire skill.md must be written in the selected output language (Traditional Chinese or English).
Format requirement

Must follow the standard skill frontmatter pattern:
name
description (trigger conditions; “pushy” to ensure it triggers appropriately)
Skill content must include

Clear “When to use” contexts (guidance writing, regulatory synthesis, checklist creation)
Step-by-step internal workflow instructions
Required output templates
Quality gates (citation requirements, ambiguity flags, “unknowns” handling)
Example prompts
11.3 Add 3 additional WOW features inside the generated skill
The generated skill must explicitly implement these three “WOW” behaviors when used:

Auto-Crosswalk Builder
Automatically creates a crosswalk table mapping guidance sections → FDA guidance/standards → international equivalents.
Citation Quality Gate
Before finalizing, performs a self-check: every major assertion has a citation; missing citations are listed as “Needs source.”
Checklist-to-Actions Converter
Converts the compliance checklist into an execution plan: tasks, owners (roles), acceptance evidence, and suggested test standards.
User can edit the produced skill.md and download it as skill.md.

12. Three Additional WOW AI Features (System-Wide)
Beyond the Note Magics and new Guidance workspace, add these three global AI features:

Regulatory Knowledge Graph (Interactive)

Builds a graph view linking: device type → claims → hazards → standards → guidance → evidence artifacts.
Click a node to preview the supporting excerpt and citations.
Grounding Inspector

An AI tool that scans any generated report and outputs:
A list of uncited claims
Potentially outdated references (by publication date)
Ambiguous language (“may”, “should consider”) that needs clarification
Produces a “Fix list” the user can apply.
Bilingual Side-by-Side Renderer

Optional mode: generates a parallel bilingual view (EN + 繁中) while preserving headings and table alignment.
Ensures the chosen output language remains the official downloadable artifact; the other language is a view/export option.
All three features must allow prompt and model selection (subject to admin control).

13. Data Model & State (Session-Level)
13.1 Core session objects
settings: theme, UI language, painter style, default model, temperature, max_tokens
api_keys: per-provider key store (session only)
history: run logs (tab/workflow, agent, model, provider, timestamps, token estimates, durations)
pipelines: saved pipeline definitions (step list + prompts + model defaults)
guidance_workspace:
input_files[] (names, types, extracted text, page markers)
output_language
retrieval_results[] (sources, citations, excerpts)
report_stepA_md
report_stepB_md
skill_md
13.2 Artifact downloads
All downloads must exclude secrets and include metadata footer:

generated timestamp
model used
provider
output language
14. Agents.yaml Extensions (Specification)
The agent catalog must be extendable to include new agents such as:

guidance_analyze_research_agent (Step A)
template_report_agent (Step B)
skill_md_generator_agent (Step C)
grounding_inspector_agent
knowledge_graph_agent
Each agent entry should support:

default model
system prompt
suggested max tokens
input/output formatting constraints
15. Security, Compliance, and Auditability
15.1 Security
No API keys in outputs, logs, downloads
Uploaded files are processed transiently; storage behavior must be disclosed (HF Spaces ephemeral filesystem assumptions)
15.2 Auditability
Each generated report stores:
Source library (citations)
Retrieval timestamp
“Assumptions & unknowns” section
Optional: export run history as CSV/JSON.
16. Performance & Reliability Requirements
Progressive rendering for long outputs (streaming when provider supports it; otherwise show run spinner + partial status).
Large PDF handling:
page range selection
maximum pages/size guidance
Deterministic-ish mode:
temperature presets (0.0 / 0.2 / 0.7)
17. Acceptance Criteria (Condensed)
Users can switch Light/Dark, English/繁中, and 20 painter styles with Jackpot.
API key UX matches the “env-first, hide env key” rule.
Every LLM feature supports prompt + model selection and editable outputs.
Guidance workspace supports paste/upload (txt/md/pdf), output language selection, retrieval + grounded citations, and produces:
Step A: 2000–3000 word markdown research report
Step B: template-based report (user template or default)
Step C: downloadable skill.md in chosen language with 3 WOW behaviors
Adds 3 WOW AI features: Knowledge Graph, Grounding Inspector, Bilingual Renderer.
All original tabs/features remain operational.
Follow-up Questions (20)
For the FDA retrieval portion, do you want the system to rely on live web access, curated offline snapshots, or both with automatic fallback?
Which FDA source should be considered authoritative for 510(k) summaries in your workflow (official 510(k) database pages, openFDA endpoints, or internally curated exports)?
Do you want the retrieval layer to support user-provided URLs (paste a link list) as an additional connector mode?
What is your preferred citation style in reports: inline numeric [1], inline (Title, Year), footnotes, or an end-of-document bibliography?
Should the Grounding Inspector enforce a minimum citation density (e.g., “≥1 citation per paragraph”) or only for “major claims”?
For “international regulations,” which jurisdictions are mandatory in every report (EU, UK, Canada, Australia, Japan, China), and which should be conditional?
Should the system support IMDRF mapping as a default section, even when the uploaded guidance is very narrow (e.g., only sterilization)?
In the template-based report (Step B), do you need a checklist table exactly matching TFDA reviewer formats (columns/phrasing), or just similar structure?
Should the default template library include multiple templates by device type (orthopedics, SaMD, sterile devices), or only one default?
Do you want the checklist to output explicit test standards and acceptance criteria suggestions, or only list what evidence is expected?
For PDF ingestion, is page-accurate quoting required (short excerpts with page numbers), or is page-level citation sufficient?
For bilingual rendering, should the secondary language be machine-translated automatically or generated from scratch with domain style constraints?
Do you want the system to preserve a source excerpt cache (snippets) to improve traceability when external links change?
What maximum guidance size should be targeted (e.g., 50 pages, 300 pages), and should the system support multi-file bundles?
Should the Skill.md generator produce one skill per guidance, or should it generalize into a reusable “device guidance composer” skill?
What triggering contexts should the generated skill description emphasize most (e.g., “medical device guidance drafting,” “regulatory research synthesis,” “compliance checklist creation”)?
Do you want the Knowledge Graph to be purely visual, or also exportable (JSON/GraphML) for downstream use?
Should the Agent Studio support versioning of prompts/outputs (so users can roll back edits), or is latest-only sufficient?
Do you require role-based presets (e.g., “Reviewer mode” vs “Sponsor mode”) that change tone, strictness, and templates?
What is your preferred definition of “excellent” report quality: maximum completeness, maximum conservatism (flag uncertainties), or maximum brevity while grounded?
