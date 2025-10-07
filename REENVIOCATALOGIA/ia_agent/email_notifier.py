# ==============================================================================
# 2. ia_agent/email_notifier.py - SISTEMA DE NOTIFICACIONES
# ==============================================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

class EmailNotifier:
    """Sistema de notificaciones por email con soporte Outlook y SMTP corporativo"""
    
    def __init__(self, email_config: dict):
        self.config = email_config
        self.logger = logging.getLogger(__name__)
        
    def _create_smtp_connection(self):
        """Crea conexión SMTP según configuración"""
        try:
            if self.config.get('use_corporate_smtp', False):
                # SMTP Corporativo
                smtp_config = self.config['corporate_smtp']
                server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
                
                if smtp_config.get('auth_required', True):
                    server.starttls()
                    server.login(self.config['username'], self.config['password'])
                
            else:
                # Outlook/Gmail estándar
                server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
                server.starttls()
                server.login(self.config['username'], self.config['password'])
            
            return server
            
        except Exception as e:
            self.logger.error(f"Error creando conexión SMTP: {str(e)}")
            return None
    
    def _send_email(self, subject: str, body: str, is_html: bool = False):
        """Envía email genérico"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg['To'] = self.config['to_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))
            
            server = self._create_smtp_connection()
            if server:
                server.send_message(msg)
                server.quit()
                self.logger.info(f"Email enviado: {subject}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error enviando email: {str(e)}")
            return False
    
    def send_system_start_notification(self):
        """Notifica inicio del sistema"""
        subject = "🤖 IA REENVIOCATALOG - Sistema Iniciado"
        
        body = f"""
        <h2>Sistema IA REENVIOCATALOG Iniciado</h2>
        
        <p><strong>Fecha/Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h3>Estado del Sistema:</h3>
        <ul>
            <li>✅ IA Agent Orquestador: Activo</li>
            <li>✅ Backend Automático: Iniciado</li>
            <li>✅ Monitor de Logs: Activo</li>
            <li>✅ Sincronización: Cada 2 minutos</li>
        </ul>
        
        <p><strong>El sistema está funcionando de forma completamente automática.</strong></p>
        <p>Recibirás notificaciones por cada sincronización y cualquier error detectado.</p>
        
        <hr>
        <p><small>Mensaje generado automáticamente por IA Agent REENVIOCATALOG</small></p>
        """
        
        self._send_email(subject, body, is_html=True)
    
    def send_sync_success_notification(self, sync_number: int, analysis: str, log_line: str):
        """Notifica sincronización exitosa con análisis IA"""
        subject = f"✅ REENVIOCATALOG - Sincronización #{sync_number} Exitosa"
        
        body = f"""
        <h2>Sincronización Exitosa #{sync_number}</h2>
        
        <p><strong>Fecha/Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h3>Análisis IA del Cambio:</h3>
        <p>{analysis}</p>
        
        <h3>Detalles Técnicos:</h3>
        <p><code>{log_line}</code></p>
        
        <h3>Estado del Sistema:</h3>
        <p>🟢 Sistema operativo - Próxima verificación en 2 minutos</p>
        
        <hr>
        <p><small>Análisis generado automáticamente por IA Agent REENVIOCATALOG</small></p>
        """
        
        self._send_email(subject, body, is_html=True)
    
    def send_error_notification(self, error_count: int, analysis: str, log_line: str):
        """Notifica errores con análisis IA"""
        subject = f"❌ REENVIOCATALOG - Error Detectado (#{error_count})"
        
        body = f"""
        <h2>Error Detectado en el Sistema</h2>
        
        <p><strong>Fecha/Hora:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Número de Error:</strong> #{error_count}</p>
        
        <h3>Análisis IA del Error:</h3>
        <p style="color: red;"><strong>{analysis}</strong></p>
        
        <h3>Log del Error:</h3>
        <p><code style="background-color: #f5f5f5; padding: 10px;">{log_line}</code></p>
        
        <h3>Acciones Automáticas:</h3>
        <ul>
            <li>🔍 IA monitoreando para recuperación automática</li>
            <li>🔄 Reinicio automático si persisten errores</li>
            <li>📧 Notificaciones continuas hasta resolución</li>
        </ul>
        
        <hr>
        <p><small>Análisis de error generado automáticamente por IA Agent REENVIOCATALOG</small></p>
        """
        
        self._send_email(subject, body, is_html=True)