# Propuesta de Nuevas Features para la Feature Store

> **Objetivo:** Identificar información que el banco utiliza en la evaluación de riesgo crediticio de clientes jurídicos pero que **no está capturada** en las feature tables actuales del Feature Store, y proponer nuevas features que los científicos de datos del equipo de Analítica Avanzada podrían aprovechar en sus modelos.

---

## Resumen Ejecutivo

Se contrastaron las 10 secciones de análisis del Dashboard de Riesgo — Clientes Jurídicos contra las feature tables existentes del Feature Store. De las 12 áreas evaluadas (incluyendo consolidación a nivel de grupo y benchmarking), solo 3 tienen cobertura alta o completa. Las restantes presentan brechas que van desde la ausencia total de datos hasta la falta de métricas derivadas que el equipo de riesgo calcula manualmente.

Se proponen **10 iniciativas** que se agrupan en tres categorías:

| Categoría | Propuestas | Descripción |
|-----------|-----------|-------------|
| **Feature tables nuevas desde fuentes no ingestadas** | 7 propuestas ([P1](#p1), [P3](#p3), [P4a](#p4a)/[b](#p4b), [P5](#p5), [P6](#p6), [P8](#p8), [P9](#p9)) | Tablas fuente del análisis de riesgo que actualmente no alimentan el Feature Store: garantías, deuda financiera del spread, contingentes, score MIBB, líneas de crédito, rentabilidad y adquirencias |
| **Feature tables nuevas derivadas de datos existentes** | 2 propuestas ([P2](#p2), [P7](#p7)) | Nuevas tablas que no requieren ingestar fuentes adicionales sino agregar y cruzar información ya disponible: consolidación a nivel de grupo económico y benchmarking por actividad económica / grupo |
| **Columnas nuevas en feature tables existentes** | 1 propuesta ([P10](#p10)) | Ratios e indicadores construidos de múltiples fuentes se incorporan como columnas adicionales en `fs_cus_deposit_liabilities` y `fs_cus_credit_risk`: banco principal, fuga de cliente, reciprocidad, concentración de deuda y contagio del score |

> ❗Las Features por grupo económico dependen tanto de fuentes aún no ingestadas en nube como de fuentes que ya tenemos disponibles.

---

## Matriz de Cobertura

Estado de la Feature Store respecto al contenido descrito en la documentación del Dashboard de Riesgo.

| Sección del Dashboard | Fuente(s) del Dashboard | Feature Table(s) Existentes | Cobertura |
|---|---|---|---|
| 1. Cifras Financieras | `dwh_d_spd_balance` (spread interno) | `fs_cus_financial_statement` | 🟡 Parcial — Partidas contables base cubiertas; falta deuda financiera granular y comparativas con EBITDA |
| 2. Central de Riesgo y Mercado de Valores | `dw_riesgo_semanal`, tablas Cobis MV (fuente de las emisiones) | `fs_cus_credit_risk`, `fs_cus_credit_risk_holder` | 🟡 Parcial — Calificaciones y montos por banco cubiertos; la parte de emisiones en mercado de valores no existe en el Feature Store |
| 3. Evolución de Riesgo BB | `dw_riesgo_semanal`, `dw_recuperacion_cartera`, `CalificacionMIBB_*` | `fs_cus_credit_portfolio`, `fs_op_credit_portfolio`, `fs_op_credit_portfolio_payment` | 🔴 Baja — Las features existentes cubren cartera pero no contingentes ni score MIBB |
| 4. Proyección de Riesgo BB y Líneas de Crédito | `dwh_r_carril_proy_riesg`, `bb4_linea_credito`, `bb1_producto_activo` | — | 🔴 Ninguna — Las features analizan comportamiento pasado de créditos; no hay proyecciones a futuro ni líneas de crédito empresariales |
| 5. Saldos de Cuentas BB | `dw_captaciones`, `ah_his_movimiento`, `cc_his_movimiento`, `dwh_d_spd_balance` | `fs_cus_checking_account`, `fs_cus_savings_account`, `fs_cus_certificate_deposit`, `fs_cus_deposit_liabilities` | 🟡 Parcial — Saldos y acreditaciones por tipo de cuenta cubiertos con profundidad temporal; falta comparativa acreditaciones vs. ventas (indicador de banco principal / fuga de cliente) y visión consolidada de liquidez total del cliente (corriente + ahorro + CDP) |
| 6. Detalle de Garantías BB | `dwh_d_garantia_oper_ac`, `cu_poliza` | — | 🔴 Ninguna |
| 7. Transacciones SAT | `dw_detalle_ordenes_sat` | `fs_cus_company_sat`, `fs_cus_company_roll_sat`, etc. | 🟢 Alta |
| 8. Cifras Actividad Económica CIIU 4 | `dwh_d_spd_balance` (spread) | `fs_cus_demographic` (solo código CIIU) | 🔴 Baja — Solo existe el código CIIU como dato demográfico; no hay estadísticas agregadas por industria, rankings por ventas, ni comparativa de crecimiento empresa vs. actividad económica |
| 9. Adquirencias | Fuente no documentada | — | 🔴 Ninguna |
| 10. Rentabilidad | `dwh_r_rentabilidad` | — | 🔴 Ninguna |
| Consolidación a nivel de grupo económico | Todas las anteriores | — (no existe nivel grupo) | 🔴 Ninguna |
| Benchmarking por grupo económico y actividad económica | `dwh_d_spd_balance` (spread), `fs_cus_demographic` | — | 🔴 Ninguna |

---

## Propuestas Detalladas

<a id="p1"></a>

### Propuesta 1: `fs_cus_guarantee` — Garantías Crediticias

En la evaluación crediticia, las garantías respaldan las operaciones de crédito y determinan la cobertura del riesgo. El banco analiza las garantías desde múltiples ángulos: monto total, tipo de garantía (hipotecaria, prendaria, fideicomiso, títulos/valores), si la garantía es **abierta** (cubre múltiples operaciones sin vencimiento fijo, ofreciendo estabilidad) o **cerrada** (vinculada a una operación específica, con riesgo de vencimiento), vigencia de pólizas de seguro sobre los bienes, y recencia de inspecciones físicas.

**Actualmente no existe ninguna feature table que capture información de garantías.** Las fuentes de garantías no alimentan el Feature Store.

**Fuente:** `dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_d_garantia_oper_ac` + `ODSDB.dbo.cu_poliza`

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Monto total de garantías vigentes** del cliente.
- **Desglose abierta vs. cerrada:** Montos y cantidades de garantías abiertas vs. cerradas. Un porcentaje alto de garantías abiertas indica mayor estabilidad de cobertura futura.
- **Desglose por tipo de garantía:** Montos en garantías hipotecarias, prendarias, de títulos/valores, fideicomisos, etc. Refleja diversificación y calidad de la cobertura.
- **Valor de endoso de póliza de seguro:** Monto asegurado sobre el bien dado en garantía. Proviene de la tabla de pólizas.
- **Antigüedad de última inspección:** Días transcurridos desde la última inspección física del bien en garantía. El reglamento exige inspecciones periódicas (1 a 2 años según el tipo).
- **Indicador de póliza vencida:** Si la póliza de seguro sobre el bien está vencida.
- **Ratio de cobertura:** Monto total de garantías dividido entre la deuda total del cliente. El banco utiliza un threshold de 140% como nivel de cobertura adecuada. Este ratio se calcula bajo el total de deuda en BB y se puede desglozar por el tipo de garantía (abierta y cerrada).

**Prioridad: 🔴 Alta** — La cobertura por garantías es un factor central en la decisión de crédito y no existe en el Feature Store.

---

<a id="p2"></a>

### Propuesta 2: `fs_grp_economic_group` — Features a Nivel de Grupo Económico

Todo el Feature Store opera a nivel de **cliente individual**. Sin embargo, la evaluación crediticia de empresas incluye una dimensión fundamental: el **grupo económico** al que pertenecen. Múltiples empresas vinculadas societariamente comparten riesgos por garantías cruzadas, préstamos inter-compañías, y el efecto **contagio**: si una empresa grande del grupo entra en problemas, puede arrastrar al resto. El Dashboard de Riesgo dedica una página completa a la consolidación de métricas a nivel de grupo.

**No existen features a nivel de grupo económico.** La clave de agrupación existe en `fs_cus_demographic` (nombre del grupo económico), pero no se computan agregaciones.

**Granularidad propuesta:** grupo económico × mes

**Conceptos propuestos a nivel de grupo:**

- **Tamaño del grupo:** Cantidad de empresas del grupo que son clientes del banco.
- **Riesgo total consolidado, depósitos totales, garantías totales y ventas totales** del grupo.
- **Calificaciones de riesgo del grupo:** Peor calificación, mejor calificación, moda, y calificación de la empresa con mayor deuda (que el banco usa como propuesta de calificación consolidada).
- **Indicador de contagio:** Señala si alguna empresa que concentra más del 20% de la deuda del grupo tiene una calificación deficiente, activando el riesgo de contagio.
- **Magnitud del contagio:** Porcentaje de deuda concentrada en la empresa que origina el contagio.
- **Concentración intra-grupo (HHI):** Índices de concentración de depósitos y riesgo entre las empresas del grupo. Un grupo con riesgo muy concentrado en una sola empresa es más vulnerable.
- **Cobertura grupal:** Garantías totales del grupo respecto a deuda con BB del grupo (cartera + contingentes).
- **Rentabilidad total del grupo**.
- **Transaccionalidad SAT del grupo** (totales como ordenante y beneficiario).

> 💡Nota: la pertenencia a un grupo económico de forma histórica se puede sacar de la `dw_ente_his`.

> ⚠️ Las métricas relativas al rol individual de cada empresa dentro del grupo (participación en deuda/depósitos/ventas, indicadores de contagio) son conceptos a granularidad **cliente × mes/año** y no pueden incluirse en esta tabla sin romper su nivel de agregación. La participación en ventas y deuda del grupo se incorporan en la [**Propuesta 7**](#p7) (`fs_cus_company_benchmark`); la participación en depósitos y los indicadores de contagio —que requieren que esta tabla ya exista— se incorporan como métricas derivadas en la [**Propuesta 10**](#p10) (Features Cross-Table).

**Prioridad: 🔴 Alta** — El análisis de grupo económico es fundamental para la decisión crediticia por la lógica de contagio y solvencia grupal.

---

<a id="p3"></a>

### Propuesta 3: `fs_cus_spread` — Deuda Financiera Granular del Spread Interno

El banco evalúa la solvencia de sus clientes jurídicos mediante el **spread interno**, un consolidado de cifras financieras con una jerarquía de confiabilidad de 5 niveles: (1) Auditado Estructurado, (2) Auditado, (3) Fiscal, (4) Interno y (5) Bases Externas. La feature table `fs_cus_financial_statement` ya captura las partidas contables principales (ventas, pasivos, patrimonio, EBITDA, fondos disponibles), pero su fuente (`dwe_e_estad_financ_emp`) corresponde al nivel 5 — el de menor confiabilidad.

**La brecha principal no está en las partidas contables base** (que conceptualmente ya existen), **sino en la descomposición de deuda financiera específica.** El spread diferencia tres componentes de deuda que representan exclusivamente obligaciones con instituciones financieras y mercado de valores, excluyendo pasivos operativos (cuentas por pagar a proveedores, provisiones, etc.). Esta distinción no es posible con `fs_cus_financial_statement`, cuyos campos de pasivos corrientes y no corrientes incluyen todo tipo de pasivos sin diferenciar su naturaleza.

**Fuente:** `dwhousebdsrv1.DWBOLIVARIANO.dbo.dwh_d_spd_balance`

**Granularidad propuesta:** cliente empresa × año fiscal

**Conceptos propuestos:**

- **Deuda financiera a corto plazo:** Obligaciones financieras con vencimiento menor a un año (documentos por pagar a instituciones financieras). Diferente de "pasivos corrientes", que incluye cuentas por pagar a proveedores y otros pasivos operativos.
- **Porción corriente de deuda financiera a largo plazo:** Cuotas de deuda a largo plazo que vencen dentro del próximo año. Sin equivalente en `fs_cus_financial_statement`.
- **Deuda financiera a largo plazo:** Obligaciones con instituciones financieras a más de un año. Diferente de "pasivos no corrientes", que incluye provisiones, jubilaciones, etc.
- **Deuda financiera total:** Suma de los tres componentes anteriores. Este valor incluye tanto deuda a Sistema Bancario como a Mercado de Valores.
- **Ratio Deuda / EBITDA:** Indicador clave de solvencia. En la evaluación de riesgo del banco: ≥7 es considerado malo, 6 es preocupante, <6 es aceptable.

> **Nota sobre redundancia con `fs_cus_financial_statement`:** Los conceptos de ventas, pasivos totales, patrimonio, EBITDA y fondos disponibles ya existen en esa tabla. Adicionalmente, los ratios Pasivos/Patrimonio y ROE pueden derivarse de columnas ya existentes. Por tanto, esta propuesta **no duplica** esos conceptos.
>
> Se recomienda además evaluar la adición de ratios derivados (Pasivos/Patrimonio, ROE, variación interanual de ventas) **dentro de `fs_cus_financial_statement`**, ya que actualmente esa tabla solo contiene partidas brutas sin ningún ratio calculado.

**Prioridad: 🟠 Media-Alta** — El valor diferencial radica en la deuda financiera granular (para el ratio Deuda/EBITDA)

---

<a id="p4a"></a>

### Propuesta 4a: `fs_cus_contingent_credit` — Comportamiento de Dividendos de Créditos Contingentes (a nivel de cliente)

Los **créditos contingentes** (avales, garantías bancarias, cartas de crédito) son productos usados principalmente en comercio exterior: el banco actúa como garante de una transacción comercial cuando el cliente no tiene fondos suficientes en cuenta para completarla. Por ejemplo, si una empresa debe pagar USD 2M a un proveedor pero solo tiene USD 1.5M disponibles, BB garantiza la transacción completa y el cliente paga la diferencia al banco en un plazo acordado (típicamente 90 días). Si no paga, el contingente **se convierte automáticamente en un crédito de cartera** con monto vencido. Esto los diferencia de los créditos de cartera tradicionales: mientras estos son desembolsos directos de dinero, los contingentes son una exposición latente que solo se activa si el cliente incumple.

Esta feature table sería la **análoga a nivel de cliente de `fs_op_credit_portfolio`** (que captura el comportamiento de dividendos a nivel de operación para créditos de cartera), pero aplicado a créditos que nacen como contingentes. Al estar a nivel de cliente, consolida todas las operaciones contingentes del cliente por mes.

Actualmente `fs_cus_credit_portfolio` segmenta créditos por tipo (inmobiliario, educativo, productivo, etc.) pero **no distingue entre cartera y contingentes**, y las features a nivel de operación (`fs_op_credit_portfolio`) solo cubren cartera.

**Fuente:** `dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_riesgo_semanal` + `dwh_h_oper_activa_conced` + `dw_tipo_operacion`

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Montos por vencer agregados:** Suma de montos futuros por vencer de todas las operaciones contingentes del cliente.
- **Dividendos pendientes agregados:** Cantidad total de dividendos pendientes de pago del cliente en operaciones contingentes, y porcentaje respecto al total de dividendos de esas operaciones.
- **Evolución temporal de dividendos:** Lags, tasas de cambio (ROC) y medias móviles exponenciales (EMA) del porcentaje de monto a pagar, para detectar si la carga de dividendos futuros del cliente está creciendo o decreciendo.
- **Transición de tipo de producto:** Cantidad y monto de operaciones contingentes del cliente que se han transformado en créditos de cartera en el periodo, últimos 6 meses y últimos 12 meses. Incluye proporción de operaciones que transicionaron respecto al total de contingentes, y velocidad de transición (tiempo promedio/mediana entre originación como contingente y conversión a cartera).
- **Indicadores de concentración por tipo de contingente:** Indicadores por producto (binarios de tenencia), % de deuda por producto y el producto principal de los creditos contingentes.

**Prioridad: 🟠 Media-Alta** — Los créditos contingentes representan exposición no capturada en las features de cartera existentes. La transición contingente→cartera es una señal de deterioro relevante para modelos predictivos.

---

<a id="p4b"></a>

### Propuesta 4b: `fs_cus_contingent_credit_payment` — Comportamiento de Pagos de Créditos Contingentes (a nivel de cliente)

Esta feature table es el **análogo a nivel de cliente de `fs_op_credit_portfolio_payment`** (que captura el comportamiento de pagos a nivel de operación para créditos de cartera), pero aplicado a créditos que nacen como contingentes. Captura cómo el cliente está pagando sus obligaciones contingentes: cuánto paga de capital, intereses, mora, y cómo evolucionan estos pagos en el tiempo.

**Fuente:** `dwhousebdsrv1.DWBOLIVARIANO.dbo.dw_recuperacion_cartera` + `dw_tipo_operacion`

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Componentes de pago agregados:** Montos pagados por el cliente en sus operaciones contingentes, desglosados en capital vencido, capital normal, intereses, mora y otros pagos. Cada componente también como porcentaje del pago total, para entender la composición.
- **Evolución temporal de pagos:** Tasas de cambio (ROC) de cada componente a múltiples horizontes, estadísticas móviles (promedio, desviación estándar, mínimo, máximo), EMA y RSI del pago total. Permite detectar patrones de deterioro (crecimiento de la proporción de mora, caída del pago de capital) o mejora.
- **Comportamiento de mora en contingentes:** Proporción del pago destinado a mora respecto al total, con promedios móviles. Es especialmente relevante porque la mora en contingentes puede anticipar la ejecución de la garantía y la transición a cartera.
- **Comportamiento post-transición:** Para créditos que iniciaron como contingentes y se transformaron en cartera, comparación del patrón de pago antes y después de la transición. Permite evaluar si la conversión a cartera mejoró o empeoró el comportamiento de pago del cliente.
- **Indicadores de bienestar:** Señales de si el cliente tiende a pagar sus créditos antes de que pasen a ser cartera. Se contruyen como porcentaje de creditos que paga antes de ser cartera en en los 12-24 últimos meses.

**Prioridad: 🟠 Media-Alta** — El comportamiento de pagos en contingentes complementa las métricas de cartera y permite detectar señales tempranas de deterioro crediticio antes de que el contingente se ejecute.

---

<a id="p5"></a>

### Propuesta 5: `fs_cus_mibb_score` — Score de Morosidad Interna (MIBB)

El MIBB es un **score interno del banco** que mide el comportamiento de mora dentro del mes, ponderado por monto. A diferencia de las calificaciones oficiales (que se actualizan mensualmente y reflejan la peor calificación del periodo), el MIBB captura microcomportamientos intra-mes: cuántos días estuvo el cliente en mora, con qué porcentaje de su deuda, y si regularizó antes del cierre. Es un indicador propietario del equipo de riesgo.

**No existe ninguna feature que capture este score.** La fuente son tablas mensuales independientes (`CalificacionMIBB_<mesaño>`) que requieren consolidación previa en una tabla histórica única.

**Fuente:** `DWANALISISR.dbo.CalificacionMIBB_<mesaño>` (requiere consolidación previa - Requerimiento a DW)

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Score MIBB mensual:** Valor numérico del score.
- **Categoría de calificación:** Clasificación derivada del score (bueno, regular, malo).

A partir de estos valores base podrían derivarse: lags temporales, máximo histórico, indicador de deterioro (¿score actual es peor que el de hace N meses?), promedio móvil y tendencia.

**Dependencia:** Requiere que el equipo de DataWarehouse consolide las tablas `CalificacionMIBB_*` en una tabla histórica única ON-PREMISE.

**Prioridad: 🟠 Media-Alta** — Score con alto potencial de valor predictivo, pero requiere trabajo previo de infraestructura.

---

<a id="p6"></a>

### Propuesta 6: `fs_cus_credit_line` — Líneas de Crédito y Cupo

Las líneas de crédito empresariales definen la capacidad de endeudamiento autorizada para un cliente: cuánto se le aprobó, cuánto ha utilizado y cuánto le queda disponible. Adicionalmente, el banco distingue entre operaciones **bajo línea de crédito** (dentro del cupo aprobado) y **fuera de línea de crédito** (que exceden el cupo y representan un riesgo adicional tolerado).

La feature table `fs_acc_portfolio` captura cupo de tarjeta de crédito, pero **no cubre líneas de crédito empresariales**.

**Fuente:** `CRM365BDSRV.BOLIVARIANO_365.dbo.bb4_linea_credito` (queda por evaluar si el origen de esta tabla son tablas del DW)

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Cupo aprobado, utilizado y disponible** en todas las líneas vigentes del cliente.
- **Porcentaje de utilización:** Cuánto del cupo aprobado ha sido utilizado.
- **Cantidad de líneas de crédito vigentes.**
- **Días hasta el vencimiento de la línea más próxima a vencer:** Para anticipar necesidades de renovación.
- **Indicador de operaciones fuera de línea:** Si el cliente tiene operaciones que exceden el cupo autorizado.

**Prioridad: 🟠 Media-Alta** — Las líneas de crédito son un componente directo de la decisión de otorgamiento.

---

<a id="p7"></a>

### Propuesta 7: `fs_cus_company_benchmark` — Benchmarking por Grupo Económico y Actividad Económica

Esta feature table posiciona a cada empresa en dos contextos comparativos: frente a las demás empresas de su **grupo económico** y frente a las empresas de su **actividad económica** (CIIU nivel 4). Un cliente puede estar creciendo en ventas, pero si su industria crece más rápido, en realidad está perdiendo participación. Del mismo modo, dentro de un grupo económico, es relevante saber qué empresa lidera en ventas, cuál concentra la deuda, y cómo se compara el crecimiento individual con el del conjunto.

Actualmente `fs_cus_demographic` contiene el código CIIU y el nombre del grupo económico del cliente, pero **no se computan estadísticas de industria, de grupo, ni posiciones relativas.**

**Granularidad propuesta:** cliente × año

**Conceptos propuestos:**

*Benchmarking por Actividad Económica (CIIU 4):*

- **Posición de la empresa** dentro de su actividad económica por nivel de ventas: ranking bruto (posición 1, 2, 3…) y **posición normalizada** (valor de 0 a 1, donde 1 es la primera posición y 0 la última entre todas las empresas de esa actividad económica).
- **Participación en ventas de la actividad económica** (porcentaje de las ventas de la empresa respecto al total de la actividad).
- **CAGR3 de la empresa y CAGR3 de la actividad económica:** Tasa de crecimiento anual compuesta a 3 años. Permite comparar la velocidad de crecimiento de la empresa vs. su industria.
- **Comparativa de crecimiento de ventas empresa vs. industria:** Variación interanual de ventas de la empresa comparada con la variación interanual de la actividad económica. Indicadores de outperformance (empresa crece mientras industria decrece) y underperformance (empresa decrece mientras industria crece).
- **Posición por deuda total** dentro de la actividad económica: ranking bruto y normalizado.
- **Participación en deuda de la actividad económica** (porcentaje de la deuda total del CIIU 4 que corresponde a esta empresa).

*Benchmarking por Grupo Económico:*

- **Posición de la empresa** dentro de su grupo económico por nivel de ventas: ranking bruto y **posición normalizada** (0 a 1).
- **Participación en ventas del grupo económico** (porcentaje de las ventas de la empresa respecto al total del grupo).
- **CAGR3 de la empresa vs. CAGR3 del grupo económico.**
- **Posición por deuda total** dentro del grupo económico: ranking bruto y normalizado.
- **Participación en deuda del grupo económico** (porcentaje de la deuda total del grupo que corresponde a esta empresa). Complementa el ranking con una magnitud relativa; es el dato base para el cálculo del indicador de contagio.
- **Participación en acreditaciones del grupo económico** (porcentaje de las acreditaciones totales del grupo que corresponden a esta empresa). Utiliza `fs_cus_deposit_liabilities` como numerador y `fs_grp_economic_group` ([Propuesta 2](#p2)) como denominador.

> **Fuente de deuda para el benchmarking:** Los indicadores de posición y participación por deuda en esta tabla utilizan como fuente el `dwh_d_spd_balance` (spread interno). Esto implica que la deuda contemplada es la **deuda financiera total** del cliente: incluye tanto obligaciones con el sistema bancario como emisiones en el mercado de valores, ya que el spread no distingue entre ambas.
>
> Si se desea construir variantes de estos indicadores acotadas al **sistema bancario**, una alternativa sería hacerla dentro de `fs_cus_credit_risk`, que sí desglosa la deuda por institución financiera (hace uso de `dw_central_riesgo_historico`). En esa tabla se podría calcular:
> - **Participación en deuda del sistema bancario** por actividad económica o grupo económico, considerando la deuda del cliente con **todos los bancos** del sistema.
> - **Participación en deuda con BB** por actividad económica o grupo económico, acotando el denominador únicamente a la deuda que el conjunto de clientes de ese CIIU o grupo mantiene con Banco Bolivariano.
>
> Ambas variantes tienen interpretaciones distintas y complementarias: la del spread mide el peso de la empresa en el mercado financiero amplio, mientras que las de `fs_cus_credit_risk` miden su relevancia dentro del portafolio del banco.

> **Integración:** Esta feature table podría incorporarse como columnas adicionales dentro de `fs_cus_financial_statement` (existente) o de `fs_cus_spread` (propuesta), dado que comparte granularidad (cliente × año) y depende directamente de las cifras financieras de esas tablas. Se mantiene como propuesta separada por claridad conceptual, pero en la implementación podría unificarse.

**Prioridad: 🟠 Media-Alta** — El benchmarking dual (grupo económico + actividad económica) contextualiza el desempeño individual y es un componente central de la evaluación de riesgo.

---

<a id="p8"></a>

### Propuesta 8: `fs_cus_profitability` — Rentabilidad del Cliente para BB

El banco mide la rentabilidad que cada cliente genera, desglosada por tipo de producto: activos (intereses devengados de préstamos), contingentes (comisiones por avales y garantías), pasivos (margen de intermediación financiera por depósitos), SAT (comisiones por transacciones), otros servicios y cuentas de orden. Este análisis permite identificar qué clientes generan valor y cuáles generan déficit, y puede ser un insumo relevante para modelos de retención.

**La tabla de rentabilidad no alimenta ninguna feature table actual.**

**Fuente:** `DWREPORTES.dbo.dwh_r_rentabilidad`

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Rentabilidad total del cliente** y **desglose por tipo de producto** (activos, contingentes, pasivos, SAT, otros servicios, etc).
- **Rentabilidad acumulada en el año (YTD)** y su **variación respecto al año anterior**.
- **Concentración de rentabilidad:** Proporción de la rentabilidad total que proviene de cada producto. Identifica dependencia excesiva de un solo tipo de ingreso.
- **Producto principal:** El tipo de producto que más rentabilidad genera para el banco desde este cliente.

**Prioridad: 🟠 Media** — Información valiosa para modelos de retención, pero secundaria para modelos de riesgo puro.

---

<a id="p9"></a>

### Propuesta 9: `fs_cus_acquirer` — Adquirencias (POS)

El banco analiza los ingresos generados por terminales POS en comercios afiliados. Este volumen transaccional refleja la actividad comercial del cliente y constituye una fuente de ingresos por comisiones para el banco.

**No existe feature table para adquirencias.** La fuente de datos no está documentada explícitamente en el Dashboard de Riesgo.

**Fuente:** Por determinar (consultar con equipo de riesgo)

**Granularidad propuesta:** cliente × mes

**Conceptos propuestos:**

- **Ingreso total por POS** en el mes.
- **Cantidad de transacciones POS** en el mes.
- **Ticket promedio** (ingreso / cant. transacciones) en el mes.
- **Desgloce por entidad financiera:** calculo de ingreso, cantidad de transacciones y su ratio por los bancos PEERs y por "BB" y "no BB". Se incluyen montos, cantidad de transacciones y ratios vs total.
- **Desgloce por medio de pago:** debito / tar. credito / tarjeta regalo / efectivo. O su agrupado tarjetas/efectivo. Se incluyen montos, cantidad de transacciones y ratios vs total.
- **Indicador de comercio con POS activo.**

**Prioridad: 🟡 Media** — Complementa el análisis de ingresos pero aplica solo a comercios afiliados al servicio de adquirencias.

---

<a id="p10"></a>

### Propuesta 10: Features Cross-Table — Métricas Derivadas de Relación Bancaria

El equipo de riesgo calcula varias métricas que cruzan información de múltiples fuentes y que actualmente no están disponibles como features. Estas métricas son centrales en la evaluación crediticia porque responden preguntas clave: ¿somos el banco principal de este cliente? ¿está fugando sus operaciones? ¿cuánto de su capacidad de endeudamiento está utilizando con nosotros? ¿qué tan buena es su relación crediticia con nosotros?

Estas features se proponen como **columnas adicionales dentro de Feature Tables ya existentes**, aprovechando datos que ya están disponibles en la Feature Store o que lo estarán tras implementar otras propuestas de este documento. No requieren crear tablas nuevas.

**Granularidad:** cliente × mes

**Conceptos propuestos:**

- **Métricas de buena relación con Banco Bolivariano:**
  - **Ratio acreditaciones vs. ventas:** Compara el flujo de acreditaciones bancarias del cliente (promedio semestral anualizado, de cuentas corrientes y de ahorro) con sus ventas anuales (de `fs_cus_financial_statement`). Un ratio cercano a 1.0 indica que BB es probablemente el banco principal del cliente (hay casos donde es superior a 1, revisar la sección *"5. Saldos de Cuentas BB"* de la documentación del dashboard de riesgo).
    - *Agregar en:* `fs_cus_deposit_liabilities` (existente), que ya consolida acreditaciones de cuentas corrientes y de ahorro del cliente
    - *Requiere:* `fs_cus_deposit_liabilities` (acreditaciones consolidadas), `fs_cus_financial_statement` (ventas anuales)
  - **Ratio de reciprocidad:** Saldo promedio de depósitos dividido entre el monto total prestado. El banco espera un mínimo de reciprocidad mínima (≈10%) para justificar la relación crediticia.
    - *Agregar en:* `fs_cus_credit_risk` (existente)
    - *Requiere:* `fs_cus_deposit_liabilities` (saldo consolidado — corriente + ahorro), `fs_cus_credit_risk` (monto total prestado por BB)
  - ~~**Share of Wallet BB:**~~ Este valor ya está en la fs_credit_risk y fs_credit_risk_holder. Pero no hay indicadores basados en esta métrica.
  - **Indicador de banco principal:** dos indicadores
    - basado en el ratio de acreditaciones/ventas: Se toma el promedio mensual de acreditaciones de los últimos 6 meses, se multiplica por 12, y el resultado se compara contra las ventas anuales del spread. Si es mayor al 70% -> 1, sino -> 0. (El threshold está abierto a discución - es un valor propuesto por Ingienería de Datos)
      - *Agregar en:* `fs_cus_deposit_liabilities`
      - *Requiere:* ratio acreditaciones vs. ventas (anterior)
    - Basado en Share of Wallet: Si es mayor o igual al 50% nos consideramos el banco principal.
      - *Agregar en:* `fs_cus_credit_risk`
      - *Requiere:* El SoW ya calculado en `fs_cus_credit_risk`
- **Indicador de fuga de cliente:** Detecta caídas abruptas en acreditaciones que podrían indicar que el cliente está trasladando sus operaciones a otro banco. Alternativas de implementación:
  - **Umbral simple:** caída `>20%` en el ratio acreditaciones/ventas en un periodo completo de 6 meses.
  - **Métricas estadísticas** (más robustas ante volatilidad):

    **CAN — Caídas Abruptas Normalizadas**

    Normaliza la tasa de cambio mensual respecto a la distribución histórica reciente. Una caída de más de 3 desviaciones estándar se considera abrupta.

    $$r_t = \frac{x_t - x_{t-1}}{x_{t-1}}, \qquad CAN_t = \frac{r_t - \mu_W}{\sigma_W}$$

    | Parámetro | Valor |
    |---|---|
    | Ventana móvil $W$ | 20 períodos |
    | Umbral caída abrupta | $CAN_t < -3$ |
    | Umbral subida abrupta | $CAN_t > 3$ |

    ---

    **CUSUM Robusto** (resistente a outliers — usa mediana y MAD)

    Detecta cambios sostenidos en el nivel de la serie. Los parámetros $k$ (drift detectable) y $h$ (umbral de alerta) se calibran según el negocio.

    $$z_t^{rob} = \frac{x_t - \text{median}(x)}{1.4826 \cdot MAD}, \qquad MAD = \text{median}\!\left(|x_t - \text{median}(x)|\right)$$

    $$C_t^{+} = \max\!\left(0,\; C_{t-1}^{+} + z_t^{rob} - k \right), \qquad C_t^{-} = \min\!\left(0,\; C_{t-1}^{-} + z_t^{rob} + k \right)$$

    Alerta cuando: $C_t^{+} > h \;$ o $\; C_t^{-} < -h$

    ---

    **EWMAC — Exponentially Weighted Moving Average Crossover**

    Compara una EMA rápida contra una EMA lenta para capturar tendencias. El cruce hacia abajo indica deterioro sostenido.

    $$EMA_{fast,t} = \alpha_f\, x_t + (1 - \alpha_f)\, EMA_{fast,t-1}$$

    $$EMA_{slow,t} = \alpha_s\, x_t + (1 - \alpha_s)\, EMA_{slow,t-1}, \qquad \alpha = \frac{2}{N + 1}$$

    La señal se estandariza para comparabilidad entre clientes:

    $$EWMAC_t^{*} = \frac{EWMAC_t - \mu(EWMAC)}{\sigma(EWMAC)}$$

    | Valor de $EWMAC_t^*$ | Interpretación |
    |---|---|
    | $> 0$ | Tendencia alcista |
    | $< 0$ | Tendencia bajista |
    | $\|EWMAC_t^*\|$ | fuerza de la tendencia |

  - *Agregar en:* `fs_cus_deposit_liabilities` (existente)
  - *Requiere:* `fs_cus_deposit_liabilities` (serie histórica de acreditaciones consolidadas — corriente + ahorro)

- **Concentración de deuda respecto a patrimonio:** Deuda del cliente en BB respecto al doble de su patrimonio (capacidad de endeudamiento). El banco no debe prestar más del 200% del patrimonio del cliente.
  - *Agregar en:* `fs_cus_credit_risk` (existente)
  - *Requiere:* `fs_cus_credit_risk` (deuda del cliente con BB), `fs_cus_financial_statement` (patrimonio)
- **Indicador de fuente de contagio:** Flag que señala si esta empresa concentra más del 20% de la deuda de su grupo económico **y** tiene una calificación deficiente.
  - *Agregar en:* `fs_cus_credit_risk` (existente)
  - *Requiere:* `fs_grp_economic_group` ([Propuesta 2](#p2), participación en deuda del grupo), `fs_cus_credit_risk` (calificación del cliente)
- **Indicador de afectado por contagio:** Flag que señala si alguna otra empresa del mismo grupo es fuente de contagio (según el indicador anterior). Permite saber si el cliente hereda riesgo de otra empresa aunque su perfil individual sea sano.
  - *Agregar en:* `fs_cus_credit_risk` (existente)
  - *Requiere:* `fs_grp_economic_group` ([Propuesta 2](#p2)), indicador de fuente de contagio (anterior, también en `fs_cus_credit_risk`)

**Prioridad: 🔴 Alta** — Estas métricas compuestas replican los análisis más importantes que el equipo de riesgo realiza manualmente. Se ubican al final por depender de varias de las propuestas anteriores.

---

## Plan de Implementación Sugerido

### Fase 1 — Fuentes Independientes de Alta Prioridad

| # | Feature Table | Dependencia | Esfuerzo Estimado |
|---|--------------|-------------|-------------------|
| 1 | `fs_cus_guarantee` | Acceso a `dwh_d_garantia_oper_ac` + `cu_poliza` | Medio |
| 3 | `fs_cus_spread` | Acceso a `dwh_d_spd_balance`. Alcance: solo información de deuda financiera y EBITDA (las partidas contables base ya existen en `fs_cus_financial_statement`). | Bajo-Medio |
| 4 | `fs_cus_contingent_credit` + `fs_cus_contingent_credit_payment` | Acceso a `dw_riesgo_semanal` + `dw_recuperacion_cartera` | Medio |

> ⚠️ Falta verificar si las tablas de **garantías** poseen informacion histórica incremental. O sea que el histórico posea garantías que ya han vencido o han sido retiradas. Esto puede determinar la **viabilidad** de la implementación o puede marcar la necesidad de **explorar otras fuentes** que sí posean esa historia.

### Fase 2 — Scores e Información Operacional

| # | Feature Table | Dependencia | Esfuerzo Estimado |
|---|--------------|-------------|-------------------|
| 5 | `fs_cus_mibb_score` | Consolidación de tablas `CalificacionMIBB_*` | Alto (infraestructura) |
| 6 | `fs_cus_credit_line` | Acceso a CRM365 `bb4_linea_credito` | Alto |
| 8 | `fs_cus_profitability` | Acceso a `dwh_r_rentabilidad` | Bajo |
| 9 | `fs_cus_acquirer` | Identificar fuente de adquirencias | Bajo (si se identifica fuente) |

> ⚠️ Dos cosas a considerar:
> 1. Para implementar fs_cus_mibb_score primero necesitamos una tabla que consolide todas las tablas `CalificacionMIBB_<mesaño>` que se crean mensualmente en **una sola estructura** ON-PREMISE.
> 2. Se a tendrá que **solicitar el DTS** de `bb4_linea_credito` y analizar la construcción para trabajar con tablas que son de DataWarehouse y no procesadas que se suben al CRM365.

### Fase 3 — Consolidaciones y Benchmarking

| # | Feature Table | Dependencia | Esfuerzo Estimado |
|---|--------------|-------------|-------------------|
| 2 | `fs_grp_economic_group` | Todas las features de nivel cliente | Alto (nuevo nivel de agregación y demasiados JOIN) |
| 7 | `fs_cus_company_benchmark` | `fs_cus_financial_statement` (existente) + [Propuesta 3](#p3) (para deuda financiera). Puede integrarse en `fs_cus_financial_statement` o `fs_cus_spread`. | Medio |

### Fase 4 — Features Derivadas (Dependen de Propuestas Anteriores)

| # | Feature Table | Dependencia | Esfuerzo Estimado |
|---|--------------|-------------|-------------------|
| 10 | Features Cross-Table (columnas en FTs existentes) | Columnas nuevas en `fs_cus_deposit_liabilities`, `fs_cus_credit_risk`. Requiere [Propuestas 2](#p2) y [4a](#p4a) para algunas métricas | Medio |

---

## Anexo: Features Existentes que ya Cubren Información Utilizada en la Evaluación de Riesgo

Para completitud, estas son las áreas de la evaluación de riesgo que **ya están bien cubiertas** por el Feature Store:

| Área | Feature Tables que la cubren | Comentario |
|---|---|---|
| Saldos de cuentas bancarias (captaciones, movimientos, sobregiros) | `fs_cus_checking_account`, `fs_cus_savings_account`, `fs_cus_certificate_deposit`, `fs_cus_deposit_liabilities` | ✅ Cobertura completa con gran profundidad temporal (lags hasta 36 meses). |
| Transacciones SAT (ordenante, beneficiario, proveedores, transferencias) | `fs_cus_company_sat`, `fs_cus_company_roll_sat`, `fs_cus_company_provider_sat`, `fs_cus_company_inter_transfers_sat`, `fs_cus_beneficiary_sat` | ✅ Cobertura completa: 1,286 features SAT en total. |
| Central de riesgo (calificaciones, montos por banco, SOW) | `fs_cus_credit_risk`, `fs_cus_credit_risk_holder` | 🟡 Parcial: excelente cobertura de calificaciones y montos. Falta: emisiones en mercado de valores. |
| Tenencia de productos bancarios | `fs_cus_holding_products`, `fs_cus_ivc` | ✅ Cobertura completa de productos y volumen de negocio. |
| Información demográfica (CIIU, segmentación, estado legal) | `fs_cus_demographic` | ✅ Datos personales, código CIIU, segmentación, estado legal. |
| Tarjetas de crédito (cupo, consumo, categorías de comercio) | `fs_acc_portfolio`, `fs_cus_portfolio`, `fs_acc_credit_card_consumption`, `fs_cus_credit_card_consumption` | ✅ Cupo, utilización, consumo por categoría. |

---

*Documento generado como insumo para el equipo de Analítica Avanzada · Banco Bolivariano*