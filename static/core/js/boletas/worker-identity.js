(() => {
    'use strict';
    const form = document.getElementById('identity-form');
    const pad = document.getElementById('signature-pad');
    const context = pad.getContext('2d');
    const signature = document.getElementById('id_signature');
    const photo = document.getElementById('id_photo');
    const preview = document.getElementById('photo-preview');
    const error = document.getElementById('identity-error');
    let drawing = false;
    let hasInk = false;
    let previewUrl;
    context.lineWidth = 4;
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.strokeStyle = '#172c38';
    function point(event) {
        const bounds = pad.getBoundingClientRect();
        return [(event.clientX - bounds.left) * pad.width / bounds.width,
            (event.clientY - bounds.top) * pad.height / bounds.height];
    }
    pad.addEventListener('pointerdown', event => {
        if (event.button !== 0) return;
        event.preventDefault();
        pad.setPointerCapture(event.pointerId);
        drawing = true;
        context.beginPath();
        context.moveTo(...point(event));
    });
    pad.addEventListener('pointermove', event => {
        if (!drawing) return;
        event.preventDefault();
        context.lineTo(...point(event));
        context.stroke();
        hasInk = true;
    });
    function finish() {
        drawing = false;
        signature.value = hasInk ? pad.toDataURL('image/png') : '';
    }
    pad.addEventListener('pointerup', finish);
    pad.addEventListener('pointercancel', finish);
    document.getElementById('clear-signature').addEventListener('click', () => {
        context.clearRect(0, 0, pad.width, pad.height);
        drawing = hasInk = false;
        signature.value = '';
    });
    if (signature.value.startsWith('data:image/png;base64,')) {
        const saved = new Image();
        saved.onload = () => { context.drawImage(saved, 0, 0, pad.width, pad.height); hasInk = true; };
        saved.src = signature.value;
    }
    photo.addEventListener('change', () => {
        error.textContent = '';
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        preview.hidden = true;
        const file = photo.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/') || file.size > 5 * 1024 * 1024) {
            error.textContent = 'Selecciona una fotografía de menos de 5 MB.';
            photo.value = '';
            return;
        }
        previewUrl = URL.createObjectURL(file);
        preview.src = previewUrl;
        preview.hidden = false;
    });
    form.addEventListener('submit', event => {
        finish();
        if (!hasInk || !photo.files.length) {
            event.preventDefault();
            error.textContent = 'Debes tomar tu foto y dibujar tu firma antes de continuar.';
            return;
        }
        const button = document.getElementById('save-identity');
        button.disabled = true;
        button.textContent = 'Guardando registro…';
    });
    window.addEventListener('pageshow', () => {
        const button = document.getElementById('save-identity');
        button.disabled = false;
        button.textContent = 'Guardar y entrar al portal';
    });
})();
