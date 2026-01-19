import os
from openai import OpenAI
from dotenv import load_dotenv
import threading
import time

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"))

# Shared dict for thread-safe collection of agent outputs
agent_outputs = {}

# Example contract text (in a real application, this would be loaded from a file)
contract_text = """
CONSULTING AGREEMENT

This Consulting Agreement (the "Agreement") is made effective as of January 1, 2025 (the "Effective Date"), by and between ABC Corporation, a Delaware corporation ("Client"), and XYZ Consulting LLC, a California limited liability company ("Consultant").

1. SERVICES. Consultant shall provide Client with the following services: strategic business consulting, market analysis, and technology implementation advice (the "Services").

2. TERM. This Agreement shall commence on the Effective Date and shall continue for a period of 12 months, unless earlier terminated.

3. COMPENSATION. Client shall pay Consultant a fee of $10,000 per month for Services rendered. Payment shall be made within 30 days of receipt of Consultant's invoice.

4. CONFIDENTIALITY. Consultant acknowledges that during the engagement, Consultant may have access to confidential information. Consultant agrees to maintain the confidentiality of all such information.

5. INTELLECTUAL PROPERTY. All materials developed by Consultant shall be the property of Client. Consultant assigns all right, title, and interest in such materials to Client.

6. TERMINATION. Either party may terminate this Agreement with 30 days' written notice. Client shall pay Consultant for Services performed through the termination date.

7. GOVERNING LAW. This Agreement shall be governed by the laws of the State of Delaware.

8. LIMITATION OF LIABILITY. Consultant's liability shall be limited to the amount of fees paid by Client under this Agreement.

9. INDEMNIFICATION. Client shall indemnify Consultant against all claims arising from use of materials provided by Client.

10. ENTIRE AGREEMENT. This Agreement constitutes the entire understanding between the parties and supersedes all prior agreements.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
"""

# TODO: Implement these agent classes

class LegalTermsChecker:
    def run(self, contract_text):
        print(">> [Legal Agent] Started analysis...")
        # CoT Prompt: Estructura el pensamiento paso a paso
        system_prompt = (
            "You are a Senior Corporate Attorney specializing in contract law. "
            "Do not just list issues. Follow this Chain of Thought strategy:\n"
            "1. Scan the text for 'Red Flag' clauses (Indemnification, Liability Caps, Jurisdiction).\n"
            "2. Analyze the balance of power: Is it one-sided?\n"
            "3. Identify ambiguous terms that could lead to litigation.\n"
            "4. Output your findings as a structured list of 'Critical Legal Risks'."
        )
        user_prompt = f"Analyze the following contract text:\n\n{contract_text}"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        agent_outputs["legal"] = response.choices[0].message.content
        print("<< [Legal Agent] Finished.")

class ComplianceValidator:
    def run(self, contract_text):
        print(">> [Compliance Agent] Started analysis...")
        # CoT Prompt: Enfoque en marcos regulatorios
        system_prompt = (
            "You are a Global Compliance Officer. "
            "Follow this Chain of Thought to validate the contract:\n"
            "1. Identify data handling clauses (Privacy, Ownership).\n"
            "2. Cross-reference with major regulations (GDPR, CCPA, HIPAA).\n"
            "3. Detect specific non-compliance declarations or waivers.\n"
            "4. List 'Compliance Violations' that could result in fines."
        )
        user_prompt = f"Review compliance for:\n\n{contract_text}"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        agent_outputs["compliance"] = response.choices[0].message.content
        print("<< [Compliance Agent] Finished.")

class FinancialRiskAssessor:
    def run(self, contract_text):
        print(">> [Financial Agent] Started analysis...")
        # CoT Prompt: Enfoque cuantitativo
        system_prompt = (
            "You are a Chief Financial Officer (CFO). "
            "Follow this Chain of Thought to assess risk:\n"
            "1. Analyze payment terms (Net days, Late fees). Are they predatory?\n"
            "2. Evaluate liability caps. What is the maximum financial exposure?\n"
            "3. Assess ROI risks based on termination clauses.\n"
            "4. Summarize 'Financial Hazards' with potential monetary impact."
        )
        user_prompt = f"Assess financial risk for:\n\n{contract_text}"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        agent_outputs["financial"] = response.choices[0].message.content
        print("<< [Financial Agent] Finished.")

# --- 2. AGENTE DE SÍNTESIS (REDUCER) ---

class SummaryAgent:
    def run(self, contract_text, inputs):
        print("\n>> [Summary Agent] Synthesizing all findings...")
        
        # Recuperación segura con valores por defecto
        legal_findings = inputs.get("legal", "No legal analysis provided.")
        compliance_findings = inputs.get("compliance", "No compliance analysis provided.")
        financial_findings = inputs.get("financial", "No financial analysis provided.")
        
        system_prompt = (
            "You are the General Counsel of the corporation. "
            "You have received three expert reports. Your job is not to repeat them, but to synthesize a verdict. "
            "Follow this thinking process:\n"
            "1. Compare the findings: Are there contradictions?\n"
            "2. Prioritize: Which risks are 'Deal Breakers' vs 'Negotiable'?\n"
            "3. Formulate a final recommendation: Sign, Negotiate, or Walk Away.\n"
        )
        
        user_prompt = f"""
        Please synthesize the following analyses into an Executive Summary.
        
        --- ORIGINAL TEXT SNIPPET ---
        {contract_text[:300]}...
        
        --- LEGAL ANALYSIS ---
        {legal_findings}
        
        --- COMPLIANCE ANALYSIS ---
        {compliance_findings}
        
        --- FINANCIAL ANALYSIS ---
        {financial_findings}
        
        Output format:
        1. Executive Verdict (GO / NO-GO)
        2. Top 3 Critical Risks
        3. Recommended Actions
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

# --- 3. ORQUESTACIÓN PARALELA ---

def analyze_contract(contract_text):
    # 1. Instanciar Agentes
    legal_checker = LegalTermsChecker()
    compliance_validator = ComplianceValidator()
    financial_assessor = FinancialRiskAssessor()
    summary_creator = SummaryAgent()

    # 2. Definir Hilos (Parallelization)
    threads = [
        threading.Thread(target=legal_checker.run, args=(contract_text,)),
        threading.Thread(target=compliance_validator.run, args=(contract_text,)),
        threading.Thread(target=financial_assessor.run, args=(contract_text,))
    ]

    # 3. Fan-Out: Iniciar todos los hilos
    start_time = time.time()
    for t in threads:
        t.start()
    
    # 4. Wait: Esperar a que terminen (Join)
    for t in threads:
        t.join()
    
    parallel_time = time.time() - start_time
    print(f"\n[Performance] Parallel execution of 3 agents took: {parallel_time:.2f} seconds.")

    # 5. Fan-In: Generar resumen final
    final_report = summary_creator.run(contract_text, agent_outputs)
    
    return final_report

# --- BLOQUE PRINCIPAL ---

if __name__ == "__main__":
    final_analysis = analyze_contract(contract_text)
    print("\n=== FINAL CONTRACT ANALYSIS ===\n")
    print(final_analysis)