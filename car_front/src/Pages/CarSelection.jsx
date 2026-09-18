import {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";

import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Chip from "@mui/material/Chip";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Divider from "@mui/material/Divider";

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
    p: 2.5,
    bgcolor: "white",
    boxShadow: "none",
};

const smallCardSx = {
    border: "1px solid black",
    borderRadius: 0,
    bgcolor: "white",
    boxShadow: "none",
};

const textFieldSx = {
    bgcolor: "white",
    "& .MuiOutlinedInput-root": {
        borderRadius: 0,
    },
};

const blackButtonSx = {
    bgcolor: "black",
    color: "white",
    borderRadius: 0,
    textTransform: "none",
    px: 3,
    py: 1,
    fontWeight: 800,
    boxShadow: "none",
    border: "1px solid black",
    "&:hover": {
        bgcolor: "#222",
        boxShadow: "none",
    },
    "&.Mui-disabled": {
        bgcolor: "#cccccc",
        color: "#666666",
        border: "1px solid #999999",
    },
};

const outlineButtonSx = {
    borderColor: "black",
    color: "black",
    borderRadius: 0,
    textTransform: "none",
    fontWeight: 800,
    "&:hover": {
        borderColor: "black",
        bgcolor: "#eeeeee",
    },
};

function getGenerationImageUrl(generation) {
    if (!generation) return "";

    if (generation.image_url) {
        return generation.image_url;
    }

    const imagePath = generation.image_path;

    if (!imagePath) return "";

    if (imagePath.startsWith("http")) {
        return imagePath;
    }

    return "";
}

function getRegionLabel(region) {
    const labels = {
        japan: "Япония",
        china: "Китай",
        "south-korea": "Южная Корея",
        korea: "Корея",
        europe: "Европа",
        usa: "США",
        russia: "Россия",
    };

    return labels[region] || region || "Регион не указан";
}

function getGenerationTitle(generation) {
    const generationText = generation.generation_num
        ? `${generation.generation_num} поколение`
        : "Поколение";

    const restylingText = generation.restyling_num
        ? `, рестайлинг ${generation.restyling_num}`
        : "";

    return `${generationText}${restylingText}`;
}

function groupGenerationsByRegion(generations) {
    return generations.reduce((groups, generation) => {
        const region = generation.region || "unknown";

        if (!groups[region]) {
            groups[region] = [];
        }

        groups[region].push(generation);
        return groups;
    }, {});
}

function buildCreateProtocolPayload({
                                        selectedBrand,
                                        selectedModel,
                                        selectedGeneration,
                                        selectedConfiguration,
                                        configurationFilters,
                                    }) {
    const payload = {
        owner_name: "Не указано",
        model: selectedModel?.id || null,
        brand_name: selectedBrand?.name || "",
        commercial_name: selectedModel?.name || "",
        body_type:
            selectedConfiguration?.body_mark ||
            configurationFilters?.body_code ||
            selectedGeneration?.body_type ||
            "",
    };

    if (selectedConfiguration?.id) {
        payload.configuration_id = selectedConfiguration.id;
    }

    return payload;
}

function buildConfigurationLabel(option) {
    if (!option) return "";

    const parts = [];

    if (option.name) {
        parts.push(option.name);
    }

    if (option.body_mark) {
        parts.push(`кузов: ${option.body_mark}`);
    }

    if (option.engine_name) {
        parts.push(`двигатель: ${option.engine_name}`);
    }

    if (option.engine_model) {
        parts.push(`модель ДВС: ${option.engine_model}`);
    }

    if (option.engine_power_kw) {
        parts.push(`${option.engine_power_kw} кВт`);
    }

    if (option.fuel_type) {
        parts.push(option.fuel_type);
    }

    if (option.transmission) {
        parts.push(option.transmission);
    }

    if (option.drive_type) {
        parts.push(option.drive_type);
    }

    if (option.seats_count) {
        parts.push(`${option.seats_count} мест`);
    }

    const period =
        option.date_start || option.date_end
            ? ` (${option.date_start || "?"} - ${option.date_end || "?"})`
            : "";

    return `${parts.join(" · ")}${period}`;
}

function CarSelection() {
    const navigate = useNavigate();
    const showGenerationSelection = Boolean(import.meta.env.VITE_SHOW_GENERATION_SELECTION);

    const emptyConfigurationFilterOptions = {
        drive_types: [],
        fuel_types: [],
        engine_models: [],
        transmissions: [],
        seats_counts: [],
        engine_powers_kw: [],
        body_marks: [],
        turbo_values: [],
    };

    const emptyConfigurationFilters = {
        drive_type: "",
        fuel_type: "",
        engine_model: "",
        transmission: "",
        seats_count: "",
        manufacture_year: "",
        body_code: "",
        engine_power: "",
        turbo_present: "",
    };

    const [brands, setBrands] = useState([]);
    const [selectedBrand, setSelectedBrand] = useState(null);

    const [models, setModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState(null);

    const [generations, setGenerations] = useState([]);
    const [selectedGeneration, setSelectedGeneration] = useState(null);

    const [configurations, setConfigurations] = useState([]);
    const [selectedConfiguration, setSelectedConfiguration] = useState(null);

    const [creatingProtocol, setCreatingProtocol] = useState(false);
    const [createProtocolError, setCreateProtocolError] = useState("");

    const [configurationFilterOptions, setConfigurationFilterOptions] = useState(
        emptyConfigurationFilterOptions
    );
    const [configurationFilters, setConfigurationFilters] = useState(
        emptyConfigurationFilters
    );

    const [brandInputValue, setBrandInputValue] = useState("");
    const [modelInputValue, setModelInputValue] = useState("");
    const [configurationInputValue, setConfigurationInputValue] = useState("");

    const [brandLoading, setBrandLoading] = useState(false);
    const [modelLoading, setModelLoading] = useState(false);
    const [generationLoading, setGenerationLoading] = useState(false);
    const [configurationLoading, setConfigurationLoading] = useState(false);
    const [configurationFilterLoading, setConfigurationFilterLoading] = useState(false);

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            async function fetchBrands() {
                try {
                    setBrandLoading(true);

                    const params = brandInputValue
                        ? {name: brandInputValue, page_size: 50}
                        : {page_size: 50};

                    const response = await api.get("/cars/brands/", {params});
                    setBrands(response.data.results || []);
                } catch (error) {
                    console.error(error);
                    setBrands([]);
                } finally {
                    setBrandLoading(false);
                }
            }

            fetchBrands();
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [brandInputValue]);

    useEffect(() => {
        if (!selectedBrand) {
            setModels([]);
            return;
        }

        const delayDebounceFn = setTimeout(() => {
            async function fetchModels() {
                try {
                    setModelLoading(true);

                    const params = modelInputValue
                        ? {
                            brand_id: selectedBrand.id,
                            name: modelInputValue,
                            page_size: 50,
                        }
                        : {
                            brand_id: selectedBrand.id,
                            page_size: 50,
                        };

                    const response = await api.get("/cars/models/", {params});
                    setModels(response.data.results || []);
                } catch (error) {
                    console.error(error);
                    setModels([]);
                } finally {
                    setModelLoading(false);
                }
            }

            fetchModels();
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [selectedBrand, modelInputValue]);

    useEffect(() => {
        if (!showGenerationSelection || !selectedModel) {
            setGenerations([]);
            return;
        }

        async function fetchGenerations() {
            try {
                setGenerationLoading(true);

                const response = await api.get("/cars/generations/", {
                    params: {
                        model_id: selectedModel.id,
                        page_size: 100,
                    },
                });

                setGenerations(response.data.results || []);
            } catch (error) {
                console.error(error);
                setGenerations([]);
            } finally {
                setGenerationLoading(false);
            }
        }

        fetchGenerations();
    }, [selectedModel, showGenerationSelection]);

    useEffect(() => {
        if (!selectedGeneration) {
            setConfigurationFilterOptions(emptyConfigurationFilterOptions);
            return;
        }

        async function fetchConfigurationFilterOptions() {
            try {
                setConfigurationFilterLoading(true);

                const response = await api.get("/cars/configuration-filter-options/", {
                    params: {
                        generation_id: selectedGeneration.id,
                    },
                });

                setConfigurationFilterOptions({
                    ...emptyConfigurationFilterOptions,
                    ...(response.data || {}),
                });
            } catch (error) {
                console.error(error);
                setConfigurationFilterOptions(emptyConfigurationFilterOptions);
            } finally {
                setConfigurationFilterLoading(false);
            }
        }

        fetchConfigurationFilterOptions();
    }, [selectedGeneration]);

    useEffect(() => {
        if (!selectedGeneration) {
            setConfigurations([]);
            return;
        }

        const delayDebounceFn = setTimeout(() => {
            async function fetchConfigurations() {
                try {
                    setConfigurationLoading(true);

                    const params = {
                        generation_id: selectedGeneration.id,
                        page_size: 100,
                    };

                    if (configurationInputValue) {
                        params.name = configurationInputValue;
                    }

                    Object.entries(configurationFilters).forEach(([key, value]) => {
                        if (value !== "" && value !== null && value !== undefined) {
                            params[key] = value;
                        }
                    });

                    const response = await api.get("/cars/configurations-filtered/", {
                        params,
                    });

                    setConfigurations(response.data.results || []);
                } catch (error) {
                    console.error(error);
                    setConfigurations([]);
                } finally {
                    setConfigurationLoading(false);
                }
            }

            fetchConfigurations();
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [selectedGeneration, configurationInputValue, configurationFilters]);

    const resetConfigurationFilters = () => {
        setConfigurationFilters(emptyConfigurationFilters);
        setSelectedConfiguration(null);
        setConfigurationInputValue("");
    };

    const handleConfigurationFilterChange = (field, value) => {
        setConfigurationFilters((prev) => ({
            ...prev,
            [field]: value,
        }));

        setSelectedConfiguration(null);
    };

    const handleSelectGeneration = (generation) => {
        setSelectedGeneration(generation);
        setSelectedConfiguration(null);
        setConfigurationInputValue("");
        setConfigurationFilters(emptyConfigurationFilters);
        setConfigurations([]);
    };

    const handleNextPage = async () => {
        if (!selectedBrand || !selectedModel) return;

        try {
            setCreatingProtocol(true);
            setCreateProtocolError("");

            const payload = buildCreateProtocolPayload({
                selectedBrand,
                selectedModel,
                selectedGeneration,
                selectedConfiguration,
                configurationFilters,
            });

            const response = await api.post("/cars/protocols/create/", payload);
            const createdProtocol = response.data;

            navigate(`/protocols/${createdProtocol.id}/measurement`);
        } catch (error) {
            console.error(error);

            const backendError =
                error.response?.data?.configuration_id?.[0] ||
                error.response?.data?.configuration_id ||
                error.response?.data?.commercial_name?.[0] ||
                error.response?.data?.brand_name?.[0] ||
                error.response?.data?.error ||
                error.response?.data?.detail;

            setCreateProtocolError(backendError || "Не удалось создать протокол");
        } finally {
            setCreatingProtocol(false);
        }
    };

    const groupedGenerations = groupGenerationsByRegion(generations);
    const bodyCodeOptions = configurationFilterOptions.body_marks || [];

    return (
        <>
            <AppHeader/>

            <Box sx={pageSx}>
                <Paper sx={pageInnerSx}>
                    <Box sx={{mb: 3}}>
                        <Typography
                            variant="h4"
                            sx={{
                                fontWeight: 800,
                                color: "black",
                                mb: 0.5,
                            }}
                        >
                            Новая машина
                        </Typography>

                        <Typography variant="body1" sx={{color: "text.secondary"}}>
                            Выберите марку и модель, чтобы начать первичный замер.
                        </Typography>
                    </Box>

                    <Paper sx={{...cardSx, mb: 2.5}}>
                        <Typography
                            variant="h5"
                            sx={{
                                fontWeight: 800,
                                mb: 2,
                                color: "black",
                            }}
                        >
                            1. Автомобиль
                        </Typography>

                        <Box
                            sx={{
                                display: "grid",
                                gridTemplateColumns: {
                                    xs: "1fr",
                                    md: "repeat(2, minmax(0, 360px))",
                                },
                                gap: 2,
                            }}
                        >
                            <Autocomplete
                                value={selectedBrand}
                                inputValue={brandInputValue}
                                disablePortal
                                options={brands}
                                getOptionLabel={(option) => option?.name || ""}
                                isOptionEqualToValue={(option, value) =>
                                    option.id === value.id
                                }
                                filterOptions={(options) => options}
                                loading={brandLoading}
                                onInputChange={(event, newInputValue) =>
                                    setBrandInputValue(newInputValue)
                                }
                                onChange={(event, newValue) => {
                                    setSelectedBrand(newValue);
                                    setSelectedModel(null);
                                    setSelectedGeneration(null);
                                    setSelectedConfiguration(null);
                                    setModels([]);
                                    setGenerations([]);
                                    setConfigurations([]);
                                    setModelInputValue("");
                                    setConfigurationInputValue("");
                                    setConfigurationFilters(emptyConfigurationFilters);
                                }}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Выберите бренд"
                                        sx={textFieldSx}
                                    />
                                )}
                            />

                            <Autocomplete
                                value={selectedModel}
                                inputValue={modelInputValue}
                                disablePortal
                                options={models}
                                getOptionLabel={(option) => option?.name || ""}
                                isOptionEqualToValue={(option, value) =>
                                    option.id === value.id
                                }
                                filterOptions={(options) => options}
                                loading={modelLoading}
                                disabled={!selectedBrand}
                                onInputChange={(event, newInputValue) =>
                                    setModelInputValue(newInputValue)
                                }
                                onChange={(event, newValue) => {
                                    setSelectedModel(newValue);
                                    setSelectedGeneration(null);
                                    setSelectedConfiguration(null);
                                    setGenerations([]);
                                    setConfigurations([]);
                                    setConfigurationInputValue("");
                                    setConfigurationFilters(emptyConfigurationFilters);
                                }}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Выберите модель"
                                        sx={textFieldSx}
                                    />
                                )}
                            />
                        </Box>
                    </Paper>

                    {showGenerationSelection && selectedModel && (
                        <Paper sx={{...cardSx, mb: 2.5}}>
                            <Box
                                sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    gap: 2,
                                    flexWrap: "wrap",
                                    mb: 2,
                                }}
                            >
                                <Box>
                                    <Typography
                                        variant="h5"
                                        sx={{
                                            fontWeight: 800,
                                            color: "black",
                                        }}
                                    >
                                        2. Поколение
                                    </Typography>

                                    <Typography
                                        variant="body2"
                                        sx={{color: "text.secondary", mt: 0.5}}
                                    >
                                        Выберите подходящее поколение автомобиля.
                                    </Typography>
                                </Box>

                                <Chip
                                    label={`${selectedBrand?.name || ""} ${
                                        selectedModel?.name || ""
                                    }`.trim()}
                                    sx={{
                                        borderRadius: 0,
                                        bgcolor: "black",
                                        color: "white",
                                        fontWeight: 800,
                                    }}
                                />
                            </Box>

                            {generationLoading && (
                                <Box
                                    sx={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 1,
                                    }}
                                >
                                    <CircularProgress size={22} sx={{color: "black"}}/>
                                    <Typography>Загрузка поколений...</Typography>
                                </Box>
                            )}

                            {!generationLoading && generations.length === 0 && (
                                <Alert severity="info" sx={{borderRadius: 0}}>
                                    Нет данных по поколениям. Можно создать протокол по выбранной марке и модели и
                                    заполнить данные вручную.
                                </Alert>
                            )}

                            {!generationLoading &&
                                Object.entries(groupedGenerations).map(
                                    ([region, regionGenerations]) => (
                                        <Box key={region} sx={{mb: 4}}>
                                            <Typography
                                                variant="h6"
                                                sx={{
                                                    mb: 2,
                                                    fontWeight: 800,
                                                    color: "black",
                                                }}
                                            >
                                                Модельный ряд {selectedBrand?.name}{" "}
                                                {selectedModel?.name} для{" "}
                                                {getRegionLabel(region)}
                                            </Typography>

                                            <Box
                                                sx={{
                                                    display: "grid",
                                                    gridTemplateColumns: {
                                                        xs: "1fr",
                                                        sm: "repeat(2, minmax(0, 1fr))",
                                                        md: "repeat(3, minmax(0, 1fr))",
                                                        lg: "repeat(4, minmax(0, 1fr))",
                                                    },
                                                    gap: 1.5,
                                                }}
                                            >
                                                {regionGenerations.map((generation) => {
                                                    const isSelected =
                                                        selectedGeneration?.id === generation.id;

                                                    return (
                                                        <Paper
                                                            key={generation.id}
                                                            onClick={() =>
                                                                handleSelectGeneration(generation)
                                                            }
                                                            sx={{
                                                                ...smallCardSx,
                                                                cursor: "pointer",
                                                                border: isSelected
                                                                    ? "3px solid black"
                                                                    : "1px solid black",
                                                                transition: "0.15s",
                                                                overflow: "hidden",
                                                                "&:hover": {
                                                                    transform: "translateY(-2px)",
                                                                },
                                                            }}
                                                        >
                                                            {generation.image_url || generation.image_path ? (
                                                                <Box
                                                                    component="img"
                                                                    src={getGenerationImageUrl(generation)}
                                                                    alt={generation.name}
                                                                    sx={{
                                                                        width: "100%",
                                                                        height: 145,
                                                                        objectFit: "contain",
                                                                        bgcolor: "#f2f2f2",
                                                                        borderBottom: "1px solid black",
                                                                    }}
                                                                />
                                                            ) : (
                                                                <Box
                                                                    sx={{
                                                                        height: 145,
                                                                        display: "flex",
                                                                        alignItems: "center",
                                                                        justifyContent: "center",
                                                                        bgcolor: "#f2f2f2",
                                                                        color: "text.secondary",
                                                                        borderBottom: "1px solid black",
                                                                    }}
                                                                >
                                                                    Нет изображения
                                                                </Box>
                                                            )}

                                                            <Box sx={{p: 1.5}}>
                                                                <Typography
                                                                    variant="subtitle1"
                                                                    sx={{
                                                                        fontWeight: 800,
                                                                        color: "black",
                                                                        lineHeight: 1.2,
                                                                    }}
                                                                >
                                                                    {generation.name}
                                                                </Typography>

                                                                <Typography
                                                                    variant="body2"
                                                                    sx={{color: "text.secondary", mt: 0.5}}
                                                                >
                                                                    {generation.date_start || "?"} -{" "}
                                                                    {generation.date_end || "?"}
                                                                </Typography>

                                                                <Box
                                                                    sx={{
                                                                        display: "flex",
                                                                        gap: 1,
                                                                        flexWrap: "wrap",
                                                                        mt: 1,
                                                                    }}
                                                                >
                                                                    <Chip
                                                                        size="small"
                                                                        label={getRegionLabel(
                                                                            generation.region
                                                                        )}
                                                                        sx={{
                                                                            borderRadius: 0,
                                                                            bgcolor: "black",
                                                                            color: "white",
                                                                            fontWeight: 700,
                                                                        }}
                                                                    />

                                                                    {generation.body_type && (
                                                                        <Chip
                                                                            size="small"
                                                                            label={generation.body_type}
                                                                            sx={{
                                                                                borderRadius: 0,
                                                                                bgcolor: "white",
                                                                                color: "black",
                                                                                border: "1px solid black",
                                                                                fontWeight: 700,
                                                                            }}
                                                                        />
                                                                    )}
                                                                </Box>

                                                                <Typography
                                                                    variant="body2"
                                                                    sx={{mt: 1}}
                                                                >
                                                                    {getGenerationTitle(generation)}
                                                                </Typography>

                                                                {generation.body_code && (
                                                                    <Typography
                                                                        variant="body2"
                                                                        sx={{
                                                                            color: "text.secondary",
                                                                            mt: 0.5,
                                                                        }}
                                                                    >
                                                                        Коды кузова: {generation.body_code}
                                                                    </Typography>
                                                                )}
                                                            </Box>
                                                        </Paper>
                                                    );
                                                })}
                                            </Box>
                                        </Box>
                                    )
                                )}
                        </Paper>
                    )}

                    {selectedGeneration && (
                        <Paper sx={{...cardSx, mb: 2.5}}>
                            <Box
                                sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    gap: 2,
                                    flexWrap: "wrap",
                                    mb: 2,
                                }}
                            >
                                <Box>
                                    <Typography
                                        variant="h5"
                                        sx={{
                                            fontWeight: 800,
                                            color: "black",
                                        }}
                                    >
                                        3. Комплектация
                                    </Typography>

                                    <Typography
                                        variant="body2"
                                        sx={{color: "text.secondary", mt: 0.5}}
                                    >
                                        Уточните параметры комплектации или создайте пустой протокол.
                                    </Typography>
                                </Box>

                                <Chip
                                    label={selectedGeneration.name || "Поколение выбрано"}
                                    sx={{
                                        borderRadius: 0,
                                        bgcolor: "white",
                                        border: "1px solid black",
                                        color: "black",
                                        fontWeight: 800,
                                    }}
                                />
                            </Box>

                            {configurationFilterLoading && (
                                <Box
                                    sx={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 1,
                                        mb: 2,
                                    }}
                                >
                                    <CircularProgress size={20} sx={{color: "black"}}/>
                                    <Typography>Загрузка фильтров...</Typography>
                                </Box>
                            )}

                            <Box
                                sx={{
                                    display: "grid",
                                    gridTemplateColumns: {
                                        xs: "1fr",
                                        sm: "repeat(2, minmax(0, 1fr))",
                                        md: "repeat(3, minmax(0, 1fr))",
                                        lg: "repeat(4, minmax(0, 1fr))",
                                    },
                                    gap: 1.5,
                                    mb: 2,
                                }}
                            >
                                <TextField
                                    label="Год выпуска"
                                    value={configurationFilters.manufacture_year}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "manufacture_year",
                                            e.target.value
                                        )
                                    }
                                    placeholder="Например 2021"
                                    sx={textFieldSx}
                                />

                                <TextField
                                    select
                                    label="Код кузова"
                                    value={configurationFilters.body_code}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "body_code",
                                            e.target.value
                                        )
                                    }
                                    disabled={bodyCodeOptions.length === 0}
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {bodyCodeOptions.map((value) => (
                                        <MenuItem key={value} value={value}>
                                            {value}
                                        </MenuItem>
                                    ))}
                                </TextField>

                                <TextField
                                    select
                                    label="Привод"
                                    value={configurationFilters.drive_type}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "drive_type",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {(configurationFilterOptions.drive_types || []).map(
                                        (value) => (
                                            <MenuItem key={value} value={value}>
                                                {value}
                                            </MenuItem>
                                        )
                                    )}
                                </TextField>

                                <TextField
                                    select
                                    label="Тип топлива"
                                    value={configurationFilters.fuel_type}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "fuel_type",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {(configurationFilterOptions.fuel_types || []).map(
                                        (value) => (
                                            <MenuItem key={value} value={value}>
                                                {value}
                                            </MenuItem>
                                        )
                                    )}
                                </TextField>

                                <TextField
                                    select
                                    label="Двигатель"
                                    value={configurationFilters.engine_model}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "engine_model",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {(configurationFilterOptions.engine_models || []).map(
                                        (value) => (
                                            <MenuItem key={value} value={value}>
                                                {value}
                                            </MenuItem>
                                        )
                                    )}
                                </TextField>

                                <TextField
                                    select
                                    label="Мощность, кВт"
                                    value={configurationFilters.engine_power}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "engine_power",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {(configurationFilterOptions.engine_powers_kw || []).map(
                                        (value) => (
                                            <MenuItem key={value} value={value}>
                                                {value} кВт
                                            </MenuItem>
                                        )
                                    )}
                                </TextField>

                                <TextField
                                    select
                                    label="Тип коробки"
                                    value={configurationFilters.transmission}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "transmission",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {(configurationFilterOptions.transmissions || []).map(
                                        (value) => (
                                            <MenuItem key={value} value={value}>
                                                {value}
                                            </MenuItem>
                                        )
                                    )}
                                </TextField>

                                <TextField
                                    select
                                    label="Кол-во мест"
                                    value={configurationFilters.seats_count}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "seats_count",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    {(configurationFilterOptions.seats_counts || []).map(
                                        (value) => (
                                            <MenuItem key={value} value={value}>
                                                {value}
                                            </MenuItem>
                                        )
                                    )}
                                </TextField>

                                <TextField
                                    select
                                    label="Турбонаддув"
                                    value={configurationFilters.turbo_present}
                                    onChange={(e) =>
                                        handleConfigurationFilterChange(
                                            "turbo_present",
                                            e.target.value
                                        )
                                    }
                                    sx={textFieldSx}
                                >
                                    <MenuItem value="">Все</MenuItem>
                                    <MenuItem value="true">Есть</MenuItem>
                                    <MenuItem value="false">Нет</MenuItem>
                                </TextField>
                            </Box>

                            <Button
                                variant="outlined"
                                onClick={resetConfigurationFilters}
                                sx={outlineButtonSx}
                            >
                                Сбросить фильтры комплектаций
                            </Button>

                            <Divider sx={{my: 2}}/>

                            <Box
                                sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    gap: 2,
                                    flexWrap: "wrap",
                                    mb: 1.5,
                                }}
                            >
                                <Typography
                                    variant="body2"
                                    sx={{
                                        color: "text.secondary",
                                        fontWeight: 700,
                                    }}
                                >
                                    {selectedConfiguration
                                        ? "Комплектация выбрана"
                                        : `Найдено комплектаций: ${configurations.length}`}
                                </Typography>

                                {configurationLoading && (
                                    <Box
                                        sx={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 1,
                                        }}
                                    >
                                        <CircularProgress size={18} sx={{color: "black"}}/>
                                        <Typography variant="body2">
                                            Поиск комплектаций...
                                        </Typography>
                                    </Box>
                                )}
                            </Box>

                            <Autocomplete
                                value={selectedConfiguration}
                                inputValue={configurationInputValue}
                                disablePortal
                                options={configurations}
                                getOptionLabel={buildConfigurationLabel}
                                isOptionEqualToValue={(option, value) =>
                                    option.id === value.id
                                }
                                filterOptions={(options) => options}
                                loading={configurationLoading}
                                onInputChange={(event, newInputValue) =>
                                    setConfigurationInputValue(newInputValue)
                                }
                                onChange={(event, newValue) =>
                                    setSelectedConfiguration(newValue)
                                }
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Выберите конфигурацию"
                                        placeholder="Можно искать по названию: X, Bolero, Highway Star..."
                                        sx={textFieldSx}
                                    />
                                )}
                            />

                            {!configurationLoading &&
                                selectedGeneration &&
                                !selectedConfiguration &&
                                configurations.length === 0 && (
                                    <Alert
                                        severity="info"
                                        sx={{mt: 2, borderRadius: 0}}
                                    >
                                        По выбранным фильтрам комплектации не найдены. Можно создать пустой протокол и
                                        заполнить данные вручную.
                                    </Alert>
                                )}
                        </Paper>
                    )}

                    <Paper
                        sx={{
                            position: "sticky",
                            bottom: 0,
                            border: "2px solid black",
                            borderRadius: 0,
                            p: 2,
                            bgcolor: "#f2f2f2",
                            boxShadow: "none",
                            zIndex: 10,
                        }}
                    >
                        <Box
                            sx={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                gap: 2,
                                flexWrap: "wrap",
                            }}
                        >
                            <Box>
                                <Typography
                                    variant="body2"
                                    sx={{
                                        color: "text.secondary",
                                        fontWeight: 700,
                                    }}
                                >
                                    После выбора марки и модели откроется сокращённая форма замерщика.
                                </Typography>

                                {createProtocolError && (
                                    <Typography
                                        variant="body2"
                                        sx={{color: "error.main", mt: 0.5}}
                                    >
                                        {createProtocolError}
                                    </Typography>
                                )}
                            </Box>

                            <Button
                                variant="contained"
                                onClick={handleNextPage}
                                disabled={
                                    !selectedBrand || !selectedModel || creatingProtocol
                                }
                                sx={blackButtonSx}
                            >
                                {creatingProtocol
                                    ? "Создание протокола..."
                                    : selectedConfiguration
                                        ? "Создать протокол по выбранной комплектации"
                                        : selectedGeneration
                                            ? "Создать пустой протокол"
                                            : "Начать первичный замер"}
                            </Button>
                        </Box>
                    </Paper>
                </Paper>
            </Box>
        </>
    );
}

export default CarSelection;