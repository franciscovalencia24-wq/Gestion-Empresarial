# Expediente Técnico-Estratégico: Altus Core B2B (Postulación Corfo)

## 1. Resumen Ejecutivo y Modelo de Negocio
**Altus Core** es la plataforma SaaS institucional desarrollada por **ALTUS AI SpA**, diseñada para revolucionar la consolidación y planificación patrimonial en Chile. Mientras que **FV Asesorías e Inversiones SpA** opera como el brazo asesor financiero (front-office) de trato directo con clientes de alto patrimonio, **ALTUS AI SpA** actúa como el proveedor tecnológico independiente (SaaS B2B).
El modelo de negocio de Altus Core para el segmento institucional (grandes empresas, corporativos, gerencias de RRHH y minería) se basa en un esquema **SaaS B2B2C**. Se cobrará una licencia anual por **usuario activo corporativo**, permitiendo a las empresas ofrecer como beneficio ejecutivo el "Reporte Patrimonial 360", escalando rápidamente sin los cuellos de botella de la asesoría 1-a-1 tradicional.

## 2. Propuesta de Valor & Reporte 360
Altus Core entrega un valor inédito en el mercado local a través de su **Reporte Patrimonial 360**, un agregador patrimonial multimodal que consolida:
- **Activos Financieros e Inmobiliarios:** Integración holística del patrimonio.
- **Auditoría de Pasivos:** Conexión automatizada con el Informe de Deudas de la Comisión para el Mercado Financiero (CMF).
- **Protección Familiar:** Análisis del informe "Conoce tu Seguro" CMF, detectando riesgos de liquidez sucesoria y pólizas cautivas bancarias.
- **Optimización Tributaria Activa:** Motores algorítmicos para el cálculo de Reliquidación (Art. 47 LIR) y Deducción de Períodos de Exceso (DPE) de AFP.

**Punto clave:** La plataforma consolida, analiza y diagnostica de forma determinista y estandarizada, **sin requerir la custodia de fondos de terceros**, eludiendo las complejas cargas regulatorias y altos costos de capital de una AGF o Corredora de Bolsa tradicional.

## 3. Benchmarking & Barreras de Entrada
El ecosistema WealthTech en Chile está polarizado entre soluciones transaccionales (Robo-advisors B2C como Fintual, Racional) y software extranjero de back-office para Family Offices ultra-ricos (Addepar, Masttro), pero carece de un **agregador patrimonial B2B2C enfocado en ejecutivos C-Level locales con un motor tributario integrado**.
- **Family Offices Locales (e.g., Alcalá, Capital Advisors):** Operan con modelos de alta fricción, basados en hojas de cálculo, altamente dependientes del capital humano y reservados solo para patrimonios líquidos sobre $5MM USD.
- **Plataformas B2C Transaccionales:** Se centran en la colocación de fondos mutuos propios. No realizan optimización tributaria compleja ni cruzan pólizas CMF con deudas hipotecarias y riesgo sucesorio.
- **Barreras de Entrada de Altus Core:** 
  1. *Efecto Red Normativo Local:* Motor de algoritmos pre-entrenado en la Ley sobre Impuesto a la Renta chilena (LIR) y adaptado a los formatos estructurados de las instituciones chilenas (CMF, SII).
  2. *Infraestructura Híbrida y Diagnóstico Integrado:* Integración nativa entre el análisis financiero, el flujo inmobiliario y el dictamen de optimización tributaria automatizado.

## 4. Arquitectura de Ciberseguridad & Protección de Datos
La plataforma Altus Core está diseñada con estándares de seguridad bancaria, en estricto cumplimiento con la **Ley 21.096 (Protección de Datos Personales)** y los principios rectores de la **Ley 21.521 (Fintec Chile)**.
- **Cifrado de Grado Institucional:** Se emplean algoritmos AES-256 (implementados nativamente en `src/security/encryption.py` mediante la suite de criptografía Fernet) para el cifrado de datos en reposo y en tránsito (TLS 1.3). Todos los PII (RUT, Nombre, Montos) permanecen ofuscados en la persistencia.
- **Arquitectura Zero-Knowledge y Pseudonimización:** Los motores de cálculo (e.g., Reliquidación, Seguros) procesan IDs pseudonimizados. En el evento extremo de una filtración de la base de datos transaccional, el payload extraído carece de valor sin las llaves maestras de cifrado (hardware/cloud KMS segregado).
- **Protección de Código Fuente y Algoritmos:** Todos los pipelines y modelos son propiedad exclusiva de ALTUS AI SpA, resguardados mediante estrictas cláusulas de confidencialidad (NDA institucionales mutuos) para contrapartes corporativas B2B, mitigando drásticamente el riesgo de fuga de Propiedad Intelectual.

## 5. Cuestionario de Defensa Corfo (Q&A)
**Q1. ¿Cuál es el grado de innovación tecnológica (Novedad)?**
*R:* Altus Core es el primer motor consolidador patrimonial nativo chileno que fusiona en un solo reporte el estado financiero, la auditoría de pólizas CMF y algoritmos de optimización tributaria complejos (DPE, Reliquidación), operando como un SaaS puro y determinista sin custodia de activos.

**Q2. ¿Cómo aborda y penetra el mercado institucional B2B?**
*R:* Se comercializa la plataforma como un programa de "Bienestar y Estructuración Financiera Ejecutiva" a grandes corporaciones (e.g. Minería, Banca). La empresa paga la licencia SaaS B2B anual y sus gerentes acceden al Reporte 360 de forma totalmente confidencial y automatizada.

**Q3. ¿Cuál es la escalabilidad del modelo de negocio?**
*R:* Al ser una plataforma estandarizada (motores en Python/Pandas) y no requerir analistas financieros manuales ni servicios de custodia, la infraestructura cloud puede atender a decenas de miles de ejecutivos simultáneamente con un costo marginal tecnológico tendiente a cero.

**Q4. ¿Cómo mitigan los riesgos de ciberseguridad y fuga de datos en el entorno corporativo?**
*R:* A través de cifrado AES-256 (`src/security/encryption.py`), pseudonimización de identidades en el ecosistema de cálculo y un cumplimiento normativo preventivo diseñado acorde a los más altos estándares de la Ley Fintec y mejores prácticas bancarias.

**Q5. ¿Cómo resguardan la propiedad intelectual (PI) del motor algorítmico?**
*R:* Mediante secretos industriales (código ofuscado/compilado en producción), Acuerdos de Confidencialidad (NDAs) institucionales que prohíben explícitamente la ingeniería inversa a clientes B2B, y la separación jurídica estratégica: FV Asesorías asume el front-office y ALTUS AI concentra y blinda la PI.

**Q6. ¿Quiénes son sus principales competidores y cuál es el diferenciador clave?**
*R:* Competimos indirectamente con Robo-advisors B2C (enfocados solo en AUM de inversiones) y Multi-Family Offices (caros, manuales y de nicho ultra-rico). Nuestro diferenciador es la visión 360° algorítmica (Tributaria + Riesgo CMF + Inversiones) accesible a fracción del costo para el segmento C-Level y gerencial.

**Q7. ¿Por qué el proyecto es pertinente para co-financiamiento y patrocinio Corfo?**
*R:* Porque democratiza el acceso a servicios de Family Office de alta sofisticación mediante ingeniería de software nacional (WealthTech), digitalizando un sector análogo, exportando valor tecnológico y mejorando la eficiencia financiera del mercado laboral altamente calificado.

**Q8. ¿Cuál es la principal barrera de entrada que han levantado frente a competidores extranjeros?**
*R:* La ingesta e inferencia nativa de documentos públicos y regulaciones de Chile (Parseo con IA de PDFs CMF, SII) y su cruce con motores de optimización de la Ley sobre Impuesto a la Renta. Plataformas top globales como Addepar carecen de localización impositiva y regulatoria chilena profunda.

**Q9. ¿Cómo aseguran la fidelización y retención de las grandes empresas (B2B)?**
*R:* El Reporte 360 genera un ciclo de valor recurrente (e.g., monitoreo continuo de deudas, optimización en la Operación Renta anual), lo que fomenta un efecto de "lock-in" estructural en los paquetes de compensación e incentivos de Recursos Humanos.

**Q10. ¿Requiere Altus Core inscripción como Asesor de Inversiones en la CMF?**
*R:* No. Debido a que ALTUS AI SpA es la entidad desarrolladora y proveedora de la tecnología SaaS (una herramienta de cálculo y software financiero) y no ejecuta custodia ni intermediación de valores, la carga regulatoria directa se minimiza. Si el cliente requiere asesoría de inversión regulada, FV Asesorías actúa como la entidad registrada competente.
