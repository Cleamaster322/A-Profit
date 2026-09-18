import {useEffect, useState} from "react";
import {useLocation, useNavigate} from "react-router-dom";

import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import api from "../../shared/api.jsx";

function AppHeader({beforeNavigate}) {
    const navigate = useNavigate();
    const location = useLocation();

    const [currentUser, setCurrentUser] = useState(null);
    const [leaving, setLeaving] = useState(false);

    const isActive = (path) => location.pathname === path;

    const canManageEmployees = Boolean(
        currentUser?.is_superuser || currentUser?.role === "executive_director"
    );
    const isMeasurer = currentUser?.role === "measurer";

    useEffect(() => {
        let isMounted = true;

        async function loadCurrentUser() {
            try {
                const response = await api.get("/cars/get-user/");

                if (isMounted) {
                    setCurrentUser(response.data);
                }
            } catch (error) {
                console.error("Ошибка загрузки текущего пользователя:", error);

                if (isMounted) {
                    setCurrentUser(null);
                }
            }
        }

        loadCurrentUser();

        return () => {
            isMounted = false;
        };
    }, []);

    const runBeforeNavigate = async () => {
        if (typeof beforeNavigate !== "function") {
            return;
        }

        await beforeNavigate();
    };

    const handleNavigate = async (path) => {
        if (leaving || location.pathname === path) {
            return;
        }

        try {
            setLeaving(true);
            await runBeforeNavigate();
            navigate(path);
        } catch (error) {
            console.error("Ошибка перед переходом:", error);
            navigate(path);
        } finally {
            setLeaving(false);
        }
    };

    const handleLogout = async () => {
        if (leaving) {
            return;
        }

        try {
            setLeaving(true);

            await runBeforeNavigate();

            await api.logout();
            navigate("/");
        } catch (error) {
            console.error("Ошибка при выходе:", error);

            await api.logout();
            navigate("/");
        } finally {
            setLeaving(false);
        }
    };

    const navButtonSx = (active) => ({
        color: active ? "white" : "black",
        backgroundColor: active ? "black" : "white",
        border: "1px solid black",
        borderRadius: 0,
        px: 2,
        py: 0.8,
        fontWeight: 700,
        textTransform: "none",
        boxShadow: "none",
        "&:hover": {
            backgroundColor: active ? "#222" : "#f2f2f2",
            boxShadow: "none",
        },
        "&.Mui-disabled": {
            color: "#777777",
            backgroundColor: "#dddddd",
            border: "1px solid #999999",
        },
    });

    return (
        <AppBar
            position="sticky"
            elevation={0}
            sx={{
                top: 0,
                zIndex: 1200,
                backgroundColor: "white",
                color: "black",
                borderBottom: "2px solid black",
                boxShadow: "none",
            }}
        >
            <Toolbar
                sx={{
                    minHeight: "56px",
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 2,
                    px: 2,
                }}
            >
                <Typography
                    variant="h6"
                    sx={{
                        fontWeight: 800,
                        whiteSpace: "nowrap",
                        color: "black",
                    }}
                >
                    Система протоколов
                </Typography>

                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        flexWrap: "wrap",
                        justifyContent: "flex-end",
                    }}
                >
                    {isMeasurer ? (
                        <Button
                            onClick={() => handleNavigate("/measurement")}
                            disabled={leaving}
                            sx={navButtonSx(isActive("/measurement"))}
                        >
                            Мои замеры
                        </Button>
                    ) : (
                        <Button
                            onClick={() => handleNavigate("/protocols")}
                            disabled={leaving}
                            sx={navButtonSx(isActive("/protocols"))}
                        >
                            Протоколы в работе
                        </Button>
                    )}

                    {!isMeasurer && <Button
                        onClick={() => handleNavigate("/protocols/completed")}
                        disabled={leaving}
                        sx={navButtonSx(isActive("/protocols/completed"))}
                    >
                        Завершенные протоколы
                    </Button>}

                    {!isMeasurer && <Button
                        onClick={() => handleNavigate("/protocols/approved")}
                        disabled={leaving}
                        sx={navButtonSx(isActive("/protocols/approved"))}
                    >
                        Утверждённые протоколы
                    </Button>}

                    {canManageEmployees && (
                        <Button
                            onClick={() => handleNavigate("/employees")}
                            disabled={leaving}
                            sx={navButtonSx(isActive("/employees"))}
                        >
                            Сотрудники
                        </Button>
                    )}

                    <Button
                        onClick={handleLogout}
                        disabled={leaving}
                        sx={{
                            color: "white",
                            backgroundColor: "black",
                            border: "1px solid black",
                            borderRadius: 0,
                            px: 2,
                            py: 0.8,
                            fontWeight: 700,
                            textTransform: "none",
                            boxShadow: "none",
                            "&:hover": {
                                backgroundColor: "#222",
                                boxShadow: "none",
                            },
                            "&.Mui-disabled": {
                                color: "#777777",
                                backgroundColor: "#dddddd",
                                border: "1px solid #999999",
                            },
                        }}
                    >
                        {leaving ? "Выход..." : "Выйти"}
                    </Button>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

export default AppHeader;