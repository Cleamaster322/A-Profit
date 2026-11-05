import { useEffect, useMemo, useRef, useState } from "react";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import CircularProgress from "@mui/material/CircularProgress";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import {
    deleteProtocolPhoto,
    renameProtocolPhoto,
    uploadProtocolPhoto,
} from "../../shared/protocolPhotoApi";
import { ProtocolPhotoImage } from "./ProtocolInspectionPhotos.jsx";

// Дополнительные фото для оператора (нюансы машины). В протокол и другие документы НЕ попадают.
// Количество не ограничено; у каждого фото обязательно название — его спрашиваем сразу после выбора.

const EXTRA_PHOTO_TYPE = "extra";
const TITLE_MAX_LENGTH = 150;

const invisibleInputSx = {
    position: "fixed",
    left: "-9999px",
    top: "-9999px",
    width: "1px",
    height: "1px",
    opacity: 0,
};

const dialogPaperSx = {border: "2px solid black", borderRadius: 0, boxShadow: "none"};

function errorText(err, fallback) {
    const data = err?.response?.data;
    return data?.title || data?.file || data?.detail || data?.error || fallback;
}

function ProtocolExtraPhotos({
    protocolId,
    photos = [],
    setPhotos,
    onRestoreLock,
    sectionPaperSx,
    sectionTitleSx,
}) {
    // Выбранное, но еще не сохраненное фото: {file, previewUrl, title}.
    const [pending, setPending] = useState(null);
    // Переименование: {photo, title}.
    const [renaming, setRenaming] = useState(null);
    // Просмотр крупно.
    const [viewing, setViewing] = useState(null);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");

    const fileInputRef = useRef(null);
    const cameraInputRef = useRef(null);

    const extraPhotos = useMemo(
        () => photos.filter((photo) => photo.photo_type === EXTRA_PHOTO_TYPE),
        [photos],
    );

    // Превью выбранного файла освобождаем, когда окно закрыто.
    useEffect(() => {
        if (!pending?.previewUrl) {
            return undefined;
        }

        const url = pending.previewUrl;
        return () => URL.revokeObjectURL(url);
    }, [pending?.previewUrl]);

    const openInput = (input) => {
        if (!input) {
            return;
        }

        input.value = "";
        input.click();
    };

    const handleFileSelected = (event) => {
        const file = event.target.files?.[0];
        event.target.value = "";

        if (!file) {
            return;
        }

        setError("");
        setPending({file, previewUrl: URL.createObjectURL(file), title: ""});
    };

    // Как у фото слотов: если блокировка потерялась (возврат из камеры), занимаем протокол и повторяем.
    const withLockRetry = async (request) => {
        try {
            return await request();
        } catch (err) {
            if (err?.response?.status !== 403 || !onRestoreLock) {
                throw err;
            }

            await onRestoreLock();
            return await request();
        }
    };

    const handleSavePending = async () => {
        const title = pending.title.trim();

        try {
            setBusy(true);
            setError("");

            const uploaded = await withLockRetry(
                () => uploadProtocolPhoto(protocolId, pending.file, EXTRA_PHOTO_TYPE, title),
            );

            setPhotos((current) => [...current, uploaded]);
            setPending(null);
        } catch (err) {
            setError(errorText(err, "Не удалось загрузить фото"));
        } finally {
            setBusy(false);
        }
    };

    const handleRename = async () => {
        const title = renaming.title.trim();

        try {
            setBusy(true);
            setError("");

            const updated = await withLockRetry(() => renameProtocolPhoto(renaming.photo.id, title));

            setPhotos((current) => current.map((photo) => (photo.id === updated.id ? updated : photo)));
            setRenaming(null);
        } catch (err) {
            setError(errorText(err, "Не удалось переименовать фото"));
        } finally {
            setBusy(false);
        }
    };

    const handleDelete = async (photo) => {
        if (!window.confirm(`Удалить фото «${photo.title}»?`)) {
            return;
        }

        try {
            setBusy(true);
            setError("");

            await withLockRetry(() => deleteProtocolPhoto(photo.id));

            setPhotos((current) => current.filter((item) => item.id !== photo.id));
        } catch (err) {
            setError(errorText(err, "Не удалось удалить фото"));
        } finally {
            setBusy(false);
        }
    };

    const titleField = (value, onChange, autoFocus = true) => (
        <TextField
            label="Название фото"
            value={value}
            onChange={(event) => onChange(event.target.value.slice(0, TITLE_MAX_LENGTH))}
            placeholder="Например: скол на лобовом стекле справа"
            required
            autoFocus={autoFocus}
            fullWidth
            helperText="Обязательно: по названию оператор поймет, что на фото"
            sx={{mt: 2, "& .MuiOutlinedInput-root": {borderRadius: 0}}}
        />
    );

    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                Дополнительные фото
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{mb: 2}}>
                Фото для оператора с нюансами по машине. В протокол и другие документы не попадают.
            </Typography>

            {error && !pending && !renaming && (
                <Alert severity="error" sx={{mb: 2, borderRadius: 0}}>
                    {error}
                </Alert>
            )}

            <Box sx={{display: "flex", gap: 1, flexWrap: "wrap", mb: extraPhotos.length ? 2 : 0}}>
                <input
                    ref={fileInputRef}
                    style={invisibleInputSx}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelected}
                />
                <input
                    ref={cameraInputRef}
                    style={invisibleInputSx}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handleFileSelected}
                />
                <Button variant="contained" size="small" disabled={busy} onClick={() => openInput(fileInputRef.current)}>
                    Загрузить
                </Button>
                <Button variant="outlined" size="small" disabled={busy} onClick={() => openInput(cameraInputRef.current)}>
                    Сделать фото
                </Button>
            </Box>

            {extraPhotos.length > 0 && (
                <Grid container spacing={2}>
                    {extraPhotos.map((photo) => (
                        <Grid size={{xs: 12, sm: 6, md: 4}} key={photo.id}>
                            <Card variant="outlined" sx={{height: "100%", display: "flex", flexDirection: "column"}}>
                                <Box
                                    onClick={() => setViewing(photo)}
                                    sx={{cursor: "zoom-in"}}
                                    title="Открыть крупно"
                                >
                                    {photo.file_url ? (
                                        <ProtocolPhotoImage key={photo.file_url} fileUrl={photo.file_url} alt={photo.title}/>
                                    ) : null}
                                </Box>
                                <CardContent sx={{flexGrow: 1}}>
                                    <Typography variant="subtitle1">{photo.title}</Typography>
                                </CardContent>
                                <CardActions sx={{display: "flex", flexWrap: "wrap", gap: 1}}>
                                    <Button
                                        variant="outlined"
                                        size="small"
                                        disabled={busy}
                                        onClick={() => {
                                            setError("");
                                            setRenaming({photo, title: photo.title});
                                        }}
                                    >
                                        Переименовать
                                    </Button>
                                    <Button
                                        variant="outlined"
                                        color="error"
                                        size="small"
                                        disabled={busy}
                                        onClick={() => handleDelete(photo)}
                                    >
                                        Удалить
                                    </Button>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            <Dialog
                open={Boolean(pending)}
                onClose={busy ? undefined : () => setPending(null)}
                maxWidth="sm"
                fullWidth
                slotProps={{paper: {sx: dialogPaperSx}}}
            >
                <DialogTitle sx={{fontWeight: 800}}>Новое дополнительное фото</DialogTitle>
                <DialogContent dividers>
                    {error && (
                        <Alert severity="error" sx={{mb: 2, borderRadius: 0}}>
                            {error}
                        </Alert>
                    )}
                    {pending && (
                        <>
                            <Box
                                component="img"
                                src={pending.previewUrl}
                                alt="Выбранное фото"
                                sx={{width: "100%", maxHeight: 360, objectFit: "contain", bgcolor: "#f5f5f5"}}
                            />
                            {titleField(pending.title, (title) => setPending((current) => ({...current, title})))}
                        </>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setPending(null)} disabled={busy}>
                        Отмена
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleSavePending}
                        disabled={busy || !pending?.title.trim()}
                    >
                        {busy ? <CircularProgress size={16}/> : "Сохранить"}
                    </Button>
                </DialogActions>
            </Dialog>

            <Dialog
                open={Boolean(renaming)}
                onClose={busy ? undefined : () => setRenaming(null)}
                maxWidth="sm"
                fullWidth
                slotProps={{paper: {sx: dialogPaperSx}}}
            >
                <DialogTitle sx={{fontWeight: 800}}>Переименовать фото</DialogTitle>
                <DialogContent dividers>
                    {error && (
                        <Alert severity="error" sx={{mb: 2, borderRadius: 0}}>
                            {error}
                        </Alert>
                    )}
                    {renaming && titleField(renaming.title, (title) => setRenaming((current) => ({...current, title})))}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setRenaming(null)} disabled={busy}>
                        Отмена
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleRename}
                        disabled={busy || !renaming?.title.trim()}
                    >
                        {busy ? <CircularProgress size={16}/> : "Сохранить"}
                    </Button>
                </DialogActions>
            </Dialog>

            <Dialog
                open={Boolean(viewing)}
                onClose={() => setViewing(null)}
                maxWidth="lg"
                fullWidth
                slotProps={{paper: {sx: dialogPaperSx}}}
            >
                <DialogTitle sx={{fontWeight: 800}}>{viewing?.title}</DialogTitle>
                <DialogContent dividers>
                    {viewing?.file_url && (
                        <ProtocolPhotoImage
                            key={`view-${viewing.file_url}`}
                            fileUrl={viewing.file_url}
                            alt={viewing.title}
                            sx={{height: "70vh", borderBottom: "none"}}
                        />
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setViewing(null)}>Закрыть</Button>
                </DialogActions>
            </Dialog>
        </Paper>
    );
}

export default ProtocolExtraPhotos;
