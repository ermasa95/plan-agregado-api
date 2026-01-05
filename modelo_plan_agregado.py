from pulp import LpProblem, LpMinimize, LpVariable, lpSum, PULP_CBC_CMD, LpStatus, value


def plan_agregado(data: dict) -> dict:
    # -------------------------
    # DATOS
    # -------------------------
    periodo = data["periodo"]
    demanda = data["demanda"]

    W0 = data["W0"]
    I0 = data["I0"]
    S0 = data.get("S0", 0)

    prod_normal = data["prod_normal"]
    prod_extra = data["prod_extra"]
    max_extra = data["max_extra"]

    c = data["costos"]

    inventario_final_min = data["inventario_final_min"]

    # -------------------------
    # MODELO
    # -------------------------
    model = LpProblem("Plan_Agregado_Red_Tomato", LpMinimize)

    # -------------------------
    # VARIABLES (idénticas al original)
    # -------------------------
    Wt = LpVariable.dicts("Wt", periodo, lowBound=0)              # CONTINUA
    Ht = LpVariable.dicts("Ht", periodo, lowBound=0, cat="Integer")
    Lt = LpVariable.dicts("Lt", periodo, lowBound=0, cat="Integer")

    Pt = LpVariable.dicts("Pt", periodo, lowBound=0)
    Ot = LpVariable.dicts("Ot", periodo, lowBound=0)
    Ct = LpVariable.dicts("Ct", periodo, lowBound=0)

    It = LpVariable.dicts("It", periodo, lowBound=0)
    St = LpVariable.dicts("St", periodo, lowBound=0)

    # -------------------------
    # FUNCIÓN OBJETIVO (idéntica)
    # -------------------------
    model += (
        lpSum(c["tiempo_regular"] * Wt[t] for t in periodo) +
        lpSum(c["tiempo_extra"] * Ot[t] for t in periodo) +
        lpSum(c["contratacion"] * Ht[t] for t in periodo) +
        lpSum(c["despido"] * Lt[t] for t in periodo) +
        lpSum(c["inventario"] * It[t] for t in periodo) +
        lpSum(c["faltante"] * St[t] for t in periodo) +
        lpSum(c["materiales"] * Pt[t] for t in periodo) +
        lpSum(c["subcontratacion"] * Ct[t] for t in periodo)
    )

    # -------------------------
    # RESTRICCIONES (idénticas)
    # -------------------------
    for i, t in enumerate(periodo):

        if i == 0:
            model += Wt[t] == W0 + Ht[t] - Lt[t]
            model += I0 + Pt[t] + Ct[t] == demanda[t] + S0 + It[t] - St[t]
        else:
            t_prev = periodo[i - 1]
            model += Wt[t] == Wt[t_prev] + Ht[t] - Lt[t]
            model += It[t_prev] + Pt[t] + Ct[t] == demanda[t] + St[t_prev] + It[t] - St[t]

        model += Pt[t] <= prod_normal * Wt[t] + prod_extra * Ot[t]
        model += Ot[t] <= max_extra * Wt[t]

    # Restricciones finales
    model += It[periodo[-1]] >= inventario_final_min
    model += St[periodo[-1]] == 0

    # -------------------------
    # RESOLVER
    # -------------------------
    model.solve(PULP_CBC_CMD(msg=0))

    # -------------------------
    # SALIDA API
    # -------------------------
    resultado = {
        "estado": LpStatus[model.status],
        "costo_total": value(model.objective),
        "detalle_por_periodo": {}
    }

    for t in periodo:
        resultado["detalle_por_periodo"][t] = {
            "W": Wt[t].value(),
            "H": Ht[t].value(),
            "L": Lt[t].value(),
            "P": Pt[t].value(),
            "OT": Ot[t].value(),
            "I": It[t].value(),
            "S": St[t].value(),
            "SUB": Ct[t].value()
        }

    return resultado
