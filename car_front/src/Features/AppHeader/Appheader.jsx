import {useEffect, useState} from "react";
import {useLocation, useNavigate} from "react-router-dom";

import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";

import api from "../../shared/api.jsx";

function AppHeader({beforeNavigate}) {
    const navigate = useNavigate();
    const location = useLocation();

    const [currentUser, setCurrentUser] = useState(null);
    const [leaving, setLeaving] = useState(false);
    const [mobileMenuAnchor, setMobileMenuAnchor] = useState(null);

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
        minHeight: 44,
        minWidth: 0,
        width: {xs: "100%", sm: "auto"},
        fontWeight: 700,
        textTransform: "none",
        whiteSpace: {xs: "normal", sm: "nowrap"},
        lineHeight: 1.2,
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

    const handleMobileNavigate = (path) => {
        setMobileMenuAnchor(null);
        handleNavigate(path);
    };

    const handleMobileLogout = () => {
        setMobileMenuAnchor(null);
        handleLogout();
    };

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
                    minHeight: {xs: "auto", sm: "56px"},
                    display: {xs: "grid", sm: "flex"},
                    gridTemplateColumns: {xs: "minmax(0, 1fr) auto", sm: "none"},
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: {xs: 1, sm: 2},
                    px: {xs: 1.5, sm: 2},
                    py: {xs: 1, sm: 0},
                }}
            >
                <Typography
                    variant="h6"
                    sx={{
                        fontWeight: 800,
                        whiteSpace: {xs: "normal", sm: "nowrap"},
                        color: "black",
                        fontSize: {xs: "1.05rem", sm: "1.25rem"},
                        lineHeight: 1.15,
                    }}
                >
                    Система протоколов
                </Typography>

                <Box
                    sx={{
                        display: {xs: "none", sm: "flex"},
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
                            minHeight: 44,
                            minWidth: 0,
                            width: "auto",
                            fontWeight: 700,
                            textTransform: "none",
                            whiteSpace: "nowrap",
                            lineHeight: 1.2,
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

                <Box sx={{display: {xs: "flex", sm: "none"}, alignItems: "center", gap: 0.75}}>
                    {isMeasurer ? (
                        <>
                            <Button
                                onClick={() => handleNavigate("/measurement")}
                                disabled={leaving}
                                sx={{...navButtonSx(isActive("/measurement")), px: 1.25}}
                            >
                                Мои замеры
                            </Button>
                            <Button
                                onClick={handleLogout}
                                disabled={leaving}
                                sx={{...navButtonSx(false), width: "auto", px: 1.25, bgcolor: "black", color: "white", "&:hover": {bgcolor: "#222"}}}
                            >
                                Выйти
                            </Button>
                        </>
                    ) : (
                        <Button
                            aria-label="Открыть меню"
                            aria-haspopup="menu"
                            aria-expanded={Boolean(mobileMenuAnchor)}
                            onClick={(event) => setMobileMenuAnchor(event.currentTarget)}
                            disabled={leaving}
                            sx={{...navButtonSx(false), width: "auto", whiteSpace: "nowrap", px: 1.5}}
                        >
                            ☰ Меню
                        </Button>
                    )}
                </Box>
            </Toolbar>
            <Menu
                anchorEl={mobileMenuAnchor}
                open={Boolean(mobileMenuAnchor)}
                onClose={() => setMobileMenuAnchor(null)}
                anchorOrigin={{vertical: "bottom", horizontal: "right"}}
                transformOrigin={{vertical: "top", horizontal: "right"}}
                sx={{display: {xs: "block", sm: "none"}}}
                slotProps={{paper: {sx: {minWidth: 230, border: "1px solid black", mt: 0.5}}}}
            >
                <MenuItem onClick={() => handleMobileNavigate("/protocols")} selected={isActive("/protocols")}>
                    Протоколы в работе
                </MenuItem>
                <MenuItem onClick={() => handleMobileNavigate("/protocols/completed")} selected={isActive("/protocols/completed")}>
                    Завершенные протоколы
                </MenuItem>
                <MenuItem onClick={() => handleMobileNavigate("/protocols/approved")} selected={isActive("/protocols/approved")}>
                    Утверждённые протоколы
                </MenuItem>
                {canManageEmployees && (
                    <MenuItem onClick={() => handleMobileNavigate("/employees")} selected={isActive("/employees")}>
                        Сотрудники
                    </MenuItem>
                )}
                <MenuItem onClick={handleMobileLogout} sx={{borderTop: "1px solid #ddd", mt: 0.5, fontWeight: 700}}>
                    Выйти
                </MenuItem>
            </Menu>
        </AppBar>
    );
}

export default AppHeader;