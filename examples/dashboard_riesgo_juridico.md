# Dashboard de Riesgo – Clientes Jurídicos
> Documento de referencia interno | Banco Bolivariano (BB)

---

## Contexto General

Este dashboard está orientado al análisis de **clientes jurídicos** dentro del proceso de otorgamiento y seguimiento de créditos. Centraliza información financiera, comportamiento de riesgo, evolución de **cartera**, garantías y transaccionalidad del cliente, permitiendo al equipo de riesgo tomar decisiones de crédito informadas y sustentadas en datos.
Dentro del mundo de clientes del dashboard se consideran tanto personas **jurídicas** como personas **naturales pertenecientes a un grupo económico**. Estas últimas se incorporan al análisis porque suelen mover volúmenes significativos de dinero (en el orden de millones) y, de omitirlas, se perdería información financiera relevante asociada al grupo empresarial.

El dashboard se estructura en tres páginas:

| Página | Nivel de análisis | Descripción |
|--------|-------------------|-------------|
| [**Empresa**](#empresa) | Código de cliente individual | Análisis detallado de cada empresa. |
| [**Grupo Económico**](#grupo) | Grupo económico completo | Consolida las métricas de todas las empresas del grupo. |
| [**Benchmarking**](#benchmarking) | Participación relativa | Compara a la empresa dentro de su grupo económico y de su actividad económica (CIIU 4). |

---

## Lista de Tablas Utilizadas

> Referencia rapida de todas las tablas consultadas en el dashboard, con su ubicacion y la seccion en la que se utilizan.

| Tabla | Servidor | Base de Datos | Sección(es) |
|-------|----------|---------------|-------------|
| `dwh_d_spd_balance` (spread) | dwhousebdsrv1 | DWBOLIVARIANO | 1, 5, 8 |
| `dw_riesgo_semanal` | dwhousebdsrv1 | DWBOLIVARIANO | 3 |
| `dwh_r_fastbi_inf_clie` | dwhousebdsrv1 | DWBOLIVARIANO | 3, 4, 5 |
| `CalificacionMIBB_<mesaño>` | DWANALISISR | DWANALISISR | 3 |
| `dwh_r_carril_cab_onepager` | dwhousebdsrv1 | DWREPORTES | 3 |
| `dwh_r_carril_proy_riesg` | dwhousebdsrv1 | DWREPORTES | 4 |
| `bb4_linea_credito` | CRM365BDSRV | BOLIVARIANO_365 | 4 |
| `bb1_producto_activo` | CRM365BDSRV | BOLIVARIANO_365 | 4 |
| `dw_captaciones` | dwhousebdsrv1 | DWBOLIVARIANO | 5 |
| `ah_his_movimiento` | dwhousebdsrv1 | ODSDB | 5 |
| `ah_cuenta` | dwhousebdsrv1 | ODSDB | 5 |
| `cc_his_movimiento` | dwhousebdsrv1 | ODSDB | 5 |
| `cc_ctacte` | dwhousebdsrv1 | ODSDB | 5 |
| `dwh_d_garantia_oper_ac` | dwhousebdsrv1 | DWBOLIVARIANO | 6 |
| `DW_PRODUCTOS` | DWHOUSEBDSRV | DWBOLIVARIANO | 6 |
| `DW_TIPO_OPERACION` | DWHOUSEBDSRV | DWBOLIVARIANO | 6 |
| `dw_estado_operacion` | DWHOUSEBDSRV | DWBOLIVARIANO | 6 |
| `cu_poliza` | dwhousebdsrv1 | ODSDB | 6 |
| `dw_detalle_ordenes_sat` | dwhousebdsrv1 | DWBOLIVARIANO | 7 |
| `dwh_r_rentabilidad` | dwhousebdsrv1 | DWREPORTES | 10 |

---

## Contenido del Dashboard

<a id="empresa"></a>

### Página: Empresa

Todo el contenido de esta página está analizado a nivel de **empresa individual** (código de cliente).

<a id="s1"></a>

#### 1. Cifras Financieras

#### Fuente de Información – Tabla `spread`

La información financiera proviene de una tabla llamada **`spread`**, que contiene los **balances financieros anuales** de las empresas. Existen cinco tipos de balance, priorizados según su nivel de confianza y calidad de información:

| Prioridad | Tipo de Balance           | Descripción |
|-----------|---------------------------|-------------|
| 1 (mayor) | Auditado Estructurado     | Máxima confianza. Balance auditado con estructura formal estandarizada. |
| 2         | Auditado                  | Balance con revisión de auditoría externa. |
| 3         | Fiscal                    | Balance declarado ante autoridades tributarias. |
| 4         | Interno                   | Balance generado por la propia empresa, sin auditoría externa. |
| 5 (menor) | Bases Externas            | Información proveniente de fuentes externas. Menor confiabilidad. |

> La priorización responde a que los balances auditados ofrecen mayor precisión y confianza sobre sus datos.

---

#### Visualizaciones de Cifras Financieras

##### Ventas
Monto total de ingresos por ventas de la empresa en el año fiscal analizado.

##### Fondos Disponibles
Liquidez inmediata con la que cuenta la empresa.

##### Ratio Pasivos / Patrimonio
- **Pasivos**: Obligaciones y deudas totales de la empresa.
- **Patrimonio**: Valor neto de la empresa (activos menos pasivos).
- **Ratio**: Mide el nivel de **apalancamiento** de la empresa. Un ratio alto indica que la empresa financia gran parte de sus operaciones con deuda. Pero esto no es netamente malo, a menos que su patrimonio decrezca y el ratio aumente con el paso del tiempo.

> **⚠️ Nota:** El banco tiene como norma no prestar más del 200% del patrimonio de la empresa.

##### Ratio Deuda vs. EBITDA
- **Ratio Deuda / EBITDA**: Mide la **solvencia** de la empresa, es decir, cuántos años de generación de caja operativa necesitaría para pagar su deuda total.
- Un ratio bajo indica mayor capacidad de pago; un ratio alto indica mayor presión sobre la empresa y menos solvencia.

El calculo de la deuda total (deuda balance) considera los siguientes 3 campos del spred:

| Concepto                         | Descripción                                                                                 |
|----------------------------------|---------------------------------------------------------------------------------------------|
| sd_DocxPagIntFin                 | Total de la deuda a Corto Plazo                                                             |
| sd_PorcCorrDeudLP                | Total de la deuda a Largo Plazo que vence en el corto plazo, o sea en este mismo año fiscal |
| sd_DocxPagInsFinBco              | Total de la deuda Largo Plazo que no vence en este mismo año fiscal                         |

Aqui no se discrimina entre deuda con el Sistema Bancario y deuda con el Mercado Financiero (emisión de bonos).

> **¿Qué es el EBITDA?**
> EBITDA son las siglas en inglés de *Earnings Before Interest, Taxes, Depreciation and Amortization*, o en español: **Ganancias antes de intereses, impuestos, depreciaciones y amortizaciones**. Es una métrica que refleja cuánto dinero genera una empresa únicamente con su operación principal, sin contar los efectos de su estructura financiera ni de la contabilidad. Es muy útil para comparar la rentabilidad operativa entre empresas, independientemente de su nivel de deuda o del país donde operan.

##### Estructura de Fondeo
Muestra cómo se financia la empresa: qué proporción proviene de deuda, y qué proporción viene de patrimonio propio.

##### Calificación Ponderada
Métrica interna del equipo de riesgo. **Su definición pertenece únicamente al equipo de riesgo** y aún no ha sido compartida formalmente con el equipo de analítica avanzada. Requiere alineación para poder interpretarla correctamente desde analítica. (Posiblemente en un futuro)

##### Score PD *(Probability of Default)*
Modelo estadístico de **regresión logística** que utiliza las cifras financieras del cliente para estimar su **probabilidad de incumplimiento** y obtener un **score crediticio**.

---

<a id="s2"></a>

#### 2. Central de Riesgo y Mercado de Valores

##### Historial de Malas Calificaciones
Visualización histórica que muestra, **por año**, si el cliente ha tenido calificaciones negativas en el sistema financiero y con qué entidades bancarias. Un caso crítico sería que en el año actual el cliente tenga malas calificaciones simultáneas con múltiples bancos. Un valor aceptable es que el cliente tenga calificación BBB o superior.

##### Gráfico Sankey (Diagrama de Cinta) – Share of Wallet
Visualización de tipo **Sankey** que comunica los **montos de crédito** que el cliente mantiene con cada institución del sistema financiero, incluyendo Banco Bolivariano. Permite identificar:
- El monto total de riesgo del cliente en el sistema financiero.
- El **porcentaje de participación de BB** sobre el total de créditos del cliente (**Share of Wallet / SOW**).

> El **Share of Wallet (SOW)** es la cartera compartida: qué fracción del total de deuda del cliente corresponde a nuestra institución frente a la competencia.

##### Emisiones en el Mercado de Valores
Visualización que muestra las **emisiones vigentes del cliente** en el mercado de valores, analizadas de forma anual. Se dividen en dos categorías:

| Tipo | Plazo | Descripción |
|------|-------|-------------|
| **Obligaciones** | Largo plazo (> 1 año) | Instrumentos de deuda con vencimiento superior a un año. |
| **Papel Comercial** | Corto plazo (≤ 1 año) | Instrumentos de deuda con vencimiento de hasta un año. |

> **Sobre las emisiones**: Las empresas pueden endeudarse a través de dos vías: bancos y mercado de valores (bonos). Las emisiones que se analizan son **bonos corporativos**, mediante los cuales las empresas recaudan capital vendiendo bonos a inversores, prometiendo reembolsar el principal más intereses periódicos. Ventaja: tasa más baja que un préstamo bancario. Desventaja: proceso más tardío. La **deuda total** de la empresa debe incluir tanto la deuda bancaria como la adquirida en el mercado de valores.

> **Fuente de datos – Emisiones**: No existe una tabla consolidada para esta información. Los datos provienen de la sección **"Gestión de Créditos" › Riesgos › Carga Inf. Mercado Valores** en Cobis. Los campos del `spread` no discriminan entre deuda bancaria y deuda emitida en el mercado de valores. Para disponer de esa discriminación se requiere validar las tablas de Cobis y conocer lo siguiente para evaluar la viabilidad de su uso:
        1. ¿Esta tabla ya existe en algún servidor ON-PREMISE?
        2. ¿Se define como tabla externa?
        3. La carga es mensual, ¿pero existe la probabilidad de que no nos llegue información por un mes o más?
        4. ¿Cuánta historia tenemos de esta data?

---

<a id="s3"></a>

#### 3. Evolución de Riesgo BB

##### Evolución de Cartera y Contingentes
Gráfico de barras **apiladas (stacked)** que muestra la evolución temporal de dos tipos de crédito:

- **Créditos de Cartera**: Créditos tradicionales otorgados al cliente.
- **Créditos Contingentes**: Productos utilizados principalmente en **comercio exterior** que funcionan como facilitadores de transacciones.

###### ¿Qué son los Créditos Contingentes?
Un crédito contingente actúa como **garantía de una transacción comercial** cuando el cliente no dispone de fondos suficientes en su cuenta corriente para completar el pago. 

**Ejemplo práctico:**
- La empresa A (cliente de BB) debe pagar USD 2.000.000 a la empresa B.
- La empresa A solo tiene USD 1.500.000 disponibles en cuenta.
- Sin un contingente, la transacción rebotaría, generando pérdida de confianza comercial y retrasos.
- Con el contingente, BB **garantiza la transacción completa**. La diferencia (USD 500.000) la debe de pagar la empresa A al banco en los proximos 90 días.
- Si el contingente no se paga, se convierte automáticamente en un **crédito de cartera** con monto vencido que el cliente A debe pagar al banco.

En síntesis: el contingente evita la caída de la transacción y protege la relación comercial del cliente.

###### Fuente de Datos

Tabla: `dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_riesgo_semanal`. El campo `cod_producto` diferencia los tipos: `7` = cartera, `9` = contingente.

```sql
select
    A.fecha_proceso,
    A.cod_cliente,
    A.cod_producto, --7 cartera, 9 contingente
    SUM(A.monto_total) AS monto,
    SUM(A.monto_castigado) AS monto_castigado
from dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_riesgo_semanal A
inner join dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_r_fastbi_inf_clie B
    on B.cod_cliente = A.cod_cliente
where
    (
        (
            B.tipo_persona = 'JURIDICA'
            AND len(B.num_cedula_ruc) = 13
        ) OR (
            B.tipo_persona = 'NATURAL'
            AND B.des_nombre_grupo_econ <> 'SIN GRUPO ECONOMICO'
        )
    )
    AND A.fecha_proceso in (
        select top 1 fecha_proceso from dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_riesgo_semanal
    )
group by A.fecha_proceso,A.cod_cliente,A.cod_producto
```

> **Nota:** La definición de crédito de cartera aquí usa `cod_producto = 7`, en lugar de usar `cod_producto_contable = 7`. Esto es porque le interesa analizar su sense real de la composición del riesgo del cliente.

##### Evolutivo de Calificación y Morosidad
Muestra la evolución del **score y nivel de morosidad** del cliente a lo largo del tiempo, desglosado por mes y año (ejemplo: todos los meses de 2021, 2022, etc.).

###### Score de Morosidad BB (MIBB)

Score calculado internamente por el equipo de riesgo (distinto a la **Calificación Ponderada** descrita en la [Sección 1](#s1) y al score de la tabla `fastbi`). Mide el comportamiento de mora intra-mes dependiendo de los días vencidos de cada operación, ponderado por el monto de las operaciones activas del mes. **MIBB** = Morosidad Interna Banco Bolivariano.

- **Fuente real (origen):** `DWANALISISR.dbo.CalificacionMIBB_<mesaño>` — una tabla por mes (ej: `CalificacionMIBB_Abr22` contiene los scores de abril 2022).
- **Nota:** La tabla `dwhousebdsrv1.DWREPORTES.dbo.dwh_r_carril_cab_onepager` (campo `co_calif_score_morosidad`) solo contiene el dato del mes actual, por lo que no sirve para construir histórico. Para desarrollar features basadas en este score se deberá solicitar la **consolidación de las tablas `CalificacionMIBB` en una sola tabla histórica**.

---

<a id="s4"></a>

#### 4. Proyección de Riesgo BB y Evolutivo de Saldos de Depósito

Esta sección proyecta a **futuro** el comportamiento del saldo de riesgo del cliente, asumiendo que paga puntualmente sus obligaciones. El objetivo es estimar:

- **Cuánto monto de riesgo** tendrá el cliente en los meses venideros.
- Si ese monto permitiría incorporar **nueva deuda** sin comprometer su capacidad de pago.
- La **solvencia proyectada** del cliente para los próximos períodos.
- Horizonte de proyección: **hasta 1 año al futuro**.

###### Fuente de Datos – Proyección de Riesgo

```sql
SELECT 
    pr_fecha_proceso
    ,pr_cliente
    ,pr_tipo
    ,pr_estado
    ,pr_des_mes
    ,pr_valor_proyeccion
FROM DWREPORTES.dbo.dwh_r_carril_proy_riesg
```

##### LC – Líneas de Crédito

Las empresas pueden tener una o más **líneas de crédito** asignadas (no hacen referencia a la cuenta de credito de las tarjetas de crédito). Se analiza el cupo libre disponible en cada línea. No es posible sobregirarse en una línea de crédito, pero sí se pueden hacer operaciones **fuera de línea** para atender la necesidad del cliente.

El indicador LC se deriva del campo `pr_estado` y clasifica cada operación en:

| Indicador | Significado |
|-----------|-------------|
| **BAJO LC** | La operación está dentro del cupo asignado de la línea de crédito. |
| **FUERA DE LC** | Operación de crédito normal que no afecta ni consume el cupo disponible de la LC. No es común seguir otorgando créditos bajo línea una vez que el cliente ya tiene deuda fuera de línea. Cuando el saldo de riesgo vuelve a ser ≤ al cupo disponible, la operación se reclasifica como "bajo de línea". |

```python
# Construcción del indicador
def indicador_lc(x):
    if x == "N         ":
        return "FUERA DE LC"
    else:
        return "BAJO LC"

df_proy_riesgo_ult_corte['indicador_lc'] = df_proy_riesgo_ult_corte['pr_estado'].apply(indicador_lc)
```

**Fuente – Líneas de Crédito:**
```sql
select
    bb4_codigo_mis,
    bb4_numero,
    bb4_monto_aprobado,
    bb4_monto_utilizado,
    bb4_monto_disponible,
    bb4_fecha_vencimiento
from CRM365BDSRV.BOLIVARIANO_365.dbo.bb4_linea_credito
where bb4_estado = 'VIGENTE'
```

##### TC – Tarjetas de Crédito

Se analiza únicamente el **cupo autorizado** de las tarjetas de crédito del cliente.

**Fuente – Cupo TC:**
```sql
select
    bb4_codigo_mis,
    bb1_product_idname,
    bb1_cupo_autorizado_base,
    bb1_cupo_utilizado_base
from CRM365BDSRV.BOLIVARIANO_365.dbo.bb1_producto_activo A
inner join dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_r_fastbi_inf_clie B
    on  A.bb4_codigo_mis = B.cod_cliente
where
    (bb1_product_idname like '%BK%' OR bb1_product_idname like '%UNION PAY%')
    and B.tipo_persona = 'JURIDICA'
    and bb1_estado_operacion = 'Normal'
    and bb1_product_idname not like '%PREPAGO%'
```

---

<a id="s5"></a>

#### 5. Saldos de Cuentas BB

Analiza el comportamiento de las cuentas del cliente en Banco Bolivariano:

- **Promedio de acreditaciones (ingresos)** en cuentas de ahorro y corrientes.
- **Saldos en CDPs** (Certificados de Depósito a Plazo).

El dato de **ventas anuales** del cliente proviene de la tabla `spread`.

##### Fuentes de Datos

**Evolución de depósitos** – `dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_captaciones` (`cod_producto`: 1 = Cta Cte, 2 = Cta Aho, 5 = CDP):

```sql
SELECT
    A.fecha_proceso,
    A.cod_cliente,
    A.cod_producto, -- 1 = Cta Cte, 2 = Cta Aho y 5 = CDP
    SUM(monto_saldo_total_dolares) AS monto_total,
    SUM(monto_saldo_prom_total_dolares) AS monto_prom
FROM dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_captaciones A
inner join dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_r_fastbi_inf_clie B on B.cod_cliente = A.cod_cliente
WHERE
    (
        (B.tipo_persona = 'JURIDICA' AND len(B.num_cedula_ruc) = 13)
        OR (B.tipo_persona = 'NATURAL' AND B.des_nombre_grupo_econ <> 'SIN GRUPO ECONOMICO')
    ) AND A.cod_fecha_proceso in (
        select max(cod_fecha_proceso) from dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_captaciones
    )
GROUP BY A.cod_cliente, A.fecha_proceso, A.cod_producto
```

**Acreditaciones en cuenta de ahorros** – `dwhousebdsrv1.ODSDB.dbo.ah_his_movimiento`:

```sql
SELECT
    YEAR(m.hm_fecha) AS year,
    MONTH(m.hm_fecha) AS month,
    d.ah_cliente AS cod_cliente,
    m.hm_correccion,
    m.hm_causa,
    SUM(m.monto_transaccion) AS monto
FROM dwhousebdsrv1.ODSDB.dbo.ah_his_movimiento AS m
LEFT JOIN dwhousebdsrv1.ODSDB.dbo.ah_cuenta AS d
    ON d.ah_cta_banco = m.hm_cta_banco
LEFT JOIN dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_r_fastbi_inf_clie c
    ON c.cod_cliente = d.ah_cliente
WHERE
    m.hm_fecha >= dateadd(month,-14,getdate()) -- solo los ultimos 14 meses
    AND m.hm_signo = 'C'
    AND c.tipo_persona = 'JURIDICA'
GROUP BY
    YEAR(m.hm_fecha),
    MONTH(m.hm_fecha),
    d.ah_cliente,
    m.hm_correccion,
    m.hm_causa
```

**Acreditaciones en cuenta corriente** – `dwhousebdsrv1.ODSDB.dbo.cc_his_movimiento`:

```sql
SELECT
    YEAR(m.hm_fecha) AS year,
    MONTH(m.hm_fecha) AS month,
    d.cc_cliente AS cod_cliente,
    m.hm_correccion,
    m.hm_causa,
    SUM(m.monto_transaccion) as monto
FROM dwhousebdsrv1.ODSDB.dbo.cc_his_movimiento AS m
LEFT JOIN dwhousebdsrv1.ODSDB.dbo.cc_ctacte AS d
    ON d.cc_cta_banco = m.hm_cta_banco
LEFT JOIN dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_r_fastbi_inf_clie c
    ON c.cod_cliente = d.cc_cliente
WHERE
    m.hm_fecha >= dateadd(month,-14,getdate()) -- solo los ultimos 14 meses
    AND m.hm_signo = 'C'
    AND c.tipo_persona = 'JURIDICA'
GROUP BY
    YEAR(m.hm_fecha),
    MONTH(m.hm_fecha),
    d.cc_cliente,
    m.hm_correccion,
    m.hm_causa
```

> **Limpieza de acreditaciones**: se excluyen desembolsos de cartera (`hm_causa = '80'`) y vencimientos de CDP (`hm_causa = '800'` y `hm_causa = '802'`).

##### ¿Para qué sirve este análisis?

###### 1. Detección de Sobregiros
Un saldo negativo es una señal de alerta sobre la salud financiera del cliente.

###### 2. Detección de Fuga del Cliente
Un decrecimiento sostenido en los montos de acreditación puede indicar que el cliente está trasladando su operación hacia otro banco.

###### 3. Validación de BB como Banco Principal
Si el cliente vende, por ejemplo, USD 1.500 millones al año, su **promedio mensual esperado de acreditaciones** debería ser aproximadamente **USD 125 millones**. Si las acreditaciones se aproximan a ese valor, BB es el banco principal donde el cliente maneja su dinero.

###### Metodología de comparación acreditaciones vs. ventas:
Se toma el promedio mensual de acreditaciones de los últimos **6 meses**, se multiplica por **12**, y el resultado se compara contra las ventas anuales del `spread`. Esa proporción representa cuánto del flujo total del cliente pasa por BB. No es un factor excluyente para el otorgamiento del crédito, pero un cliente que maneja más dinero con nosotros se considera menos riesgoso. El análisis de la brecha entre ventas y acreditaciones se realiza solo para el mes actual; no se evalúa su evolución temporal.

**Interpretación de ventas vs acreditaciones:**
- **Si las acreditaciones son mayores a lo esperado:**
Puede deberse a ventas de activos, aumento de patrimonio, levantamiento de inversión, etc. No es necesariamente negativo, pero amerita investigación.
- **Si las acreditaciones son menores a lo esperado:**
Es una señal de que el cliente **está llevando dinero a otro banco**.

###### Otros Indicadores de Relación con el Cliente

Métricas complementarias para evaluar la relación con BB (ninguna es factor excluyente por sí sola):

| Indicador | Valor Esperado (baseline) | Interpretación |
|-----------|--------------------------|----------------|
| **Reciprocidad** | ≥ 10% del monto prestado | El cliente debería mantener en saldo promedio al menos el 10% de lo que se le prestó. |
| **Share of Wallet (SOW)** | > 50% | BB aporta más de la mitad del crédito total del cliente → es el banco principal. |

> 💡Insight de Héctor: *el banco en el que el cliente tiene más deuda suele ser el banco donde más acreditaciones registra*. Por tanto, el SOW es un indicador que se correlaciona directamente con el nivel de acreditaciones.

---

<a id="s6"></a>

#### 6. Detalle de Garantías BB

Tabla que muestra las garantías que el cliente tiene registradas con Banco Bolivariano. Las columnas disponibles son:

| Columna | Descripción |
|---------|-------------|
| `tipo_garantia` | Clasificación del tipo de garantía (hipoteca, prenda, etc.). |
| `cod_interno` | Código interno de identificación de la garantía. |
| `monto_actual` | Monto vigente de la garantía (`ga_monto_garantia_act`). Puede variar con el tiempo por depreciación o modificaciones al bien, según el avaluó. |
| `estado` | Indica si la garantía está vigente o no. |
| `descripcion` | Descripción detallada del bien dado en garantía. |
| `fecha_inspeccion` | Fecha de la última inspección del bien. Por reglamento debe ser de máximo 1 a 2 años de antigüedad. |
| `fecha_vigencia_poliza` | Fecha de vencimiento de la póliza asociada a la garantía. No es determinante para el crédito, pero se verifica que esté vigente y al día en renovaciones. |
| `valor_endoso_poliza` | Valor por el que el bien está asegurado (puede ser menor al valor real del bien). Ej: una casa de USD 45.000 puede estar asegurada por USD 40.000. Fuente: `dwhousebdsrv1.ODSDB.dbo.cu_poliza`, campo `po_monto_endozo`. |

##### Tipos de Garantía

- Avales y Garantías de Instituciones Financieras
- Fideicomiso
- Hipotecaria
- Otras Garantías
- Prendaria
- Títulos y Valores

##### Estado y Vigencia de una Garantía

La vigencia depende del tipo de contrato:
- **Garantía cerrada**: su vigencia está determinada por la fecha de vencimiento de la operación a la que fue registrada.
- **Garantía abierta**: puede usarse en más de una operación, sin fecha de caducidad automática. Para pasar a estado cerrado, el dueño debe venir a retirarla.

##### ¿Para qué sirve el análisis de garantías?

El objetivo principal es calcular el ratio `monto_garantias_total / deuda_bb`, que representa el nivel de **cobertura** de la deuda. Las garantías del grupo económico cobran especial importancia porque pueden ser compartidas: si la empresa A incumple sus pagos, el banco puede ejecutar la garantía registrada a nombre de la empresa B, siempre que ambas pertenezcan al mismo grupo económico. Por lo que es necesario hacer un análisis de las garantías de la empresa y de su grupo económico.

###### Threshold de Cobertura

La cobertura ideal es del **140%**, calculada sobre la **deuda del cliente con BB** (cartera + contingentes). Clientes con cobertura inferior no son automáticamente rechazados: clientes con un perfil crediticio muy sólido pueden recibir crédito sin garantía hasta **USD 300.000** (para clientes normales), con posibilidad de excepciones.

###### Análisis por Tipo de Garantía (Abierta vs. Cerrada)

Es relevante analizar el monto de garantías segregado entre **abiertas** y **cerradas**, ya que su comportamiento difiere significativamente:

- Las garantías **cerradas** están atadas a una operación específica y vencen junto con ella. Esto significa que pueden desaparecer en el corto plazo si la operación asociada vence en los próximos meses.
- Las garantías **abiertas** pueden estar vinculadas a una, muchas o ninguna operación en particular y permanecen vigentes hasta que el cliente solicite su retiro, lo que les otorga mayor estabilidad como respaldo crediticio a futuro. (fuente: Documentación del Modelo de Garantías)

Por tanto, dos clientes con el mismo monto total de garantías pueden tener perfiles de cobertura muy distintos: uno respaldado mayoritariamente por garantías abiertas (mayor certeza de cobertura futura) y otro por garantías cerradas próximas a vencer (cobertura en riesgo). Este análisis se realiza por fuera del dashboard.

###### Identificador de Cliente en la Tabla de Garantías

La tabla contiene cuatro campos de código de cliente (`ga_cod_garante`, `ga_cod_propietario`, `ga_cod_principal`, `ga_cod_dueno_gar`). El que debe usarse como identificador **MIS** es **`ga_cod_principal`**, ya que no necesariamente el dueño de la garantía es quien la utiliza.

##### Fuente de Datos

Tabla principal: `dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_d_garantia_oper_ac`

```sql
select
    fecha_proceso,
    cod_cliente,      -- codigo cliente del dueño de la operacion
    cod_operacion,    -- codigo de la operacion a la que está sujeta la garantía
    ga_cod_principal, -- cod cliente de quien solicitó la operacion
    ga_cod_garantia,  -- identificador unico de la garantía
    ga_cod_externo,
    ga_cod_estado,
    ga_fecha_ingreso,
    ga_fecha_constitucion,
    ga_fecha_inspeccion,
    ga_fec_ven_ope, -- fecha de vencimiento de la garantía (abierta: sin fecha fija)
    ga_desc_sbs,          -- tipo de garantia (nivel alto)
    ga_cod_tipo_garantia, -- nemonico del tipo de garantia (más desagregado)
    ga_instruccion,
    ga_descripcion,
    p.des_producto, -- producto de la operacion
    eo.des_estado,
    des_grupo_tipo_oper, -- tipo de operacion
    des_tipo_operacion,  -- tipo de operacion más desagregado
    ga_monto_garantia_orig,
    ga_monto_garantia_act
FROM dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_d_garantia_oper_ac as g
INNER JOIN DWHOUSEBDSRV.DWBOLIVARIANO.DBO.DW_PRODUCTOS p with (nolock)
    ON g.id_producto = p.COD_PRODUCTO
INNER JOIN DWHOUSEBDSRV.DWBOLIVARIANO.DBO.DW_TIPO_OPERACION toper with (nolock)
    ON g.id_toperacion = toper.cod_tipo_operacion_id
LEFT JOIN DWHOUSEBDSRV.DWBOLIVARIANO.DBO.dw_estado_operacion eo with (nolock)
    ON g.ga_cod_estado_oper=eo.cod_estado and g.id_producto=eo.id_producto
where 
    cod_fecha_proceso = (select max(cod_fecha_proceso) from dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_d_garantia_oper_ac)
    and ga_monto_garantia_act >= 1
    and ga_cod_tipo_garantia <> 'CONMU'
    and ga_cod_estado in ('V','P')
    and ga_cod_tipo_garantia not in ('BINM','BINMFID','CERALM','COMFLET','CON','CONFAC','HIPOCE','PAG','POLSEGLEA','PRAGR')
```

**Fuente – Valor de endoso de póliza** (`dwhousebdsrv1.ODSDB.dbo.cu_poliza`):

```sql
WITH MaxDates AS (
    SELECT
        po_custodia,
        MAX(po_fvigencia_fin) AS MaxPurchaseDate
    FROM
        dwhousebdsrv1.ODSDB.dbo.cu_poliza
    GROUP BY
        po_custodia
),
MaxAmounts AS (
    SELECT
        p.po_custodia,
        p.po_fvigencia_fin,
        p.po_monto_endozo,
        ROW_NUMBER() OVER (PARTITION BY p.po_custodia ORDER BY p.po_monto_endozo DESC) AS rn
    FROM
        dwhousebdsrv1.ODSDB.dbo.cu_poliza p
    INNER JOIN
        MaxDates md
    ON
        p.po_custodia = md.po_custodia AND p.po_fvigencia_fin = md.MaxPurchaseDate
)
SELECT
    po_custodia,
    po_fvigencia_fin,
    po_monto_endozo
FROM
    MaxAmounts
WHERE
    rn = 1;
```

---

<a id="s7"></a>

#### 7. Transacciones SAT

**Fuente:** `dwhousebdsrv1.dwbolivariano.dbo.dw_detalle_ordenes_sat`

El análisis de transacciones se divide en dos perspectivas complementarias:

##### 7.1 Ordenantes (el cliente paga)
El cliente es quien origina el pago. Los servicios analizados son:

- Pago a proveedores
- Orden de pago
- Transacciones internacionales
- Impuestos aduaneros
- Pago de IESS
- Pago a terceros

Este análisis se usa principalmente para **estimar los ingresos del cliente**. Interesa el **monto total** movido (suma global de todos los servicios), no un análisis desagregado por servicio. A mayor volumen de movimientos, mayor es la **prioridad del cliente** para el banco.

> **Insight estratégico**: Si un cliente prioritario (con alto volumen de movimientos) busca crédito y BB no lo otorga, el cliente puede acudir a otro banco. Una vez que ese banco le da el crédito, el cliente tiende a migrar paulatinamente todos sus servicios hacia esa entidad. Por tanto, atender bien a los clientes prioritarios es clave para la retención.

##### 7.2 Beneficiarios (recepción de pagos - clientes y no clientes)

###### Si el cliente es un no-cliente de BB:
Se utiliza el análisis por beneficiario como **proxy de sus ingresos reales**. Al no tener cuentas en BB, no se dispone de información sobre sus acreditaciones, por lo que los pagos recibidos (e.g., como proveedor de clientes de BB) son una forma más fiel de estimar su capacidad de generar ingresos. Esta información es valiosa si el no-cliente solicita un crédito.

###### Si el cliente sí es cliente de BB:
Existe un producto llamado **PP Facturas** (crédito de cartera) pensado para relaciones comerciales circulares entre empresas:

- El **Cliente A** le paga regularmente al **Cliente B** (ambos clientes de BB).
- El Cliente B quiere comprar productos/servicios al Cliente A.
- BB puede otorgar a Cliente B un crédito **PP Facturas**, respaldado en los ingresos que recibe del Cliente A, para financiar esas compras.

> **Insight de Héctor**: Existe una **relación uno a uno** entre las acreditaciones en cuentas de ahorro/corrientes y el flujo como ordenante. Esto tiene sentido porque las acreditaciones representan los **ingresos** del cliente y los pagos como ordenante representan sus **egresos**.

<a id="s8"></a>

#### 8. Cifras Actividad Económica CIIU 4

> **CIIU 4** (*Clasificación Industrial Internacional Uniforme, Nivel 4*): estándar internacional para clasificar actividades económicas por sector productivo.

En esta sección se encuentra una tabla con el top de empresas con más ventas por la Actividad Económica a la que la empresa pertenece y su participación respecto al resto (en el año fiscal inmediato anterior - el más actual disponible). Información que se muestra:
- `ventas`: monto de ventas de la empresa en ese año fiscal
- `var. ventas`: % de variación de ventas respecto al año anterior
- `Ebitda`: Valor Ebitda de la empresa
- `ROE`: Retorno sobre el patrimonio (Return On Equity). Por definición el ROE se calcula como: utilidad_neta/patrimonio_promedio, donde el patrimonio_promedio_2024 = (patrimonio_2023 + patrimonio_2024)/2. (Queda por validar si Hector calcula el ROE usando el patrimonio actual o el patrimonio promedio)
- `Deuda/Ebitda`: Ratio que comunica en cuantos años ebitda termina de pagar su deuda actual. ¿Cuándo la deuda es muy alta?
  - `>=7`: es demasiado, malo.
  - `==6`: es preocupante.
  - ` <6`: es aceptable.
- `Calif.Cifras Pond`: Calificación de riesgo ponderada (métrica interna de riesgo, equivalente a la **Calificación Ponderada** descrita en la [Sección 1](#s1)) acorde a valores de Cifras Financieras (spread)

Además, se muestran los valores de estas columnas agrupados por la Actividad Económica CIIU 4. Esto nos da los valores por la industria en general: ventas, porcentaje de crecimiento de ventas, EBITDA, ROE y Deuda/EBITDA.

El valor de `var. ventas` del agrupado de todo el CIIU 4 sirve para comparar si una empresa ha aumentado su `var. ventas` debido al crecimiento de la industria o no. Aquí te dejo varias interpretaciones del `var. ventas`:

| `var. ventas` de Empresa | `var. ventas` de Industria | Conclusión |
|---------|-----------|------------|
| crece | crece | Puede ser que la empresa creció su nivel de ventas debido al crecimiento de la industria. |
| crece | decrece | Insight importante: a pesar de que a la industria le fue mal en ventas, a esta empresa le fue bien. |
| decrece | crece | Insight importante: a pesar de que a la industria le fue bien en ventas, a esta empresa le fue mal. |
| decrece | decrece | Puede ser que la empresa decreció su nivel de ventas debido al decrecimiento de la industria. |

---

<a id="s9"></a>

#### 9. Adquirencias

Muestra los ingresos generados por los **POS (Point of Sale)** de los comercios afiliados a Banco Bolivariano. Cubre los **últimos 24 meses** y permite evaluar el volumen de transaccionalidad del cliente como comercio afiliado, complementando el análisis de ingresos de la [Sección 7](#s7).

---

<a id="s10"></a>

#### 10. Rentabilidad

Analiza la rentabilidad que el cliente genera para el banco, desglosada por los siguientes productos y servicios:

| Producto / Servicio |
|---------------------|
| Activos |
| Contingentes |
| Pasivos |
| SAT |
| Otros Servicios |
| Cuentas de Orden |

Para cada uno se calculan los siguientes indicadores:

| Indicador | Descripción |
|-----------|-------------|
| **Rentabilidad total año anterior** | Rentabilidad acumulada durante el año fiscal anterior completo. |
| **Rentabilidad últimos 12 meses** | Rentabilidad acumulada en los 12 meses inmediatamente anteriores al corte actual. |
| **Rentabilidad YTD** | Rentabilidad acumulada desde el inicio del año fiscal actual hasta el mes de corte (*Year-to-Date*). |
| **Rentabilidad YTD año anterior** | Rentabilidad YTD del año anterior en el mismo período de comparación. |
| **Variación rentabilidad YTD** | Diferencia porcentual entre el YTD actual y el YTD del año anterior. |

##### Fuente de Datos

Tabla: `DWREPORTES.dbo.dwh_r_rentabilidad`

> Esta tabla es alimentada por el **equipo de Planificación Financiera**.

---

<a id="grupo"></a>

### Página: Grupo Económico

Esta página replica la mayoría de las secciones de la página Empresa, pero consolidando la información a nivel de **grupo económico**. El análisis a este nivel es fundamental porque:

- Una empresa puede tener indicadores individuales desfavorables, pero su grupo económico puede compensar con buenos saldos, garantías sólidas o bajo endeudamiento.
- Permite detectar casos de **contagio** de calificación de riesgo [(ver más abajo)](#contagio), donde una empresa aparenta tener mala calificación sin ser necesariamente mala pagadora.

#### Secciones incluidas

Las siguientes secciones funcionan de forma análoga a sus equivalentes en la página Empresa, con los datos consolidados a nivel de grupo:

1. [Cifras Financieras](#s1)
2. [Central de Riesgo y Mercado de Valores](#s2)
3. [Evolución de Riesgo BB](#s3)
4. [Proyección de Riesgo BB](#s4): Aquí no incluye a las personas naturales del grupo.
5. [Saldos de Cuentas BB](#s5): Aquí incluye gráficos adicionales de distribución.
6. [Detalle de Garantías BB](#s6)
7. [Transacciones SAT](#s7)
8. [Adquirencias](#s9) (últimos 24 meses)
9. [Rentabilidad](#s10)

#### Distribuciones adicionales en Saldos de Cuentas BB

En la página de Grupo Económico, la sección de saldos incorpora tres gráficos de distribución que muestran cómo se reparte el indicador entre las empresas del grupo:

| Gráfico de distribución | Descripción |
|-------------------------|-------------|
| **Saldos promedio anual** | Distribución de los saldos promedio de cada empresa del grupo durante el año. |
| **Saldos CDP actual** | Distribución de los saldos vigentes en Certificados de Depósito a Plazo. |
| **Acreditaciones últimos 6 meses** | Distribución de las acreditaciones promedio mensuales de cada empresa. |

#### Calificaciones de Riesgo a Nivel de Grupo

Las calificaciones de riesgo (calificación de riesgo, calificación ponderada y score de morosidad MIBB) **no se calculan de forma agrupada**. En las visualizaciones se muestran las calificaciones de cada empresa del grupo por separado, ya que actualmente no existe una metodología de consolidación.

**Posibles métricas de consolidación** (propuesta del equipo de Ingeniería de Datos, pendiente de validación):

| Métrica | Descripción |
|---------|-------------|
| **Mínima** | La mejor calificación dentro del grupo. |
| **Máxima** | La peor calificación dentro del grupo. |
| **Moda** | La calificación más frecuente entre las empresas. |
| **Calificación del mayor deudor** | La calificación de la empresa que concentra la mayor proporción de deuda del grupo. |

<a id="contagio"></a>

#### Contagio de Calificación de Riesgo

A nivel de grupo económico se produce un fenómeno llamado **contagio**: si una empresa que concentra **más del 20% de la deuda total del grupo** recibe una mala calificación de riesgo, **todas las empresas del grupo heredan esa calificación**.

Estas son las implicaciones:

- Una mala calificación en la vista individual de una empresa **no implica necesariamente que esa empresa sea mala pagadora**; puede tratarse de un contagio provocado por otra empresa de su grupo.
- Para determinar si la calificación es propia o heredada, se debe cruzar con el histórico de la empresa individual: si históricamente ha sido buena pagadora, es probable que su calificación negativa sea efecto del contagio.

---

<a id="benchmarking"></a>

### Página: Benchmarking

Esta página amplía el análisis posicionando a la empresa dentro de dos marcos de referencia comparativos: su **grupo económico** y su **actividad económica (CIIU 4)**. Permite evaluar el peso relativo y el desempeño de la empresa frente a sus pares.

#### Métricas de Benchmarking

Se calculan las siguientes métricas para cada uno de los dos ejes comparativos (grupo económico y actividad económica):

| Métrica | Descripción |
|---------|-------------|
| **% Participación en ventas** | Proporción de las ventas de la empresa respecto al total del grupo económico o de la actividad económica. |
| **Variación de Ventas** | Cambio porcentual en ventas de la empresa respecto al período anterior. |
| **CAGR3** | *Compound Annual Growth Rate* calculado sobre **3 años**. Expresa el crecimiento anual de ventas como si fuera un interés compuesto, suavizando la volatilidad interanual. |

> **Fórmula del CAGR:**
> $$\text{CAGR}_n = \left(\frac{\text{Ventas}_{\text{año final}}}{\text{Ventas}_{\text{año inicial}}}\right)^{\frac{1}{n}} - 1$$
> Donde $n = 3$ años.

#### Interpretación

- Un **% de participación alto** dentro del grupo económico indica que la empresa es la principal generadora de ingresos del conglomerado.
- Comparar la **variación de ventas** de la empresa contra la de su CIIU 4 permite identificar si el crecimiento o decrecimiento es propio o está impulsado por la industria (mismo análisis de la [Sección 8](#s8)).
- El **CAGR3** complementa la variación de ventas anual con una perspectiva de mediano plazo, filtrando picos o caídas atípicas de un solo año.

---

*Documento elaborado a partir de sesiones de levantamiento de información con el equipo de riesgo (Hector Vinueza Barroso).*
