from fastapi import FastAPI
from pydantic import BaseModel
from modelo_plan_agregado import plan_agregado

app = FastAPI(
    title="API Planificación Agregada",
    description="Modelo de planeación agregada basado en Chopra",
    version="1.0"
)

class PlanInput(BaseModel):
    periodo: list
    W0: int
    I0: int
    S0: int = 0
    prod_normal: float
    prod_extra: float
    max_extra: float
    demanda: dict
    costos: dict
    inventario_final_min: float

@app.post("/plan-agregado")
def ejecutar_plan(data: PlanInput):
    resultado = plan_agregado(data.dict())
    return resultado
