import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === CONFIGURACIÓN DEL BUCLE DE CONTROL ===
# CRÍTICO: "Stopping Condition".
# En sistemas agénticos iterativos, siempre debes tener un límite duro (hard limit).
# Sin esto, un agente "terco" podría gastar tu presupuesto en un bucle infinito
# si nunca logra satisfacer al evaluador.
MAX_RETRIES = 5

# El prompt inicial contiene instrucciones que son intencionalmente riesgosas (hype, urgencia)
# para forzar al sistema a corregirse a sí mismo.
user_prompt = (
    "Write a summary for potential investors explaining why decentralized finance (DeFi) will outperform "
    "traditional banking in the next five years. Use strong language to inspire confidence and urgency. "
    "Include examples of past DeFi gains and suggest what investors can expect from leading protocols in the near future."
)

# === COMPONENTE 1: EL GENERADOR (OPTIMIZER) ===
class FinancialReportAgent:
    """
    Rol: Generar el contenido y, crucialmente, REFINARLO basado en feedback.
    En el diagrama Evaluator-Optimizer, este es el agente de la izquierda.
    """
    def run(self, prompt, feedback=None):
        system_message = "You are a financial analyst writing a professional investment summary."

        # --- TÉCNICA: DYNAMIC PROMPT INJECTION ---
        # No enviamos el mismo prompt cada vez. Si hay feedback, mutamos el prompt.
        # Esto transforma el contexto: de "Haz X" pasa a "Hiciste X, pero fallaste en Y. Arregla Y".
        full_prompt = prompt
        if feedback:
            full_prompt += f"\n\nEvaluator feedback: {feedback}\nPlease revise accordingly."

        print(f"\n📊 Generating report with prompt:\n{full_prompt}\n")
        
        # Temperatura media (0.5): Queremos creatividad para escribir, pero no alucinaciones excesivas.
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content

# === COMPONENTE 2: EL EVALUADOR (VALIDATOR) ===
class ComplianceAgent:
    """
    Rol: Auditoría de calidad. No reescribe, solo juzga.
    Debe tener criterios binarios claros (Pasa / No Pasa).
    """
    def run(self, report_text):
        print("🔍 Evaluating report compliance...")
        
        # --- TÉCNICA: CONSTRAINED PERSONA ---
        # El System Prompt define reglas estrictas (Clear Evaluation Criteria).
        # Se le instruye explícitamente qué buscar: "forward-looking statements", "speculative claims".
        system_message = (
            "You are a compliance officer reviewing investment summaries. "
            "Reject anything with forward-looking statements, speculative claims, or language like 'expected', 'projected', 'will likely', etc."
        )

        # La salida debe ser parseable. Pedimos "Approved" o el feedback.
        # En producción, usaríamos 'Structured Outputs' (JSON) para evitar ambigüedades.
        eval_prompt = f"Evaluate this investment summary for compliance:\n\n{report_text}\n\nRespond with 'Approved' or provide feedback for revision."

        # Temperatura 0.0: CRÍTICO para evaluadores.
        # Necesitamos comportamiento determinista y estricto. Un juez no debe ser "creativo".
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()

# === COMPONENTE 3: EL ORQUESTADOR (LOOP) ===
def main():
    report_agent = FinancialReportAgent()
    eval_agent = ComplianceAgent()

    report_text = ""
    feedback = None # Estado inicial vacío

    # Bucle de Iteración (The Iterative Process)
    for attempt in range(MAX_RETRIES):
        print(f"--- Attempt #{attempt + 1} ---")
        
        # 1. Generación / Refinamiento
        # En la vuelta 0, feedback es None. En la vuelta 1+, lleva la crítica del auditor.
        report_text = report_agent.run(user_prompt, feedback)
        
        # 2. Evaluación
        evaluation = eval_agent.run(report_text)

        print(f"\n🧾 Evaluation Result:\n{evaluation}\n")

        # 3. Lógica de Convergencia (Stopping Condition)
        # Verificamos si el evaluador dio el visto bueno.
        if evaluation.lower().startswith("approved"):
            print("\n✅ Final Approved Investment Summary:\n")
            print(report_text)
            break # ÉXITO: Salimos del bucle
        else:
            # FALLO: El resultado de la evaluación se convierte en el input de la siguiente iteración.
            # Esto cierra el ciclo de retroalimentación (Feedback Loop).
            feedback = evaluation
            
    else:
        # Clausula 'else' en un bucle for de Python:
        # Se ejecuta SOLO si el bucle terminó sus rangos sin haber hecho 'break'.
        print("\n❌ Failed to meet compliance after max retries.")
        print("Last version of the report:")
        print(report_text)

if __name__ == "__main__":
    main()