# Atlas de Técnicas Culinarias: De la Ciencia a la Sartén

> Manual de referencia para cocineros curiosos | ~~Primera~~ Segunda edición revisada

---

## Índice

- [Fundamentos de la Cocción](#fundamentos)
- [Reacciones Químicas en la Cocina](#reacciones)
- [Técnicas por Medio de Transferencia](#técnicas)
- [Gestión de Tiempos y Temperaturas](#tiempos)
- [Fermentación y Cultivos Vivos](#fermentación)
- [Recetas como Algoritmos](#recetas)
- [Conversión de Unidades y Fórmulas](#fórmulas)

---

## Fundamentos de la Cocción

<a id="fundamentos"></a>

### ¿Qué es cocinar?

Cocinar es aplicar **energía** a los alimentos para transformar su estructura molecular, volviéndolos más digeribles, seguros y sabrosos. Toda técnica culinaria se reduce a tres mecanismos de transferencia de calor:

| Mecanismo | Medio | Rango de temperatura | Ejemplo clásico |
|-----------|-------|---------------------|-----------------|
| 🔴 **Conducción** | Contacto directo sólido-sólido | 150–300 °C (superficie) | Sear de carne en sartén de hierro |
| 🟠 **Convección** | Movimiento de fluido (aire, agua, aceite) | 60–230 °C | Hornear pan, freír, hervir |
| 🟡 **Radiación** | Ondas electromagnéticas (IR) | 250–800 °C (fuente) | Gratinar bajo la salamandra, brasas |

> 💡 **Dato curioso:** Un horno convencional calienta principalmente por **radiación** de sus paredes, no por convección del aire. Los hornos con ventilador forzado sí añaden un componente convectivo significativo, reduciendo tiempos de cocción en un ~25%.

### Los Cinco Sabores Fundamentales

La percepción gustativa humana distingue cinco sabores base, cada uno asociado a moléculas y funciones biológicas específicas:

1. **Dulce** — Detectado por receptores T1R2/T1R3
    1. Azúcares simples: glucosa, fructosa, sacarosa
    2. Polialcoholes: sorbitol, xilitol
    3. Proteínas dulces: taumatina, monelina
        - La taumatina es ~2,000 veces más dulce que la sacarosa
        - Se usa como potenciador de sabor en la industria alimentaria
2. **Salado** — Canal iónico ENaC
    1. Cloruro de sodio (NaCl) — el más común
    2. Cloruro de potasio (KCl) — sustituto bajo en sodio
    3. Sales minerales complejas
        - Sal del Himalaya (contiene 84 minerales traza)
        - Flor de sal de Guérande
        - Sal negra volcánica (kala namak — con notas sulfurosas)
3. **Ácido** — Receptores sensibles a H⁺
    1. Ácido cítrico (cítricos)
    2. Ácido acético (vinagre)
    3. Ácido láctico (fermentaciones)
4. **Amargo** — Familia de receptores T2R (~25 subtipos)
    1. Cafeína (café, té)
    2. Quinina (agua tónica)
    3. Compuestos fenólicos (cacao, aceite de oliva virgen extra)
5. **Umami** — Receptores T1R1/T1R3
    1. Glutamato monosódico (MSG)
    2. Nucleótidos: inosinato y guanilato
        - La combinación glutamato + nucleótidos produce **sinergia umami**
        - El efecto es multiplicativo, no aditivo
    3. Fuentes naturales ricas en umami:
        - Parmesano (1,680 mg glutamato libre / 100 g)
        - Salsa de soja (950 mg / 100 g)
        - Tomate maduro (246 mg / 100 g)
        - Alga kombu (3,190 mg / 100 g)

> ⚠ El MSG ha sido injustamente demonizado durante décadas. Estudios doble ciego del _Journal of the American Medical Association_ no encontraron correlación entre MSG y el llamado "síndrome del restaurante chino". El glutamato libre está presente de forma natural en tomates, quesos y carnes curadas.

---

## Reacciones Químicas en la Cocina

<a id="reacciones"></a>

### Reacción de Maillard

La reacción de Maillard no es una sola reacción sino una **cascada de cientos** de reacciones entre aminoácidos y azúcares reductores que ocurren a temperaturas superiores a ~140 °C. Es responsable del sabor del pan tostado, la carne sellada, el café y el chocolate.

La velocidad de la reacción depende de:

- **Temperatura** — Se acelera exponencialmente según Arrhenius:

$$k = A \cdot e^{-E_a / (R \cdot T)}$$

donde $k$ es la constante de velocidad, $E_a$ la energía de activación (~100–150 kJ/mol para Maillard), $R = 8.314\,\text{J}\cdot\text{mol}^{-1}\cdot\text{K}^{-1}$ y $T$ la temperatura absoluta en Kelvin.

- **pH** — Más rápida en condiciones alcalinas (pH 7–9)
- **Actividad de agua** ($a_w$) — Máxima velocidad entre $a_w = 0.4$ y $0.6$
- **Tipo de azúcar y aminoácido presentes**

> 🧪 **Hack culinario:** Añadir una pizca de bicarbonato de sodio a las cebollas antes de caramelizarlas sube el pH y acelera la Maillard, reduciendo el tiempo de caramelización de 45 a ~20 minutos.

#### Productos de la Reacción de Maillard

```
Aminoácido + Azúcar reductor
         ↓ (> 140 °C)
   Base de Schiff
         ↓
  Producto de Amadori
         ↓ (deshidratación, fragmentación)
  ┌──────┴──────────┐
  │                 │
Furfurales      Reductonas      → Aromas volátiles
  │                 │                (pirazinas, furanos,
  └──────┬──────────┘                 tiofenos, aldehídos)
         ↓
   Melanoidinas  → Color pardo
```

### Caramelización

A diferencia de Maillard, la caramelización involucra **solo azúcares** (sin aminoácidos) sometidos a alta temperatura:

| Azúcar | Punto de caramelización | Notas de sabor |
|--------|------------------------|----------------|
| Fructosa | 110 °C | Caramelo delicado, floral |
| Glucosa | 150 °C | Moderado, ligeramente ácido |
| Sacarosa | 160 °C | Clásico caramelo, toffee |
| Lactosa | 202 °C | Dulce de leche, mantequilla |
| Maltosa | 180 °C | Malteado, cerveza |

> La caramelización es una reacción de **pirólisis**: ruptura de enlaces por calor. A medida que avanza, los productos pasan de dulce → ácido → amargo. Controlar el punto exacto de quiebre es lo que separa un caramelo elegante de azúcar quemada.

### Desnaturalización de Proteínas

Cuando cocinamos un huevo, las proteínas (ovoalbúmina, ovomucoide, lisozima) se **desnaturalizan**: pierden su estructura terciaria y se agregan formando una red sólida. Este proceso es irreversible y progresivo:

1. **62 °C** — La ovoalbúmina comienza a desnaturalizarse
    1. Clara aún translúcida
    2. Textura gelatinosa
    3. Ideal para huevos poché
2. **68 °C** — Clara opaca, yema cremosa
    1. Huevo mollet perfecto
    2. Punto preferido en cocina francesa
3. **73 °C** — Clara firme, yema semilíquida
    1. Huevo pasado por agua clásico
    2. La yema fluye al cortar
4. **80 °C** — Clara y yema completamente cuajadas
    1. Huevo duro
    2. Si se excede ~~este punto~~ 90 °C, aparece un borde verdoso de sulfuro de hierro (FeS) entre yema y clara

> 📌 **Temperatura, no tiempo:** La cocina moderna (sous-vide) explota el hecho de que la *textura final* depende de la **temperatura**, no de la duración. Un huevo a 63 °C durante 45 minutos tiene una textura radicalmente distinta a uno hervido 6 minutos a 100 °C.

---

## Técnicas por Medio de Transferencia

<a id="técnicas"></a>

### Mapa de Técnicas Culinarias

| Técnica | Medio | Temp. típica | Tiempo | Mejor para |
|---------|-------|-------------|--------|-----------|
| 🟢 Sous-vide | Agua (vacío) | 50–85 °C | 1–72 h | Proteínas, vegetales precisos |
| 🔵 Pochado | Agua | 70–82 °C | 3–20 min | Huevos, pescados delicados |
| 🔵 Hervido | Agua | 100 °C | 5–120 min | Pasta, legumbres, fondos |
| 🟡 Vapor | Vapor de agua | 100 °C | 5–30 min | Vegetales, dim sum |
| 🟠 Salteado | Aceite (poco) | 180–230 °C | 2–8 min | Wok, vegetales al dente |
| 🟠 Fritura profunda | Aceite (inmersión) | 160–190 °C | 2–15 min | Empanizados, buñuelos |
| 🔴 Horneado | Aire caliente | 150–250 °C | 10–180 min | Pan, pasteles, gratinados |
| 🔴 Grill / Brasa | Radiación IR | 250–500 °C | 3–30 min | Carnes, vegetales asados |
| ⚡ Wok hei | Llama + conducción | > 350 °C | 30–90 s | Stir-fry cantonés |

### Sous-vide en Detalle

La cocción sous-vide (del francés *"bajo vacío"*) es el paradigma de la **cocina de precisión**. Los alimentos se sellan al vacío y se cocinan en un baño de agua a temperatura controlada con precisión de ±0.1 °C.

#### Temperaturas de Referencia para Proteínas

```python
# Tabla de referencia sous-vide (proteínas comunes)
SOUS_VIDE_TEMPS = {
    "huevo_cremoso":    {"temp_c": 63.0, "tiempo_min": 45,   "nota": "Yema líquida sedosa"},
    "huevo_fudge":      {"temp_c": 65.0, "tiempo_min": 45,   "nota": "Yema tipo fudge"},
    "salmon_translucido":{"temp_c": 46.0, "tiempo_min": 40,  "nota": "Textura sashimi cocido"},
    "salmon_tierno":    {"temp_c": 52.0, "tiempo_min": 40,   "nota": "Escamas se separan"},
    "pollo_pechuga":    {"temp_c": 63.5, "tiempo_min": 90,   "nota": "Jugosa, segura"},
    "res_medium_rare":  {"temp_c": 55.0, "tiempo_min": 120,  "nota": "Centro rosado uniforme"},
    "res_medium":       {"temp_c": 60.0, "tiempo_min": 120,  "nota": "Rosa pálido uniforme"},
    "cerdo_chuleta":    {"temp_c": 60.0, "tiempo_min": 120,  "nota": "Jugosa con borde rosado"},
    "costilla_res":     {"temp_c": 62.0, "tiempo_min": 4320, "nota": "72h = textura braseada"},
}

def calcular_espesor_tiempo(espesor_cm: float, temp_agua: float, temp_interna: float) -> float:
    """
    Estima el tiempo (minutos) para que el centro alcance la temperatura objetivo.
    Basado en la solución simplificada de la ecuación de calor unidimensional.
    """
    import math
    # Difusividad térmica promedio de carne: ~1.3 × 10⁻⁷ m²/s
    alpha = 1.3e-7  # m²/s
    L = espesor_cm / 100 / 2  # medio espesor en metros
    ratio = (temp_agua - temp_interna) / (temp_agua - 5.0)  # asumiendo temp inicial 5°C
    # Tiempo Fourier para alcanzar el 99% de equilibrio
    Fo = (L ** 2) / alpha * math.log(ratio) * 0.4
    return max(Fo / 60, 30)  # mínimo 30 minutos por seguridad
```

> **⚠ Seguridad alimentaria:** Para pasteurización sous-vide, la combinación tiempo-temperatura debe cumplir las tablas del USDA. Por ejemplo, carne de res a 55 °C requiere al menos **89.4 minutos** de sostenimiento.

---

## Gestión de Tiempos y Temperaturas

<a id="tiempos"></a>

### La Regla del Arrastre Térmico

Al retirar una pieza de carne grande del horno, su temperatura interna **sigue subiendo** entre 3 y 8 °C por redistribución del calor desde la corteza. Este fenómeno se llama *carry-over cooking*:

- **Pollo entero (2 kg):** +5–8 °C en 15 min de reposo
- **Lomo de res (1.5 kg):** +5–7 °C en 10 min de reposo
- **Chuleta de cerdo (300 g):** +3–4 °C en 5 min de reposo

La ecuación de transferencia de calor en una esfera (aproximación para piezas grandes) sigue la *ley de Fourier*:

$$\frac{\partial T}{\partial t} = \alpha \nabla^2 T$$

donde $\alpha$ es la difusividad térmica del alimento. En la práctica esto significa: **retira la carne del horno cuando esté 5 °C por debajo** de la temperatura objetivo.

### Puntos de Cocción de Carnes (Temperatura Interna)

| Punto | Res (°C) | Cerdo (°C) | Pollo (°C) | Color del centro |
|-------|---------|-----------|-----------|-----------------|
| Blue / Bleu | 46–49 | ❌ No aplica | ❌ No aplica | Rojo frío |
| Rare / Poco hecho | 50–53 | ❌ No aplica | ❌ No aplica | Rojo cálido |
| Medium Rare | 54–57 | ❌ No aplica | ❌ No aplica | Rosa rojizo |
| Medium | 58–62 | 60–63 | ❌ No aplica | Rosa uniforme |
| Medium Well | 63–67 | 64–68 | ❌ No aplica | Rosa pálido |
| Well Done | 68–74 | 69–74 | 74+ | Sin rosa |
| Desmenuzable | 88–95 | 88–95 | 88–95 | Fibras se separan |

> 🍖 **Nota importante:** La seguridad con cerdo y pollo requiere temperaturas mínimas más altas que con res, debido a la posible presencia de *Trichinella spiralis* (cerdo) y *Salmonella* / *Campylobacter* (aves). Las temperaturas sous-vide pueden ser menores si el tiempo de exposición compensa.

### Tiempos de Fermentación por Tipo de Masa

| Masa | Temperatura ambiente | Primera fermentación | Segunda fermentación | Índice de hidratación |
|------|---------------------|---------------------|---------------------|----------------------|
| Pan francés | 24 °C | 1.5–2 h | 45–60 min | 65% |
| Ciabatta | 24 °C | 2–3 h | 1–1.5 h | 80% |
| Baguette poolish | 24 °C | 12 h (poolish) + 2 h | 1.5 h | 68% |
| Pizza napolitana | 22 °C | 8–24 h | 4–6 h (bolas) | 62% |
| Masa madre | 22–26 °C | 4–6 h | 12–18 h (frío) | 75% |

> El **índice de hidratación** se define como la relación porcentual entre el peso del agua y el peso de la harina en la fórmula panadera:
>
> $$H = \frac{m_{\text{agua}}}{m_{\text{harina}}} \times 100$$

---

## Fermentación y Cultivos Vivos

<a id="fermentación"></a>

### Tipos de Fermentación

La fermentación es un proceso metabólico anaeróbico (o parcialmente anaeróbico) donde microorganismos transforman sustratos orgánicos:

1. **Fermentación alcohólica** (levaduras: *Saccharomyces cerevisiae*)
    1. Sustrato: glucosa
    2. Productos: etanol + CO₂
    3. Aplicaciones:
        - Pan (CO₂ expande la masa, el alcohol se evapora al hornear)
        - Vino (el etanol permanece; el CO₂ se libera o retiene según tipo)
        - Cerveza
            - Ale: fermentación alta (15–24 °C), levaduras *S. cerevisiae*
            - Lager: fermentación baja (7–13 °C), levaduras *S. pastorianus*
            - Lambic: fermentación espontánea con microflora silvestre
2. **Fermentación láctica** (bacterias: *Lactobacillus*, *Leuconostoc*)
    1. Sustrato: glucosa o lactosa
    2. Producto: ácido láctico
    3. Aplicaciones:
        - Yogur y kéfir
        - Chucrut y kimchi
        - Encurtidos lactofermentados (sin vinagre)
            - Salmuera al 2–3% de sal
            - Temperatura ideal: 18–22 °C
            - Tiempo: 3–14 días según acidez deseada
3. **Fermentación acética** (bacterias: *Acetobacter*, *Gluconobacter*)
    1. Sustrato: etanol
    2. Producto: ácido acético
    3. Aplicaciones:
        - Vinagre de vino, sidra, arroz
        - Kombucha (fermentación mixta con SCOBY)

La ecuación global simplificada de la fermentación alcohólica:

$$\text{C}_6\text{H}_{12}\text{O}_6 \xrightarrow{\text{levadura}} 2\text{C}_2\text{H}_5\text{OH} + 2\text{CO}_2$$

De cada mol de glucosa (180 g) se obtienen 2 moles de etanol (92 g) y 2 moles de CO₂ (88 g). En la práctica, el rendimiento teórico es del ~51% para el etanol.

### Masa Madre: El Cultivo Milenario

La masa madre es un cultivo simbiótico de levaduras silvestres (*Candida milleri*, *Kazachstania exigua*) y bacterias lácticas (*Lactobacillus sanfranciscensis*, *L. brevis*). Su mantenimiento requiere disciplina:

| Parámetro | Valor óptimo | Consecuencia si se desvía |
|-----------|-------------|--------------------------|
| Ratio harina:agua | 1:1 (100% hidratación) | < 1:1 → cultivo denso, lento; > 1:1 → acelera pero pierde fuerza |
| Temperatura | 22–26 °C | < 18 °C → dominan lactobacilos (muy ácido); > 30 °C → dominan levaduras (poco complejo) |
| Frecuencia de alimentación | Cada 12–24 h a temp. ambiente | > 48 h sin alimentar → exceso de ácido acético, aroma a acetona |
| Ratio de refresco | 1:5:5 (cultivo:harina:agua) | Más cultivo = más ácido; menos = más tiempo de fermentación |

> 🍞 **Mito derribado:** La masa madre no es "más sana" que el pan con levadura comercial en términos nutricionales. Sin embargo, la fermentación prolongada **reduce fitatos** (mejorando absorción de minerales), genera **ácidos orgánicos** que actúan como conservantes naturales, y desarrolla un perfil aromático incomparablemente más complejo.

---

## Recetas como Algoritmos

<a id="recetas"></a>

### Braise Universal (Braseado)

Toda receta de braseado sigue el mismo algoritmo, independientemente de la proteína:

```python
def braise(proteina: str, liquido: str, aromaticos: list[str],
           tiempo_h: float = 3.0, temp_c: float = 150.0) -> str:
    """
    Algoritmo universal de braseado.

    Pasos:
    1. Sellar la proteína (Maillard)
    2. Construir sofrito con aromáticos
    3. Desglasar con el líquido
    4. Cocción lenta y baja
    5. Reducir la salsa
    """
    pasos = []

    # Paso 1: Sear a fuego alto
    pasos.append(f"Secar {proteina} con toallas de papel")
    pasos.append(f"Sellar {proteina} en aceite humeante (230°C) — 2-3 min por lado")

    # Paso 2: Sofrito
    pasos.append(f"Sudar {', '.join(aromaticos)} en la misma olla — 5-7 min")

    # Paso 3: Desglasar
    pasos.append(f"Desglasar con {liquido}, raspando los fondos (sucs)")

    # Paso 4: Cocción lenta
    pasos.append(f"Cubrir hasta 2/3 la pieza. Tapar. Horno a {temp_c}°C por {tiempo_h}h")

    # Paso 5: Salsa
    pasos.append("Retirar proteína. Reducir líquido a 1/3 del volumen. Montar con mantequilla.")

    return "\n".join(f"  {i+1}. {p}" for i, p in enumerate(pasos))
```

### Variaciones del Algoritmo

| Proteína | Líquido | Aromáticos | Tiempo | Temp. | Platillo |
|----------|---------|-----------|--------|-------|---------|
| Osobuco | Vino blanco + fondo | Zanahoria, apio, cebolla | 3 h | 150 °C | Ossobuco alla Milanese |
| Costilla corta | Vino tinto + fondo | Mirepoix + tomillo + laurel | 3.5 h | 150 °C | Short ribs braseadas |
| 🐓 Muslos de pollo | Cerveza + mostaza | Cebolla, ajo, hongos | 1.5 h | 160 °C | Coq à la bière |
| 🐑 Pierna de cordero | Fondo + tomate | Ajo, romero, anchoas | 4 h | 140 °C | Gigot braisé |
| 🥬 Coles de Bruselas | Sidra | Manzana, tocino, salvia | 45 min | 170 °C | Braise vegetariano invernal |

> 🧑‍🍳 **Principio del braseado:** El líquido **no debe cubrir** la pieza completamente. La parte sumergida se cuece por convección; la expuesta se cuece por el vapor atrapado bajo la tapa. Esta dualidad crea una corteza superior distinta de la base tierna.

---

## Conversión de Unidades y Fórmulas

<a id="fórmulas"></a>

### Tabla de Equivalencias

| Medida | Equivalencia métrica | Notas |
|--------|---------------------|-------|
| 1 cup (US) | 236.6 mL | Para líquidos |
| 1 cup harina | ~125 g | Varía por tipo: integral 130 g, 00 fina 115 g |
| 1 cup azúcar | ~200 g | Azúcar granulada |
| 1 tbsp | 14.8 mL | Cucharada americana |
| 1 tsp | 4.9 mL | Cucharadita americana |
| 1 oz (peso) | 28.35 g | Onza avoirdupois |
| 1 fl oz | 29.57 mL | Onza fluida |
| 1 lb | 453.6 g | Libra |
| 1 stick mantequilla | 113 g | = 1/2 cup = 8 tbsp |

### Fórmula Panadera

En panadería profesional, todos los ingredientes se expresan como **porcentaje del peso de la harina** (que siempre es 100%). Esto permite escalar recetas trivialmente:

$$m_i = P_i \times m_{\text{harina}} / 100$$

#### Ejemplo: Baguette Tradicional

| Ingrediente | Porcentaje panadero | Para 1 kg de harina | Para 500 g de harina |
|------------|--------------------|--------------------|---------------------|
| Harina T65 | 100% | 1,000 g | 500 g |
| Agua | 68% | 680 g | 340 g |
| Sal | 2% | 20 g | 10 g |
| Levadura fresca | 0.8% | 8 g | 4 g |

### Cálculo de ABV en Fermentación

El contenido de alcohol por volumen (ABV) en bebidas fermentadas se estima con la densidad inicial (OG) y final (FG), medidas con un hidrómetro o refractómetro:

$$\text{ABV} \approx (OG - FG) \times 131.25$$

Ejemplo: una cerveza con $OG = 1.052$ y $FG = 1.010$:

$$\text{ABV} = (1.052 - 1.010) \times 131.25 = 5.5\%$$

### Escalado de Recetas y Proporciones

Para escalar una receta de $n_1$ porciones a $n_2$ porciones:

$$m_{\text{nuevo}} = m_{\text{original}} \times \frac{n_2}{n_1}$$

Sin embargo, **no todos los ingredientes escalan linealmente**:

- **Especias y sal:** Escalan al ~80% del factor (la intensidad percibida no es lineal)
- **Levaduras:** Escalan inversamente con el tiempo de fermentación disponible
- **Gelificantes (gelatina, agar):** Escalan proporcionalmente al volumen de líquido, no al número de porciones
- **Tiempos de cocción:** Escalan con el volumen, no con la masa, siguiendo aproximadamente:

$$t_2 \approx t_1 \times \left(\frac{V_2}{V_1}\right)^{2/3}$$

> 📐 **Truco de panadero:** Para convertir recetas americanas (cups) a peso, invierte primero en una balanza digital de 0.1 g de precisión. Es la herramienta más transformadora que puedes tener en la cocina. Las medidas volumétricas introducen errores de hasta ±20% en ingredientes secos.

---

### Glosario Rápido

| Término | Definición |
|---------|-----------|
| *Brunoise* | Corte en cubos de 3 mm |
| *Chiffonade* | Corte en tiras finas de hojas verdes |
| *Desglasar* | Añadir líquido a una sartén caliente para disolver los fondos caramelizados |
| *Emulsión* | Mezcla estable de dos líquidos inmiscibles (agua + grasa) |
| *Fond* / *Sucs* | Residuos caramelizados adheridos al fondo de la sartén |
| *Juliana* | Corte en bastones de 3 mm × 3 mm × 5 cm |
| *Maillard* | Reacción de pardeamiento no enzimático entre aminoácidos y azúcares |
| *Mirepoix* | Base aromática: 50% cebolla, 25% zanahoria, 25% apio |
| *Nappe* | Consistencia de una salsa que cubre el dorso de una cuchara |
| *Temperar* | Igualar temperaturas gradualmente (ej: huevo frío → mezcla caliente) |

---

> 🏅 **Reto culinario:** Prepara un **demi-glace** clásico desde cero: huesos de res tostados → fondo oscuro (24 h) → reducción con espagnole → colar → reducir a la mitad. El resultado es la salsa madre más compleja de la cocina francesa, y la base de decenas de salsas derivadas.

~~Este manual cubre solo técnicas fundamentales — las técnicas de pastelería y cocina molecular se cubrirán en la tercera edición.~~
