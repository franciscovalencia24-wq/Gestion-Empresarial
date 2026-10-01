import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Añadir el directorio raíz al path para que pueda importar 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.connection import Base
from src.database.models import Prospect, ClientProfile

# Crear una base de datos en memoria para las pruebas
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas
Base.metadata.create_all(bind=engine)

class TestKYCReporte360Flow(unittest.TestCase):
    def setUp(self):
        # Limpiar base de datos
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Iniciar sesión
        self.db = TestingSessionLocal()
        
    def tearDown(self):
        self.db.close()

    @patch('src.web.report_generator_ui.SessionLocal')
    @patch('src.web.report_generator_ui.st')
    def test_flujo_con_gastos_declarados(self, mock_st, mock_session_local):
        """
        Escenario 1: Cliente con gastos recurrentes declarados (ej: 36M anual)
        Debería inyectarse automáticamente 3M mensual en el flujo sucesorio.
        """
        mock_session_local.return_value = self.db
        
        # Estado de sesión falso
        fake_session_state = {}
        mock_st.session_state = fake_session_state
        
        # 1. Crear prospecto en BD en memoria
        prospect = Prospect(
            rut="99.999.999-9", 
            nombre="Test Cliente", 
            gastos_recurrentes=36000000.0
        )
        prospect.profile = ClientProfile()
        self.db.add(prospect)
        self.db.commit()
        
        # 2. Ejecutar la carga de sesión tal como en el UI
        from src.web.report_generator_ui import load_client_data_to_session
        load_client_data_to_session("99.999.999-9")
        
        # 3. Validar estado de sesión
        self.assertIn('reporte_360_data', fake_session_state)
        reporte_data = fake_session_state['reporte_360_data']
        
        self.assertIn('flujo_sucesorio', reporte_data)
        flujo = reporte_data['flujo_sucesorio']
        
        self.assertIn('gastos_vida', flujo)
        # Se espera que 36M anual / 12 = 3M mensual
        self.assertEqual(flujo['gastos_vida'], 3000000.0)
        
        # Verificar que el mensaje de éxito de Streamlit fue llamado
        mock_st.success.assert_called()

    @patch('src.web.report_generator_ui.SessionLocal')
    @patch('src.web.report_generator_ui.st')
    def test_flujo_borde_vacio(self, mock_st, mock_session_local):
        """
        Escenario 2: Cliente con gastos nulos o cero.
        Debería aplicar fallback sin arrojar excepciones.
        """
        mock_session_local.return_value = self.db
        
        # Estado de sesión falso
        fake_session_state = {}
        mock_st.session_state = fake_session_state
        
        # 1. Crear prospecto con gastos recurrentes None
        prospect_null = Prospect(
            rut="88.888.888-8", 
            nombre="Cliente Null", 
            gastos_recurrentes=None
        )
        self.db.add(prospect_null)
        
        # 2. Crear prospecto con gastos recurrentes 0.0
        prospect_zero = Prospect(
            rut="77.777.777-7", 
            nombre="Cliente Zero", 
            gastos_recurrentes=0.0
        )
        self.db.add(prospect_zero)
        self.db.commit()
        
        from src.web.report_generator_ui import load_client_data_to_session
        
        # Probar Null
        load_client_data_to_session("88.888.888-8")
        flujo_null = fake_session_state['reporte_360_data']['flujo_sucesorio']
        self.assertNotIn('gastos_vida', flujo_null)
        
        # Probar Cero
        load_client_data_to_session("77.777.777-7")
        flujo_zero = fake_session_state['reporte_360_data']['flujo_sucesorio']
        self.assertNotIn('gastos_vida', flujo_zero)

if __name__ == '__main__':
    unittest.main(verbosity=2)
