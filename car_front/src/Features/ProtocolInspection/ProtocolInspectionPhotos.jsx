import { useEffect, useMemo, useRef, useState } from "react";

import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import CircularProgress from "@mui/material/CircularProgress";

import {
    deleteProtocolPhoto,
    fetchProtocolPhotoBlob,
    uploadProtocolPhoto,
} from "../../shared/protocolPhotoApi";
import {
    clearPhotoCaptureMarker,
    readPhotoCaptureMarker,
    savePhotoCaptureMarker,
} from "./photoCaptureMarker";

const imageAccept = "image/*";

const invisibleInputSx = {
    position: "fixed",
    left: "-9999px",
    top: "-9999px",
    width: "1px",
    height: "1px",
    opacity: 0,
};

const photoBoxSx = {
    width: "100%",
    height: 220,
    backgroundColor: "#ffffff",
    borderBottom: "1px solid #e0e0e0",
};

// Фото с защищённого адреса (нужен JWT) — грузим через api и показываем blob.
// Компонент монтируется с key={fileUrl}, поэтому при смене фото состояние начинается заново.
function ProtocolPhotoImage({ fileUrl, alt }) {
    const [src, setSrc] = useState("");
    const [failed, setFailed] = useState(false);

    useEffect(() => {
        let cancelled = false;
        let objectUrl = "";

        fetchProtocolPhotoBlob(fileUrl)
            .then((blob) => {
                if (cancelled) {
                    return;
                }

                objectUrl = URL.createObjectURL(blob);
                setSrc(objectUrl);
            })
            .catch(() => {
                if (!cancelled) {
                    setFailed(true);
                }
            });

        return () => {
            cancelled = true;

            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [fileUrl]);

    if (!src) {
        return (
            <Box
                sx={{
                    ...photoBoxSx,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "text.secondary",
                }}
            >
                {failed ? "Не удалось загрузить фото" : <CircularProgress size={24} />}
            </Box>
        );
    }

    return (
        <CardMedia
            component="img"
            image={src}
            alt={alt}
            sx={{
                ...photoBoxSx,
                objectFit: "contain",
            }}
        />
    );
}

// Группа «Фотофиксация»: слоты фото из схемы (photo_slots.py), которые
// показываются после одного блока страницы протокола. В каждом слоте одно фото.
function ProtocolInspectionPhotos({
    protocolId,
    group,
    slots = [],
    photos = [],
    setPhotos,
    onRestoreLock,
    sectionPaperSx,
    sectionTitleSx,
}) {
    const [uploadingType, setUploadingType] = useState(null);
    const [deletingId, setDeletingId] = useState(null);
    const [error, setError] = useState("");
    const [lostCapture, setLostCapture] = useState(null);

    const sectionRef = useRef(null);
    const fileInputRefs = useRef({});
    const cameraInputRefs = useRef({});

    const groupSlots = useMemo(
        () => slots.filter((slot) => slot.group === group),
        [slots, group]
    );

    const photosByType = useMemo(() => {
        const result = {};

        photos.forEach((photo) => {
            result[photo.photo_type] = photo;
        });

        return result;
    }, [photos]);

    const getUploadErrorText = (err, defaultMessage) => {
        return (
            err?.response?.data?.file ||
            err?.response?.data?.photo_type ||
            err?.response?.data?.error ||
            err?.response?.data?.detail ||
            defaultMessage
        );
    };

    // Загрузка с одним повтором: если сервер ответил 403 (блокировка протокола
    // потеряна, например после возврата из камеры), занимаем протокол заново
    // и отправляем фото ещё раз.
    const uploadWithLockRetry = async (file, photoType) => {
        try {
            return await uploadProtocolPhoto(protocolId, file, photoType);
        } catch (err) {
            if (err?.response?.status !== 403 || !onRestoreLock) {
                throw err;
            }

            await onRestoreLock();

            return await uploadProtocolPhoto(protocolId, file, photoType);
        }
    };

    // Отметка дожила до загрузки страницы — значит, вкладку выгрузили,
    // пока была открыта камера, и снимок потерян. Показывает её та группа,
    // из которой открывали камеру.
    useEffect(() => {
        if (!protocolId) {
            return;
        }

        const marker = readPhotoCaptureMarker(protocolId);

        if (!marker || marker.group !== group) {
            return;
        }

        clearPhotoCaptureMarker(protocolId);
        setLostCapture(marker);
        sectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, [protocolId, group]);

    // Страница пережила переход в камеру: снимок придёт через onChange
    // (или пользователь отменил съёмку), отметка больше не нужна.
    useEffect(() => {
        if (!protocolId) {
            return;
        }

        const handleVisibilityChange = () => {
            if (document.visibilityState === "visible") {
                clearPhotoCaptureMarker(protocolId);
            }
        };

        document.addEventListener("visibilitychange", handleVisibilityChange);

        return () => {
            document.removeEventListener("visibilitychange", handleVisibilityChange);
        };
    }, [protocolId]);

    const openInput = (input) => {
        if (!input) {
            return;
        }

        input.value = "";
        input.click();
    };

    const openCamera = (input, slotTitle) => {
        setLostCapture(null);
        savePhotoCaptureMarker(protocolId, slotTitle, group);
        openInput(input);
    };

    const handlePhotoUpload = async (event, slot) => {
        const file = event.target.files?.[0];

        if (!file) {
            event.target.value = "";
            return;
        }

        try {
            setError("");
            setUploadingType(slot.photo_type);

            const uploadedPhoto = await uploadWithLockRetry(file, slot.photo_type);

            setPhotos((currentPhotos) => [
                ...currentPhotos.filter((photo) => photo.photo_type !== slot.photo_type),
                uploadedPhoto,
            ]);
        } catch (err) {
            setError(getUploadErrorText(err, "Не удалось загрузить фото"));
        } finally {
            setUploadingType(null);
            event.target.value = "";
        }
    };

    const handleDeletePhoto = async (photoId) => {
        try {
            setError("");
            setDeletingId(photoId);

            await deleteProtocolPhoto(photoId);

            setPhotos((currentPhotos) => currentPhotos.filter((photo) => photo.id !== photoId));
        } catch (err) {
            setError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                "Не удалось удалить фото"
            );
        } finally {
            setDeletingId(null);
        }
    };

    if (!groupSlots.length) {
        return null;
    }

    return (
        <Paper ref={sectionRef} sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                Фотофиксация
            </Typography>

            {lostCapture && (
                <Alert
                    severity="warning"
                    onClose={() => setLostCapture(null)}
                    sx={{ mb: 3, borderRadius: 0 }}
                >
                    Фото «{lostCapture.slotLabel}» не загружено: пока была открыта
                    камера, браузер перезагрузил страницу. Сделайте фото ещё раз или
                    сфотографируйте обычной камерой и нажмите «Загрузить».
                </Alert>
            )}

            {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 0 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={2}>
                {groupSlots.map((slot) => {
                    const photo = photosByType[slot.photo_type];
                    const isUploading = uploadingType === slot.photo_type;
                    const isDeleting = photo && deletingId === photo.id;

                    return (
                        <Grid item xs={12} sm={6} md={4} key={slot.photo_type}>
                            <Card variant="outlined" sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
                                {photo?.file_url ? (
                                    <ProtocolPhotoImage
                                        key={photo.file_url}
                                        fileUrl={photo.file_url}
                                        alt={slot.title}
                                    />
                                ) : (
                                    <Box
                                        sx={{
                                            ...photoBoxSx,
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            bgcolor: "#f5f5f5",
                                            color: "text.secondary",
                                        }}
                                    >
                                        Фото не загружено
                                    </Box>
                                )}

                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Typography variant="subtitle1">
                                        {slot.title}
                                    </Typography>

                                    {slot.description && (
                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{ mt: 0.5 }}
                                        >
                                            {slot.description}
                                        </Typography>
                                    )}
                                </CardContent>

                                <CardActions
                                    sx={{
                                        display: "flex",
                                        flexWrap: "wrap",
                                        gap: 1,
                                    }}
                                >
                                    <input
                                        ref={(element) => {
                                            fileInputRefs.current[slot.photo_type] = element;
                                        }}
                                        style={invisibleInputSx}
                                        type="file"
                                        accept={imageAccept}
                                        onChange={(event) => handlePhotoUpload(event, slot)}
                                    />

                                    <input
                                        ref={(element) => {
                                            cameraInputRefs.current[slot.photo_type] = element;
                                        }}
                                        style={invisibleInputSx}
                                        type="file"
                                        accept={imageAccept}
                                        capture="environment"
                                        onChange={(event) => handlePhotoUpload(event, slot)}
                                    />

                                    <Button
                                        variant="contained"
                                        size="small"
                                        disabled={isUploading}
                                        onClick={() =>
                                            openInput(fileInputRefs.current[slot.photo_type])
                                        }
                                    >
                                        {isUploading ? (
                                            <>
                                                <CircularProgress size={16} sx={{ mr: 1 }} />
                                                Загрузка
                                            </>
                                        ) : photo ? (
                                            "Заменить"
                                        ) : (
                                            "Загрузить"
                                        )}
                                    </Button>

                                    <Button
                                        variant="outlined"
                                        size="small"
                                        disabled={isUploading}
                                        onClick={() =>
                                            openCamera(
                                                cameraInputRefs.current[slot.photo_type],
                                                slot.title
                                            )
                                        }
                                    >
                                        Сделать фото
                                    </Button>

                                    {photo && (
                                        <Button
                                            variant="outlined"
                                            color="error"
                                            size="small"
                                            disabled={isDeleting}
                                            onClick={() => handleDeletePhoto(photo.id)}
                                        >
                                            {isDeleting ? "Удаление..." : "Удалить"}
                                        </Button>
                                    )}
                                </CardActions>
                            </Card>
                        </Grid>
                    );
                })}
            </Grid>
        </Paper>
    );
}

export default ProtocolInspectionPhotos;
