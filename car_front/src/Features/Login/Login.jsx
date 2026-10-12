import {useCallback, useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";

import api from "../../shared/api.jsx";
import {getApiErrorMessage} from "../../shared/errorHandler.jsx";

import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";

function Login() {
    const [loading, setLoading] = useState(false);
    const [checkingAuth, setCheckingAuth] = useState(true);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const navigate = useNavigate();

    const navigateByRole = useCallback(async () => {
        const response = await api.get("/cars/get-user/");
        if (!response.data.role) {
            throw new Error("Пользователь не имеет роли");
        }

        navigate(response.data.role === "measurer" ? "/measurement" : "/protocols");
    }, [navigate]);

    useEffect(() => {
        const accessToken = localStorage.getItem("accessToken");
        const refreshToken = localStorage.getItem("refreshToken");

        if (accessToken && refreshToken) {
            api.get("/cars/brands/")
                .then(() => navigateByRole())
                .catch(() => {
                    localStorage.removeItem("accessToken");
                    localStorage.removeItem("refreshToken");
                })
                .finally(() => {
                    setCheckingAuth(false);
                });
        } else {
            setCheckingAuth(false);
        }
    }, [navigateByRole]);

    async function submitData() {
        setLoading(true);
        setError(null);

        try {
            const response = await api.post("/cars/token/", {
                username,
                password,
            });

            if (response.status === 200) {
                localStorage.setItem("accessToken", response.data.access);
                localStorage.setItem("refreshToken", response.data.refresh);

                await api.setTokenAuth();

                await navigateByRole();
            } else {
                setError("Ошибка авторизации");
            }
        } catch (e) {
            setError(
                e.response?.status === 401
                    ? "Неверный логин или пароль"
                    : getApiErrorMessage(e, "Ошибка авторизации")
            );
        } finally {
            setLoading(false);
        }
    }

    if (checkingAuth) {
        return (
            <Box
                sx={{
                    minHeight: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: "#f2f2f2",
                }}
            >
                <CircularProgress sx={{color: "black"}}/>
            </Box>
        );
    }

    return (
        <Box
            sx={{
                width: "100vw",
                minHeight: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#f2f2f2",
                px: 2,
            }}
        >
            <Paper
                component="form"
                noValidate
                autoComplete="off"
                onSubmit={(e) => {
                    e.preventDefault();

                    if (!loading && username && password) {
                        submitData();
                    }
                }}
                sx={{
                    width: "100%",
                    maxWidth: 400,
                    p: 4,
                    border: "2px solid black",
                    borderRadius: 0,
                    boxShadow: "none",
                    backgroundColor: "white",
                }}
            >
                <Typography
                    variant="h5"
                    sx={{
                        mb: 1,
                        fontWeight: 700,
                        color: "black",
                    }}
                >
                    Вход в систему
                </Typography>

                <Typography
                    variant="body2"
                    sx={{
                        mb: 3,
                        color: "text.secondary",
                    }}
                >
                    Введите логин и пароль для работы с протоколами.
                </Typography>

                {error && (
                    <Alert
                        severity="error"
                        sx={{
                            mb: 2,
                            borderRadius: 0,
                        }}
                    >
                        {error}
                    </Alert>
                )}

                <TextField
                    fullWidth
                    label="Логин"
                    variant="outlined"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={loading}
                    sx={{
                        mb: 2,
                        "& .MuiOutlinedInput-root": {
                            borderRadius: 0,
                        },
                    }}
                />

                <TextField
                    fullWidth
                    label="Пароль"
                    variant="outlined"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    sx={{
                        mb: 3,
                        "& .MuiOutlinedInput-root": {
                            borderRadius: 0,
                        },
                    }}
                />

                <Button
                    fullWidth
                    type="submit"
                    variant="contained"
                    disabled={loading || !username || !password}
                    sx={{
                        py: 1.2,
                        backgroundColor: "black",
                        color: "white",
                        borderRadius: 0,
                        textTransform: "none",
                        fontWeight: 700,
                        boxShadow: "none",
                        "&:hover": {
                            backgroundColor: "#222",
                            boxShadow: "none",
                        },
                    }}
                >
                    {loading ? "Вход..." : "Войти"}
                </Button>
            </Paper>
        </Box>
    );
}

export default Login;