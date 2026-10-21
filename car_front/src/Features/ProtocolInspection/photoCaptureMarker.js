// Отметка «камера открыта». Если Android выгрузил вкладку, пока открыта камера,
// снимок до страницы не доходит; отметка переживает перезагрузку и позволяет
// сообщить пользователю, что фото нужно сделать заново.
const MARKER_TTL_MS = 15 * 60 * 1000; // старше 15 минут — уже не относится к делу

const markerKey = (protocolId) => `protocolPhotoCapture:${protocolId}`;

export function savePhotoCaptureMarker(protocolId, slotLabel) {
    try {
        localStorage.setItem(
            markerKey(protocolId),
            JSON.stringify({slotLabel, startedAt: Date.now()}),
        );
    } catch {
        // хранилище недоступно: без отметки просто не будет предупреждения
    }
}

export function readPhotoCaptureMarker(protocolId) {
    try {
        const raw = localStorage.getItem(markerKey(protocolId));
        if (!raw) return null;

        const marker = JSON.parse(raw);

        if (!marker?.startedAt || Date.now() - marker.startedAt > MARKER_TTL_MS) {
            localStorage.removeItem(markerKey(protocolId));
            return null;
        }

        return marker;
    } catch {
        return null;
    }
}

export function clearPhotoCaptureMarker(protocolId) {
    try {
        localStorage.removeItem(markerKey(protocolId));
    } catch {
        // ничего не делаем
    }
}
