# Ejercicio 2 — Descripción PEAS de agentes inteligentes

## Contexto

En el capítulo 2 de *Artificial Intelligence: A Modern Approach* (Russell & Norvig),
un agente se entiende mejor cuando se especifica su **entorno de tarea**. Una forma
estándar de hacerlo es la descripción **PEAS**:

| Letra | Significado | Pregunta guía |
|---|---|---|
| **P** | *Performance* (medida de desempeño) | ¿Cómo se evalúa el éxito del agente? |
| **E** | *Environment* (entorno) | ¿En qué mundo opera? ¿Quién más actúa ahí? |
| **A** | *Actuators* (actuadores) | ¿Qué acciones puede ejecutar? |
| **S** | *Sensors* (sensores) | ¿Qué información puede percibir? |

Este ejercicio **no requiere programar**. Consiste en analizar distintos tipos de
aplicaciones reales y describir cada una con el esquema PEAS.

## Objetivo

Para cada una de las **8 aplicaciones** listadas abajo, redacta una descripción
PEAS completa y coherente. Debes pensar como diseñador del agente: qué optimiza,
dónde actúa, con qué puede mover o modificar el mundo, y qué puede observar.

## Aplicaciones a analizar

Describe PEAS para cada una de estas aplicaciones:

1. **Asistente virtual de voz** (p. ej. Siri, Alexa o Google Assistant en un altavoz inteligente).
2. **Robot aspirador doméstico** (p. ej. Roomba u otro robot que limpia pisos de un departamento).
3. **Sistema de recomendación de streaming** (p. ej. Netflix o Spotify que sugiere películas o canciones).
4. **Vehículo autónomo en ciudad** (conducción sin conductor en calles urbanas con tráfico y peatones).
5. **Agente de trading algorítmico en bolsa** (compra y venta automática de acciones en mercados financieros).
6. **Sistema de diagnóstico médico asistido por IA** (apoya a un médico a interpretar síntomas e imágenes clínicas).
7. **Dron de inspección de infraestructura** (revisa grietas, corrosión o fugas en puentes, tuberías o líneas eléctricas).
8. **Agente jugador de ajedrez** (programa que compite contra un humano u otro agente en partidas completas).

## Instrucciones

Para **cada** aplicación entrega una sección con este formato:

```markdown
### N. Nombre de la aplicación

- **Performance:** ...
- **Environment:** ...
- **Actuators:** ...
- **Sensors:** ...
```

### Criterios de calidad

- **Performance:** incluye métricas concretas (precisión, tiempo, costo, satisfacción del usuario, ganancia, seguridad, etc.), no solo “hacerlo bien”.
- **Environment:** menciona si es parcialmente observable o totalmente observable, si es estocástico o determinista, episódico o secuencial, estático o dinámico, y discreto o continuo (según aplique).
- **Actuators:** lista acciones reales que el agente puede ejecutar, no capacidades vagas.
- **Sensors:** lista percepciones concretas (cámara, micrófono, API, historial de usuario, cotizaciones de mercado, etc.).

### Ejemplo breve (solo como referencia de formato)

**Aplicación:** termostato inteligente de una casa.

- **Performance:** mantener la temperatura deseada con mínimo consumo de energía y máxima comodidad del habitante.
- **Environment:** interior de una vivienda; cambia con clima exterior, ventanas abiertas y presencia de personas.
- **Actuators:** encender/apagar calefacción o aire acondicionado; ajustar temperatura objetivo; enviar alertas al usuario.
- **Sensors:** termómetro interior, horario, presencia (movimiento), lectura de clima exterior vía internet.

> El termostato **no** está en la lista de las 8 aplicaciones: es solo un ejemplo.
> Debes completar las ocho aplicaciones indicadas arriba.

## Entrega

Un documento (Markdown o PDF) con las **8 descripciones PEAS**, numeradas y con título
claro para cada aplicación.

Opcional pero recomendado: al final de cada descripción, añade **2–3 líneas** que
justifiquen por qué clasificaste el entorno como observable/estocástico/secuencial/etc.

## Criterios de aceptación

- No usar IA para generar las respuestas de este ejercicio.
- Hay exactamente **8** descripciones PEAS, una por cada aplicación de la lista.
- Cada descripción tiene los cuatro componentes (**P**, **E**, **A**, **S**) claramente identificados.
- Las respuestas son específicas de la aplicación (evita copiar la misma descripción genérica para todas).
- El entorno (**E**) incluye al menos una clasificación AIMA (p. ej. parcialmente observable, estocástico, secuencial).
- Redacción clara, en español, sin ambigüedades evidentes.

## Pistas

- Un mismo tipo de agente puede tener **distintos PEAS** según el contexto: un dron de inspección en un túnel no es igual que uno en un campo abierto.
- **Performance** y **Environment** suelen confundirse: la medida de desempeño dice *qué optimizas*; el entorno dice *dónde ocurre la tarea y qué condiciones enfrentas*.
- Si dudas entre dos sensores o actuadores, pregúntate: *¿esto lo usa el agente para decidir, o solo el humano que lo supervisa?* Solo cuenta lo que el **agente** percibe o controla.

## Desarrollo

### 1. Asistente virtual de voz

- **Performance:** Exactitud de las respuestas, tiempo utilizado para procesar instrucciones, cantidad de instrucciones para poder realizar una peticion. 
- **Environment:** Voz del usuario, ruido externo.
Clasificacion AIMA: Parcialmente observable
- **Actuators:** Búsqueda web, verificación de fuentes, generar recordatorios, reproducir musica.
- **Sensors:** Micrófono, red inalámbrica.
Considero que es parcialmente observable debido a que se depende de un micrófono que detecta sonidos para poder realizar una acción, lo cual no tiene completo control debido a aspectos desconocidos como el ruido.

### 2. Robot aspirador doméstico

- **Performance:** Tiempo sin detectar suciedad, distancia recorrida número de recamaras limpias.
- **Environment:** Cuartos, baños, puertas, escaleras, personas, mascotas, muebles.
Clasificacion AIMA: Dinámico
- **Actuators:** Avanzar, rotar, aspirar, esperar
- **Sensors:** Sensor infrarrojo, cámara, giroscopio
Considero que es dinámico porque el desempeño del robot cambia conforme pasa el tiempo, cada momento que pasa en lo que el robot decide una acción el entorno puede variar.

### 3. Sistema de recomendación de streaming

- **Performance:** Exactitud de las respuestas, tiempo utilizado para procesar instrucciones, tiempo de uso por el usuario. 
- **Environment:** Paquetes de red, perfiles de usuario.
Clasificacion AIMA: Discreto
- **Actuators:** Buscar música, armar playlist, recomendar canciones
- **Sensors:** Historial de reproducción, calificaciones previas, historial de búsqueda.
Se considera discreto debido a que las percepciones y las acciones están delimitadas, por lo que tiene un número definido de estados.

### 4. Vehículo autónomo en ciudad

- **Performance:** Distancia recorrida, número de clientes atendidos en un día, calificación por parte de los usuarios, cantidad de gasolina/energía utilizada.
- **Environment:** Calles, automóviles, peatones, clima, topes, baches, señalización, anilmales.
Clasificacion AIMA: Secuencial
- **Actuators:** Tocar claxon, rotar el volante, acelerar, frenar, abrir/cerrar puertas, avanzar, dar reversa.
- **Sensors:** Sensor infrarrojo, acelerómetro, cámara, giroscopio, GPS, micrófono.
Se considera secuencial debido a que las acciones que realiza no quedan aisladas en una instancia, por ejemplo, el carro debe tomar decisiones de acuerdo a su posición y velocidad que pueden afectar futuras acciones como estacionarse o dar la vuelta en una calle.

### 5. Agente de trading algorítmico en bolsa

- **Performance:** Cantidad de dinero ganado, cantidad de acciones compradas, cantidad de operaciones realizadas.
- **Environment:** Paquetes de red, páginas web.
Clasificacion AIMA: Episódico
- **Actuators:** Comprar, vender
- **Sensors:** Cierre de mercado diario (API), noticias financieras (scrapping de páginas web)
Considero que es episódico porque las acciones realizables no dependen de las acciones anteriores, en cambio, solo importa realizar una acción cuando se percibe el entorno.

### 6. Sistema de diagnóstico médico asistido por IA

- **Performance:** Pacientes diagnosticados correctamente, tiempo de atención al paciente, calificación por parte de los pacientes.
- **Environment:** Paciente, consultorio, doctor/enfermero.
Clasificacion AIMA: Estocástico, parcialmente observable.
- **Actuators:** Análisar sintomas, tomar medidas, realizar preguntas de seguimiento, sacar conclusiones.
- **Sensors:** Cámara, micrófono, báscula, sensor infrarrojo.
Se consideraría estocástico y parcialmente observable porque el hecho de realizar un diagnóstico de un paciente no es 100% certero, puede existir aspectos del paciente que no se hayan considerado, lo cual puede afectar el diagnóstico.

### 7. Dron de inspección de infraestructura

- **Performance:** Calificación por parte del usuario, número de incidencias reportadas, cantidad de errores de los reportes generados.
- **Environment:** Trabajadores, estructura de la obra, clima, animales.
Clasificacion AIMA: Dinámico
- **Actuators:** Ascender, descender, tomar fotografía, tomar un video, enviar reporte/información, rotar, analizar imágenes/cuadros.
- **Sensors:** Cámara, sensor infrarrojo, micrófono
Considero que es dinámico porque el dron tiene que adaptarse a un ambiente que cambia conforme pasa el tiempo, el factor más presente sería el clima o el viento, el cual el dron tiene que adaptarse.

### 8. Agente jugador de ajedrez

- **Performance:** Número de partidas ganadas, tiempo de procesamiento/tomar decisiones
- **Environment:** Tablero, reloj
Clasificacion AIMA: Observable y determinista
- **Actuators:** Mover una pieza
- **Sensors:** Cámara, cronómetro
Considero que es observable porque el tablero donde se juega el ajedrez contiene toda la información necesaria para poder realizar una acción; además sería determinista porque sabemos como funciona cada pieza y que el estado cambia por las acciones del agente.