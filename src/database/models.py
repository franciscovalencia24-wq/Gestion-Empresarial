from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from src.database.connection import Base
from datetime import datetime

class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(20), unique=True, index=True, nullable=False)
    nombre = Column(String(200), nullable=True)
    telefono = Column(String(30), nullable=True) 
    email = Column(String(150), nullable=True)
    ciudad = Column(String(100), nullable=True)
    
    # Nuevos campos específicos del Excel indicado
    nombre_asesor = Column(String(200), nullable=True)
    supervisor = Column(String(200), nullable=True)
    tipo_negocio = Column(String(100), nullable=True)
    monto_suscrito = Column(Float, nullable=True)
    saldo_administrado = Column(Float, nullable=True)
    origen_info = Column(String(150), nullable=True)
    titulo_profesional = Column(String(150), nullable=True)
    
    observaciones = Column(Text, nullable=True)
    status_contacto = Column(String(30), default="Pendiente")
    es_cliente = Column(Integer, default=0)
    
    # Representante Legal (Empresas PJ)
    nombre_rrll = Column(String(200), nullable=True)
    rut_rrll = Column(String(30), nullable=True)

    # Inteligencia OSINT (Fase 3)
    score_liquidez = Column(Integer, default=0)
    ultimo_evento = Column(String(500), nullable=True)
    fecha_hallazgo = Column(String(50), nullable=True)
    link_fuente = Column(String(500), nullable=True)
    origen_web = Column(Integer, default=0) # 1 si viene del bot scraper

    # Estado Previsional y Renta Vitalicia
    estado_previsional = Column(String(100), nullable=True) # Activo, Retiro Programado, Renta Vitalicia Simple, Renta Vitalicia Garantizada
    periodo_garantizado_rv_meses = Column(Integer, default=0)
    
    # Relaciones Fase D
    profile = relationship("ClientProfile", back_populates="prospect", uselist=False, cascade="all, delete-orphan")
    cartolas = relationship("CartolaSummary", back_populates="prospect", cascade="all, delete-orphan")
    portfolios = relationship("ClientPortfolio", back_populates="prospect", cascade="all, delete-orphan")
    properties = relationship("ClientProperty", back_populates="prospect", cascade="all, delete-orphan")
    insurances = relationship("ClientInsurance", back_populates="prospect", cascade="all, delete-orphan")
    inventories = relationship("ClientInventory", back_populates="prospect", cascade="all, delete-orphan")
    heirs = relationship("ClientHeir", back_populates="prospect", cascade="all, delete-orphan")
    debts = relationship("ClientDebt", back_populates="prospect", cascade="all, delete-orphan")
    companies = relationship("ClientCompany", back_populates="prospect", cascade="all, delete-orphan")
    company_shareholders = relationship("CompanyShareholder", back_populates="prospect", cascade="all, delete-orphan")
    company_representatives = relationship("CompanyRepresentative", back_populates="prospect", cascade="all, delete-orphan")
    macro_history = relationship("ClientMacroHistory", back_populates="prospect", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prospect(rut='{self.rut}', nombre='{self.nombre}', status='{self.status_contacto}')>"

    def get_related_prospects(self, db_session):
        """
        Retorna una lista de Prospects relacionados (bidireccional: dueños -> empresas y empresas -> dueños).
        Utilizado para heredar notas, audios y consultas Macro dinámicamente.
        """
        related_ids = set()
        
        def get_p_by_rut(r):
            if not r: return None
            r_clean = r.replace(".", "").upper()
            p = db_session.query(Prospect).filter_by(rut=r_clean).first()
            if not p:
                p = db_session.query(Prospect).filter_by(rut=r).first()
            return p

        # 1. Empresas que este prospecto posee
        for company in self.companies:
            p = get_p_by_rut(company.rut_empresa)
            if p:
                related_ids.add(p.id)
                    
        # 2. Socios/Accionistas de este prospecto (si es empresa)
        for socio in self.company_shareholders:
            p = get_p_by_rut(socio.rut)
            if p:
                related_ids.add(p.id)
                    
        # 3. Prospectos que declararon a este prospecto como su empresa
        from src.database.models import ClientCompany, CompanyShareholder
        my_clean = self.rut.replace(".", "").upper() if self.rut else ""
        
        if my_clean:
            inverse_companies = db_session.query(ClientCompany).all()
            for ic in inverse_companies:
                if ic.rut_empresa and ic.rut_empresa.replace(".", "").upper() == my_clean:
                    related_ids.add(ic.prospect_id)
                
            # 4. Prospectos que declararon a este prospecto como su socio
            inverse_socios = db_session.query(CompanyShareholder).all()
            for isocio in inverse_socios:
                if isocio.rut and isocio.rut.replace(".", "").upper() == my_clean:
                    related_ids.add(isocio.prospect_id)
            
        if self.id in related_ids:
            related_ids.remove(self.id)
            
        if related_ids:
            return db_session.query(Prospect).filter(Prospect.id.in_(list(related_ids))).all()
        return []


class ClientProfile(Base):
    """
    Perfil Avanzado del Cliente (Fase D).
    """
    __tablename__ = "client_profiles"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), unique=True)
    
    fecha_nacimiento = Column(Date, nullable=True)
    edad = Column(Integer, nullable=True)
    edad_actuarial = Column(Integer, nullable=True)
    
    # Nuevos Perfilamientos
    segmento_cliente = Column(String(50), nullable=True)
    tipo_persona = Column(String(20), default="PN")
    nivel_riesgo = Column(String(50), nullable=True)
    experiencia_inversiones = Column(String(50), nullable=True)
    
    estado_civil = Column(String(50), nullable=True)
    cantidad_herederos = Column(Integer, default=0)
    objetivo_inversion = Column(String(200), nullable=True)
    
    # Flags y Alertas
    secciones_omitidas = Column(Text, nullable=True) # JSON con las secciones marcadas como omitidas
    fecha_ultima_act_seguros = Column(DateTime, nullable=True)
    fecha_ultima_act_deudas = Column(DateTime, nullable=True)
    
    # Patrimonio
    patrimonio_inmobiliario = Column(Float, default=0.0)
    patrimonio_liquido = Column(Float, default=0.0)
    vehiculos = Column(Integer, default=0)
    
    # Flujos de Caja Opcionales (Requerimiento)
    ingresos_mensuales = Column(Float, nullable=True, default=0.0)
    egresos_mensuales = Column(Float, nullable=True, default=0.0)
    renta_anual_declarada = Column(Float, nullable=True, default=0.0) # Desde Carpeta Tributaria
    
    # Perfil de Inversión / Tributario
    nivel_riesgo = Column(String(50), nullable=True) # Conservador, Moderado, Agresivo
    perfil_tributario = Column(String(100), nullable=True)
    tramo_impositivo_estimado = Column(Float, nullable=True) # ej. 0.35 para 35%
    
    # Notas / Psicología / Alertas
    observaciones_estrategicas = Column(Text, nullable=True)
    notas_neuroventas = Column(Text, nullable=True) # Para la caja de texto de Psicología
    alertas_sistema = Column(Text, nullable=True) # Para la caja de Alertas y Notificaciones
    audio_path = Column(String(500), nullable=True) # Ruta de la nota de audio
    
    # Datos específicos para Persona Jurídica (PJ)
    fecha_constitucion = Column(Date, nullable=True)
    notaria_constitucion = Column(String(200), nullable=True)
    repertorio_constitucion = Column(String(100), nullable=True)
    fecha_ultima_vigencia = Column(Date, nullable=True)
    documentos_legales_path = Column(String(500), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prospect = relationship("Prospect", back_populates="profile")

class CompetitorProfile(Base):
    __tablename__ = "competitor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    tipo = Column(String(50), nullable=True) # Banco, Corredora, Family Office
    pros = Column(Text, nullable=True)
    contras = Column(Text, nullable=True)
    estrategias = Column(Text, nullable=True)
    publico_objetivo = Column(Text, nullable=True)
    nichos_abandonados = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClientHeir(Base):
    """
    Registro detallado de herederos y asignación legal.
    """
    __tablename__ = "client_heirs"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    rut = Column(String(30), nullable=True)
    relacion = Column(String(100), nullable=True)
    nombre = Column(String(200), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    porcentaje_asignacion = Column(Float, default=0.0)
    es_estudiante = Column(Boolean, default=False) # Para pensión de sobrevivencia Hijos 18-24 años (DL 3500 Art 5)
    
    prospect = relationship("Prospect", back_populates="heirs")


class CartolaSummary(Base):
    """
    Resumen Mensual extraído de Cartolas mediante Document AI / Gemini Multimodal (Fase D).
    """
    __tablename__ = "cartola_summaries"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    mes = Column(String(20), nullable=False) # ej. "2026-04"
    institucion_bancaria = Column(String(100), nullable=True)
    
    saldo_inicial = Column(Float, default=0.0)
    saldo_final = Column(Float, default=0.0)
    
    total_ingresos = Column(Float, default=0.0)
    total_egresos = Column(Float, default=0.0)
    
    # Categorización automática por IA
    gasto_supermercado = Column(Float, default=0.0)
    gasto_seguros = Column(Float, default=0.0)
    gasto_creditos = Column(Float, default=0.0)
    gasto_ocio = Column(Float, default=0.0)
    
    capacidad_ahorro_estimada = Column(Float, default=0.0)
    
    analisis_ia = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prospect = relationship("Prospect", back_populates="cartolas")
    transactions = relationship("CartolaTransaction", back_populates="cartola_summary", cascade="all, delete-orphan")


class ClientPortfolio(Base):
    __tablename__ = "client_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    institucion = Column(String(100), nullable=True) # Ej: Consorcio, Principal, AFP Habitat
    activo = Column(String(150), nullable=True) # Ej: AAPL, Fondo Mutuo X, Ahorro Obligatorio, APV
    tipo_activo = Column(String(50), nullable=True) # Cotización Obligatoria, APV-A, APV-B, Depósito Convenido (DC-R), Depósito Convenido (DC-L), Cuenta 2, Fondo Mutuo, Acciones, Depósito a Plazo, Otro
    
    monto_original = Column(Float, default=0.0)
    moneda_original = Column(String(10), default="CLP") # CLP, USD, UF
    monto_clp = Column(Float, default=0.0) # Monto convertido a pesos chilenos para consolidar
    
    objetivo_personal = Column(String(300), nullable=True) # Ej: "Renovar auto en enero 2027"
    rentabilidad_objetivo = Column(Float, nullable=True) # Ej: 10.0 (%)
    fecha_inicio_objetivo = Column(DateTime, nullable=True)
    fecha_fin_objetivo = Column(DateTime, nullable=True)
    
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)
    
    prospect = relationship("Prospect", back_populates="portfolios")


class CartolaTransaction(Base):
    """
    Movimientos detallados (Opcional). Solo se llena si se solicita extracción profunda.
    """
    __tablename__ = "cartola_transactions"

    id = Column(Integer, primary_key=True, index=True)
    cartola_summary_id = Column(Integer, ForeignKey("cartola_summaries.id"))
    
    fecha = Column(String(20), nullable=True)
    descripcion = Column(String(300), nullable=True)
    monto = Column(Float, nullable=False) # Positivo ingreso, Negativo egreso
    categoria_ia = Column(String(100), nullable=True)
    
    cartola_summary = relationship("CartolaSummary", back_populates="transactions")

class ClientProperty(Base):
    """
    Registro de bienes raíces y patrimonio inmobiliario.
    """
    __tablename__ = "client_properties"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    rol = Column(String(50), nullable=True)
    comuna = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    
    # Datos SII
    destino = Column(String(100), nullable=True)
    fojas = Column(String(50), nullable=True)
    numero = Column(String(50), nullable=True)
    ano = Column(Integer, nullable=True)
    porcentaje_derecho = Column(Float, default=100.0)
    avaluo_fiscal = Column(Float, default=0.0)
    
    valor_comercial_estimado = Column(Float, default=0.0)
    deuda_hipotecaria = Column(Float, default=0.0)
    dividendo_mensual = Column(Float, default=0.0)
    
    # Datos de Hipoteca Detallados
    hipoteca_institucion = Column(String(100), nullable=True)
    hipoteca_monto_inicial = Column(Float, default=0.0)
    hipoteca_saldo_actual = Column(Float, default=0.0)
    hipoteca_fecha_escritura = Column(String(50), nullable=True)
    hipoteca_valor_tasacion = Column(Float, default=0.0)
    hipoteca_monto_asegurado = Column(Float, default=0.0)
    hipoteca_tasa_interes = Column(Float, default=0.0)
    hipoteca_tipo_tasa = Column(String(50), nullable=True)
    hipoteca_cuota_actual = Column(Integer, default=0)
    hipoteca_total_cuotas = Column(Integer, default=0)
    hipoteca_fecha_ultima_actualizacion = Column(String(20), nullable=True)
    
    # Datos Arriendo
    arriendo_mensual = Column(Float, default=0.0)
    arriendo_moneda = Column(String(20), nullable=True)
    arriendo_fecha_contrato = Column(String(50), nullable=True)
    arriendo_periodo_reajuste = Column(Integer, nullable=True)
    gastos_comunes = Column(Float, default=0.0)
    contribuciones_anuales = Column(Float, default=0.0)
    gastos_mantencion_anual = Column(Float, default=0.0)
    plusvalia_esperada_anual = Column(Float, default=0.0)
    
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prospect = relationship("Prospect", back_populates="properties")


class ClientInsurance(Base):
    """
    Registro y análisis de pólizas de seguros.
    """
    __tablename__ = "client_insurances"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    tipo_seguro = Column(String(100), nullable=True) # Vida, Salud, Oncológico, Vehículo
    compania = Column(String(100), nullable=True)
    numero_poliza = Column(String(100), nullable=True)
    estado = Column(String(50), default="VIGENTE")
    
    prima_mensual = Column(Float, default=0.0)
    moneda = Column(String(20), default="UF")
    capital_asegurado = Column(Float, default=0.0)
    deducible = Column(Float, default=0.0)
    
    coberturas = Column(Text, nullable=True)
    beneficios_clave = Column(Text, nullable=True)
    exclusiones = Column(Text, nullable=True)
    
    # Nuevos campos CMF y UI
    asegurado = Column(String(200), nullable=True)
    contratante = Column(String(200), nullable=True)
    colectivo_individual = Column(String(50), nullable=True)
    bien_asegurado_tipo = Column(String(100), nullable=True)
    alias_patente = Column(String(100), nullable=True)
    medio_pago = Column(String(100), nullable=True)
    
    # Ley 21.420 / Circular 20 SII / APV Póliza
    fecha_contratacion = Column(String(50), nullable=True)
    es_apv_poliza = Column(Boolean, default=False)
    
    analisis_ia = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prospect = relationship("Prospect", back_populates="insurances")

class ClientInventory(Base):
    """
    Registro detallado de inventario patrimonial (Bienes Raíces, Vehículos, Financiero, Arte, etc.)
    """
    __tablename__ = "client_inventories"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    categoria = Column(String(100), nullable=False) # e.g., 'Bienes Raíces', 'Vehículos', 'Instrumentos Financieros', 'Arte/Otros'
    descripcion = Column(String(300), nullable=True)
    valor_comercial = Column(Float, default=0.0)
    deuda_asociada = Column(Float, default=0.0)
    
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prospect = relationship("Prospect", back_populates="inventories")

class ClientDebt(Base):
    """
    Registro detallado de deudas extraídas desde CMF (informe CSV)
    """
    __tablename__ = "client_debts"
    
    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    institucion = Column(String(200), nullable=True)
    tipo_credito = Column(String(100), nullable=True)
    monto_original = Column(Float, default=0.0)
    monto_actual = Column(Float, default=0.0)
    carga_financiera = Column(Float, default=0.0) # Cuota
    fecha_otorgamiento = Column(String(50), nullable=True)
    fecha_vencimiento = Column(String(50), nullable=True)
    
    # Flags de mora o alertas
    monto_mora = Column(Float, default=0.0)
    
    observaciones = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    prospect = relationship("Prospect", back_populates="debts")

class ClientCompany(Base):
    """
    Registro de participación en sociedades (Desde Carpeta Tributaria SII)
    """
    __tablename__ = "client_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    rut_empresa = Column(String(30), nullable=True)
    razon_social = Column(String(200), nullable=True)
    fecha_incorporacion = Column(String(50), nullable=True)
    porcentaje_capital = Column(Float, default=0.0)
    porcentaje_utilidades = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    prospect = relationship("Prospect", back_populates="companies")

class CompanyShareholder(Base):
    """
    Registro de socios o accionistas para un cliente Persona Jurídica.
    """
    __tablename__ = "company_shareholders"
    
    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    rut = Column(String(30), nullable=True)
    nombre = Column(String(200), nullable=True)
    porcentaje_participacion = Column(Float, default=0.0)
    capital_aportado = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    prospect = relationship("Prospect", back_populates="company_shareholders")

class CompanyRepresentative(Base):
    """
    Registro de representantes legales para un cliente Persona Jurídica.
    """
    __tablename__ = "company_representatives"
    
    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    rut = Column(String(30), nullable=True)
    nombre = Column(String(200), nullable=True)
    poderes_restricciones = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    prospect = relationship("Prospect", back_populates="company_representatives")

class MarketVision(Base):
    """
    Registro temporal de visiones de mercado por institución y período.
    Permite manejar PDFs y scraping asíncrono sin contaminar meses anteriores.
    """
    __tablename__ = "market_visions"

    id = Column(Integer, primary_key=True, index=True)
    institucion = Column(String(100), index=True, nullable=False)
    periodo = Column(String(20), index=True, nullable=False) # Formato YYYY-MM
    fuente = Column(String(50), nullable=True) # "Web Scraper", "PDF Subido"
    
    contenido_bruto = Column(Text, nullable=True)
    resumen_corto = Column(Text, nullable=True)
    resumen_extendido = Column(Text, nullable=True)
    
    fecha_ingesta = Column(DateTime, default=datetime.utcnow)

class ClientMacroHistory(Base):
    """
    Historial de consultas Macro hechas por o para un prospecto/cliente específico.
    """
    __tablename__ = "client_macro_history"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    
    pregunta = Column(Text, nullable=False)
    respuesta_final = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    
    prospect = relationship("Prospect", back_populates="macro_history")

class MarketStat(Base):
    """
    Registro cuantitativo diario de índices, FX y tasas de mercado.
    """
    __tablename__ = "market_stats"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(50), index=True, nullable=False) # e.g., 'USDCLP', 'SP500', 'UF'
    nombre = Column(String(100), nullable=True)
    fecha = Column(Date, index=True, nullable=False)
    valor_cierre = Column(Float, nullable=False)
    tipo_activo = Column(String(50), nullable=True) # 'FX', 'Indice', 'Tasa', 'Local'
    fuente = Column(String(50), nullable=True) # 'Yahoo Finance', 'mindicador.cl'
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketNews(Base):
    """
    Registro cualitativo de noticias y feeds RSS para análisis macroeconómico y LinkedIn.
    """
    __tablename__ = "market_news"

    id = Column(Integer, primary_key=True, index=True)
    fuente = Column(String(100), nullable=False) # e.g., 'Reuters Business'
    titular = Column(String(500), nullable=False)
    resumen = Column(Text, nullable=True)
    link = Column(String(500), nullable=True)
    fecha_publicacion = Column(DateTime, index=True, nullable=True)
    
    # Campo para almacenar si el LLM usó esto para un post de LinkedIn
    usado_para_linkedin = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class CompanyFinancialMovement(Base):
    """
    Registro contable de facturas emitidas (ingresos), facturas recibidas (egresos),
    gastos, previred, impuestos y transferencias para FV Asesorías / ALTUS AI.
    """
    __tablename__ = "company_financial_movements"

    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String(100), default="FV Asesorías SpA", index=True) # "FV Asesorías SpA", "ALTUS AI SpA"
    tipo_movimiento = Column(String(20), nullable=False) # "INGRESO" (Abono/Venta), "EGRESO" (Compra/Gasto)
    categoria = Column(String(100), nullable=True) # "UP FRONT", "TRAILER FEE", "DEL GIRO", "ACTIVO FIJO", "SUELDO", "PREVIRED", "IMPUESTOS", "ARRIENDO", "OTROS"
    
    fecha = Column(Date, index=True, nullable=True)
    periodo = Column(String(20), index=True, nullable=True) # YYYY-MM
    folio_factura = Column(String(50), nullable=True)
    
    rut_contraparte = Column(String(30), nullable=True)
    razon_social = Column(String(250), nullable=True)
    concepto = Column(Text, nullable=True)
    
    monto_exento = Column(Float, default=0.0)
    monto_neto = Column(Float, default=0.0)
    monto_iva = Column(Float, default=0.0)
    monto_total = Column(Float, default=0.0)
    
    cuenta_corriente = Column(String(100), nullable=True) # e.g. "CTA. CTE. BCI: FV ASESORIAS", "CTA. CTE. BANCO CHILE: FCO", "CTA. CTE. BANCO SANTANDER: NATALIA"
    observaciones = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class CompanyAccount(Base):
    """
    Cuentas corrientes y de inversión asociadas a la empresa o socios.
    """
    __tablename__ = "company_accounts"

    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String(100), default="FV Asesorías SpA", index=True)
    banco = Column(String(100), nullable=False)
    titular = Column(String(100), nullable=False)
    alias = Column(String(150), nullable=False) # e.g. "CTA. CTE. BCI: FV ASESORIAS"
    saldo_actual = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

