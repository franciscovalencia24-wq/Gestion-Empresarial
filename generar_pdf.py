from fpdf import FPDF
import os

class PremiumPDF(FPDF):
    def header(self):
        # Logo grande centrado
        if os.path.exists('src/web/assets/NUEVO LOGO FV.png'):
            # El logo es horizontal, vamos a darle un buen tamano (w=120) y centrarlo (x=45)
            self.image('src/web/assets/NUEVO LOGO FV.png', x=45, y=15, w=120)
        self.ln(45)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(16, 75, 60) # Verde oscuro corporativo
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(50, 50, 50) # Gris oscuro para lectura premium
        self.multi_cell(0, 6, text)
        self.ln(6)

    def numbered_item(self, number, title, body):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(16, 75, 60)
        self.cell(10, 6, f"{number}.", align='L')
        self.cell(0, 6, title, ln=True, align='L')
        
        self.set_font('Arial', '', 11)
        self.set_text_color(50, 50, 50)
        self.set_x(20) # Indentacion
        self.multi_cell(0, 6, body)
        self.ln(4)

pdf = PremiumPDF()
pdf.add_page()

# Tituo Principal
pdf.set_font('Arial', 'B', 18)
pdf.set_text_color(20, 20, 20)
pdf.cell(0, 10, 'Bienvenido al Futuro de la Gestion Patrimonial', ln=True, align='C')
pdf.set_draw_color(16, 75, 60)
pdf.set_line_width(0.5)
pdf.line(20, pdf.get_y(), 190, pdf.get_y())
pdf.ln(10)

pdf.chapter_body(
    "En el complejo entorno economico actual, la verdadera seguridad no se encuentra en acumular "
    "activos aislados, sino en construir una arquitectura financiera solida, dinamicamente blindada "
    "y tributariamente eficiente.\n\n"
    "En FV Asesorias e Inversiones, hemos trascendido la asesoria tradicional para convertirnos en su "
    "Digital Family Office (DFO). Integramos tecnologia de Inteligencia Artificial y modelamiento estadistico "
    "institucional para proteger lo que mas importa: el legado de su familia."
)

pdf.chapter_title("Nuestra Metodologia: Arquitectura Tecnologica Aplicada")

pdf.numbered_item(
    "1", "Vision 360 Instantanea",
    "Nuestros sistemas de Ingesta Inteligente leen y consolidan automaticamente sus cartolas, "
    "estados de cuenta y posiciones en distintas instituciones financieras, entregandole una radiografia "
    "patrimonial neta, centralizada y sin sesgos comerciales."
)

pdf.numbered_item(
    "2", "Pruebas de Estres Institucionales (Modelo Monte Carlo)",
    "No predecimos el futuro; nos preparamos matematicamente para el. Proyectamos su supervivencia "
    "financiera y sus flujos de caja frente a 10.000 escenarios de crisis economicas reales, asegurando "
    "que su estandar de vida sea inquebrantable hasta los 90+ anos."
)

pdf.numbered_item(
    "3", "Ingenieria Tributaria y Sucesoria",
    "Nuestro motor legal analiza constantemente oportunidades fiscales. Por ejemplo, estructuramos seguros "
    "con ahorro altamente eficientes para garantizar transmisiones patrimoniales de forma agil y de libre "
    "designacion, eficiencia en el impuesto a la herencia (Ley N 16.271), y optimizando el uso de los recursos "
    "en vida en terminos tributarios."
)

pdf.numbered_item(
    "4", "Monitoreo Competitivo Autonomo",
    "Si otra institucion le ofrece un producto, lo analizamos en segundos. Nuestros sistemas leen la letra "
    "chica de los folletos competidores y le entregamos una evaluacion objetiva sobre sus verdaderos costos "
    "ocultos y riesgos."
)

pdf.ln(5)
pdf.set_draw_color(200, 200, 200)
pdf.line(20, pdf.get_y(), 190, pdf.get_y())
pdf.ln(5)

pdf.chapter_title("Nuestro Compromiso: Paz Mental")
pdf.chapter_body(
    "Nuestro negocio no es venderle productos financieros transaccionales. Nuestro negocio es entregarle "
    "claridad, tiempo y tranquilidad.\n\n"
    "Ser cliente de FV Asesorias significa tener la certeza de que existe un equipo de expertos cuidando su "
    "capital 24/7 con la mejor tecnologia. Ademas, contamos con la solidez de ser distribuidores exclusivos de "
    "Principal Financial Group, una de las administradoras de inversiones y ahorro a largo plazo mas grandes, "
    "antiguas y prestigiosas del mundo (Fortune 500). Este respaldo institucional internacional nos permite "
    "brindarle garantias de clase mundial, permitiendole a usted enfocarse exclusivamente en disfrutar su vida "
    "y su familia."
)

pdf.ln(5)
# Call to action and contact
pdf.set_fill_color(245, 245, 245)
pdf.set_draw_color(16, 75, 60)
pdf.set_line_width(0.5)
pdf.rect(15, pdf.get_y(), 180, 25, 'FD')
pdf.set_y(pdf.get_y() + 5)
pdf.set_font('Arial', 'B', 12)
pdf.set_text_color(16, 75, 60)
pdf.cell(0, 6, "Esta preparado para llevar su estructura financiera al siguiente nivel?", ln=True, align='C')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(50, 50, 50)
pdf.cell(0, 6, "contacto@fv-inversiones.com   |   +56 9 6677 9662", ln=True, align='C')

try:
    pdf.output('Propuesta_FV_Asesorias_V2.pdf')
    print("PDF Premium generado exitosamente")
except Exception as e:
    print(f"Error guardando PDF: {e}")
