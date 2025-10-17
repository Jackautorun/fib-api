import argparse, os, json, requests
API_URL="https://api.perplexity.ai/chat/completions"; MODEL="sonar-pro"
PROMPT_TMPL="""Goal: find the SINGLE best method to {topic}
Constraints: {constraints}
Deliverables:
1) ranked options (max 5) with pros/cons, risks, prerequisites
2) pick ONE winner with a step-by-step plan
3) cite ≥5 independent sources with permanent links/DOI
4) prefer recency < {recency} and official standards/guidelines
5) list failure modes, rollback, and cost/time estimates
Rules: no claim without citation; dedup near-duplicates; prefer meta-analyses, RCTs, specs, vendor docs; if evidence conflicts, explain and choose.
Search focus domains: {domains}
Output strictly in the following Markdown one-pager:

# Best Method: <name>
Decision: <Deploy | Pilot | Reject>

## Why this
- OEC impact: <number% + reason>
- Constraints fit: <time/budget/platform>
- Key risks + mitigations: <3 bullets>

## How to execute (Step-by-step)
1) ...
2) ...
3) ...
Quick-start D1: <5-item checklist>

## Alternatives compared (max 4)
- <alt> — Pros/Cons — Why not chosen

## Evidence (>=5)
1) <link/DOI> — finding
2) ...
Conflict notes: <if any>

## Guardrails & Costs
- Latency/Error/Fairness/Legal: <status + thresholds>
- Cost & Time: <numbers>
Owner: <name> | Review date: <yyyy-mm-dd>
"""
def call_pplx(api_key,prompt):
    h={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"}
    body={"model":MODEL,"messages":[
        {"role":"system","content":"You are a method-finder. Produce a single rigorous one-pager with verifiable citations."},
        {"role":"user","content":prompt}],
        "temperature":0.2,"top_p":0.9,"max_tokens":2000,"return_citations":True}
    r=requests.post(API_URL,headers=h,data=json.dumps(body),timeout=120); r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--topic",required=True); ap.add_argument("--constraints",required=True)
    ap.add_argument("--domains",default=""); ap.add_argument("--recency",default="365d")
    ap.add_argument("--max-sources",default="8"); ap.add_argument("--out",default="runs/best_method.md")
    args=ap.parse_args()
    api=os.getenv("PPLX_API_KEY");  assert api, "Missing PPLX_API_KEY"
    prompt=PROMPT_TMPL.format(topic=args.topic,constraints=args.constraints,domains=args.domains,recency=args.recency)
    md=call_pplx(api,prompt).strip()
    os.makedirs(os.path.dirname(args.out) or ".",exist_ok=True)
    with open(args.out,"w",encoding="utf-8") as f: f.write(md)
    print(f"Wrote {args.out}")
if __name__=="__main__": main()
