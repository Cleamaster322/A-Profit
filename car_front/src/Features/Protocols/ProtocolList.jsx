import {useEffect, useMemo, useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../shared/api.jsx";
import {baseURL} from "../../shared/config.jsx";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Grid from "@mui/material/Grid";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";

import AppHeader from "../AppHeader/AppHeader.jsx";

function getStatusText(status) {
    switch (status) {
        case "draft":
            return "Черновик";
        case "in_progress":
            return "В работе";
        case "completed":
            return "Завершён";
        case "approved":
            return "Утверждён";
        case "cancelled":
            return "Отменён";
        default:
            return status || "Неизвестно";
    }
}

function getStatusChipSx(status) {
    if (status === "completed") {
        return {
            bgcolor: "black",
            color: "white",
            borderRadius: 0,
            fontWeight: 700,
        };
    }

    if (status === "in_progress") {
        return {
            bgcolor: "black",
            color: "white",
            borderRadius: 0,
            fontWeight: 700,
        };
    }

    if (status === "draft") {
        return {
            bgcolor: "white",
            color: "black",
            border: "1px solid black",
            borderRadius: 0,
            fontWeight: 700,
        };
    }

    return {
        bgcolor: "#f5f5f5",
        color: "black",
        border: "1px solid #999",
        borderRadius: 0,
        fontWeight: 700,
    };
}

function getWebSocketUrl() {
    const backendUrl = new URL(baseURL);
    const wsProtocol = backendUrl.protocol === "https:" ? "wss:" : "ws:";

    return `${wsProtocol}//${backendUrl.host}/ws/protocols/`;
}

function createProtocolWebSocket() {
    const accessToken = localStorage.getItem("accessToken");

    if (!accessToken) {
        return null;
    }

    return new WebSocket(getWebSocketUrl(), ["jwt", accessToken]);
}

function getProtocolTitle(protocol) {
    const brand = protocol.brand_name || "";
    const model = protocol.commercial_name || "";
    const title = `${brand} ${model}`.trim();

    return title || "Автомобиль не указан";
}

function ProtocolCard({
                          protocol,
                          onOpen,
                          onReleaseLock,
                          onApprove,
                          onCancel,
                          canManageProtocols,
                          showReviewActions,
                      }) {
    const isLocked = protocol.status === "in_progress";
    const isReturnedForRevision = Boolean(protocol.returned_for_revision);

    return (
        <Paper
            sx={{
                height: "100%",
                border: isReturnedForRevision ? "2px solid #b3261e" : "2px solid black",
                borderRadius: 0,
                p: 2.5,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                boxShadow: "none",
                bgcolor: isReturnedForRevision ? "#fff5f5" : "white",
                transition: "0.15s",
                "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: "4px 4px 0 black",
                },
            }}
        >
            <Box>
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        gap: 1,
                        mb: 2,
                    }}
                >
                    <Typography
                        variant="h6"
                        sx={{
                            fontWeight: 800,
                            color: "black",
                            lineHeight: 1.2,
                        }}
                    >
                        № {protocol.protocol_number || protocol.id}
                    </Typography>

                    <Chip
                        size="small"
                        label={getStatusText(protocol.status)}
                        sx={getStatusChipSx(protocol.status)}
                    />
                </Box>

                <Typography
                    variant="subtitle1"
                    sx={{
                        fontWeight: 800,
                        color: "black",
                        mb: 1.5,
                        minHeight: 24,
                    }}
                >
                    {getProtocolTitle(protocol)}
                </Typography>
                {isReturnedForRevision && (
                    <Box sx={{mb: 1.5}}>
                        <Chip
                            size="small"
                            label="Возвращён на доработку"
                            sx={{
                                bgcolor: "#fff",
                                color: "#b3261e",
                                border: "1px solid #b3261e",
                                borderRadius: 0,
                                fontWeight: 800,
                                mb: protocol.revision_comment ? 1 : 0,
                            }}
                        />

                        {protocol.revision_comment && (
                            <Typography
                                variant="body2"
                                sx={{
                                    color: "#b3261e",
                                    fontWeight: 600,
                                    lineHeight: 1.35,
                                }}
                            >
                                <b>Причина:</b> {protocol.revision_comment}
                            </Typography>
                        )}
                    </Box>
                )}

                <Box sx={{display: "grid", gap: 0.7}}>
                    <Typography variant="body2" sx={{color: "black"}}>
                        <b>VIN:</b> {protocol.vin || "—"}
                    </Typography>

                    <Typography variant="body2" sx={{color: "black"}}>
                        <b>Год:</b> {protocol.manufacture_year || "—"}
                    </Typography>

                    <Typography variant="body2" sx={{color: "black"}}>
                        <b>Категория:</b> {protocol.vehicle_category || "—"}
                    </Typography>

                    {isLocked && (
                        <Typography variant="body2" sx={{color: "black"}}>
                            <b>Редактирует:</b>{" "}
                            {protocol.locked_by_full_name ||
                                protocol.locked_by_username ||
                                "другой пользователь"}
                        </Typography>
                    )}
                </Box>
            </Box>

            <Box
                sx={{
                    display: "flex",
                    justifyContent: "flex-start",
                    gap: 1,
                    flexWrap: "wrap",
                    mt: 3,
                }}
            >
                <Button
                    onClick={() => onOpen(protocol)}
                    variant="contained"
                    disabled={isLocked}
                    sx={{
                        bgcolor: isLocked ? "#d0d0d0" : "black",
                        color: isLocked ? "#666666" : "white",
                        textTransform: "none",
                        borderRadius: 0,
                        px: 2.5,
                        py: 0.8,
                        fontWeight: 700,
                        boxShadow: "none",
                        border: isLocked ? "1px solid #999999" : "1px solid black",
                        "&:hover": {
                            bgcolor: isLocked ? "#d0d0d0" : "#222",
                            boxShadow: "none",
                        },
                        "&.Mui-disabled": {
                            bgcolor: "#d0d0d0",
                            color: "#666666",
                            border: "1px solid #999999",
                        },
                    }}
                >
                    {isLocked ? "В работе" : "Открыть"}
                </Button>

                {isLocked && canManageProtocols && (
                    <Button
                        variant="outlined"
                        onClick={() => onReleaseLock(protocol.id)}
                        sx={{
                            borderColor: "black",
                            color: "black",
                            borderRadius: 0,
                            textTransform: "none",
                            px: 2,
                            py: 0.8,
                            fontWeight: 700,
                            "&:hover": {
                                borderColor: "black",
                                bgcolor: "#eeeeee",
                            },
                        }}
                    >
                        Освободить
                    </Button>
                )}
                {showReviewActions && canManageProtocols && protocol.status === "completed" && (
                    <>
                        <Button
                            variant="contained"
                            onClick={() => onApprove(protocol.id)}
                            sx={{
                                bgcolor: "black",
                                color: "white",
                                textTransform: "none",
                                borderRadius: 0,
                                px: 2,
                                py: 0.8,
                                fontWeight: 700,
                                boxShadow: "none",
                                border: "1px solid black",
                                "&:hover": {
                                    bgcolor: "#222",
                                    boxShadow: "none",
                                },
                            }}
                        >
                            Утвердить
                        </Button>

                        <Button
                            variant="outlined"
                            onClick={() => onCancel(protocol.id)}
                            sx={{
                                borderColor: "#b3261e",
                                color: "#b3261e",
                                borderRadius: 0,
                                textTransform: "none",
                                px: 2,
                                py: 0.8,
                                fontWeight: 700,
                                "&:hover": {
                                    borderColor: "#b3261e",
                                    bgcolor: "#fff5f5",
                                },
                            }}
                        >
                            Вернуть на доработку
                        </Button>
                    </>
                )}
            </Box>
        </Paper>
    );
}

function ProtocolList({
                          title,
                          description,
                          statuses,
                          emptyTitle,
                          emptyDescription,
                          showCreateButton = false,
                      }) {
    const navigate = useNavigate();

    const [protocols, setProtocols] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [searchQuery, setSearchQuery] = useState("");
    const [currentUser, setCurrentUser] = useState(null);

    const showReviewActions = statuses.includes("completed");

    const loadProtocols = async (options = {}) => {
        const {silent = false} = options;

        try {
            if (!silent) {
                setLoading(true);
            }

            setError("");

            const response = await api.get("/cars/protocols/");
            const data = response.data;

            let items = [];

            if (Array.isArray(data)) {
                items = data;
            } else if (Array.isArray(data?.results)) {
                items = data.results;
            }

            const filteredByStatus = items.filter((item) =>
                statuses.includes(item.status)
            );

            setProtocols(filteredByStatus);
        } catch (err) {
            console.error(err);
            setError("Не удалось загрузить протоколы");
        } finally {
            if (!silent) {
                setLoading(false);
            }
        }
    };

    const loadCurrentUser = async () => {
        try {
            const response = await api.get("/cars/get-user/");
            setCurrentUser(response.data);
        } catch (error) {
            console.error("Ошибка загрузки текущего пользователя:", error);
        }
    };

    useEffect(() => {
        loadCurrentUser();
        loadProtocols();

        const refreshTimer = setTimeout(() => {
            loadProtocols({silent: true});
        }, 500);

        const handleWindowFocus = () => {
            loadProtocols({silent: true});
        };

        window.addEventListener("focus", handleWindowFocus);

        return () => {
            clearTimeout(refreshTimer);
            window.removeEventListener("focus", handleWindowFocus);
        };
    }, []);

    useEffect(() => {
        let socket = null;
        let reconnectTimer = null;
        let reconnectDelay = 1000;
        let stopped = false;

        const scheduleReconnect = (delay = reconnectDelay) => {
            if (stopped || reconnectTimer) {
                return;
            }

            reconnectTimer = setTimeout(() => {
                reconnectTimer = null;
                connect();
            }, delay);
            reconnectDelay = Math.min(reconnectDelay * 2, 10000);
        };

        const connect = () => {
            if (stopped || socket) {
                return;
            }

            const nextSocket = createProtocolWebSocket();
            if (!nextSocket) {
                return;
            }

            socket = nextSocket;

            nextSocket.onopen = () => {
                reconnectDelay = 1000;
                console.log("Protocols WebSocket connected");
            };

            nextSocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type !== "protocol_status_changed") {
                        return;
                    }

                    const updatedProtocol = data.protocol;

                    setProtocols((prevProtocols) =>
                        prevProtocols.map((protocol) =>
                            protocol.id === updatedProtocol.id
                                ? {
                                    ...protocol,
                                    status: updatedProtocol.status,
                                    locked_by: updatedProtocol.locked_by,
                                    locked_by_id: updatedProtocol.locked_by_id,
                                    locked_by_username: updatedProtocol.locked_by_username,
                                    locked_by_full_name: updatedProtocol.locked_by_full_name,
                                    returned_for_revision: updatedProtocol.returned_for_revision,
                                    revision_comment: updatedProtocol.revision_comment,
                                    cancelled_at: updatedProtocol.cancelled_at,
                                    cancelled_by: updatedProtocol.cancelled_by,
                                    cancelled_by_id: updatedProtocol.cancelled_by_id,
                                    cancelled_by_username: updatedProtocol.cancelled_by_username,
                                    cancelled_by_full_name: updatedProtocol.cancelled_by_full_name,
                                }
                                : protocol
                        )
                    );
                } catch (error) {
                    console.error("Protocols WebSocket message error:", error);
                }
            };

            nextSocket.onerror = (error) => {
                console.error("Protocols WebSocket error:", error);
            };

            nextSocket.onclose = async (event) => {
                if (socket !== nextSocket) {
                    return;
                }

                socket = null;

                if (stopped) {
                    return;
                }

                if (event.code === 4401) {
                    try {
                        await api.refreshAccessToken();
                        reconnectDelay = 1000;
                    } catch {
                        return;
                    }
                }

                scheduleReconnect(event.code === 4401 ? 0 : reconnectDelay);
            };
        };

        const handleTokenRefresh = () => {
            if (socket) {
                socket.close(4001, "access token refreshed");
            } else {
                connect();
            }
        };

        window.addEventListener("auth:token-refreshed", handleTokenRefresh);
        connect();

        return () => {
            stopped = true;
            window.removeEventListener("auth:token-refreshed", handleTokenRefresh);
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
            socket?.close(1000, "component unmounted");
            socket = null;
        };
    }, []);

    const filteredProtocols = useMemo(() => {
        const query = searchQuery.trim().toLowerCase();

        if (!query) {
            return protocols;
        }

        return protocols.filter((protocol) => {
            const values = [
                protocol.protocol_number,
                protocol.brand_name,
                protocol.commercial_name,
                protocol.vin,
                protocol.manufacture_year,
                protocol.vehicle_category,
            ];

            return values.some((value) =>
                String(value || "").toLowerCase().includes(query)
            );
        });
    }, [protocols, searchQuery]);

    const handleCreate = () => {
        navigate("/home", {
            state: {
                mode: "create_protocol",
            },
        });
    };

    const handleOpen = (protocol) => {
        navigate(`/protocols/${protocol.id}/inspection`);
    };

    const canManageProtocols = Boolean(
        currentUser?.is_superuser ||
        currentUser?.role === "manager" ||
        currentUser?.role === "executive_director"
    );

    const handleManagerReleaseLock = async (protocolId) => {
        const confirmed = window.confirm(
            "Освободить протокол? Он снова станет доступен как черновик."
        );

        if (!confirmed) {
            return;
        }

        try {
            await api.post(`/cars/protocols/${protocolId}/manager-release-lock/`);

            setProtocols((prevProtocols) =>
                prevProtocols.map((protocol) =>
                    protocol.id === protocolId
                        ? {
                            ...protocol,
                            status: "draft",
                            locked_by: null,
                            locked_by_id: null,
                            locked_by_username: null,
                            locked_by_full_name: null,
                        }
                        : protocol
                )
            );
        } catch (error) {
            console.error("Ошибка освобождения протокола:", error);

            alert(
                error.response?.data?.detail ||
                error.response?.data?.error ||
                "Не удалось освободить протокол"
            );
        }
    };

    const handleApproveProtocol = async (protocolId) => {
        const confirmed = window.confirm(
            "Утвердить протокол? После этого он попадёт в утверждённые."
        );

        if (!confirmed) {
            return;
        }

        try {
            await api.post(`/cars/protocols/${protocolId}/approve/`);

            setProtocols((prevProtocols) =>
                prevProtocols.filter((protocol) => protocol.id !== protocolId)
            );
        } catch (error) {
            console.error("Ошибка утверждения протокола:", error);

            alert(
                error.response?.data?.detail ||
                error.response?.data?.error ||
                "Не удалось утвердить протокол"
            );
        }
    };

    const handleCancelProtocol = async (protocolId) => {
        const revisionComment = window.prompt(
            "Укажите причину возврата протокола на доработку:"
        );

        if (revisionComment === null) {
            return;
        }

        try {
            await api.cancelProtocol(protocolId, revisionComment);

            setProtocols((prevProtocols) =>
                prevProtocols.filter((protocol) => protocol.id !== protocolId)
            );
        } catch (error) {
            console.error("Ошибка возврата протокола на доработку:", error);

            alert(
                error.response?.data?.detail ||
                error.response?.data?.error ||
                "Не удалось вернуть протокол на доработку"
            );
        }
    };

    return (
        <>
            <AppHeader/>

            <Box
                sx={{
                    bgcolor: "#f2f2f2",
                    px: 3,
                    py: 3,
                    boxSizing: "border-box",
                }}
            >
                <Paper
                    sx={{
                        border: "2px solid black",
                        borderRadius: 0,
                        p: 3,
                        bgcolor: "#f2f2f2",
                        boxShadow: "none",
                        boxSizing: "border-box",
                    }}
                >
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
                            <Typography
                                variant="h4"
                                sx={{
                                    fontWeight: 800,
                                    color: "black",
                                    mb: 0.5,
                                }}
                            >
                                {title}
                            </Typography>

                            <Typography
                                variant="body1"
                                sx={{
                                    color: "text.secondary",
                                }}
                            >
                                {description}
                            </Typography>
                        </Box>

                        {showCreateButton && (
                            <Button
                                variant="contained"
                                onClick={handleCreate}
                                sx={{
                                    bgcolor: "black",
                                    color: "white",
                                    textTransform: "none",
                                    borderRadius: 0,
                                    px: 3,
                                    py: 1.2,
                                    fontWeight: 800,
                                    boxShadow: "none",
                                    "&:hover": {
                                        bgcolor: "#222",
                                        boxShadow: "none",
                                    },
                                }}
                            >
                                Создать протокол
                            </Button>
                        )}
                    </Box>

                    <Box
                        sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            gap: 2,
                            flexWrap: "wrap",
                            mb: 3,
                        }}
                    >
                        <TextField
                            value={searchQuery}
                            onChange={(event) => setSearchQuery(event.target.value)}
                            placeholder="Поиск по номеру, марке, модели, VIN или году"
                            size="small"
                            sx={{
                                width: {
                                    xs: "100%",
                                    md: 480,
                                },
                                bgcolor: "white",
                                "& .MuiOutlinedInput-root": {
                                    borderRadius: 0,
                                },
                            }}
                            slotProps={{
                                input: {
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            Поиск:
                                        </InputAdornment>
                                    ),
                                },
                            }}
                        />

                        <Typography
                            variant="body2"
                            sx={{
                                color: "text.secondary",
                                fontWeight: 600,
                            }}
                        >
                            Найдено: {filteredProtocols.length}
                        </Typography>
                    </Box>

                    {error && (
                        <Alert
                            severity="error"
                            sx={{
                                mb: 3,
                                borderRadius: 0,
                            }}
                        >
                            {error}
                        </Alert>
                    )}

                    {loading ? (
                        <Box
                            sx={{
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                minHeight: 240,
                            }}
                        >
                            <CircularProgress sx={{color: "black"}}/>
                        </Box>
                    ) : filteredProtocols.length === 0 ? (
                        <Paper
                            sx={{
                                border: "2px dashed black",
                                borderRadius: 0,
                                p: 4,
                                bgcolor: "white",
                                boxShadow: "none",
                                textAlign: "center",
                            }}
                        >
                            <Typography
                                variant="h6"
                                sx={{
                                    fontWeight: 800,
                                    mb: 1,
                                }}
                            >
                                {emptyTitle}
                            </Typography>

                            <Typography
                                variant="body2"
                                sx={{
                                    color: "text.secondary",
                                    mb: showCreateButton ? 3 : 0,
                                }}
                            >
                                {emptyDescription}
                            </Typography>

                            {showCreateButton && (
                                <Button
                                    variant="contained"
                                    onClick={handleCreate}
                                    sx={{
                                        bgcolor: "black",
                                        color: "white",
                                        textTransform: "none",
                                        borderRadius: 0,
                                        px: 3,
                                        py: 1,
                                        fontWeight: 700,
                                        boxShadow: "none",
                                        "&:hover": {
                                            bgcolor: "#222",
                                            boxShadow: "none",
                                        },
                                    }}
                                >
                                    Создать протокол
                                </Button>
                            )}
                        </Paper>
                    ) : (
                        <Grid container spacing={2.5}>
                            {filteredProtocols.map((protocol) => (
                                <Grid
                                    item
                                    xs={12}
                                    sm={6}
                                    md={4}
                                    lg={3}
                                    xl={2.4}
                                    key={protocol.id}
                                >
                                    <ProtocolCard
                                        protocol={protocol}
                                        onOpen={handleOpen}
                                        onReleaseLock={handleManagerReleaseLock}
                                        onApprove={handleApproveProtocol}
                                        onCancel={handleCancelProtocol}
                                        canManageProtocols={canManageProtocols}
                                        showReviewActions={showReviewActions}
                                    />
                                </Grid>
                            ))}
                        </Grid>
                    )}
                </Paper>
            </Box>
        </>
    );
}

export default ProtocolList;