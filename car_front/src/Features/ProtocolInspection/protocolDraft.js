const DRAFT_VERSION = 1;
const DRAFT_TTL_MS = 3 * 24 * 60 * 60 * 1000; // черновик живёт 3 суток

// поля, которыми управляет сервер, а не пользователь
const SERVER_ONLY_FIELDS = new Set(["status", "revision_comment"]);

const draftKey = (protocolId) => `protocolDraft:v${DRAFT_VERSION}:${protocolId}`;

const isSame = (a, b) => JSON.stringify(a) === JSON.stringify(b);

function getChangedFields(base, form) {
    const changed = {};

    Object.keys(form || {}).forEach((key) => {
        if (SERVER_ONLY_FIELDS.has(key)) return;
        if (!isSame(form[key], base?.[key])) {
            changed[key] = form[key];
        }
    });

    return changed;
}

export function saveProtocolDraft(protocolId, serverForm, currentForm) {
    const fields = getChangedFields(serverForm, currentForm);

    try {
        if (!Object.keys(fields).length) {
            localStorage.removeItem(draftKey(protocolId));
            return;
        }

        localStorage.setItem(
            draftKey(protocolId),
            JSON.stringify({version: DRAFT_VERSION, savedAt: Date.now(), fields}),
        );
    } catch {
        // хранилище переполнено или недоступно: черновик не критичен
    }
}

export function readProtocolDraft(protocolId) {
    try {
        const raw = localStorage.getItem(draftKey(protocolId));
        if (!raw) return null;

        const draft = JSON.parse(raw);

        if (
            draft?.version !== DRAFT_VERSION
            || !draft.fields
            || Date.now() - draft.savedAt > DRAFT_TTL_MS
        ) {
            localStorage.removeItem(draftKey(protocolId));
            return null;
        }

        return draft;
    } catch {
        return null;
    }
}

export function clearProtocolDraft(protocolId) {
    try {
        localStorage.removeItem(draftKey(protocolId));
    } catch {
        // ничего не делаем
    }
}

export function applyProtocolDraft(serverForm, draft) {
    const fields = {};

    Object.keys(draft.fields).forEach((key) => {
        if (key in serverForm && !SERVER_ONLY_FIELDS.has(key)) {
            fields[key] = draft.fields[key];
        }
    });

    return {
        form: {...serverForm, ...fields},
        count: Object.keys(fields).length,
    };
}