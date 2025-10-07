document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const fileCount = document.getElementById('fileCount');
    const uploadForm = document.getElementById('uploadForm');
    const processBtn = document.getElementById('processBtn');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const statusCards = document.getElementById('statusCards');
    const resultSection = document.getElementById('resultSection');
    const resultContent = document.getElementById('resultContent');

    // === Evento: mostrar archivos seleccionados ===
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            fileCount.textContent = `${files.length} archivo(s) seleccionado(s)`;
            fileCount.className = 'text-success';
        } else {
            fileCount.textContent = 'No se han seleccionado archivos';
            fileCount.className = 'text-muted';
        }
    });

    // === Evento: enviar formulario ===
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const files = fileInput.files;
        if (files.length === 0) {
            alert('Debe seleccionar al menos un archivo.');
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('archivos', files[i]);
        }

        prepareUIBeforeUpload(files);
        simulateProgressBars(files);

        try {
            const response = await sendFilesToServer(formData);
            showResults(response, files.length);
        } catch (error) {
            showError(error);
        }
    });

    // === Configurar UI inicial de tarjetas de progreso ===
    function prepareUIBeforeUpload(files) {
        progressSection.style.display = 'block';
        processBtn.disabled = true;
        statusCards.innerHTML = '';

        Array.from(files).forEach((file, i) => {
            statusCards.innerHTML += createStatusCard(file.name, i);
        });
    }

    // === Crear tarjeta HTML de progreso por archivo ===
    function createStatusCard(fileName, index) {
        return `
            <div class="col-md-6 mb-3">
                <div class="card status-card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title d-flex justify-content-between">
                            <span class="text-truncate">${fileName}</span>
                            <span id="statusIcon${index}" class="text-muted">
                                <i class="bi bi-hourglass-split"></i>
                            </span>
                        </h5>
                        <div class="progress" style="height: 8px;">
                            <div id="fileProgress${index}" class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="statusText${index}" class="text-muted">En cola</small>
                    </div>
                </div>
            </div>
        `;
    }

    // === Simular progreso de carga por archivo ===
    function simulateProgressBars(files) {
        Array.from(files).forEach((_, i) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    updateFileStatus(i, 'Completado', true);
                } else {
                    updateFileStatus(i, `${Math.round(progress)}% procesado`);
                }
                document.getElementById(`fileProgress${i}`).style.width = `${progress}%`;
            }, 300 + (i * 100));
        });
    }

    // === Actualizar texto e ícono del estado del archivo ===
    function updateFileStatus(index, text, success = false) {
        const statusText = document.getElementById(`statusText${index}`);
        const statusIcon = document.getElementById(`statusIcon${index}`);
        statusText.textContent = text;
        statusText.className = success ? 'text-success' : 'text-muted';
        if (success) {
            statusIcon.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
        }
    }

    // === Enviar archivos al backend usando XMLHttpRequest ===
    function sendFilesToServer(formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/procesar', true);

            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = `${percent}%`;
                    progressText.textContent = `${percent}%`;
                }
            };

            xhr.onload = () => {
                if (xhr.status === 200) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(xhr);
                }
            };

            xhr.onerror = () => reject(xhr);
            xhr.send(formData);
        });
    }

    // === Mostrar resultados después de subir ===
    function showResults(response, totalFiles) {
        resultContent.innerHTML = `
            <p><i class="bi bi-file-earmark-excel"></i> <strong>Archivo generado:</strong> ${response.ruta_final}</p>
            <p><i class="bi bi-check2-circle"></i> <strong>Archivos procesados:</strong> ${response.archivos_procesados} de ${totalFiles}</p>
            <p><i class="bi bi-exclamation-triangle"></i> <strong>Líneas omitidas:</strong> ${response.total_lineas_omitidas}</p>
            ${response.advertencias.length > 0 ? 
                `<div class="mt-3 alert alert-warning">
                    <h5><i class="bi bi-exclamation-octagon"></i> Advertencias:</h5>
                    <ul class="mb-0">${response.advertencias.map(adv => `<li>${adv}</li>`).join('')}</ul>
                </div>` : 
                '<div class="mt-3 alert alert-success"><i class="bi bi-check-all"></i> Todos los archivos se procesaron correctamente</div>'
            }
        `;

        progressSection.style.display = 'none';
        resultSection.style.display = 'block';
    }

    // === Manejo de errores durante subida ===
    function showError(xhr) {
        let errorMsg = 'Error al procesar los archivos';
        try {
            const response = JSON.parse(xhr.responseText);
            errorMsg += `: ${response.error || response.message || xhr.statusText}`;
        } catch (e) {
            errorMsg += `: ${xhr.statusText}`;
        }

        alert(errorMsg);
        processBtn.disabled = false;
    }
});
