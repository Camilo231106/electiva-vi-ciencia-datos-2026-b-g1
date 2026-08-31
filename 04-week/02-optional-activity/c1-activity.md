# Actividad Práctica – C1 Activity – Semana 04
## Diagnóstico de datos de un proceso — Caso aplicado: Servientrega

**Autor:** Cristian Camilo Quiguanas Ossa
**Facultad de Ingeniería, Corporación Universitaria del Huila (CORHUILA)**
**Ciencia de Datos · Electiva VI · 2026-B**
**Agosto de 2026**

---

## 0. La empresa

**Servientrega** es una compañía colombiana de mensajería y logística fundada el 29 de noviembre de 1982 por los hermanos Jesús y Luz Mary Guerrero, que inició operaciones con solo tres envíos diarios entre Bogotá, Cali y Buenaventura (La Nación, 2019; Encolombia, 2020). Hoy es la empresa de mensajería con mayor posicionamiento de Colombia, con más de 3.500 Centros de Soluciones que cubren cerca del 98 % del territorio nacional, presencia en varios países de América y España, y servicios como "Hoy Mismo", "Ya Mismo" (entregas en horas) y rastreo de envíos vía app y código QR (Encolombia, 2020; Semana, 2023). Esta cobertura, volumen de envíos y digitalización del servicio la convierten en un caso real y pertinente para aplicar un diagnóstico de datos de proceso.

---

## 1. Proceso, problema y pregunta de datos

**Proceso elegido:** entrega de última milla de encomiendas en la operación regional de Servientrega en el Huila (Neiva y municipios cercanos), desde que el paquete sale del Centro de Soluciones hasta que se confirma la entrega al destinatario.

**Problema real:** aunque Servientrega promete franjas de entrega como "Hoy Mismo" o "Ya Mismo" (Semana, 2023), en zonas con topografía difícil, vías rurales y alta variabilidad climática —como buena parte del Huila— un porcentaje de los envíos no se cumple dentro del tiempo ofrecido. Esto genera reprocesos (segundos intentos de entrega), llamadas al call center, reclamos y desgaste de la promesa de "entrega segura" que es la marca histórica de la compañía (Bienpensado, 2014).

**Pregunta de datos que se quiere responder:**

> ¿Qué factores operativos, geográficos y externos explican mejor los incumplimientos de la ventana de entrega prometida en la operación de última milla de Servientrega en el Huila, y qué tan probable es que una guía específica se retrase dado su origen, destino, hora de despacho y condiciones del entorno?

---

## 2. Inventario de datos

Se identificaron 7 fuentes/campos de datos disponibles (o fácilmente integrables) en la operación real de Servientrega, clasificados según su nivel de estructura.

| # | Fuente / campo | Descripción | Tipo de dato | Formato típico |
|---|-----------------|-------------|--------------|-----------------|
| 1 | Sistema de guías y trazabilidad (core logístico) | Número de guía, origen, destino, Centro de Soluciones, fecha/hora de admisión, fecha/hora prometida y fecha/hora real de entrega | **Estructurado** | Tablas de base de datos relacional |
| 2 | App de rastreo / lector de código de barras del mensajero | Escaneo por punto de control (admisión, bodega, en ruta, entregado, con o sin código QR de pago) | **Estructurado** | Registros de eventos (BD / CSV) |
| 3 | GPS del vehículo o dispositivo del mensajero | Latitud, longitud, velocidad y marca de tiempo durante el recorrido de reparto | **Estructurado** | Stream de eventos (Parquet / BD de series de tiempo) |
| 4 | API de tráfico y rutas (Google Maps / HERE) | Congestión, tiempo estimado de recorrido, cierres viales por tramo | **Semiestructurado** | JSON |
| 5 | API meteorológica (OpenWeather u otra) | Lluvia, visibilidad, alertas por deslizamiento en vías del Huila | **Semiestructurado** | JSON |
| 6 | Registros del call center / chat de PQR | Texto libre de quejas, motivo de reclamo, calificación del cliente sobre el servicio | **No estructurado** | Texto libre (logs de chat, correos, grabaciones transcritas) |
| 7 | Fotos de "entrega segura" (evidencia) | Foto o firma digital tomada por el mensajero al momento de confirmar la entrega | **No estructurado** | Imágenes (JPEG/PNG) |

**Resumen de clasificación:** 3 fuentes estructuradas, 2 semiestructuradas y 2 no estructuradas, evidenciando la **variedad** típica de un problema de Big Data dentro de la operación real de la compañía.

---

## 3. Tipo de analítica aplicable y justificación de Big Data

### 3.1 Tipos de analítica a aplicar

| Tipo de analítica | Pregunta que responde | Aplicación en Servientrega |
|---|---|---|
| **Descriptiva** | ¿Qué pasó? | Dashboard de % de guías entregadas dentro de la franja prometida, por Centro de Soluciones, municipio y franja horaria en el Huila. |
| **Diagnóstica** | ¿Por qué pasó? | Cruce de guías retrasadas con clima, tráfico y tipo de vía (urbana/rural) para identificar causas raíz, p. ej. lluvias fuertes en vías terciarias que conectan con municipios como Pitalito o Garzón. |
| **Predictiva** | ¿Qué va a pasar? | Modelo que estima, al momento de despachar una guía, la probabilidad de que no cumpla la ventana prometida, según destino, hora de salida y pronóstico del clima. |
| **Prescriptiva** | ¿Qué debo hacer? | Motor de recomendación que sugiere reordenar rutas, adelantar despachos o reasignar mensajeros en zonas de alto riesgo antes de que ocurra el incumplimiento. |

Se recomienda una implementación progresiva —descriptiva → diagnóstica → predictiva → prescriptiva—, dado que los niveles predictivo y prescriptivo solo son confiables si la base descriptiva y diagnóstica está bien construida (Digital.ai, 2023; Metrica Software, 2026).

### 3.2 ¿Es un caso de Big Data? Justificación con las "V"

Sí. El concepto de Big Data nació con las 3V de Laney (volumen, velocidad, variedad) y luego se amplió con veracidad y valor (TechTarget, s.f.; Sounder, 2024). Aplicado a la operación real de Servientrega:

- **Volumen:** Servientrega opera con más de 3.500 Centros de Soluciones a nivel nacional (Encolombia, 2020); solo en la regional Huila se generan miles de guías diarias, y si se suma el GPS de cada mensajero reportando cada pocos segundos, el volumen de registros crece exponencialmente.
- **Velocidad:** los escaneos de trazabilidad, el GPS y las API de tráfico/clima producen datos en tiempo casi real, indispensables para servicios de entrega en horas como "Ya Mismo" (Semana, 2023).
- **Variedad:** conviven datos estructurados (sistema de guías, GPS), semiestructurados (APIs externas) y no estructurados (PQR, fotos de entrega segura), tal como muestra el inventario de la sección 2.
- **Veracidad:** el GPS puede fallar en zonas rurales del Huila con poca señal, las fotos pueden ser borrosas y las PQR pueden estar mal clasificadas, por lo que la calidad del dato debe validarse antes de usarse en los modelos.
- **Valor:** reducir los incumplimientos de entrega protege directamente el activo de marca más importante de la compañía —"Servientrega es entrega segura"— y reduce costos de reprocesos y llamadas al call center (Bienpensado, 2014; Teradata, 2022).

La combinación de estas cinco dimensiones confirma que este es un problema de Big Data real y no algo abordable con una simple hoja de cálculo.

---

## 4. Ciclo de vida del proyecto de datos

```
 ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
 │ PREGUNTA  │ --> │  OBTENER  │ --> │  LIMPIAR  │ --> │ ANALIZAR  │ --> │VISUALIZAR │
 └───────────┘     └───────────┘     └───────────┘     └───────────┘     └─────┬─────┘
                                                                                │
                                                                                v
                                                                          ┌───────────┐
                                                                          │  DECIDIR  │
                                                                          └───────────┘
```

**Aplicación al caso Servientrega – regional Huila:**

1. **Pregunta:** ¿qué explica los incumplimientos de entrega en el Huila y qué tan probable es que una guía específica se retrase?
2. **Obtener:** extraer datos del sistema de guías y trazabilidad, del GPS de los mensajeros, consumir las API de tráfico y clima, y recolectar las PQR del call center y las fotos de entrega segura de los Centros de Soluciones del Huila.
3. **Limpiar:** eliminar guías duplicadas o canceladas, corregir coordenadas GPS erróneas en zonas rurales, estandarizar nombres de municipios y veredas, normalizar el texto de las PQR y descartar fotos ilegibles.
4. **Analizar:** calcular el % de cumplimiento por Centro de Soluciones (descriptiva), correlacionar incumplimientos con clima/vías rurales (diagnóstica), entrenar un modelo que prediga el riesgo de retraso por guía (predictiva) y simular reasignaciones de ruta (prescriptiva).
5. **Visualizar:** construir un dashboard con mapa de calor de incumplimientos por municipio del Huila, tendencia mensual de cumplimiento y panel de alerta temprana para guías en riesgo.
6. **Decidir:** con base en las alertas, el equipo operativo de la regional ajusta horarios de despacho, refuerza mensajeros en zonas críticas (p. ej. vías rurales en épocas de lluvia) y comunica proactivamente al cliente cuando el riesgo de retraso es alto; el ciclo se reinicia midiendo el impacto de estos ajustes.

---

## 5. Problem & Data (English section – README requirement)

Servientrega is Colombia's leading courier and logistics company, founded in 1982, and it promises delivery windows such as "Hoy Mismo" and "Ya Mismo" to its customers nationwide. In the Huila regional operation, however, a portion of last-mile deliveries fail to meet the promised time window because of difficult terrain, rural roads, and highly variable weather conditions. The company currently lacks a clear, data-driven view of which factors most often cause these delays and which shipments are most at risk before they are dispatched. Answering this requires combining structured tracking and GPS data from the company's own systems with semi-structured traffic and weather data from external APIs, plus unstructured data such as customer complaint logs and delivery-proof photos. The analytics approach needs to progress from descriptive dashboards showing how often delays occur, to diagnostic analysis explaining why they happen, to predictive models estimating the delay risk of each new shipment, and finally to prescriptive recommendations for adjusting routes and dispatch schedules. Given the volume of shipments, the near real-time nature of tracking and weather data, the variety of data formats involved, and the data quality challenges typical of rural GPS coverage, this is a genuine Big Data problem for the company's regional operation.

---

## Referencias bibliográficas

- Bienpensado. (2014). *Breve historia de las marcas: Servientrega*. Recuperado de https://bienpensado.com/historia-marca-servientrega/
- Digital.ai. (2023). *Gartner's Analytics Maturity Model*. Recuperado de https://digital.ai/catalyst-blog/it-decision-making-through-the-lens-of-gartners-analytics-maturity-model/
- Domo. (s.f.). *The 4 Types of Data Analytics Explained + Examples*. Recuperado de https://www.domo.com/learn/article/data-analytics-types
- Encolombia. (2020). *Servientrega es Colombia, cobertura de Servientrega*. Recuperado de https://encolombia.com/economia/empresas/logistica/servientrega-es-colombia/
- La Nación. (2019). *Servientrega*. Recuperado de https://lanacion.com.ec/breve-historia-de-las-marcas-servientrega/
- Metrica Software. (2026). *4 Types of Data Analytics: Descriptive, Diagnostic, Predictive, Prescriptive*. Recuperado de https://metricasoftware.com/4-types-of-data-analytics-descriptive-diagnostic-predictive-prescriptive/
- Semana. (2023). *La empresa que revolucionó la mensajería en Colombia y hoy entrega paquetes en minutos*. Recuperado de https://www.semana.com/hablan-las-marcas/articulo/la-empresa-que-revoluciono-la-mensajeria-en-colombia-y-hoy-entrega-paquetes-en-minutos/202300/
- Sounder, R. (2024). *5 V's of Big Data Demystified — Volume, Velocity, Variety, Value & Veracity*. Medium. Recuperado de https://medium.com/@sounder.rahul/5-vs-of-big-data-demystified-volume-velocity-variety-value-veracity-61783552682f
- TechTarget. (s.f.). *What Are the 3 V's of Big Data?*. Recuperado de https://www.techtarget.com/whatis/definition/3Vs
- Teradata. (2022). *What are the 5 V's of Big Data?*. Recuperado de https://www.teradata.com/glossary/what-are-the-5-v-s-of-big-data

---

