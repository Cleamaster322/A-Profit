import {useCallback, useEffect, useMemo, useState} from "react";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";
import {getApiErrorMessage} from "../shared/errorHandler.jsx";

import Alert from "@mui/material/Alert";
import Autocomplete from "@mui/material/Autocomplete";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {commonSx} from "../theme.js";

// Поверки СИ / аттестации ИО: вносит исполнительный директор или admin.
// В протокол идет поверка, действующая на дату отбора; при пересечении — старая, пока действует.

const pageSx = {...commonSx.page, boxSizing: "border-box"};
const pageInnerSx = {...commonSx.pageInner, boxSizing: "border-box"};
const textFieldSx = commonSx.field;

const EMPTY_FORM = {number: "", start_date: "", months: "12"};

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

function VerificationFields({value, onChange, disabled}) {
    const endDate = calculateEndDate(value.start_date, value.months);

    return (
        <Box
            sx={{
                display: "grid",
                gridTemplateColumns: {xs: "1fr", md: "minmax(0, 2fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)"},
                gap: 2,
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
        </Box>
    );
}

function EquipmentVerifications() {
    const [currentUser, setCurrentUser] = useState(null);
    const [equipment, setEquipment] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [form, setForm] = useState(EMPTY_FORM);
    const [editing, setEditing] = useState(null);
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
        setSuccessMessage("");
        setErrorMessage("");
    };

    const payloadOf = (value) => ({
        number: value.number,
        start_date: value.start_date || null,
        months: value.months === "" ? null : Number(value.months),
    });

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
            setSuccessMessage("Поверка исправлена");
        } catch (error) {
            setErrorMessage(getApiErrorMessage(error, "Не удалось исправить поверку"));
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
                                                    <TableCell/>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {[...selected.verifications].reverse().map((item) => (
                                                    editing?.id === item.id ? (
                                                        <TableRow key={item.id}>
                                                            <TableCell colSpan={5}>
                                                                <VerificationFields value={editing} onChange={setEditing} disabled={saving}/>
                                                                <Box sx={{display: "flex", gap: 1, mt: 1.5}}>
                                                                    <Button onClick={handleSaveEdit} disabled={saving} sx={commonSx.primaryButton}>
                                                                        Сохранить
                                                                    </Button>
                                                                    <Button onClick={() => setEditing(null)} disabled={saving} sx={commonSx.secondaryButton}>
                                                                        Отмена
                                                                    </Button>
                                                                </Box>
                                                            </TableCell>
                                                        </TableRow>
                                                    ) : (
                                                        <TableRow key={item.id}>
                                                            <TableCell>{item.number}</TableCell>
                                                            <TableCell>{formatDate(item.start_date)}</TableCell>
                                                            <TableCell>{item.months} мес.</TableCell>
                                                            <TableCell>
                                                                {formatDate(item.end_date)}
                                                                {item.id === selected.current_verification_id && (
                                                                    <Chip
                                                                        label="сейчас в протоколе"
                                                                        size="small"
                                                                        sx={{...commonSx.inversePill, ml: 1}}
                                                                    />
                                                                )}
                                                            </TableCell>
                                                            <TableCell align="right">
                                                                <Button
                                                                    onClick={() => setEditing({
                                                                        id: item.id,
                                                                        number: item.number,
                                                                        start_date: item.start_date,
                                                                        months: String(item.months),
                                                                    })}
                                                                    disabled={saving}
                                                                    sx={{...commonSx.secondaryButton, minHeight: 0, py: 0.5}}
                                                                >
                                                                    Исправить
                                                                </Button>
                                                            </TableCell>
                                                        </TableRow>
                                                    )
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
        </>
    );
}

export default EquipmentVerifications;
