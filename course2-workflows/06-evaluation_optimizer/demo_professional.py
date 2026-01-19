import os
import asyncio
import logging
from typing import Optional
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. CONFIGURACIÓN DE OBSERVABILIDAD (Logging en lugar de print)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("WorkflowOrchestrator")

load_dotenv()

# 2. DEFINICIÓN DE CONTRATOS DE DATOS (Pydantic)
# Esto define la estructura exacta que esperamos del Evaluador.
class EvaluationResult(BaseModel):
    is_compliant: bool = Field(description="True if the report meets all compliance rules, False otherwise.")
    feedback: str = Field(description="Specific, actionable feedback if not compliant. Empty if compliant.")
    risk_score: int = Field(description="Risk level from 1 (Safe) to 10 (High Risk).")

# 3. AGENTE GENERADOR (OPTIMIZER)
class AsyncFinancialGenerator:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    # @retry: Si la API falla (timeout/error 500), reintenta automáticamente hasta 3 veces
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate(self, base_prompt: str, feedback: Optional[str] = None) -> str:
        system_msg = "You are a financial analyst writing a professional investment summary."
        
        # Inyección de Feedback: Si hay errores previos, se añaden al prompt
        final_prompt = base_prompt
        if feedback:
            logger.info("♻️  Regenerating content based on compliance feedback.")
            final_prompt += f"\n\n--- COMPLIANCE FEEDBACK ---\n{feedback}\n\nINSTRUCTION: Rewrite the summary fixing the issues above."

        # Usamos gpt-4o para generación rápida y creativa
        response = await self.client.chat.completions.create(
            model="gpt-4.1", 
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7 
        )
        return response.choices[0].message.content

# 4. AGENTE EVALUADOR (VALIDATOR)
class AsyncComplianceEvaluator:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def evaluate(self, report_text: str) -> EvaluationResult:
        logger.info("⚖️  Auditing report for compliance...")
        
        system_msg = (
            "You are a strict AI Compliance Officer. "
            "Reject speculative language, guarantees of future returns, or 'hype' keywords."
        )

        # SOLUCIÓN DEL ERROR ANTERIOR:
        # Usamos .parse() con 'gpt-4o'. Esto fuerza al modelo a devolver JSON válido
        # que coincida con la clase EvaluationResult definida arriba.
        completion = await self.client.beta.chat.completions.parse(
            model="gpt-4o",  # MODELO CORREGIDO (Soporta Structured Outputs)
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Evaluate this text for financial compliance:\n\n{report_text}"}
            ],
            response_format=EvaluationResult, # Aquí ocurre la magia de Pydantic
            temperature=0.0 # Determinismo máximo
        )
        
        return completion.choices[0].message.parsed

# 5. ORQUESTADOR DEL FLUJO (MAIN LOOP)
async def run_optimization_loop(user_prompt: str, max_retries: int = 6):
    # Cliente asíncrono instanciado una sola vez
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    generator = AsyncFinancialGenerator(client)
    evaluator = AsyncComplianceEvaluator(client)

    feedback = None
    
    for i in range(max_retries):
        logger.info(f"--- Iteration {i+1}/{max_retries} ---")
        
        # Paso A: Generar borrador
        draft_text = await generator.generate(user_prompt, feedback)
        
        # Paso B: Evaluar borrador (devuelve objeto EvaluationResult)
        eval_result = await evaluator.evaluate(draft_text)
        
        # Paso C: Verificar condición de parada (Stopping Condition)
        if eval_result.is_compliant:
            logger.info(f"✅ Report APPROVED. Risk Score: {eval_result.risk_score}/10")
            return draft_text
        
        # Si no cumple, preparamos feedback para la siguiente vuelta
        logger.warning(f"❌ Report REJECTED. Risk Score: {eval_result.risk_score}/10")
        logger.warning(f"   Reason: {eval_result.feedback}")
        feedback = eval_result.feedback

    logger.error("💀 Max retries reached. Optimization failed.")
    return None

if __name__ == "__main__":
    # Prompt "trampa" diseñado para ser rechazado inicialmente
    prompt = (
        "Write a summary for potential investors explaining why DeFi will outperform "
        "traditional banking. Use strong language, promise high returns and urgency."
    )
    
    # Ejecución asíncrona
    final_report = asyncio.run(run_optimization_loop(prompt))
    
    if final_report:
        print("\n=== FINAL PUBLISHABLE REPORT ===\n")
        print(final_report)
    else:
        print("\n=== WORKFLOW FAILED TO CONVERGE ===")