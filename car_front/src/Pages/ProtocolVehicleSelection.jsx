import {useEffect, useMemo, useRef, useState} from "react";
import {useNavigate, useParams} from "react-router-dom";
import dayjs from "dayjs";
import "dayjs/locale/ru";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {AdapterDayjs} from "@mui/x-date-pickers/AdapterDayjs";
import {DatePicker} from "@mui/x-date-pickers/DatePicker";
import {LocalizationProvider} from "@mui/x-date-pickers/LocalizationProvider";

const pageSx = {
    minHeight: "calc(100vh - 56px)",
    bgcolor: "#f2f2f2",
    px: 3,
    py: 3,
};

const pageInnerSx = {
    minHeight: "calc(100vh - 112px)",
    border: "2px solid black",
    borderRadius: 0,
    p: 3,
    bgcolor: "#f2f2f2",
    boxShadow: "none",
};

const cardSx = {
    border: "2px solid black",
    borderRadius: 0,
    bgcolor: "white",
    boxShadow: "none",
};

const buttonSx = {
    bgcolor: "black",
    color: "white",
    borderRadius: 0,
    textTransform: "none",
    fontWeight: 800,
    px: 2.5,
    py: 1,
    boxShadow: "none",
    "&:hover": {
        bgcolor: "#222",
        boxShadow: "none",
    },
};

const configurationChipSx = {
    borderRadius: 0,
    bgcolor: "#eeeeee",
    color: "black",
    fontWeight: 500,
};

function getGenerationImageUrl(generation) {
    if (generation?.image_url) {
        return generation.image_url;
    }

    if (generation?.image_path?.startsWith("http")) {
        return generation.image_path;
    }

    return "";
}

function getRegionLabel(region) {
    const labels = {
        japan: "Япония",
        korea: "Корея",
        "south-korea": "Южная Корея",
        china: "Китай",
        europe: "Европа",
        usa: "США",
        russia: "Россия",
    };

    return labels[region] || region || "Регион не указан";
}

function getGenerationTitle(generation) {
    const generationNumber = generation.generation_num
        ? `${generation.generation_num} поколение`
        : "Поколение не указано";
    const restyling = generation.restyling_num
        ? `, рестайлинг ${generation.restyling_num}`
        : "";

    return `${generationNumber}${restyling}`;
}

function groupGenerationsByRegion(generations) {
    return generations.reduce((groups, generation) => {
        const region = generation.region || "unknown";
        groups[region] = groups[region] || [];
        groups[region].push(generation);
        return groups;
    }, {});
}

function getPowerLabel(powerKw) {
    const numericPower = Number(powerKw);

    if (!Number.isFinite(numericPower)) {
        return String(powerKw);
    }

    return `${numericPower} кВт / ${Math.round(numericPower * 1.35962)} л.с.`;
}

function getDriveLabel(driveType) {
    const labels = {
        front: "Передний",
        rear: "Задний",
        full: "Полный",
        "4x2_front": "4x2, передний",
        "4x2_rear": "4x2, задний",
        "4x4": "4x4, полный",
    };

    return labels[driveType] || driveType;
}

function getTransmissionLabel(transmission) {
    const labels = {
        automatic: "Автоматическая",
        manual: "Механическая",
        variator: "Вариатор",
        robot: "Роботизированная",
        reductor: "Редуктор",
    };

    return labels[transmission] || transmission;
}

function getSeatsLabel(seats) {
    return seats ? `${seats} мест` : seats;
}

function getFilterOptionLabel(field, option) {
    if (field === "fuel_type") return getFuelLabel(option);
    if (field === "drive_type") return getDriveLabel(option);
    if (field === "transmission") return getTransmissionLabel(option);
    if (field === "seats_count") return getSeatsLabel(option);
    if (field === "engine_power") return getPowerLabel(option);

    return option;
}

function getFuelLabel(fuelType) {
    const labels = {
        petrol: "Бензин",
        diesel: "Дизель",
        hybrid: "Гибрид",
        electric: "Электро",
    };

    return labels[fuelType] || fuelType;
}

function ProtocolVehicleSelection() {
    const {id} = useParams();
    const navigate = useNavigate();

    const [protocol, setProtocol] = useState(null);
    const [generations, setGenerations] = useState([]);
    const [configurations, setConfigurations] = useState([]);
    const [selectedGeneration, setSelectedGeneration] = useState(null);
    const [selectedConfiguration, setSelectedConfiguration] = useState(null);
    const [manufactureMonth, setManufactureMonth] = useState("");
    const [filterOptions, setFilterOptions] = useState({
        drive_types: [],
        fuel_types: [],
        engine_models: [],
        transmissions: [],
        seats_counts: [],
        engine_powers_kw: [],
        body_marks: [],
        front_tires: [],
        rear_tires: [],
    });
    const [filters, setFilters] = useState({
        drive_type: "",
        fuel_type: "",
        engine_model: "",
        transmission: "",
        seats_count: "",
        engine_power: "",
        body_code: "",
        front_tires: "",
        rear_tires: "",
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const configurationSectionRef = useRef(null);
    const restoredFiltersRef = useRef(false);
    const shouldScrollToConfigurationRef = useRef(false);

    useEffect(() => {
        async function loadProtocol() {
            try {
                setLoading(true);
                const response = await api.get(`/cars/protocols/${id}/full/`);
                let data = response.data;

                if (!["approved", "cancelled"].includes(data.status)) {
                    await api.post(`/cars/protocols/${id}/start-editing/`);
                    const refreshed = await api.get(`/cars/protocols/${id}/full/`);
                    data = refreshed.data;
                }

                setProtocol(data);
                setManufactureMonth(data.manufacture_date ? data.manufacture_date.slice(0, 7) : "");
                setSelectedGeneration(data.generation || null);
                setSelectedConfiguration(data.configuration || null);
            } catch (requestError) {
                console.error("Ошибка загрузки выбора автомобиля:", requestError);
                setError(
                    requestError.response?.data?.detail ||
                    "Не удалось открыть выбор автомобиля"
                );
            } finally {
                setLoading(false);
            }
        }

        if (id) {
            loadProtocol();
        }
    }, [id]);

    useEffect(() => {
        if (!protocol?.model || ["approved", "cancelled"].includes(protocol.status)) {
            return;
        }

        async function loadGenerations() {
            try {
                const response = await api.get("/cars/generations/", {
                    params: {
                        model_id: protocol.model,
                        manufacture_date: manufactureMonth || undefined,
                        page_size: 100,
                    },
                });
                const loadedGenerations = response.data.results || [];
                setGenerations(loadedGenerations);

                if (protocol.generation && typeof protocol.generation !== "object") {
                    setSelectedGeneration(
                        loadedGenerations.find(
                            (generation) => generation.id === protocol.generation
                        ) || null
                    );
                }
            } catch (requestError) {
                console.error("Ошибка загрузки поколений:", requestError);
                setError("Не удалось загрузить поколения автомобиля");
            }
        }

        loadGenerations();
    }, [protocol, manufactureMonth]);

    useEffect(() => {
        if (!selectedGeneration?.id) {
            setConfigurations([]);
            return;
        }

        async function loadConfigurations() {
            try {
                const response = await api.get("/cars/configurations-filtered/", {
                    params: {
                        generation_id: selectedGeneration.id,
                        manufacture_date: manufactureMonth || undefined,
                        page_size: 100,
                        ...Object.fromEntries(
                            Object.entries(filters).filter(([, value]) => value)
                        ),
                    },
                });
                const loadedConfigurations = response.data.results || [];
                setConfigurations(loadedConfigurations);

                if (
                    protocol?.configuration &&
                    !restoredFiltersRef.current
                ) {
                    const selectedConfigurationId = typeof protocol.configuration === "object"
                        ? protocol.configuration.id
                        : protocol.configuration;
                    const savedConfiguration = loadedConfigurations.find(
                        (configuration) => configuration.id === selectedConfigurationId
                    );

                    if (savedConfiguration) {
                        setSelectedConfiguration(savedConfiguration);
                        setFilters({
                            drive_type: savedConfiguration.drive_type || "",
                            fuel_type: savedConfiguration.fuel_type || "",
                            engine_model: savedConfiguration.engine_model || "",
                            transmission: savedConfiguration.transmission || "",
                            seats_count: savedConfiguration.seats_count || "",
                            engine_power: savedConfiguration.engine_power_kw
                                ? String(savedConfiguration.engine_power_kw)
                                : "",
                            body_code: savedConfiguration.body_mark || "",
                            front_tires: savedConfiguration.front_tires || "",
                            rear_tires: savedConfiguration.rear_tires || "",
                        });
                        restoredFiltersRef.current = true;
                    }
                }
            } catch (requestError) {
                console.error("Ошибка загрузки конфигураций:", requestError);
                setError("Не удалось загрузить конфигурации");
            }
        }

        loadConfigurations();
    }, [selectedGeneration, manufactureMonth, filters, protocol]);

    useEffect(() => {
        if (!selectedGeneration?.id) {
            return;
        }

        async function loadFilterOptions() {
            try {
                const response = await api.get("/cars/configuration-filter-options/", {
                    params: {
                        generation_id: selectedGeneration.id,
                        manufacture_date: manufactureMonth || undefined,
                        ...Object.fromEntries(
                            Object.entries(filters).filter(([, value]) => value)
                        ),
                    },
                });
                setFilterOptions((previous) => ({...previous, ...(response.data || {})}));
            } catch (requestError) {
                console.error("Ошибка загрузки фильтров конфигураций:", requestError);
            }
        }

        loadFilterOptions();
    }, [selectedGeneration, manufactureMonth, filters]);

    useEffect(() => {
        if (
            !shouldScrollToConfigurationRef.current ||
            !selectedGeneration?.id ||
            !configurations.length
        ) {
            return;
        }

        shouldScrollToConfigurationRef.current = false;

        const scrollTimer = setTimeout(() => {
            requestAnimationFrame(() => {
                configurationSectionRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            });
        }, 250);

        return () => clearTimeout(scrollTimer);
    }, [selectedGeneration, configurations.length]);

    const groupedGenerations = useMemo(
        () => groupGenerationsByRegion(generations),
        [generations]
    );

    const handleGenerationSelect = (generation) => {
        shouldScrollToConfigurationRef.current = true;
        setSelectedGeneration(generation);
        setSelectedConfiguration(null);
        setFilters({
            drive_type: "",
            fuel_type: "",
            engine_model: "",
            transmission: "",
            seats_count: "",
            engine_power: "",
            body_code: "",
            front_tires: "",
            rear_tires: "",
        });
    };

    const handleConfirm = async () => {
        if (!manufactureMonth || !selectedGeneration || !selectedConfiguration) {
            setError("Укажите месяц выпуска, поколение и конфигурацию");
            return;
        }

        try {
            setSaving(true);
            setError("");
            await api.post(`/cars/protocols/${id}/select-configuration/`, {
                generation_id: selectedGeneration.id,
                configuration_id: selectedConfiguration.id,
                manufacture_date: manufactureMonth,
            });
            navigate(`/protocols/${id}/inspection`, {
                state: {openDataReview: true},
            });
        } catch (requestError) {
            console.error("Ошибка сохранения выбора автомобиля:", requestError);
            setError(
                requestError.response?.data?.detail ||
                "Не удалось сохранить выбор автомобиля"
            );
        } finally {
            setSaving(false);
        }
    };

    const releaseLockBeforeLeaving = async () => {
        if (!id || ["approved", "cancelled"].includes(protocol?.status)) {
            return;
        }

        try {
            await api.post(`/cars/protocols/${id}/return-to-draft/`);
        } catch (requestError) {
            console.error("Ошибка освобождения протокола:", requestError);
        }
    };

    const handleBackToProtocol = async () => {
        await releaseLockBeforeLeaving();
        navigate(`/protocols/${id}/inspection`);
    };

    if (loading) {
        return (
            <>
                <AppHeader />
                <Box sx={pageSx}>
                    <Paper sx={pageInnerSx}>
                        <CircularProgress sx={{color: "black"}} />
                    </Paper>
                </Box>
            </>
        );
    }

    return (
        <>
            <AppHeader beforeNavigate={releaseLockBeforeLeaving} />
            <Box sx={pageSx}>
                <Box sx={pageInnerSx}>
                    <Box
                        sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "flex-start",
                            gap: 2,
                            flexWrap: "wrap",
                            mb: 3,
                        }}
                    >
                        <Box>
                            <Typography variant="h4" sx={{fontWeight: 800, color: "black"}}>
                                Выбор автомобиля
                            </Typography>
                            <Typography variant="body1" sx={{color: "text.secondary", mt: 0.5}}>
                                Выберите поколение по фотографии, региону и характеристикам, затем конфигурацию.
                            </Typography>
                        </Box>
                        <Button
                            variant="outlined"
                            onClick={handleBackToProtocol}
                            sx={{...buttonSx, bgcolor: "white", color: "black", border: "1px solid black"}}
                        >
                            Вернуться к протоколу
                        </Button>
                    </Box>

                    {error && <Alert severity="error" sx={{mb: 2, borderRadius: 0}}>{error}</Alert>}

                    <Paper
                        sx={{
                            ...cardSx,
                            p: {xs: 1.5, md: 2},
                            mb: 2,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: 2,
                            flexWrap: "wrap",
                        }}
                    >
                        <Box sx={{minWidth: 0, flex: "1 1 420px"}}>
                            <Typography variant="h6" sx={{fontWeight: 800, lineHeight: 1.2}}>
                                Дата выпуска автомобиля
                            </Typography>
                            <Typography variant="body2" sx={{color: "text.secondary", mt: 0.5}}>
                                Месяц из документов. По нему отфильтруются поколения и конфигурации.
                            </Typography>
                        </Box>
                        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ru">
                            <DatePicker
                                label="Месяц и год"
                                views={["year", "month"]}
                                openTo="month"
                                format="MMMM YYYY"
                                value={manufactureMonth ? dayjs(`${manufactureMonth}-01`) : null}
                                onChange={(value) => {
                                    const nextManufactureMonth = value?.isValid()
                                        ? value.format("YYYY-MM")
                                        : "";

                                    setManufactureMonth(nextManufactureMonth);
                                    setSelectedGeneration(null);
                                    setSelectedConfiguration(null);
                                    setFilters((previous) => ({...previous}));
                                    setError("");
                                }}
                                slotProps={{
                                    textField: {
                                        size: "small",
                                        sx: {bgcolor: "white", width: {xs: "100%", sm: 220}},
                                    },
                                    popper: {
                                        sx: {
                                            "& .MuiDateCalendar-root": {
                                                height: 270,
                                                minHeight: 0,
                                            },
                                            "& .MuiMonthCalendar-root": {
                                                minHeight: 0,
                                                height: 210,
                                            },
                                        },
                                    },
                                }}
                            />
                        </LocalizationProvider>
                    </Paper>

                    <Box sx={{display: "flex", gap: 1, mb: 2, flexWrap: "wrap"}}>
                        <Chip label={protocol?.brand_name || "Марка"} sx={{borderRadius: 0, bgcolor: "black", color: "white", fontWeight: 800}} />
                        <Chip label={protocol?.commercial_name || "Модель"} sx={{borderRadius: 0, bgcolor: "white", border: "1px solid black", fontWeight: 800}} />
                    </Box>

                    {Object.entries(groupedGenerations).map(([region, regionGenerations]) => (
                        <Box key={region} sx={{mb: 3}}>
                            <Typography variant="h5" sx={{fontWeight: 800, mb: 1.5}}>
                                {getRegionLabel(region)}
                            </Typography>
                            <Box
                                sx={{
                                    display: "grid",
                                    gridTemplateColumns: {xs: "1fr", sm: "repeat(2, minmax(0, 1fr))", lg: "repeat(4, minmax(0, 1fr))"},
                                    gap: 1.5,
                                }}
                            >
                                {regionGenerations.map((generation) => {
                                    const selected = selectedGeneration?.id === generation.id;
                                    const imageUrl = getGenerationImageUrl(generation);

                                    return (
                                        <Paper
                                            key={generation.id}
                                            onClick={() => handleGenerationSelect(generation)}
                                            sx={{
                                                ...cardSx,
                                                cursor: "pointer",
                                                overflow: "hidden",
                                                border: selected ? "3px solid black" : "1px solid black",
                                                "&:hover": {boxShadow: "4px 4px 0 black"},
                                            }}
                                        >
                                            {imageUrl ? (
                                                <Box component="img" src={imageUrl} alt={generation.name} sx={{width: "100%", height: 150, objectFit: "contain", bgcolor: "#f2f2f2", borderBottom: "1px solid black"}} />
                                            ) : (
                                                <Box sx={{height: 150, display: "flex", alignItems: "center", justifyContent: "center", bgcolor: "#f2f2f2", color: "text.secondary"}}>
                                                    Фото отсутствует
                                                </Box>
                                            )}
                                            <Box sx={{p: 1.5}}>
                                                <Typography sx={{fontWeight: 800}}>{generation.name}</Typography>
                                                <Typography variant="body2" sx={{mt: 0.5}}>{getGenerationTitle(generation)}</Typography>
                                                <Typography variant="body2" sx={{color: "text.secondary", mt: 0.5}}>
                                                    {generation.date_start || "?"} - {generation.date_end || "?"}
                                                </Typography>
                                                {generation.body_code && (
                                                    <Typography variant="body2" sx={{color: "text.secondary", mt: 0.5}}>
                                                        Код кузова: {generation.body_code}
                                                    </Typography>
                                                )}
                                            </Box>
                                        </Paper>
                                    );
                                })}
                            </Box>
                        </Box>
                    ))}

                    {selectedGeneration && (
                        <Paper ref={configurationSectionRef} sx={{...cardSx, p: 2.5, mb: 10, scrollMarginTop: 76}}>
                            <Box
                                sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    gap: 2,
                                    flexWrap: "wrap",
                                    mb: 1,
                                }}
                            >
                                <Typography variant="h5" sx={{fontWeight: 800}}>
                                    Конфигурация
                                </Typography>
                                <Button
                                    variant="outlined"
                                    onClick={() => {
                                        setFilters({
                                            drive_type: "",
                                            fuel_type: "",
                                            engine_model: "",
                                            transmission: "",
                                            seats_count: "",
                                            engine_power: "",
                                            body_code: "",
                                            front_tires: "",
                                            rear_tires: "",
                                        });
                                        setSelectedConfiguration(null);
                                        setError("");
                                    }}
                                    sx={{
                                        borderColor: "black",
                                        color: "black",
                                        borderRadius: 0,
                                        textTransform: "none",
                                        fontWeight: 700,
                                        "&:hover": {
                                            borderColor: "black",
                                            bgcolor: "#eeeeee",
                                        },
                                    }}
                                >
                                    Сбросить фильтры
                                </Button>
                            </Box>
                            <Typography variant="body2" sx={{color: "text.secondary", mb: 1.5}}>
                                {manufactureMonth
                                    ? `Подходящие конфигурации для ${manufactureMonth}. Данные парсера пока не подставляются.`
                                    : "Дата не указана: показаны все конфигурации выбранного поколения."}
                            </Typography>
                            <Box
                                sx={{
                                    display: "grid",
                                    gridTemplateColumns: {xs: "1fr", sm: "repeat(2, minmax(0, 1fr))", lg: "repeat(4, minmax(0, 1fr))"},
                                    gap: 1.5,
                                    mb: 2,
                                }}
                            >
                                {[
                                    ["fuel_type", "Топливо", filterOptions.fuel_types],
                                    ["engine_model", "Модель двигателя", filterOptions.engine_models],
                                    ["engine_power", "Мощность, кВт / л.с.", filterOptions.engine_powers_kw],
                                    ["seats_count", "Количество мест", filterOptions.seats_counts],
                                    ["body_code", "Код кузова", filterOptions.body_marks],
                                    ["front_tires", "Передние шины", filterOptions.front_tires],
                                    ["rear_tires", "Задние шины", filterOptions.rear_tires],
                                    ["drive_type", "Привод", filterOptions.drive_types],
                                    ["transmission", "Коробка передач", filterOptions.transmissions],
                                ].filter(([field, , options]) =>
                                    (options || []).length > 1 || filters[field]
                                ).map(([field, label, options]) => (
                                    <TextField
                                        key={field}
                                        select
                                        label={label}
                                        value={filters[field]}
                                        onChange={(event) => {
                                            setFilters((previous) => ({
                                                ...previous,
                                                [field]: event.target.value,
                                            }));
                                            setSelectedConfiguration(null);
                                        }}
                                        sx={{bgcolor: "white"}}
                                    >
                                        <MenuItem value="">Все</MenuItem>
                                        {(options || []).map((option) => (
                                            <MenuItem key={option} value={option}>
                                                {getFilterOptionLabel(field, option)}
                                            </MenuItem>
                                        ))}
                                    </TextField>
                                ))}
                            </Box>
                            <Box sx={{display: "grid", gap: 1}}>
                                <Typography variant="body2" sx={{fontWeight: 700, color: "text.secondary", mb: 0.5}}>
                                    Найдено конфигураций: {configurations.length}
                                </Typography>
                                {configurations.map((configuration) => {
                                    const selected = selectedConfiguration?.id === configuration.id;
                                    return (
                                        <Button
                                            key={configuration.id}
                                            variant="outlined"
                                            onClick={() => setSelectedConfiguration(configuration)}
                                            sx={{
                                                justifyContent: "flex-start",
                                                textAlign: "left",
                                                borderRadius: 0,
                                                borderColor: selected ? "black" : "#999",
                                                borderWidth: selected ? 2 : 1,
                                                color: "black",
                                                bgcolor: selected ? "#f2f2f2" : "white",
                                                textTransform: "none",
                                                py: 1.5,
                                                px: 2,
                                                display: "grid",
                                                gridTemplateColumns: {xs: "1fr", md: "minmax(180px, 1.2fr) 2fr"},
                                                alignItems: "center",
                                                gap: 1.5,
                                                "&:hover": {
                                                    borderColor: "black",
                                                    bgcolor: "#f5f5f5",
                                                },
                                            }}
                                        >
                                            <Box>
                                                <Typography sx={{fontWeight: 800, color: "black"}}>
                                                    {configuration.name || `Конфигурация №${configuration.id}`}
                                                </Typography>
                                                <Typography variant="body2" sx={{color: "text.secondary", mt: 0.35}}>
                                                    {configuration.engine_model || configuration.engine_name || "Двигатель не указан"}
                                                </Typography>
                                            </Box>

                                            <Box sx={{display: "flex", gap: 0.7, flexWrap: "wrap"}}>
                                                {configuration.fuel_type && (
                                                    <Chip size="small" label={`Топливо: ${getFuelLabel(configuration.fuel_type)}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.engine_power_kw && (
                                                    <Chip size="small" label={`Мощность: ${getPowerLabel(configuration.engine_power_kw)}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.drive_type && (
                                                    <Chip size="small" label={`Привод: ${getDriveLabel(configuration.drive_type)}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.transmission && (
                                                    <Chip size="small" label={`Коробка: ${getTransmissionLabel(configuration.transmission)}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.seats_count && (
                                                    <Chip size="small" label={`Места: ${getSeatsLabel(configuration.seats_count)}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.body_mark && (
                                                    <Chip size="small" label={`Кузов: ${configuration.body_mark}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.front_tires && (
                                                    <Chip size="small" label={`Передние шины: ${configuration.front_tires}`} sx={configurationChipSx} />
                                                )}
                                                {configuration.rear_tires && (
                                                    <Chip size="small" label={`Задние шины: ${configuration.rear_tires}`} sx={configurationChipSx} />
                                                )}
                                                <Typography variant="body2" sx={{width: "100%", color: "text.secondary", mt: 0.2}}>
                                                    {configuration.date_start || "?"} - {configuration.date_end || "?"}
                                                </Typography>
                                            </Box>
                                        </Button>
                                    );
                                })}
                                {manufactureMonth && configurations.length === 0 && (
                                    <Alert severity="info" sx={{borderRadius: 0}}>
                                        Для выбранного месяца конфигурации не найдены.
                                    </Alert>
                                )}
                            </Box>
                        </Paper>
                    )}

                    <Paper sx={{position: "fixed", bottom: 0, left: 0, right: 0, p: 1.5, borderTop: "2px solid black", borderRadius: 0, bgcolor: "white", zIndex: 20}}>
                        <Box sx={{display: "flex", justifyContent: "flex-end", gap: 1.5, maxWidth: 1400, mx: "auto"}}>
                            <Button
                                variant="contained"
                                onClick={handleConfirm}
                                disabled={saving || !selectedGeneration || !selectedConfiguration}
                                sx={buttonSx}
                            >
                                {saving
                                    ? "Сохранение..."
                                    : selectedConfiguration
                                        ? `Подтвердить: ${selectedConfiguration.name || `конфигурация №${selectedConfiguration.id}`}`
                                        : "Выберите конфигурацию"}
                            </Button>
                        </Box>
                    </Paper>
                </Box>
            </Box>
        </>
    );
}

export default ProtocolVehicleSelection;
