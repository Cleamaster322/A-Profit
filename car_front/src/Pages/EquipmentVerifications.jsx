import {useCallback, useEffect, useMemo, useState} from "react";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";
import {getApiErrorMessage} from "../shared/errorHandler.jsx";

import Alert from "@mui/material/Alert";
import Autocomplete from "@mui/material/Autocomplete";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import IconButton from "@mui/material/IconButton";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Switch from "@mui/material/Switch";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import {commonSx} from "../theme.js";

// Поверки СИ / аттестации ИО: вносит исполнительный директор или admin.
// В протокол идет поверка, действующая на дату отбора; при пересечении — старая, пока действует,
// или новая с даты своего начала, если так выбрано. Переключатель «Используется сейчас» в истории
// включен ровно у одной поверки; включение другой делает используемой ее (как радиокнопки).

const pageSx = {...commonSx.page, boxSizing: "border-box"};
const pageInnerSx = {...commonSx.pageInner, boxSizing: "border-box"};
// Белый фон только у рамки ввода: у общего стиля он на всем поле и вылезает под подсказкой.
const textFieldSx = {
    ...commonSx.field,
    bgcolor: "transparent",
    "& .MuiOutlinedInput-root": {...commonSx.field["& .MuiOutlinedInput-root"], bgcolor: "white"},
};

const EMPTY_FORM = {number: "", start_date: "", months: "12", supersedes_previous: false};

const ENDED_HINT = "Срок закончился — использовать нельзя";

// Окна изменения и удаления — как «Изменение сотрудника» на странице «Сотрудники».
const modalPaperSx = {
    border: "2px solid black",
    borderRadius: 0,
    boxShadow: "none",
    bgcolor: "white",
    width: "100%",
    maxWidth: 640,
};
const modalBackdropSx = {bgcolor: "rgba(0, 0, 0, 0.35)", backdropFilter: "blur(4px)"};
const closeButtonSx = {
    color: "black",
    borderRadius: 0,
    border: "1px solid black",
    width: 36,
    height: 36,
    fontWeight: 800,
    "&:hover": {bgcolor: "#eeeeee"},
};

function ModalHeader({title, subtitle, onClose, disabled}) {
    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: 2,
                borderBottom: "2px solid black",
                px: 2.5,
                py: 2,
            }}
        >
            <Box>
                <Typography variant="h5" sx={{fontWeight: 800, color: "black", mb: 0.5}}>
                    {title}
                </Typography>
                <Typography variant="body2" sx={{color: "text.secondary"}}>
                    {subtitle}
                </Typography>
            </Box>
            <IconButton onClick={onClose} disabled={disabled} sx={closeButtonSx}>
                ×
            </IconButton>
        </Box>
    );
}

function todayIso() {
    const now = new Date();
    const pad = (value) => String(value).padStart(2, "0");
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

// Даты в формате ГГГГ-ММ-ДД сравниваются как строки.
function isEnded(verification) {
    return Boolean(verification.end_date) && verification.end_date < todayIso();
}

function isNotStarted(verification) {
    return verification.start_date > todayIso();
}

function nowSwitchHint(verification) {
    if (isEnded(verification)) {
        return ENDED_HINT;
    }
    if (isNotStarted(verification)) {
        return `Начнет действовать с ${formatDate(verification.start_date)}`;
    }
    return "";
}

const STATUS_LABELS = {
    expired: "Поверка закончилась",
    missing: "Нет поверки",
    expiring: "Заканчивается в ближайшие 2 недели",
};

function formatDate(value) {
    const [year, month, day] = String(value || "").split("-");
    return year && month && day ? `${day}.${month}.${year}` : "";
}

// Окончание = начало + N месяцев − 1 день; если такого числа в месяце нет
// (29.02 + 12 мес.) — последний день месяца. Как verification_end_date на сервере.
function calculateEndDate(startDate, months) {
    const [year, month, day] = String(startDate || "").split("-").map(Number);
    const count = Number(months);
    if (!year || !month || !day || !Number.isInteger(count) || count < 1) {
        return "";
    }

    const monthIndex = month - 1 + count;
    const endYear = year + Math.floor(monthIndex / 12);
    const endMonth = monthIndex % 12;
    const lastDay = new Date(endYear, endMonth + 1, 0).getDate();
    const end = new Date(endYear, endMonth, Math.min(day, lastDay));
    if (day <= lastDay) {
        end.setDate(end.getDate() - 1);
    }

    const pad = (value) => String(value).padStart(2, "0");
    return `${pad(end.getDate())}.${pad(end.getMonth() + 1)}.${end.getFullYear()}`;
}

function VerificationFields({value, onChange, disabled, orientationLocked = false, compact = false}) {
    const endDate = calculateEndDate(value.start_date, value.months);

    return (
        <Box
            sx={{
                display: "grid",
                gridTemplateColumns: compact
                    ? {xs: "1fr", sm: "repeat(2, minmax(0, 1fr))"}
                    : {
                        xs: "1fr",
                        md: "minmax(0, 2fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 2fr)",
                    },
                gap: 2,
                // Поля не растягиваются по высоте соседнего поля с подсказкой.
                alignItems: "start",
                pt: compact ? 1 : 0,
            }}
        >
            <TextField
                label="Номер свидетельства / протокола"
                value={value.number}
                onChange={(event) => onChange({...value, number: event.target.value})}
                disabled={disabled}
                fullWidth
                sx={textFieldSx}
            />
            <TextField
                label="Дата начала"
                type="date"
                value={value.start_date}
                onChange={(event) => onChange({...value, start_date: event.target.value})}
                disabled={disabled}
                fullWidth
                sx={textFieldSx}
                slotProps={{inputLabel: {shrink: true}}}
            />
            <TextField
                label="Срок, мес."
                type="number"
                value={value.months}
                onChange={(event) => onChange({...value, months: event.target.value})}
                disabled={disabled}
                fullWidth
                sx={textFieldSx}
                slotProps={{htmlInput: {min: 1, max: 240}}}
            />
            <TextField
                label="Действует до"
                value={endDate}
                fullWidth
                sx={textFieldSx}
                slotProps={{input: {readOnly: true}, inputLabel: {shrink: true}}}
            />
            <TextField
                select
                label="Использовать эту поверку"
                value={value.supersedes_previous ? "new" : "old"}
                onChange={(event) => onChange({...value, supersedes_previous: event.target.value === "new"})}
                disabled={disabled || orientationLocked}
                helperText={orientationLocked ? ENDED_HINT : "Важно, только если старая поверка ещё действует"}
                fullWidth
                sx={textFieldSx}
            >
                <MenuItem value="old">После окончания старой поверки</MenuItem>
                <MenuItem value="new">Сразу с даты начала, старая перестаёт использоваться</MenuItem>
            </TextField>
        </Box>
    );
}

function EquipmentVerifications() {
    const [currentUser, setCurrentUser] = useState(null);
    const [equipment, setEquipment] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [form, setForm] = useState(EMPTY_FORM);
    // Окно «Изменение поверки»: {id, number, start_date, months, supersedes_previous, ended}.
    const [editing, setEditing] = useState(null);
    // Окно удаления: поверка и введенное слово подтверждения.
    const [deleting, setDeleting] = useState(null);
    const [deleteConfirmText, setDeleteConfirmText] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    const canManage = Boolean(currentUser?.is_superuser || currentUser?.role === "executive_director");
    const selected = useMemo(
        () => equipment.find((item) => item.id === selectedId) || null,
        [equipment, selectedId],
    );
    const attention = equipment.filter((item) => STATUS_LABELS[item.status]);

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            setErrorMessage("");

            const userResponse = await api.get("/cars/get-user/");
            setCurrentUser(userResponse.data);

            if (!(userResponse.data.is_superuser || userResponse.data.role === "executive_director")) {
                return;
            }

            const response = await api.get("/cars/equipment/");
            setEquipment(Array.isArray(response.data) ? response.data : []);
        } catch (error) {
            setErrorMessage(getApiErrorMessage(error, "Не удалось загрузить поверки оборудования"));
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const replaceEquipment = (updated) => {
        setEquipment((previous) => previous.map((item) => (item.id === updated.id ? updated : item)));
    };

    const selectEquipment = (item) => {
        setSelectedId(item?.id ?? null);
        setForm(EMPTY_FORM);
        setEditing(null);
        setDeleting(null);
        setSuccessMessage("");
        setErrorMessage("");
    };

    const startEdit = (item) => {
        setErrorMessage("");
        setSuccessMessage("");
        setEditing({
            id: item.id,
            number: item.number,
            start_date: item.start_date,
            months: String(item.months),
            supersedes_previous: Boolean(item.supersedes_previous),
            ended: isEnded(item),
        });
    };

    const startDelete = (item) => {
        setErrorMessage("");
        setSuccessMessage("");
        setDeleteConfirmText("");
        setDeleting(item);
    };

    const payloadOf = (value) => ({
        number: value.number,
        start_date: value.start_date || null,
        months: value.months === "" ? null : Number(value.months),
        supersedes_previous: Boolean(value.supersedes_previous),
    });

    // «Используется сейчас»: включить другую поверку (если перепутали). Выключить текущую нельзя —
    // нужно включить другую, тогда прежняя выключится сама.
    const handleUseNow = async (verification) => {
        if (verification.id === selected?.current_verification_id) {
            return;
        }

        try {
            setSaving(true);
            setErrorMessage("");
            setSuccessMessage("");

            const response = await api.post(`/cars/equipment-verifications/${verification.id}/use-now/`);
            replaceEquipment(response.data);
            setSuccessMessage(`Сейчас используется поверка ${verification.number}`);
        } catch (error) {
            setErrorMessage(getApiErrorMessage(error, "Не удалось переключить поверку"));
        } finally {
            setSaving(false);
        }
    };

    const handleAdd = async () => {
        if (!selected) {
            return;
        }

        try {
            setSaving(true);
            setErrorMessage("");
            setSuccessMessage("");

            const response = await api.post(
                `/cars/equipment/${selected.id}/verifications/create/`,
                payloadOf(form),
            );
            replaceEquipment(response.data);
            setForm(EMPTY_FORM);
            setSuccessMessage(`Поверка для ${selected.code} добавлена`);
        } catch (error) {
            setErrorMessage(getApiErrorMessage(error, "Не удалось добавить поверку"));
        } finally {
            setSaving(false);
        }
    };

    const handleSaveEdit = async () => {
        try {
            setSaving(true);
            setErrorMessage("");
            setSuccessMessage("");

            const response = await api.patch(
                `/cars/equipment-verifications/${editing.id}/update/`,
                payloadOf(editing),
            );
            replaceEquipment(response.data);
            setEditing(null);
            setSuccessMessage("Поверка изменена");
        } catch (error) {
            setErrorMessage(getApiErrorMessage(error, "Не удалось изменить поверку"));
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        if (deleteConfirmText.trim().toLowerCase() !== "удалить") {
            setErrorMessage("Для удаления нужно ввести слово «УДАЛИТЬ».");
            return;
        }

        try {
            setSaving(true);
            setErrorMessage("");
            setSuccessMessage("");

            const response = await api.delete(
                `/cars/equipment-verifications/${deleting.id}/delete/`,
                {data: {confirm_text: deleteConfirmText}},
            );
            replaceEquipment(response.data);
            setSuccessMessage(`Поверка ${deleting.number} удалена`);
            setDeleting(null);
            setDeleteConfirmText("");
        } catch (error) {
            setErrorMessage(getApiErrorMessage(error, "Не удалось удалить поверку"));
        } finally {
            setSaving(false);
        }
    };

    return (
        <>
            <AppHeader/>

            <Box sx={pageSx}>
                <Paper sx={pageInnerSx}>
                    <Typography variant="h4" sx={{fontWeight: 800, color: "black", mb: 0.5}}>
                        Поверки оборудования
                    </Typography>
                    <Typography variant="body1" sx={{color: "text.secondary", mb: 3}}>
                        Поверки СИ и аттестации ИО для таблиц протокола и технической записи.
                        В протокол идет поверка, действующая на дату отбора.
                    </Typography>

                    {loading && <CircularProgress color="inherit"/>}

                    {!loading && !canManage && (
                        <Alert severity="warning" sx={{borderRadius: 0}}>
                            Страница доступна только исполнительному директору и администратору.
                        </Alert>
                    )}

                    {errorMessage && (
                        <Alert severity="error" sx={{mb: 2, borderRadius: 0, whiteSpace: "pre-line"}}>
                            {errorMessage}
                        </Alert>
                    )}
                    {successMessage && (
                        <Alert severity="success" sx={{mb: 2, borderRadius: 0}}>
                            {successMessage}
                        </Alert>
                    )}

                    {!loading && canManage && (
                        <>
                            {attention.length > 0 && (
                                <Alert severity="warning" sx={{mb: 3, borderRadius: 0}}>
                                    <Typography sx={{fontWeight: 700, mb: 1}}>Требуют внимания:</Typography>
                                    {attention.map((item) => (
                                        <Box key={item.id} sx={{display: "flex", gap: 1, alignItems: "center", flexWrap: "wrap", mb: 0.5}}>
                                            <Button
                                                onClick={() => selectEquipment(item)}
                                                sx={{...commonSx.secondaryButton, minHeight: 0, py: 0.25, px: 1}}
                                            >
                                                {item.code}
                                            </Button>
                                            <Typography variant="body2">
                                                {item.name} — {STATUS_LABELS[item.status]}
                                            </Typography>
                                        </Box>
                                    ))}
                                </Alert>
                            )}

                            <Autocomplete
                                options={equipment}
                                value={selected}
                                onChange={(event, item) => selectEquipment(item)}
                                getOptionLabel={(item) => `${item.code} ${item.name}`}
                                isOptionEqualToValue={(option, value) => option.id === value.id}
                                noOptionsText="Ничего не найдено"
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Оборудование (название или инв. №, например СИ035)"
                                        sx={textFieldSx}
                                    />
                                )}
                                sx={{mb: 3, maxWidth: 760}}
                            />

                            {selected && (
                                <>
                                    <Typography variant="h6" sx={{...commonSx.sectionTitle, mb: 2}}>
                                        Новая поверка
                                    </Typography>
                                    <VerificationFields value={form} onChange={setForm} disabled={saving}/>
                                    <Button
                                        onClick={handleAdd}
                                        disabled={saving || !form.number.trim() || !form.start_date || !form.months}
                                        sx={{...commonSx.primaryButton, mt: 2, mb: 4}}
                                    >
                                        {saving ? "Сохранение..." : "Добавить поверку"}
                                    </Button>

                                    <Typography variant="h6" sx={{...commonSx.sectionTitle, mb: 1}}>
                                        История поверок: {selected.code} {selected.name}
                                    </Typography>
                                    <Box sx={{overflowX: "auto"}}>
                                        <Table size="small" sx={{border: "2px solid black", minWidth: 640}}>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell sx={{fontWeight: 700}}>Номер</TableCell>
                                                    <TableCell sx={{fontWeight: 700}}>Начало</TableCell>
                                                    <TableCell sx={{fontWeight: 700}}>Срок</TableCell>
                                                    <TableCell sx={{fontWeight: 700}}>Действует до</TableCell>
                                                    <TableCell sx={{fontWeight: 700}}>Используется сейчас</TableCell>
                                                    <TableCell/>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {[...selected.verifications].reverse().map((item) => (
                                                        <TableRow key={item.id}>
                                                            <TableCell>{item.number}</TableCell>
                                                            <TableCell>{formatDate(item.start_date)}</TableCell>
                                                            <TableCell>{item.months} мес.</TableCell>
                                                            <TableCell>{formatDate(item.end_date)}</TableCell>
                                                            <TableCell>
                                                                <Tooltip title={nowSwitchHint(item)}>
                                                                    <span>
                                                                        <Switch
                                                                            checked={item.id === selected.current_verification_id}
                                                                            onChange={() => handleUseNow(item)}
                                                                            disabled={saving || Boolean(nowSwitchHint(item))}
                                                                            slotProps={{input: {"aria-label": "Используется сейчас"}}}
                                                                        />
                                                                    </span>
                                                                </Tooltip>
                                                            </TableCell>
                                                            <TableCell align="right" sx={{whiteSpace: "nowrap"}}>
                                                                <Button
                                                                    onClick={() => startEdit(item)}
                                                                    disabled={saving}
                                                                    sx={{...commonSx.secondaryButton, minHeight: 0, py: 0.5, mr: 1}}
                                                                >
                                                                    Изменить
                                                                </Button>
                                                                <Button
                                                                    onClick={() => startDelete(item)}
                                                                    disabled={saving}
                                                                    sx={{...commonSx.secondaryButton, minHeight: 0, py: 0.5}}
                                                                >
                                                                    Удалить
                                                                </Button>
                                                            </TableCell>
                                                        </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </Box>
                                </>
                            )}
                        </>
                    )}
                </Paper>
            </Box>

            <Dialog
                open={Boolean(editing)}
                onClose={saving ? undefined : () => setEditing(null)}
                maxWidth="sm"
                fullWidth
                slotProps={{backdrop: {sx: modalBackdropSx}, paper: {sx: modalPaperSx}}}
            >
                {editing && (
                    <>
                        <ModalHeader
                            title="Изменение поверки"
                            subtitle={selected ? `${selected.code} ${selected.name}` : ""}
                            onClose={() => setEditing(null)}
                            disabled={saving}
                        />
                        <DialogContent sx={{p: 2.5}}>
                            {errorMessage && (
                                <Alert severity="error" sx={{mb: 2, borderRadius: 0, whiteSpace: "pre-line"}}>
                                    {errorMessage}
                                </Alert>
                            )}
                            <VerificationFields
                                value={editing}
                                onChange={setEditing}
                                disabled={saving}
                                orientationLocked={editing.ended}
                                compact
                            />
                            <Box sx={{display: "flex", gap: 1, mt: 2.5, flexWrap: "wrap"}}>
                                <Button
                                    onClick={handleSaveEdit}
                                    disabled={saving || !editing.number.trim() || !editing.start_date || !editing.months}
                                    sx={commonSx.primaryButton}
                                >
                                    {saving ? "Сохранение..." : "Сохранить"}
                                </Button>
                                <Button onClick={() => setEditing(null)} disabled={saving} sx={commonSx.secondaryButton}>
                                    Отмена
                                </Button>
                            </Box>
                        </DialogContent>
                    </>
                )}
            </Dialog>

            <Dialog
                open={Boolean(deleting)}
                onClose={saving ? undefined : () => setDeleting(null)}
                maxWidth="sm"
                fullWidth
                slotProps={{backdrop: {sx: modalBackdropSx}, paper: {sx: modalPaperSx}}}
            >
                {deleting && (
                    <>
                        <ModalHeader
                            title="Удаление поверки"
                            subtitle={selected ? `${selected.code} ${selected.name}` : ""}
                            onClose={() => setDeleting(null)}
                            disabled={saving}
                        />
                        <DialogContent sx={{p: 2.5}}>
                            {errorMessage && (
                                <Alert severity="error" sx={{mb: 2, borderRadius: 0, whiteSpace: "pre-line"}}>
                                    {errorMessage}
                                </Alert>
                            )}
                            <Typography sx={{fontWeight: 800, color: "black", mb: 1}}>
                                Для удаления поверки {deleting.number} от {formatDate(deleting.start_date)} введите
                                слово «УДАЛИТЬ».
                            </Typography>
                            <Typography variant="body2" sx={{color: "text.secondary", mb: 2}}>
                                Если эта поверка стояла в уже выпущенных протоколах, при пересборке там окажется
                                другая поверка или ее не будет вовсе.
                            </Typography>
                            <TextField
                                fullWidth
                                value={deleteConfirmText}
                                onChange={(event) => setDeleteConfirmText(event.target.value)}
                                placeholder="УДАЛИТЬ"
                                disabled={saving}
                                sx={{...textFieldSx, mb: 2}}
                            />
                            <Box sx={{display: "flex", gap: 1, flexWrap: "wrap"}}>
                                <Button
                                    onClick={handleDelete}
                                    disabled={saving || deleteConfirmText.trim().toLowerCase() !== "удалить"}
                                    sx={commonSx.primaryButton}
                                >
                                    {saving ? "Удаление..." : "Удалить"}
                                </Button>
                                <Button onClick={() => setDeleting(null)} disabled={saving} sx={commonSx.secondaryButton}>
                                    Отмена
                                </Button>
                            </Box>
                        </DialogContent>
                    </>
                )}
            </Dialog>
        </>
    );
}

export default EquipmentVerifications;
