// script.js - Comportamiento de la UI del sincronizador Excel OneDrive con automatización

class SincronizadorUI {
    constructor() {
        this.elementos = {};
        this.intervalos = {};
        this.estado = {
            monitorActivo: false,
            configuracionVisible: false,
            modoAutomatico: true  // NUEVO: Indicar que está en modo automático
        };
        
        this.inicializarElementos();
        this.configurarEventListeners();
        this.inicializarUI();
    }

    inicializarElementos() {
        // Elementos de control
        this.elementos.btnIniciar = document.getElementById('btnIniciar');
        this.elementos.btnDetener = document.getElementById('btnDetener');
        this.elementos.btnSincronizar = document.getElementById('btnSincronizar');
        this.elementos.btnRefreshStatus = document.getElementById('btnRefreshStatus');
        this.elementos.btnRefreshLogs = document.getElementById('btnRefreshLogs');
        this.elementos.btnLimpiarLogs = document.getElementById('btnLimpiarLogs');
        
        // Elementos de configuración
        this.elementos.btnToggleConfig = document.getElementById('btnToggleConfig');
        this.elementos.configContent = document.getElementById('configContent');
        this.elementos.rutaOrigen = document.getElementById('rutaOrigen');
        this.elementos.rutaDestino = document.getElementById('rutaDestino');
        this.elementos.intervaloVerificacion = document.getElementById('intervaloVerificacion');
        this.elementos.intervaloForzado = document.getElementById('intervaloForzado');
        this.elementos.btnGuardarConfig = document.getElementById('btnGuardarConfig');
        this.elementos.btnCargarConfig = document.getElementById('btnCargarConfig');
        
        // Elementos de estado
        this.elementos.statusIndicator = document.getElementById('statusIndicator');
        this.elementos.statusDot = document.getElementById('statusDot');
        this.elementos.statusText = document.getElementById('statusText');
        this.elementos.estadoOrigen = document.getElementById('estadoOrigen');
        this.elementos.estadoDestino = document.getElementById('estadoDestino');
        this.elementos.monitorActivo = document.getElementById('monitorActivo');
        this.elementos.watchdogEstado = document.getElementById('watchdogEstado');
        this.elementos.ultimaVerificacion = document.getElementById('ultimaVerificacion');
        this.elementos.reintentosFallidos = document.getElementById('reintentosFallidos');
        this.elementos.infoOrigen = document.getElementById('infoOrigen');
        this.elementos.infoDestino = document.getElementById('infoDestino');
        
        // NUEVOS elementos para sincronización automática
        this.elementos.proximaSincronizacion = document.getElementById('proximaSincronizacion');
        this.elementos.contadorSincronizaciones = document.getElementById('contadorSincronizaciones');
        this.elementos.tiempoRestante = document.getElementById('tiempoRestante');
        this.elementos.modoAutomatico = document.getElementById('modoAutomatico');
        this.elementos.estadoOneDrive = document.getElementById('estadoOneDrive');
        
        // Elementos de logs
        this.elementos.selectLineasLog = document.getElementById('selectLineasLog');
        this.elementos.logsContainer = document.getElementById('logsContainer');
        
        // Elementos de overlay
        this.elementos.loadingOverlay = document.getElementById('loadingOverlay');
        this.elementos.notificationContainer = document.getElementById('notificationContainer');
    }

    configurarEventListeners() {
        // Controles principales
        this.elementos.btnIniciar.addEventListener('click', () => this.iniciarMonitor());
        this.elementos.btnDetener.addEventListener('click', () => this.detenerMonitor());
        this.elementos.btnSincronizar.addEventListener('click', () => this.forzarSincronizacion());
        
        // Configuración
        this.elementos.btnToggleConfig.addEventListener('click', () => this.toggleConfiguracion());
        this.elementos.btnGuardarConfig.addEventListener('click', () => this.guardarConfiguracion());
        this.elementos.btnCargarConfig.addEventListener('click', () => this.cargarConfiguracion());
        
        // Actualización de estado
        this.elementos.btnRefreshStatus.addEventListener('click', () => this.actualizarEstado());
        this.elementos.btnRefreshLogs.addEventListener('click', () => this.cargarLogs());
        this.elementos.btnLimpiarLogs.addEventListener('click', () => this.limpiarLogs());
        
        // Cambio de líneas de log
        this.elementos.selectLineasLog.addEventListener('change', () => this.cargarLogs());
        
        // Validación en tiempo real de intervalos
        this.elementos.intervaloVerificacion.addEventListener('input', (e) => {
            this.validarIntervalo(e.target, 1, 300);
        });
        
        this.elementos.intervaloForzado.addEventListener('input', (e) => {
            this.validarIntervalo(e.target, 10, 3600);
            this.actualizarTextoIntervalo(e.target.value);
        });
    }

    inicializarUI() {
        this.mostrarLoading('Inicializando interfaz automática...');
        
        // Mostrar notificación del modo automático
        setTimeout(() => {
            this.mostrarNotificacion(
                'Sistema configurado para sincronización automática cada 10 minutos',
                'info',
                '⏰ Modo Automático'
            );
        }, 1000);
        
        // Cargar configuración inicial
        this.cargarConfiguracion();
        
        // Actualizar estado inicial
        this.actualizarEstado();
        
        // Iniciar actualización automática cada 5 segundos (más frecuente para el modo automático)
        this.intervalos.estadoAuto = setInterval(() => {
            this.actualizarEstado();
        }, 5000);
        
        // NUEVO: Iniciar countdown para próxima sincronización
        this.intervalos.countdown = setInterval(() => {
            this.actualizarCountdown();
        }, 1000);
        
        // Cargar logs iniciales
        this.cargarLogs();
        
        // NUEVO: Actualizar logs automáticamente cada 10 segundos
        this.intervalos.logsAuto = setInterval(() => {
            this.cargarLogs();
        }, 10000);
        
        this.ocultarLoading();
        this.mostrarNotificacion('Sistema automático iniciado correctamente', 'success', 'Sistema');
    }

    // === NUEVOS MÉTODOS PARA SINCRONIZACIÓN AUTOMÁTICA ===
    
    actualizarTextoIntervalo(valor) {
        //"""Actualiza el texto explicativo del intervalo"""
        const minutos = Math.floor(valor / 60);
        const segundos = valor % 60;
        
        let texto = '';
        if (minutos > 0) {
            texto = `${minutos} minuto${minutos > 1 ? 's' : ''}`;
            if (segundos > 0) {
                texto += ` y ${segundos} segundo${segundos > 1 ? 's' : ''}`;
            }
        } else {
            texto = `${segundos} segundo${segundos > 1 ? 's' : ''}`;
        }
        
        // Buscar elemento de ayuda para el intervalo
        const helpText = document.querySelector('.interval-help');
        if (helpText) {
            helpText.textContent = `Sincronización automática cada ${texto}`;
        }
    }
    
    actualizarCountdown() {
       // """NUEVO: Actualiza el countdown para la próxima sincronización"""
        if (!this.elementos.tiempoRestante) return;
        
        // Obtener el tiempo restante del último estado
        const tiempoRestante = parseInt(this.elementos.tiempoRestante.dataset.segundos || 0);
        
        if (tiempoRestante > 0) {
            const nuevoTiempo = tiempoRestante - 1;
            this.elementos.tiempoRestante.dataset.segundos = nuevoTiempo;
            
            const minutos = Math.floor(nuevoTiempo / 60);
            const segundos = nuevoTiempo % 60;
            
            this.elementos.tiempoRestante.textContent = `${minutos}:${segundos.toString().padStart(2, '0')}`;
            
            // Cambiar color según el tiempo restante
            if (nuevoTiempo <= 60) {
                this.elementos.tiempoRestante.className = 'countdown-value countdown-urgent';
            } else if (nuevoTiempo <= 180) {
                this.elementos.tiempoRestante.className = 'countdown-value countdown-warning';
            } else {
                this.elementos.tiempoRestante.className = 'countdown-value countdown-normal';
            }
        }
    }

    // === MÉTODOS DE API (ACTUALIZADOS) ===
    async iniciarMonitor() {
        try {
            this.mostrarLoading('Iniciando monitor automático...');
            
            const response = await fetch('/api/iniciar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const resultado = await response.json();
            
            if (resultado.exito) {
                this.estado.monitorActivo = true;
                this.actualizarBotonesControl();
                this.mostrarNotificacion(
                    'Monitor automático iniciado - Sincronización cada 10 minutos', 
                    'success', 
                    '⏰ Monitor Automático'
                );
                this.actualizarEstado();
            } else {
                this.mostrarNotificacion(resultado.mensaje, 'error', 'Error');
            }
            
        } catch (error) {
            console.error('Error iniciando monitor:', error);
            this.mostrarNotificacion('Error de conexión con el servidor', 'error', 'Error');
        } finally {
            this.ocultarLoading();
        }
    }

    async detenerMonitor() {
        try {
            this.mostrarLoading('Deteniendo monitor automático...');
            
            const response = await fetch('/api/detener', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const resultado = await response.json();
            
            if (resultado.exito) {
                this.estado.monitorActivo = false;
                this.actualizarBotonesControl();
                this.mostrarNotificacion(
                    'Monitor automático detenido', 
                    'success', 
                    '🛑 Monitor'
                );
                this.actualizarEstado();
            } else {
                this.mostrarNotificacion(resultado.mensaje, 'error', 'Error');
            }
            
        } catch (error) {
            console.error('Error deteniendo monitor:', error);
            this.mostrarNotificacion('Error de conexión con el servidor', 'error', 'Error');
        } finally {
            this.ocultarLoading();
        }
    }

    async forzarSincronizacion() {
        try {
            this.mostrarLoading('Forzando sincronización inmediata...');
            
            const response = await fetch('/api/sincronizar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const resultado = await response.json();
            
            if (resultado.exito) {
                this.mostrarNotificacion(
                    `${resultado.mensaje} (Manual)`, 
                    'success', 
                    '🔧 Sincronización Manual'
                );
                this.actualizarEstado();
                this.cargarLogs();
            } else {
                this.mostrarNotificacion(resultado.mensaje, 'error', 'Error de Sincronización');
            }
            
        } catch (error) {
            console.error('Error forzando sincronización:', error);
            this.mostrarNotificacion('Error de conexión con el servidor', 'error', 'Error');
        } finally {
            this.ocultarLoading();
        }
    }

    async actualizarEstado() {
        try {
            const response = await fetch('/api/estado');
            const estado = await response.json();
            
            if (estado.error) {
                console.error('Error obteniendo estado:', estado.error);
                return;
            }
            
            this.actualizarInterfazEstado(estado);
            
        } catch (error) {
            console.error('Error actualizando estado:', error);
            this.actualizarEstadoConexion(false);
        }
    }

    // === MÉTODOS DE INTERFAZ (ACTUALIZADOS) ===
    actualizarInterfazEstado(estado) {
        // Actualizar estado de conexión
        this.actualizarEstadoConexion(true);
        
        // Actualizar estado del monitor
        this.estado.monitorActivo = estado.monitor_activo || false;
        this.actualizarBotonesControl();
        
        // Actualizar indicadores básicos
        this.elementos.monitorActivo.textContent = estado.monitor_activo ? 'Sí' : 'No';
        this.elementos.monitorActivo.className = estado.monitor_activo ? 'status-value text-success' : 'status-value text-danger';
        
        // NUEVO: Actualizar modo automático
        if (this.elementos.modoAutomatico) {
            const modoAuto = estado.sincronizacion_automatica || false;
            this.elementos.modoAutomatico.textContent = modoAuto ? 'Automático (10 min)' : 'Manual';
            this.elementos.modoAutomatico.className = modoAuto ? 'status-value text-success' : 'status-value text-info';
        }
        
        // NUEVO: Actualizar estado de OneDrive
        if (this.elementos.estadoOneDrive) {
            const oneDriveActivo = estado.onedrive_activo || false;
            this.elementos.estadoOneDrive.textContent = oneDriveActivo ? 'Activo' : 'Inactivo';
            this.elementos.estadoOneDrive.className = oneDriveActivo ? 'status-value text-success' : 'status-value text-warning';
        }
        
        // Actualizar estado de watchdog
        if (estado.watchdog_disponible) {
            const watchdogActivo = estado.watchdog_activo || false;
            this.elementos.watchdogEstado.textContent = watchdogActivo ? 'Activo' : 'Inactivo';
            this.elementos.watchdogEstado.className = watchdogActivo ? 'status-value text-success' : 'status-value text-warning';
        } else {
            this.elementos.watchdogEstado.textContent = 'No Disponible';
            this.elementos.watchdogEstado.className = 'status-value text-muted';
        }
        
        // NUEVO: Actualizar información de sincronización automática
        if (this.elementos.proximaSincronizacion && estado.proxima_sincronizacion_automatica) {
            const fecha = new Date(estado.proxima_sincronizacion_automatica);
            this.elementos.proximaSincronizacion.textContent = fecha.toLocaleTimeString();
        }
        
        if (this.elementos.contadorSincronizaciones) {
            this.elementos.contadorSincronizaciones.textContent = estado.contador_sincronizaciones || 0;
        }
        
        if (this.elementos.tiempoRestante) {
            const tiempoRestante = estado.tiempo_restante_proxima_sync || 0;
            this.elementos.tiempoRestante.dataset.segundos = tiempoRestante;
            
            const minutos = Math.floor(tiempoRestante / 60);
            const segundos = tiempoRestante % 60;
            this.elementos.tiempoRestante.textContent = `${minutos}:${segundos.toString().padStart(2, '0')}`;
        }
        
        // Actualizar última verificación
        this.elementos.ultimaVerificacion.textContent = estado.ultima_sincronizacion_automatica || 'N/A';
        
        // Actualizar reintentos fallidos
        const reintentos = estado.reintentos_fallidos || 0;
        this.elementos.reintentosFallidos.textContent = reintentos;
        this.elementos.reintentosFallidos.className = reintentos > 0 ? 'status-value text-warning' : 'status-value text-success';
        
        // Actualizar estado de archivos
        this.actualizarEstadoArchivos(estado);
    }

    actualizarEstadoArchivos(estado) {
        // Estado del archivo origen
        if (estado.archivo_origen_existe) {
            this.elementos.estadoOrigen.textContent = 'Encontrado';
            this.elementos.estadoOrigen.className = 'stat-value text-success';
            
            if (estado.info_origen) {
                this.elementos.infoOrigen.innerHTML = this.formatearInfoArchivo(estado.info_origen, estado.origen_hash);
            }
        } else {
            this.elementos.estadoOrigen.textContent = 'No encontrado';
            this.elementos.estadoOrigen.className = 'stat-value text-danger';
            this.elementos.infoOrigen.innerHTML = '<p class="text-muted">Archivo no encontrado</p>';
        }
        
        // Estado del archivo destino
        if (estado.archivo_destino_existe) {
            this.elementos.estadoDestino.textContent = 'Encontrado';
            this.elementos.estadoDestino.className = 'stat-value text-success';
            
            if (estado.info_destino) {
                this.elementos.infoDestino.innerHTML = this.formatearInfoArchivo(estado.info_destino);
            }
        } else {
            this.elementos.estadoDestino.textContent = 'No encontrado';
            this.elementos.estadoDestino.className = 'stat-value text-warning';
            this.elementos.infoDestino.innerHTML = '<p class="text-muted">Archivo aún no sincronizado</p>';
        }
        
        // NUEVO: Mostrar estado de sincronización
        if (estado.archivos_sincronizados !== undefined) {
            const syncStatus = document.getElementById('estadoSincronizacion');
            if (syncStatus) {
                if (estado.archivos_sincronizados) {
                    syncStatus.textContent = '✅ Sincronizado';
                    syncStatus.className = 'sync-status sync-ok';
                } else {
                    syncStatus.textContent = '⚠️ Desincronizado';
                    syncStatus.className = 'sync-status sync-pending';
                }
            }
        }
    }

    actualizarEstadoConexion(conectado) {
        if (conectado) {
            this.elementos.statusText.textContent = 'Conectado';
            this.elementos.statusDot.classList.add('active');
        } else {
            this.elementos.statusText.textContent = 'Desconectado';
            this.elementos.statusDot.classList.remove('active');
        }
    }

    actualizarBotonesControl() {
        if (this.estado.monitorActivo) {
            this.elementos.btnIniciar.disabled = true;
            this.elementos.btnDetener.disabled = false;
            this.elementos.btnSincronizar.disabled = false;
            
            // NUEVO: Cambiar texto de botones en modo automático
            this.elementos.btnIniciar.innerHTML = '<i class="fas fa-play"></i> Sistema Activo';
            this.elementos.btnDetener.innerHTML = '<i class="fas fa-stop"></i> Detener Automático';
            this.elementos.btnSincronizar.innerHTML = '<i class="fas fa-sync"></i> Sincronizar Ahora';
        } else {
            this.elementos.btnIniciar.disabled = false;
            this.elementos.btnDetener.disabled = true;
            this.elementos.btnSincronizar.disabled = false;
            
            this.elementos.btnIniciar.innerHTML = '<i class="fas fa-play"></i> Iniciar Automático';
            this.elementos.btnDetener.innerHTML = '<i class="fas fa-stop"></i> Detenido';
            this.elementos.btnSincronizar.innerHTML = '<i class="fas fa-sync"></i> Sincronizar Manual';
        }
    }

    toggleConfiguracion() {
        this.estado.configuracionVisible = !this.estado.configuracionVisible;
        
        if (this.estado.configuracionVisible) {
            this.elementos.configContent.classList.remove('collapsed');
            this.elementos.btnToggleConfig.innerHTML = '<i class="fas fa-chevron-up"></i>';
        } else {
            this.elementos.configContent.classList.add('collapsed');
            this.elementos.btnToggleConfig.innerHTML = '<i class="fas fa-chevron-down"></i>';
        }
    }

    // === MÉTODOS DE CONFIGURACIÓN (ACTUALIZADOS) ===
    async cargarConfiguracion() {
        try {
            const response = await fetch('/api/configuracion');
            const config = await response.json();
            
            if (config.error) {
                console.error('Error cargando configuración:', config.error);
                return;
            }
            
            this.elementos.rutaOrigen.value = config.ruta_origen || '';
            this.elementos.rutaDestino.value = config.ruta_destino || '';
            this.elementos.intervaloVerificacion.value = config.intervalo_verificacion || 5;
            this.elementos.intervaloForzado.value = config.intervalo_forzado || 600;
            
            // NUEVO: Actualizar texto del intervalo
            this.actualizarTextoIntervalo(config.intervalo_forzado || 600);
            
        } catch (error) {
            console.error('Error cargando configuración:', error);
            this.mostrarNotificacion('Error cargando configuración', 'error', 'Error');
        }
    }

    async guardarConfiguracion() {
        try {
            this.mostrarLoading('Guardando configuración...');
            
            const configuracion = {
                ruta_origen: this.elementos.rutaOrigen.value.trim(),
                ruta_destino: this.elementos.rutaDestino.value.trim(),
                intervalo_verificacion: parseInt(this.elementos.intervaloVerificacion.value),
                intervalo_forzado: parseInt(this.elementos.intervaloForzado.value)
            };
            
            // Validaciones mejoradas
            if (!configuracion.ruta_origen || !configuracion.ruta_destino) {
                this.mostrarNotificacion('Las rutas de origen y destino son obligatorias', 'warning', 'Validación');
                this.ocultarLoading();
                return;
            }
            
            if (configuracion.intervalo_verificacion < 1 || configuracion.intervalo_verificacion > 300) {
                this.mostrarNotificacion('El intervalo de verificación debe estar entre 1 y 300 segundos', 'warning', 'Validación');
                this.ocultarLoading();
                return;
            }
            
            if (configuracion.intervalo_forzado < 60) {
                this.mostrarNotificacion('Para modo automático, el intervalo mínimo es 60 segundos (1 minuto)', 'warning', 'Validación');
                this.ocultarLoading();
                return;
            }
            
            if (configuracion.intervalo_forzado > 3600) {
                this.mostrarNotificacion('El intervalo máximo es 3600 segundos (1 hora)', 'warning', 'Validación');
                this.ocultarLoading();
                return;
            }
            
            const response = await fetch('/api/configuracion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configuracion)
            });
            
            const resultado = await response.json();
            
            if (resultado.exito) {
                this.mostrarNotificacion(resultado.mensaje, 'success', 'Configuración');
                this.actualizarTextoIntervalo(configuracion.intervalo_forzado);
            } else {
                this.mostrarNotificacion(resultado.mensaje, 'error', 'Error de Configuración');
            }
            
        } catch (error) {
            console.error('Error guardando configuración:', error);
            this.mostrarNotificacion('Error guardando configuración', 'error', 'Error');
        } finally {
            this.ocultarLoading();
        }
    }

    // === MÉTODOS DE LOGS (ACTUALIZADOS) ===
    async cargarLogs() {
        try {
            const lineas = this.elementos.selectLineasLog.value;
            const response = await fetch(`/api/logs?lineas=${lineas}`);
            const datos = await response.json();
            
            if (datos.error) {
                this.elementos.logsContainer.innerHTML = `<p class="text-danger">Error cargando logs: ${datos.error}</p>`;
                return;
            }
            
            if (!datos.logs || datos.logs.length === 0) {
                this.elementos.logsContainer.innerHTML = '<p class="text-muted">No hay logs disponibles</p>';
                return;
            }
            
            // Formatear y mostrar logs con mejor resaltado para modo automático
            const logsHTML = datos.logs.map(linea => {
                const claseCSS = this.obtenerClaseLog(linea);
                const lineaFormateada = this.formatearLineaLog(linea);
                return `<div class="log-line ${claseCSS}">${lineaFormateada}</div>`;
            }).join('');
            
            this.elementos.logsContainer.innerHTML = logsHTML;
            
            // Scroll al final
            this.elementos.logsContainer.scrollTop = this.elementos.logsContainer.scrollHeight;
            
        } catch (error) {
            console.error('Error cargando logs:', error);
            this.elementos.logsContainer.innerHTML = '<p class="text-danger">Error de conexión cargando logs</p>';
        }
    }

    async limpiarLogs() {
        if (!confirm('¿Estás seguro de que quieres limpiar todos los logs?')) {
            return;
        }
        
        try {
            this.mostrarLoading('Limpiando logs...');
            
            const response = await fetch('/api/limpiar-logs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const resultado = await response.json();
            
            if (resultado.exito) {
                this.mostrarNotificacion(resultado.mensaje, 'success', 'Logs');
                this.cargarLogs();
            } else {
                this.mostrarNotificacion(resultado.mensaje, 'error', 'Error');
            }
            
        } catch (error) {
            console.error('Error limpiando logs:', error);
            this.mostrarNotificacion('Error limpiando logs', 'error', 'Error');
        } finally {
            this.ocultarLoading();
        }
    }

    // === MÉTODOS UTILITARIOS (ACTUALIZADOS) ===
    formatearInfoArchivo(info, hash = null) {
        const tamaño = this.formatearTamaño(info.tamaño);
        const fecha = info.fecha_str || 'N/A';
        
        let html = `
            <p><strong>Tamaño:</strong> <span class="file-size">${tamaño}</span></p>
            <p><strong>Modificado:</strong> <span class="file-date">${fecha}</span></p>
        `;
        
        if (hash) {
            html += `<p><strong>Hash:</strong> <span class="file-hash">${hash}</span></p>`;
        }
        
        return html;
    }

    formatearTamaño(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    obtenerClaseLog(linea) {
        // NUEVO: Clases especiales para sincronización automática
        if (linea.includes('SINCRONIZACIÓN AUTOMÁTICA')) return 'log-auto';
        if (linea.includes('ERROR')) return 'log-error';
        if (linea.includes('WARNING')) return 'log-warning';
        if (linea.includes('INFO')) return 'log-info';
        if (linea.includes('exitosamente') || linea.includes('✅')) return 'log-success';
        if (linea.includes('🔄') || linea.includes('⏰')) return 'log-sync';
        return '';
    }
    
    formatearLineaLog(linea) {
        // NUEVO: Formatear líneas de log con iconos y resaltado
        let lineaFormateada = this.escaparHTML(linea);
        
        // Resaltar sincronizaciones automáticas
        lineaFormateada = lineaFormateada.replace(/SINCRONIZACIÓN AUTOMÁTICA #(\d+)/g, 
            '<span class="auto-sync-marker">SINCRONIZACIÓN AUTOMÁTICA #$1</span>');
        
        // Resaltar horas
        lineaFormateada = lineaFormateada.replace(/\[([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\]/g, 
            '<span class="log-timestamp">[$1]</span>');
        
        // Resaltar niveles de log
        lineaFormateada = lineaFormateada.replace(/(ERROR|WARNING|INFO):/g, 
            '<span class="log-level log-level-$1">$1:</span>');
        
        return lineaFormateada;
    }

    escaparHTML(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    validarIntervalo(input, min, max) {
        const valor = parseInt(input.value);
        
        if (isNaN(valor) || valor < min || valor > max) {
            input.classList.add('error');
            input.title = `Debe estar entre ${min} y ${max}`;
        } else {
            input.classList.remove('error');
            input.title = '';
        }
    }

    mostrarLoading(mensaje = 'Cargando...') {
        const spinner = this.elementos.loadingOverlay.querySelector('p');
        if (spinner) {
            spinner.textContent = mensaje;
        }
        this.elementos.loadingOverlay.classList.add('show');
    }

    ocultarLoading() {
        this.elementos.loadingOverlay.classList.remove('show');
    }

    mostrarNotificacion(mensaje, tipo = 'info', titulo = '') {
        const iconos = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        const notificacion = document.createElement('div');
        notificacion.className = `notification ${tipo}`;
        
        notificacion.innerHTML = `
            <div class="notification-icon">
                <i class="${iconos[tipo]}"></i>
            </div>
            <div class="notification-content">
                ${titulo ? `<div class="notification-title">${titulo}</div>` : ''}
                <div class="notification-message">${mensaje}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        this.elementos.notificationContainer.appendChild(notificacion);

        // Auto-eliminar después de 8 segundos (más tiempo para modo automático)
        setTimeout(() => {
            if (notificacion.parentElement) {
                notificacion.remove();
            }
        }, 8000);

        // Efecto de entrada
        setTimeout(() => {
            notificacion.style.transform = 'translateX(0)';
            notificacion.style.opacity = '1';
        }, 100);
    }

    // === MÉTODOS DE GESTIÓN DE EVENTOS ===
    destruir() {
        // Limpiar intervalos
        Object.values(this.intervalos).forEach(intervalo => {
            clearInterval(intervalo);
        });
        
        // Remover event listeners si es necesario
        console.log('UI destruida correctamente');
    }
}

// === INICIALIZACIÓN ACTUALIZADA ===
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar la aplicación
    window.sincronizadorUI = new SincronizadorUI();
    
    // Mostrar información sobre el modo automático
    setTimeout(() => {
        if (window.sincronizadorUI) {
            window.sincronizadorUI.mostrarNotificacion(
                'El sistema sincronizará automáticamente cada 10 minutos. Puedes forzar sincronizaciones manuales cuando necesites.',
                'info',
                '💡 Información'
            );
        }
    }, 3000);
    
    // Manejar errores globales
    window.addEventListener('error', function(e) {
        console.error('Error global:', e.error);
        if (window.sincronizadorUI) {
            window.sincronizadorUI.mostrarNotificacion(
                'Ocurrió un error inesperado en la aplicación', 
                'error', 
                'Error del Sistema'
            );
        }
    });
    
    // Manejar errores de red
    window.addEventListener('offline', function() {
        if (window.sincronizadorUI) {
            window.sincronizadorUI.mostrarNotificacion(
                'Conexión perdida. La sincronización automática continuará cuando se restaure la conexión.',
                'warning',
                'Sin Conexión'
            );
        }
    });
    
    window.addEventListener('online', function() {
        if (window.sincronizadorUI) {
            window.sincronizadorUI.mostrarNotificacion(
                'Conexión restaurada - Sincronización automática activa',
                'success',
                'Conexión'
            );
            // Actualizar estado cuando se recupere la conexión
            window.sincronizadorUI.actualizarEstado();
        }
    });
    
    // Prevenir cierre accidental si el monitor está activo
    window.addEventListener('beforeunload', function(e) {
        if (window.sincronizadorUI && window.sincronizadorUI.estado.monitorActivo) {
            const mensaje = 'El monitor de sincronización automática está activo. ¿Estás seguro de que quieres cerrar?';
            e.returnValue = mensaje;
            return mensaje;
        }
    });
    
    console.log('🚀 Sincronizador Excel OneDrive (Modo Automático) iniciado correctamente');
});

// === CSS DINÁMICO PARA NUEVAS FUNCIONALIDADES ===
const estilosAutomaticos = `
    .countdown-value {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .countdown-normal { color: #28a745; }
    .countdown-warning { color: #ffc107; }
    .countdown-urgent { color: #dc3545; animation: pulse 1s infinite; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .log-auto {
        background: linear-gradient(90deg, #e3f2fd, #bbdefb);
        border-left: 4px solid #2196f3;
        font-weight: bold;
    }
    
    .log-sync {
        background: linear-gradient(90deg, #f3e5f5, #e1bee7);
        border-left: 4px solid #9c27b0;
    }
    
    .auto-sync-marker {
        background: #2196f3;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
    }
    
    .log-timestamp {
        color: #666;
        font-size: 0.9em;
    }
    
    .log-level {
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 0.8em;
        font-weight: bold;
    }
    
    .log-level-ERROR { background: #ffebee; color: #c62828; }
    .log-level-WARNING { background: #fff8e1; color: #f57c00; }
    .log-level-INFO { background: #e8f5e8; color: #2e7d32; }
    
    .sync-status {
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
    }
    
    .sync-ok { background: #e8f5e8; color: #2e7d32; }
    .sync-pending { background: #fff8e1; color: #f57c00; }
    
    .interval-help {
        font-size: 0.85em;
        color: #666;
        margin-top: 4px;
        font-style: italic;
    }
`;

// Inyectar estilos
const styleSheet = document.createElement('style');
styleSheet.textContent = estilosAutomaticos;
document.head.appendChild(styleSheet);