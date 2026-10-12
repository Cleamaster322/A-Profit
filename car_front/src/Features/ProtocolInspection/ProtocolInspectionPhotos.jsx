import { useMemo, useRef, useState } from "react";

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
    uploadProtocolPhoto,
} from "../../shared/protocolPhotoApi";

const DOCX_PHOTO_SLOTS = [
    {
        type: "stand_test_photo",
        label: "Фото 1. Испытания на тормозном стенде",
        sortOrder: 1,
    },
    {
        type: "gas_test_photo",
        label: "Фото 2. Измерение уровня выбросов отработавших газов",
        sortOrder: 2,
    },
    {
        type: "noise_test_photo",
        label: "Фото 3. Измерение уровня шума",
        sortOrder: 3,
    },
];

const imageAccept = "image/*";

const invisibleInputSx = {
    position: "fixed",
    left: "-9999px",
    top: "-9999px",
    width: "1px",
    height: "1px",
    opacity: 0,
};

function ProtocolInspectionPhotos({
    protocolId,
    photos = [],
    setPhotos,
    sectionPaperSx,
    sectionTitleSx,
    subsectionTitleSx,
}) {
    const [uploadingType, setUploadingType] = useState(null);
    const [deletingId, setDeletingId] = useState(null);
    const [error, setError] = useState("");

    const mainFileInputRefs = useRef({});
    const mainCameraInputRefs = useRef({});
    const additionalFileInputRef = useRef(null);
    const additionalCameraInputRef = useRef(null);

    const photosByType = useMemo(() => {
        const result = {};

        photos.forEach((photo) => {
            if (!result[photo.photo_type]) {
                result[photo.photo_type] = photo;
            }
        });

        return result;
    }, [photos]);

    const additionalPhotos = useMemo(() => {
        return photos.filter((photo) => !photo.is_docx_photo);
    }, [photos]);

    const sortPhotos = (items) => {
        return [...items].sort((a, b) => {
            if (a.sort_order === b.sort_order) {
                return a.id - b.id;
            }

            return a.sort_order - b.sort_order;
        });
    };

    const getUploadErrorText = (err, defaultMessage) => {
        return (
            err?.response?.data?.file ||
            err?.response?.data?.photo_type ||
            err?.response?.data?.error ||
            err?.response?.data?.detail ||
            defaultMessage
        );
    };

    const openInput = (input) => {
        if (!input) {
            return;
        }

        input.value = "";
        input.click();
    };

    const handleMainPhotoUpload = async (event, slot) => {
        const file = event.target.files?.[0];

        if (!file) {
            event.target.value = "";
            return;
        }

        try {
            setError("");
            setUploadingType(slot.type);

            const uploadedPhoto = await uploadProtocolPhoto(
                protocolId,
                file,
                slot.type,
                slot.sortOrder
            );

            const nextPhotos = sortPhotos([
                ...photos.filter((photo) => photo.photo_type !== slot.type),
                uploadedPhoto,
            ]);

            setPhotos(nextPhotos);
        } catch (err) {
            setError(getUploadErrorText(err, "Не удалось загрузить фото"));
        } finally {
            setUploadingType(null);
            event.target.value = "";
        }
    };

    const handleAdditionalPhotosUpload = async (event) => {
        const files = Array.from(event.target.files || []);

        if (!files.length) {
            event.target.value = "";
            return;
        }

        try {
            setError("");
            setUploadingType("other");

            const uploadedPhotos = [];

            for (const file of files) {
                const uploadedPhoto = await uploadProtocolPhoto(
                    protocolId,
                    file,
                    "other",
                    10
                );

                uploadedPhotos.push(uploadedPhoto);
            }

            setPhotos(sortPhotos([...photos, ...uploadedPhotos]));
        } catch (err) {
            setError(getUploadErrorText(err, "Не удалось загрузить дополнительные фото"));
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

            setPhotos(photos.filter((photo) => photo.id !== photoId));
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

    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                3. Фото автомобиля
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 0 }}>
                    {error}
                </Alert>
            )}

            <Typography variant="h6" sx={subsectionTitleSx}>
                Фото для протокола
            </Typography>

            <Grid container spacing={2} sx={{ mb: 4 }}>
                {DOCX_PHOTO_SLOTS.map((slot) => {
                    const photo = photosByType[slot.type];
                    const isUploading = uploadingType === slot.type;
                    const isDeleting = photo && deletingId === photo.id;

                    return (
                        <Grid item xs={12} md={4} key={slot.type}>
                            <Card variant="outlined">
                                {photo?.file_url ? (
                                    <CardMedia
                                        component="img"
                                        image={photo.file_url}
                                        alt={slot.label}
                                        sx={{
                                            height: 220,
                                            width: "100%",
                                            objectFit: "contain",
                                            backgroundColor: "#ffffff",
                                            borderBottom: "1px solid #e0e0e0",
                                        }}
                                    />
                                ) : (
                                    <Box
                                        sx={{
                                            height: 220,
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            bgcolor: "#f5f5f5",
                                            color: "text.secondary",
                                            borderBottom: "1px solid #e0e0e0",
                                        }}
                                    >
                                        Фото не загружено
                                    </Box>
                                )}

                                <CardContent>
                                    <Typography variant="subtitle1">
                                        {slot.label}
                                    </Typography>

                                    {photo?.file_path && (
                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                            sx={{ mt: 1, wordBreak: "break-all" }}
                                        >
                                            {photo.file_path}
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
                                            mainFileInputRefs.current[slot.type] = element;
                                        }}
                                        style={invisibleInputSx}
                                        type="file"
                                        accept={imageAccept}
                                        onChange={(event) =>
                                            handleMainPhotoUpload(event, slot)
                                        }
                                    />

                                    <input
                                        ref={(element) => {
                                            mainCameraInputRefs.current[slot.type] = element;
                                        }}
                                        style={invisibleInputSx}
                                        type="file"
                                        accept={imageAccept}
                                        capture="environment"
                                        onChange={(event) =>
                                            handleMainPhotoUpload(event, slot)
                                        }
                                    />

                                    <Button
                                        variant="contained"
                                        size="small"
                                        disabled={isUploading}
                                        onClick={() =>
                                            openInput(mainFileInputRefs.current[slot.type])
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
                                            openInput(mainCameraInputRefs.current[slot.type])
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

            <Typography variant="h6" sx={subsectionTitleSx}>
                Дополнительные фото
            </Typography>

            <Box
                sx={{
                    mb: 2,
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 1,
                }}
            >
                <input
                    ref={additionalFileInputRef}
                    style={invisibleInputSx}
                    multiple
                    type="file"
                    accept={imageAccept}
                    onChange={handleAdditionalPhotosUpload}
                />

                <input
                    ref={additionalCameraInputRef}
                    style={invisibleInputSx}
                    type="file"
                    accept={imageAccept}
                    capture="environment"
                    onChange={handleAdditionalPhotosUpload}
                />

                <Button
                    variant="contained"
                    disabled={uploadingType === "other"}
                    onClick={() => openInput(additionalFileInputRef.current)}
                >
                    {uploadingType === "other" ? (
                        <>
                            <CircularProgress size={16} sx={{ mr: 1 }} />
                            Загрузка
                        </>
                    ) : (
                        "Добавить дополнительные фото"
                    )}
                </Button>

                <Button
                    variant="outlined"
                    disabled={uploadingType === "other"}
                    onClick={() => openInput(additionalCameraInputRef.current)}
                >
                    Сделать дополнительное фото
                </Button>
            </Box>

            {additionalPhotos.length === 0 ? (
                <Alert severity="info" sx={{ borderRadius: 0 }}>
                    Дополнительные фото не загружены.
                </Alert>
            ) : (
                <Grid container spacing={2}>
                    {additionalPhotos.map((photo) => {
                        const isDeleting = deletingId === photo.id;

                        return (
                            <Grid item xs={12} sm={6} md={3} key={photo.id}>
                                <Card variant="outlined">
                                    <CardMedia
                                        component="img"
                                        image={photo.file_url}
                                        alt={photo.caption || "Дополнительное фото"}
                                        sx={{
                                            height: 160,
                                            width: "100%",
                                            objectFit: "contain",
                                            backgroundColor: "#ffffff",
                                            borderBottom: "1px solid #e0e0e0",
                                        }}
                                    />

                                    <CardContent>
                                        <Typography variant="body2">
                                            {photo.caption || "Дополнительное фото"}
                                        </Typography>
                                    </CardContent>

                                    <CardActions>
                                        <Button
                                            variant="outlined"
                                            color="error"
                                            size="small"
                                            disabled={isDeleting}
                                            onClick={() => handleDeletePhoto(photo.id)}
                                        >
                                            {isDeleting ? "Удаление..." : "Удалить"}
                                        </Button>
                                    </CardActions>
                                </Card>
                            </Grid>
                        );
                    })}
                </Grid>
            )}
        </Paper>
    );
}

export default ProtocolInspectionPhotos;