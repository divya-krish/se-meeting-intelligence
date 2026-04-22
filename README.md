# SE Meeting Intelligence

**Turn a 47-minute discovery call transcript into a complete CRM package in under 30 seconds.**

Built by a Ex-Solutions Engineer, for Solutions Engineers. Uses Claude AI (Anthropic) to extract structured intelligence from raw call transcripts — no templates, no manual copy-paste, no forgotten action items.

🔗 **[Live Demo →](https://divya-krish.github.io/se-meeting-intelligence)**

---

## What It Does

Paste in a raw transcript. Get back:

| Output | Details |
|---|---|
| **Call Summary** | 2–3 sentence executive summary |
| **Customer Info** | Company, contacts, industry |
| **Technical Requirements** | Extracted pain points and requirements |
| **Cloudflare Products** | Relevant products matched to the deal |
| **Competitive Signals** | Competitors mentioned with context |
| **Action Items** | Structured table with owner (SE / AE / Customer) and due date |
| **Next Steps** | Agreed-upon next steps |
| **Deal Signals** | Stage, urgency, budget, decision date, decision makers |
| **CRM Note** | 150–200 word Salesforce-ready activity note, third person |
| **Follow-up Email** | Full draft with subject line, ready to review and send |

---

## The Business Case

| | Manual | With SE Meeting Intelligence |
|---|---|---|
| Time to complete CRM note | 30–45 min | < 30 seconds |
| Fields captured | Inconsistent | 8 structured fields, every call |
| Action items logged | Often missed | 100% captured |
| Competitive signals flagged | Depends on SE | Auto-detected |
| SE time saved per week (5 calls) | — | **~3.5 hours** |
| SE org of 20 (annualized) | — | **~3,640 hours recovered** |

---

## Quick Start

### Prerequisites
- Python 3.8+
- An [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
git clone https://github.com/dkrish/se-meeting-intelligence.git
cd se-meeting-intelligence
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run It

```bash
# Process a transcript file → prints markdown to terminal
python main.py sample_data/sample_transcript.txt

# Save output to a file
python main.py sample_data/sample_transcript.txt --output output/acme_notes.md

# Get raw JSON (for CRM API integrations)
python main.py sample_data/sample_transcript.txt --format json

# Pipe from clipboard or another tool
cat my_transcript.txt | python main.py
```

### Sample Output

Running against the included Acme Financial sample transcript produces:

```
🔄  Processing transcript with Claude...
✅  Done in 8.3s

# 📋 SE Meeting Intelligence Report
*Generated: April 21, 2026 at 9:14 AM*

---
⏱️ 45 minutes saved | 📊 8 fields extracted | ✅ 7 action items | ⚠️ 2 competitive signals detected
---

## 📝 Call Summary
Acme Financial Services discovery call focused on three critical security gaps: DDoS protection
failures (3 incidents in Q4), credential stuffing vulnerability (50K accounts compromised), and
client-side JavaScript risk. Customer has $2.8M board-approved budget, Zscaler renewal pressure
in August, and a June 1st decision deadline — creating strong conditions for a competitive
displacement.

...
```

---

## Architecture

```
transcript.txt
      │
      ▼
  main.py  ──── Claude API (claude-opus-4-5) ────▶  Structured JSON
      │
      ├── --format markdown  ──▶  Markdown report (default)
      └── --format json      ──▶  Raw JSON (CRM API ready)
```

**Single API call. No chunking, no multi-step pipelines.** The prompt is designed to extract all fields in one pass using Claude's long context window.

---

## File Structure

```
se-meeting-intelligence/
├── main.py                          # CLI entrypoint
├── requirements.txt                 # anthropic>=0.40.0
├── sample_data/
│   └── sample_transcript.txt        # 47-min Acme Financial discovery call
├── output/                          # Generated notes land here
├── docs/
│   └── index.html                   # GitHub Pages live demo
└── README.md
```

---

## Live Demo

The [GitHub Pages dashboard](https://dkrish.github.io/se-meeting-intelligence) shows the full output from the Acme Financial sample call — no API key required. It demonstrates:

- The complete structured output across 5 tabs (Summary, Actions, Technical, CRM Note, Email Draft)
- Before/After productivity impact (BUR improvement visualization)
- What a real SE team deployment would look like at scale

---

## Extending This

**Add more products:** Update `EXTRACTION_PROMPT` in `main.py` to bias toward your company's product portfolio.

**Slack integration:** Pipe JSON output to a Slack webhook to auto-post call summaries to your `#se-deals` channel.

**CRM write-back:** Use `--format json` and feed the output to Salesforce REST API to auto-create Activity records.

**Batch processing:** Loop over a directory of transcripts — the CLI supports stdin, so `cat *.txt | python main.py` works with minor shell scripting.

---

## Why Claude

Claude's 200K token context window handles full-length enterprise call transcripts (1–2 hours) without chunking. The structured JSON output is deterministic enough for downstream automation while remaining readable for human review.

---

*Built to demonstrate AI-powered compression of SE internal work time. The goal: every hour an SE spends on admin is an hour not spent with a customer.*
