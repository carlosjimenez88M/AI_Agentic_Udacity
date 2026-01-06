# 🔄 Feedback Loops con LLMs - Guía Completa

## 📚 ¿Qué es un Feedback Loop?

Un **Feedback Loop** (ciclo de retroalimentación) es un patrón donde:
1. El LLM genera algo (código, texto, etc.)
2. Evaluamos el resultado automáticamente (tests, validaciones)
3. Si no es correcto, le damos feedback específico al LLM
4. El LLM mejora su respuesta basándose en ese feedback
5. Repetimos hasta lograr el resultado deseado

---

## 🎯 Objetivo del Ejercicio

Crear una función `process_data()` que:
- Calcule **suma**, **promedio** o **mediana** de una lista
- Filtre valores no numéricos (strings, None, etc.)
- Maneje listas vacías retornando `None`
- Valide modos inválidos levantando `ValueError`

**Sin escribir el código nosotros mismos** - el LLM lo genera y mejora iterativamente.

---

## 🏗️ Arquitectura del Feedback Loop

```
┌─────────────────────────────────────────────────────────┐
│                   FEEDBACK LOOP CYCLE                    │
└─────────────────────────────────────────────────────────┘

1. DEFINIR TAREA          2. GENERAR CÓDIGO
   ┌──────────┐              ┌──────────┐
   │ Task     │──────────────>│   LLM    │
   │ + Tests  │              │ Generate │
   └──────────┘              └──────────┘
                                   │
                                   ▼
5. MEJORAR               3. EJECUTAR & PROBAR
   ┌──────────┐              ┌──────────┐
   │   LLM    │<──────────────│  Run     │
   │ Improve  │              │  Tests   │
   └──────────┘              └──────────┘
       ▲                           │
       │                           ▼
       │                    4. GENERAR FEEDBACK
       │                       ┌──────────┐
       └───────────────────────│ Format   │
           (si fallan tests)   │ Feedback │
                               └──────────┘
```

---

## 📝 Paso a Paso - Implementación Completa

### PASO 1: Definir la Tarea Claramente

```python
task_description = """
Create a Python function called `process_data` that:

1. Accept a list as first parameter and 'mode' parameter (default: 'average')
2. Support three modes: 'sum', 'average', 'median'
3. Filter out non-numeric values
4. Return None if list is empty
5. Raise ValueError if invalid mode

Examples:
- process_data([1, 2, 3, 4, 5], mode='average') → 3.0
- process_data([1, 2, 'a', 3], mode='sum') → 6
- process_data([], mode='sum') → None
"""
```

**💡 Lección**: Una descripción clara y específica es crucial para que el LLM entienda qué hacer.

---

### PASO 2: Definir Test Cases (TDD)

```python
test_cases = [
    # Tests básicos
    {"inputs": ([1, 2, 3, 4, 5], "sum"), "expected": 15},
    {"inputs": ([1, 2, 3, 4, 5], "average"), "expected": 3.0},

    # Edge cases
    {"inputs": ([], "sum"), "expected": None},
    {"inputs": ([1, 2, "a", 3], "sum"), "expected": 6},  # Filtra 'a'
    {"inputs": ([1, 3, 4], "median"), "expected": 3},

    # Error handling
    {"inputs": ([1, 2, 3], "invalid_mode"), "expected": ValueError},
]
```

**💡 Lección**: Los tests son tu "criterio de éxito" - definen cuándo el código es correcto.

---

### PASO 3: Generación Inicial

```python
initial_prompt = f"""
You are an expert Python developer.

{task_description}

Write only the function surrounded by ```python and ``` without explanations.
"""

# LLM genera primera versión
response = llm.generate(initial_prompt)
code = extract_code(response)

# Ejecutar tests
results = execute_code(code, test_cases)
# Resultado: Puede que pasen solo 4/12 tests inicialmente
```

**💡 Lección**: La primera versión rara vez es perfecta - está bien, ese es el punto del loop.

---

### PASO 4: Crear Feedback Estructurado

```python
def format_feedback(results):
    """
    Convierte resultados de tests en feedback legible para el LLM
    """
    feedback = []

    # Si hay error de ejecución
    if results["execution_error"]:
        feedback.append(f"ERROR: {results['execution_error']['error_type']}")
        feedback.append(f"Message: {results['execution_error']['error_message']}")
        return "\n".join(feedback)

    # Resumen
    feedback.append(f"Tests: {results['passed']} passed, {results['failed']} failed")

    # Detalles de tests fallidos
    if results["failed"] > 0:
        feedback.append("\nFailed Test Cases:")
        for test in results["test_results"]:
            if not test["passed"]:
                feedback.append(f"\nTest #{test['test_id']}:")
                feedback.append(f"  Inputs: {test['inputs']}")
                feedback.append(f"  Expected: {test['expected']}")
                feedback.append(f"  Actual: {test['actual']}")

    return "\n".join(feedback)
```

**Ejemplo de feedback generado:**
```
Test Results: 4 passed, 8 failed

Failed Test Cases:

Test #5:
  Inputs: ([], 'sum')
  Expected: None
  Actual: 0

Test #6:
  Inputs: ([1, 2, 'a', 3], 'sum')
  Expected: 6
  Error: unsupported operand type(s) for +: 'int' and 'str'
```

**💡 Lección**: Feedback específico y estructurado es clave - el LLM necesita saber exactamente qué falló.

---

### PASO 5: Loop de Mejora Iterativa

```python
iterations = []
current_code = initial_code
current_feedback = initial_feedback

# Máximo 3 iteraciones de mejora
for i in range(3):
    # Si todos pasan, terminar
    if all_tests_passed():
        print("✅ Success! All tests passed.")
        break

    # Crear prompt con feedback
    feedback_prompt = f"""
    You wrote this function:
    ```python
    {current_code}
    ```

    Test results:
    {current_feedback}

    Please improve the code to fix all issues.
    Write only the improved function.
    """

    # LLM mejora el código
    improved_code = llm.generate(feedback_prompt)

    # Ejecutar tests de nuevo
    results = execute_code(improved_code, test_cases)
    feedback = format_feedback(results)

    # Guardar iteración
    iterations.append({
        "iteration": i + 1,
        "code": improved_code,
        "passed": results["passed"],
        "failed": results["failed"]
    })

    # Actualizar para siguiente iteración
    current_code = improved_code
    current_feedback = feedback
```

**Progreso típico:**
- Iteración 0: 4/12 tests ✅ (implementación básica)
- Iteración 1: 8/12 tests ✅ (agrega median, filtra no-numéricos)
- Iteración 2: 11/12 tests ✅ (maneja listas vacías)
- Iteración 3: 12/12 tests ✅ (valida modo inválido)

**💡 Lección**: Cada iteración se enfoca en los tests que aún fallan, mejorando incrementalmente.

---

## 🔑 Conceptos Clave del Patrón

### 1. **Test-Driven Development (TDD)**
- Defines los tests ANTES de escribir el código
- Los tests son tu "norte" - el criterio objetivo de éxito

### 2. **Feedback Específico**
- No solo "está mal" → "Esto falló por esta razón específica"
- El LLM puede enfocarse en problemas concretos

### 3. **Mejora Iterativa**
- No esperas perfección en la primera iteración
- Cada ciclo mejora sobre el anterior

### 4. **Automatización**
- Todo el proceso puede correr sin intervención humana
- Puedes aplicarlo a múltiples tareas en paralelo

---

## 🎓 Cómo Replicar Este Patrón

### Template Genérico

```python
def feedback_loop(task_description, test_cases, max_iterations=5):
    """
    Template genérico para cualquier tarea con feedback loop
    """
    # 1. Generación inicial
    code = llm.generate(task_description)

    # 2. Loop de mejora
    for i in range(max_iterations):
        # 2a. Ejecutar y evaluar
        results = evaluate(code, test_cases)

        # 2b. Si cumple criterio de éxito, terminar
        if results["success"]:
            return code, results

        # 2c. Generar feedback estructurado
        feedback = format_feedback(results)

        # 2d. Pedir mejora al LLM
        code = llm.improve(code, feedback)

    return code, results
```

### Aplicaciones del Patrón

1. **Generación de Código**
   - Tests: Unit tests
   - Feedback: Test failures, errores de sintaxis

2. **Escritura de Documentación**
   - Tests: Criterios de calidad (claridad, completitud)
   - Feedback: Secciones faltantes, ambigüedades

3. **Traducción**
   - Tests: Fluency, accuracy checks
   - Feedback: Errores gramaticales, inconsistencias

4. **Análisis de Datos**
   - Tests: Validación de resultados esperados
   - Feedback: Discrepancias, errores de cálculo

---

## 📊 Ventajas vs. Desarrollo Tradicional

| Aspecto | Tradicional | Feedback Loop |
|---------|-------------|---------------|
| **Velocidad** | Horas/días | Minutos |
| **Iteraciones** | Manual, lenta | Automática, rápida |
| **Cobertura** | Variable | Sistemática (todos los tests) |
| **Escalabilidad** | 1 tarea a la vez | N tareas en paralelo |
| **Consistencia** | Varía por desarrollador | Consistente (basado en tests) |

---

## ⚠️ Limitaciones y Consideraciones

### Cuándo SÍ usar Feedback Loops:
✅ Tareas bien definidas con criterios claros de éxito
✅ Tests automáticos disponibles
✅ Problemas que requieren múltiples iteraciones
✅ Automatización de debugging

### Cuándo NO usar:
❌ Tareas creativas sin criterio objetivo
❌ Problemas que requieren contexto profundo del dominio
❌ Cuando el feedback no puede ser automatizado
❌ Tareas únicas que no justifican el setup

---

## 🚀 Ejercicios para Practicar

### Ejercicio 1: SQL Query Generator
Crea un feedback loop que genere queries SQL:
- Task: Generar query para obtener top 10 clientes por ventas
- Tests: Validar sintaxis, verificar resultado con datos de prueba
- Feedback: Errores de SQL, resultados incorrectos

### Ejercicio 2: API Response Parser
- Task: Parsear respuesta JSON de una API
- Tests: Validar campos extraídos, tipos de datos
- Feedback: Campos faltantes, errores de parsing

### Ejercicio 3: Regex Pattern Generator
- Task: Generar regex para validar emails
- Tests: Casos de emails válidos/inválidos
- Feedback: False positives, false negatives

---

## 📖 Recursos Adicionales

- **Test-Driven Development**: Libro "Test Driven Development" by Kent Beck
- **LLM Prompting**: OpenAI Prompt Engineering Guide
- **Code Execution**: Python `exec()` documentation (con precauciones de seguridad)

---

## ✅ Checklist para Tu Propio Feedback Loop

- [ ] Definir tarea claramente (task description)
- [ ] Crear test cases comprehensivos
- [ ] Implementar función de ejecución/evaluación
- [ ] Crear formato de feedback estructurado
- [ ] Implementar loop con condición de salida
- [ ] Agregar logging para análisis
- [ ] Validar con casos de prueba reales
- [ ] Documentar el proceso

---

## 🎯 Conclusión

Los **Feedback Loops** transforman la forma en que usamos LLMs:
- De generación "one-shot" → Refinamiento iterativo
- De outputs variables → Resultados consistentes
- De procesos manuales → Automatización completa

**El patrón es simple pero poderoso**: generar → evaluar → retroalimentar → mejorar → repetir.

¡Ahora tienes las herramientas para implementar este patrón en tus propios proyectos! 🚀
