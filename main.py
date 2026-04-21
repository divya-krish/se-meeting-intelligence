#!/usr/bin/env python3
"""
SE Meeting Intelligence
Transforms raw call transcripts into structured CRM-ready notes using Claude API.

Usage:
    python main.py sample_data/sample_transcript.txt
    python main.py transcript.txt --output output/notes.md
    cat transcript.txt | python main.py
    python main.py transcript.txt --format json
"""

import anthropic
import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert Solutions Engineering assistant specializing in enterprise software sales at Cloudflare.

You analyze customer call transcripts and extract structured information for CRM documentation with high accuracy.

Always respond with valid JSON only — no markdown, no explanation, just the JSON object."""

EXTRACTION_PROMPT = """Analyze this customer call transcript and extract the following information.

Return ONLY a valid JSON object with this exact structure:

{{
  "call_summary": "2-3 sentence executive summary of the call and key outcomes",
  "customer_info": {{
    "company": "company name",
    "contacts": ["Name, Title", "Name, Title"],
    "industry": "industry vertical"
  }},
  "technical_requirements": [
    "specific technical requirement or pain point"
  ],
  "cloudflare_products_relevant": [
    "Cloudflare product or feature relevant to this deal"
  ],
  "competitive_signals": [
    "competitor product or vendor mentioned (include context)"
  ],
  "action_items": [
    {{
      "action": "specific action item",
      "owner": "SE or AE or Customer",
      "due": "timeline if mentioned, else TBD"
    }}
  ],
  "next_steps": [
    "agreed next step"
  ],
  "deal_signals": {{
    "stage": "Discovery or Qualification or Validation or Negotiation",
    "urgency": "High or Medium or Low",
    "urgency_reason": "why this urgency level",
    "budget": "budget information if mentioned",
    "decision_date": "decision timeline if mentioned",
    "decision_makers": ["Name, Title"]
  }},
  "crm_note": "Professional 150-200 word CRM activity note ready to paste into Salesforce. Use third person. Include key discussion points, customer pain points, competitive context, and agreed next steps.",
  "follow_up_email": "Professional follow-up email to the customer. Include subject line. Reference specific discussion points. Confirm action items and next steps.",
  "time_analysis": {{
    "estimated_manual_minutes": 45,
    "fields_extracted": 8,
    "action_items_found": 0,
    "competitive_signals_found": 0
  }}
}}

Count action_items_found and competitive_signals_found from the actual data you extract.

Transcript:
{transcript}"""


def process_transcript(transcript_text: str) -> dict:
    """Process a transcript using Claude API and return structured data."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT.format(transcript=transcript_text)
            }
        ]
    )

    response_text = message.content[0].text.strip()

    # Clean up response if wrapped in markdown code blocks
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    return json.loads(response_text)


def format_markdown(data: dict) -> str:
    """Format extracted data as clean markdown."""

    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    output = []

    output.append("# 📋 SE Meeting Intelligence Report")
    output.append(f"*Generated: {now}*")
    output.append("")

    # Time saved banner
    time_data = data.get("time_analysis", {})
    saved = time_data.get("estimated_manual_minutes", 45)
    fields = time_data.get("fields_extracted", 8)
    actions = time_data.get("action_items_found", 0)
    signals = time_data.get("competitive_signals_found", 0)

    output.append("---")
    output.append(f"⏱️ **{saved} minutes saved** &nbsp;|&nbsp; "
                  f"📊 {fields} fields extracted &nbsp;|&nbsp; "
                  f"✅ {actions} action items &nbsp;|&nbsp; "
                  f"⚠️ {signals} competitive signals detected")
    output.append("")
    output.append("---")
    output.append("")

    # Summary
    output.append("## 📝 Call Summary")
    output.append(data.get("call_summary", "N/A"))
    output.append("")

    # Customer Info
    output.append("## 🏢 Customer Information")
    customer = data.get("customer_info", {})
    output.append(f"| Field | Value |")
    output.append(f"|---|---|")
    output.append(f"| **Company** | {customer.get('company', 'N/A')} |")
    output.append(f"| **Industry** | {customer.get('industry', 'N/A')} |")
    contacts = customer.get("contacts", [])
    output.append(f"| **Contacts** | {', '.join(contacts)} |")
    output.append("")

    # Deal Signals
    output.append("## 🎯 Deal Signals")
    signals_data = data.get("deal_signals", {})
    urgency = signals_data.get("urgency", "Medium")
    urgency_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(urgency, "🟡")
    output.append(f"| Signal | Value |")
    output.append(f"|---|---|")
    output.append(f"| **Stage** | {signals_data.get('stage', 'N/A')} |")
    output.append(f"| **Urgency** | {urgency_emoji} {urgency} — {signals_data.get('urgency_reason', '')} |")
    output.append(f"| **Budget** | {signals_data.get('budget', 'N/A')} |")
    output.append(f"| **Decision Date** | {signals_data.get('decision_date', 'N/A')} |")
    dms = signals_data.get("decision_makers", [])
    output.append(f"| **Decision Makers** | {', '.join(dms)} |")
    output.append("")

    # Technical Requirements
    output.append("## ⚙️ Technical Requirements")
    for req in data.get("technical_requirements", []):
        output.append(f"- {req}")
    output.append("")

    # Cloudflare Products
    output.append("## 🟠 Cloudflare Products Relevant")
    for product in data.get("cloudflare_products_relevant", []):
        output.append(f"- {product}")
    output.append("")

    # Competitive Signals
    output.append("## ⚠️ Competitive Signals")
    comp_signals = data.get("competitive_signals", [])
    if comp_signals:
        for signal in comp_signals:
            output.append(f"- {signal}")
    else:
        output.append("- No competitive signals detected")
    output.append("")

    # Action Items
    output.append("## ✅ Action Items")
    output.append("| Owner | Action | Due |")
    output.append("|---|---|---|")
    for item in data.get("action_items", []):
        owner = item.get("owner", "TBD")
        action = item.get("action", "")
        due = item.get("due", "TBD")
        output.append(f"| **{owner}** | {action} | {due} |")
    output.append("")

    # Next Steps
    output.append("## 🔜 Next Steps")
    for step in data.get("next_steps", []):
        output.append(f"- {step}")
    output.append("")

    # CRM Note
    output.append("## 📊 CRM Note — Salesforce Ready")
    output.append("> *Copy and paste directly into Salesforce Activity*")
    output.append("")
    output.append("```")
    output.append(data.get("crm_note", ""))
    output.append("```")
    output.append("")

    # Follow-up Email
    output.append("## 📧 Follow-up Email Draft")
    output.append("> *Review and send from your email client*")
    output.append("")
    output.append("```")
    output.append(data.get("follow_up_email", ""))
    output.append("```")
    output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="SE Meeting Intelligence — Transform call transcripts into CRM-ready notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py sample_data/sample_transcript.txt
  python main.py transcript.txt --output output/notes.md
  python main.py transcript.txt --format json
  cat transcript.txt | python main.py
        """
    )
    parser.add_argument(
        "transcript",
        nargs="?",
        help="Path to transcript file (or pipe via stdin)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: prints to terminal)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    # Read transcript
    if args.transcript:
        transcript_path = Path(args.transcript)
        if not transcript_path.exists():
            print(f"❌ Error: File not found: {args.transcript}", file=sys.stderr)
            sys.exit(1)
        transcript_text = transcript_path.read_text()
    elif not sys.stdin.isatty():
        transcript_text = sys.stdin.read()
    else:
        print("❌ Error: Please provide a transcript file or pipe transcript via stdin", file=sys.stderr)
        print("\nExample: python main.py sample_data/sample_transcript.txt", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    print("", file=sys.stderr)
    print("🔄  Processing transcript with Claude...", file=sys.stderr)
    start_time = time.time()

    data = process_transcript(transcript_text)

    elapsed = time.time() - start_time
    print(f"✅  Done in {elapsed:.1f}s", file=sys.stderr)
    print("", file=sys.stderr)

    # Format output
    if args.format == "json":
        output = json.dumps(data, indent=2)
    else:
        output = format_markdown(data)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
        print(f"📄  Output saved to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
