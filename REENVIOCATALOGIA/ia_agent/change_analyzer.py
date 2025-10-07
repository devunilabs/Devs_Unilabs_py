# ==============================================================================
# 3. ia_agent/change_analyzer.py - ANÁLISIS INTELIGENTE CON LANGCHAIN
# ==============================================================================
# ia_agent/change_analyzer.py - ANÁLISIS INTELIGENTE MEJORADO CON LANGCHAIN
import re
import json
import os
from datetime import datetime
from typing import Dict, Any
import logging

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class ChangeAnalyzer:
    """Analizador inteligente mejorado con IA real visible"""
    
    def __init__(self, langchain_config: dict):
        self.config = langchain_config
        self.logger = logging.getLogger(__name__)
        self.llm = self._setup_llm()
        
        # Contadores para visibilidad
        self.total_analyses = 0
        self.ai_overrides = 0
        self.confidence_history = []
        
        # Contexto empresarial para decisiones
        self.business_context = {
            'critical_keywords': ['catalogo', 'precio', 'price', 'stock', 'inventario', 'inventory'],
            'business_hours': (8, 18),
            'critical_size_mb': 0.5,
            'conflict_indicators': ['editing', 'locked', 'temp', 'backup']
        }
    
    def _setup_llm(self):
        """Configura LLM con fallbacks mejorados"""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain no disponible, usando análisis inteligente simulado")
            return None
        
        try:
            # Verificar configuración de OpenAI
            if (self.config.get('provider') == 'openai' and 
                self.config.get('openai_api_key') and 
                self.config['openai_api_key'] != 'sk-your-api-key-here'):
                
                llm = ChatOpenAI(
                    model=self.config.get('model', 'gpt-3.5-turbo'),
                    temperature=self.config.get('temperature', 0.1),
                    api_key=self.config['openai_api_key'],
                    max_tokens=400
                )
                
                # Test de conexión
                test_response = llm([HumanMessage(content="Test")])
                
                self.logger.info("IA REAL configurada con OpenAI")
                self.logger.info(f"Modelo activo: {self.config.get('model', 'gpt-3.5-turbo')}")
                return llm
            
        except Exception as e:
            self.logger.warning(f"Error configurando OpenAI: {e}")
        
        # Usar análisis inteligente simulado
        self.logger.info("Usando análisis inteligente simulado (sin costo)")
        return None
    
    def analyze_sync_success(self, log_line: str) -> str:
        """Analiza una sincronización exitosa CON IA"""
        self.total_analyses += 1
        
        if self.llm:
            return self._analyze_with_llm(log_line, "sincronización exitosa")
        else:
            return self._analyze_intelligent_sync(log_line)
    
    def analyze_error(self, log_line: str) -> str:
        """Analiza un error del sistema CON IA"""
        self.total_analyses += 1
        
        if self.llm:
            return self._analyze_with_llm(log_line, "error del sistema")
        else:
            return self._analyze_intelligent_error(log_line)
    
    def analyze_file_change(self, log_line: str) -> str:
        """Analiza cambios en archivos CON IA"""
        self.total_analyses += 1
        
        if self.llm:
            return self._analyze_with_llm(log_line, "cambio en archivo")
        else:
            return self._analyze_intelligent_change(log_line)
    
    def analyze_conflict_situation(self, context_data: dict) -> Dict[str, Any]:
        """NUEVO: Analiza situaciones de conflicto de edición"""
        self.total_analyses += 1
        
        if self.llm:
            return self._analyze_conflict_with_llm(context_data)
        else:
            return self._analyze_conflict_intelligent(context_data)
    
    def _analyze_with_llm(self, log_line: str, context: str) -> str:
        """Análisis con LangChain/OpenAI REAL"""
        try:
            system_message = SystemMessage(content=f"""
            Eres un Analista IA especializado en sistemas de sincronización empresarial.
            
            CONTEXTO EMPRESARIAL:
            - Sistema: REENVIOCATALOG - Sincronización de catálogos críticos
            - Impacto: Alto - afecta precios, inventarios y operaciones
            - Usuarios: Equipos de ventas, operaciones e inventarios
            - Criticidad: Cambios deben sincronizarse rápida y correctamente
            
            Tu tarea es analizar logs y proporcionar:
            1. Análisis técnico claro
            2. Impacto empresarial
            3. Recomendaciones de acción
            4. Nivel de urgencia (1-10)
            5. Presencia de conflictos potenciales
            
            Contexto específico: {context}
            
            Responde de forma profesional y directa. Enfócate en impacto empresarial.
            """)
            
            user_message = HumanMessage(content=f"Analiza este evento del sistema: {log_line}")
            
            response = self.llm([system_message, user_message])
            
            # Agregar indicador de IA real
            analysis = f"[ANÁLISIS IA REAL] {response.content}"
            
            # Extraer nivel de confianza si es posible
            confidence = self._extract_confidence_from_response(response.content)
            self.confidence_history.append(confidence)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error en análisis LLM: {e}")
            return self._get_fallback_analysis(log_line, context)
    
    def _analyze_conflict_with_llm(self, context_data: dict) -> Dict[str, Any]:
        """Analiza conflictos de edición con IA real"""
        try:
            system_prompt = """Eres un Especialista IA en resolución de conflictos de archivos empresariales.

SITUACIÓN: Múltiples usuarios pueden estar editando el mismo archivo crítico simultáneamente.

CONTEXTO EMPRESARIAL:
- Archivo: Catálogo Excel crítico con precios e inventarios
- Impacto: Conflictos pueden causar pérdida de datos o inconsistencias
- Usuarios: Equipos trabajan simultáneamente en diferentes secciones

DECISIONES DISPONIBLES:
- FORCE_SYNC: Sincronizar inmediatamente (riesgo de sobrescribir)
- WAIT_USERS: Esperar que terminen las ediciones
- BACKUP_MERGE: Crear backup y sincronizar
- ALERT_USERS: Notificar conflicto a usuarios

Responde en JSON:
{
    "recommendation": "FORCE_SYNC|WAIT_USERS|BACKUP_MERGE|ALERT_USERS",
    "risk_level": "Alto|Medio|Bajo",
    "business_impact": "descripción del impacto",
    "confidence": 85,
    "reasoning": "explicación detallada"
}"""
            
            user_prompt = f"""ANÁLISIS DE CONFLICTO REQUERIDO:

CONTEXTO:
- Usuarios editando origen: {context_data.get('source_editing', False)}
- Usuarios editando destino: {context_data.get('dest_editing', False)}
- Archivo crítico: {context_data.get('is_critical', True)}
- Horario laboral: {context_data.get('business_hours', True)}
- Última sincronización: {context_data.get('last_sync_minutes', 'N/A')} min

¿Cuál es la mejor estrategia para manejar este conflicto?"""

            response = self.llm([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Parsear respuesta JSON
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['analysis_type'] = 'real_ai_conflict'
                return analysis
        
        except Exception as e:
            self.logger.error(f"Error en análisis de conflicto IA: {e}")
        
        return self._analyze_conflict_intelligent(context_data)
    
    def _analyze_intelligent_sync(self, log_line: str) -> str:
        """Análisis inteligente de sincronización (sin API)"""
        # Extraer información del log
        sync_match = re.search(r'SINCRONIZACIÓN #(\d+)', log_line, re.IGNORECASE)
        sync_num = sync_match.group(1) if sync_match else "N/A"
        
        time_match = re.search(r'(\d+\.\d+)s', log_line)
        time_taken = time_match.group(1) if time_match else "N/A"
        
        # Análisis contextual inteligente
        is_fast = float(time_taken) < 1.0 if time_taken != "N/A" else False
        is_critical_file = any(keyword in log_line.lower() for keyword in self.business_context['critical_keywords'])
        
        # Generar análisis inteligente
        analysis = f"[ANÁLISIS IA SIMULADO] Sincronización #{sync_num} procesada"
        
        if is_fast:
            analysis += f" - RENDIMIENTO ÓPTIMO ({time_taken}s). "
        elif time_taken != "N/A":
            analysis += f" - Tiempo aceptable ({time_taken}s). "
        
        if is_critical_file:
            analysis += "Archivo crítico sincronizado correctamente. IMPACTO EMPRESARIAL: Alto - precios e inventarios actualizados."
        else:
            analysis += "Archivo estándar procesado. IMPACTO EMPRESARIAL: Medio - operaciones normales."
        
        analysis += f" CONFIANZA IA: 87%. ESTADO: Sistema operando dentro de parámetros normales."
        
        self.confidence_history.append(87)
        
        return analysis
    
    def _analyze_intelligent_error(self, log_line: str) -> str:
        """Análisis inteligente de errores"""
        error_type = "ERROR ESTÁNDAR"
        urgency = "MEDIA"
        business_impact = "MEDIO"
        
        if "CRÍTICO" in log_line.upper():
            error_type = "ERROR CRÍTICO"
            urgency = "ALTA"
            business_impact = "ALTO"
        elif "WARNING" in log_line.upper() or "ADVERTENCIA" in log_line.upper():
            error_type = "ADVERTENCIA"
            urgency = "BAJA"
            business_impact = "BAJO"
        
        # Detectar tipo de problema
        if "hash" in log_line.lower():
            problem_type = "verificación de integridad"
        elif "permiso" in log_line.lower() or "permission" in log_line.lower():
            problem_type = "acceso a archivos"
        elif "onedrive" in log_line.lower():
            problem_type = "sincronización OneDrive"
        else:
            problem_type = "sistema general"
        
        analysis = f"[ANÁLISIS IA SIMULADO] {error_type} detectado en {problem_type}. "
        analysis += f"URGENCIA: {urgency}. IMPACTO EMPRESARIAL: {business_impact}. "
        analysis += f"RECOMENDACIÓN IA: Monitorear para resolución automática. "
        
        if urgency == "ALTA":
            analysis += "ACCIÓN REQUERIDA: Investigar inmediatamente."
        elif urgency == "MEDIA":
            analysis += "ACCIÓN REQUERIDA: Revisar en próximos 15 minutos."
        else:
            analysis += "ACCIÓN REQUERIDA: Monitoreo rutinario."
        
        confidence = 92 if urgency == "ALTA" else 85
        analysis += f" CONFIANZA IA: {confidence}%."
        
        self.confidence_history.append(confidence)
        
        return analysis
    
    def _analyze_intelligent_change(self, log_line: str) -> str:
        """Análisis inteligente de cambios en archivos"""
        # Extraer información
        byte_match = re.search(r'([+-]?\d+(?:,\d+)*)\s*bytes', log_line)
        has_bytes = byte_match is not None
        
        # Detectar palabras clave críticas
        is_critical = any(keyword in log_line.lower() for keyword in self.business_context['critical_keywords'])
        
        # Análisis contextual
        now = datetime.now()
        is_business_hours = self.business_context['business_hours'][0] <= now.hour < self.business_context['business_hours'][1]
        
        analysis = "[ANÁLISIS IA SIMULADO] Cambio en archivo detectado. "
        
        if is_critical:
            analysis += "CONTENIDO CRÍTICO identificado (catálogo/precios). "
            business_impact = "ALTO"
            urgency = "INMEDIATA" if is_business_hours else "ALTA"
        else:
            analysis += "Contenido estándar modificado. "
            business_impact = "MEDIO"
            urgency = "NORMAL"
        
        if has_bytes:
            analysis += f"Cambio cuantificado detectado. "
        
        analysis += f"IMPACTO EMPRESARIAL: {business_impact}. "
        analysis += f"URGENCIA DE SINCRONIZACIÓN: {urgency}. "
        
        if is_business_hours:
            analysis += "Horario laboral activo - sincronización prioritaria. "
        else:
            analysis += "Fuera de horario crítico - sincronización estándar. "
        
        confidence = 95 if is_critical else 80
        analysis += f"CONFIANZA IA: {confidence}%."
        
        self.confidence_history.append(confidence)
        
        return analysis
    
    def _analyze_conflict_intelligent(self, context_data: dict) -> Dict[str, Any]:
        """Análisis inteligente de conflictos (sin API)"""
        source_editing = context_data.get('source_editing', False)
        dest_editing = context_data.get('dest_editing', False)
        is_critical = context_data.get('is_critical', True)
        business_hours = context_data.get('business_hours', True)
        
        # Lógica de decisión inteligente
        if source_editing and dest_editing:
            recommendation = "WAIT_USERS"
            risk_level = "Alto"
            reasoning = "IA detectó edición simultánea en origen y destino. Esperar estabilidad para evitar pérdida de datos."
            confidence = 95
        elif dest_editing and is_critical:
            recommendation = "BACKUP_MERGE" 
            risk_level = "Medio"
            reasoning = "Usuario editando archivo crítico en destino. Crear backup antes de sincronizar para preservar cambios."
            confidence = 88
        elif source_editing:
            recommendation = "WAIT_USERS"
            risk_level = "Medio"
            reasoning = "Edición activa en archivo origen. Esperar finalización para sincronización limpia."
            confidence = 85
        elif business_hours and is_critical:
            recommendation = "FORCE_SYNC"
            risk_level = "Bajo"
            reasoning = "Horario crítico sin conflictos activos. Sincronización inmediata recomendada."
            confidence = 92
        else:
            recommendation = "ALERT_USERS"
            risk_level = "Bajo"  
            reasoning = "Situación estable. Notificar a usuarios sobre próxima sincronización."
            confidence = 80
        
        self.confidence_history.append(confidence)
        
        return {
            'recommendation': recommendation,
            'risk_level': risk_level,
            'business_impact': f"Gestión automática de conflicto tipo '{recommendation}' aplicada",
            'confidence': confidence,
            'reasoning': reasoning,
            'analysis_type': 'simulated_intelligent'
        }
    
    def _extract_confidence_from_response(self, response_text: str) -> int:
        """Extrae nivel de confianza de respuesta IA"""
        # Buscar patrones de confianza
        confidence_patterns = [
            r'confianza[:\s]+(\d+)%',
            r'confidence[:\s]+(\d+)%',
            r'certeza[:\s]+(\d+)%'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response_text.lower())
            if match:
                return int(match.group(1))
        
        # Valor por defecto basado en palabras clave
        if any(word in response_text.lower() for word in ['crítico', 'urgent', 'immedia']):
            return 90
        elif any(word in response_text.lower() for word in ['probable', 'likely', 'normal']):
            return 75
        else:
            return 80
    
    def _get_fallback_analysis(self, log_line: str, context: str) -> str:
        """Análisis de fallback cuando LLM falla"""
        return f"[ANÁLISIS IA SIMULADO] Evento detectado: {context}. Sistema procesando automáticamente. Log: {log_line[:100]}... CONFIANZA IA: 75%."
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Estadísticas del analizador para visibilidad"""
        avg_confidence = 0
        if self.confidence_history:
            avg_confidence = sum(self.confidence_history[-20:]) / len(self.confidence_history[-20:])
        
        return {
            'analyzer_type': 'real_ai' if self.llm else 'simulated_intelligent',
            'model': self.config.get('model', 'business_intelligence_engine'),
            'total_analyses': self.total_analyses,
            'ai_overrides': self.ai_overrides,
            'average_confidence': round(avg_confidence, 1),
            'recent_confidence_trend': self.confidence_history[-10:] if len(self.confidence_history) >= 10 else self.confidence_history,
            'langchain_available': LANGCHAIN_AVAILABLE,
            'api_connected': self.llm is not None
        }