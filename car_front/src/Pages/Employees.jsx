import {useEffect, useState} from "react";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";

import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Grid from "@mui/material/Grid";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Divider from "@mui/material/Divider";
import MenuItem from "@mui/material/MenuItem";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import IconButton from "@mui/material/IconButton";
import {commonSx} from "../theme.js";

const pageSx = {...commonSx.page, boxSizing: "border-box"};
const pageInnerSx = {...commonSx.pageInner, boxSizing: "border-box"};
const cardSx = commonSx.card;

const employeeCardSx = {
    border: "1px solid black",
    borderRadius: 0,
    p: 1.25,
    boxShadow: "none",
    bgcolor: "white",
    minHeight: 135,
};

const modalPaperSx = {
    border: "2px solid black",
    borderRadius: 0,
    boxShadow: "none",
    bgcolor: "white",
    width: "100%",
    maxWidth: 560,
};

const textFieldSx = commonSx.field;
const blackButtonSx = commonSx.primaryButton;
const outlineButtonSx = commonSx.secondaryButton;

const USER_ROLES = [
    {
        value: "measurer",
        label: "Замерщик",
    },
    {
        value: "operator",
        label: "Оформитель",
    },
    {
        value: "manager",
        label: "Руководитель",
    },
    {
        value: "executive_director",
        label: "Исполнительный директор",
    },
];

function getErrorText(error) {
    const data = error.response?.data;

    if (!data) {
        return "Ошибка сети или сервер недоступен";
    }

    if (data.detail) {
        return data.detail;
    }

    if (data.username) {
        return Array.isArray(data.username) ? data.username.join(" ") : data.username;
    }

    if (data.password) {
        return Array.isArray(data.password) ? data.password.join(" ") : data.password;
    }

    if (data.current_password) {
        return Array.isArray(data.current_password)
            ? data.current_password.join(" ")
            : data.current_password;
    }

    if (data.new_password) {
        return Array.isArray(data.new_password)
            ? data.new_password.join(" ")
            : data.new_password;
    }

    if (data.role) {
        return Array.isArray(data.role) ? data.role.join(" ") : data.role;
    }

    if (data.email) {
        return Array.isArray(data.email) ? data.email.join(" ") : data.email;
    }

    if (data.error) {
        return data.error;
    }

    return "Не удалось выполнить запрос";
}

function Employees() {
    const [currentUser, setCurrentUser] = useState(null);
    const [users, setUsers] = useState([]);

    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);

    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    const [form, setForm] = useState({
        username: "",
        password: "",
        passwordRepeat: "",
        first_name: "",
        last_name: "",
        email: "",
        role: "measurer",
    });

    const [deleteUserId, setDeleteUserId] = useState(null);
    const [deleteConfirmText, setDeleteConfirmText] = useState("");
    const [deleting, setDeleting] = useState(false);

    const [editUserId, setEditUserId] = useState(null);
    const [editForm, setEditForm] = useState({
        first_name: "",
        last_name: "",
        email: "",
        role: "measurer",
        new_password: "",
        current_password: "",
    });
    const [updating, setUpdating] = useState(false);

    const canManageEmployees = Boolean(
        currentUser?.is_superuser || currentUser?.role === "executive_director"
    );

    const editingUser = users.find((user) => user.id === editUserId) || null;

    const handleChange = (event) => {
        const {name, value} = event.target;

        setForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const loadPageData = async () => {
        try {
            setLoading(true);
            setErrorMessage("");

            const userResponse = await api.get("/cars/get-user/");
            const user = userResponse.data;

            setCurrentUser(user);

            const userCanManageEmployees = Boolean(
                user.is_superuser || user.role === "executive_director"
            );

            if (!userCanManageEmployees) {
                setUsers([]);
                return;
            }

            const usersResponse = await api.get("/cars/get-all-users/");
            setUsers(Array.isArray(usersResponse.data) ? usersResponse.data : []);
        } catch (error) {
            console.error("Ошибка загрузки сотрудников:", error);
            setErrorMessage(getErrorText(error));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPageData();
    }, []);

    const handleCreateUser = async (event) => {
        event.preventDefault();

        setErrorMessage("");
        setSuccessMessage("");

        const username = form.username.trim();
        const password = form.password;
        const passwordRepeat = form.passwordRepeat;

        if (!username) {
            setErrorMessage("Введите логин сотрудника");
            return;
        }

        if (!password) {
            setErrorMessage("Введите пароль сотрудника");
            return;
        }

        if (password !== passwordRepeat) {
            setErrorMessage("Пароли не совпадают");
            return;
        }

        try {
            setCreating(true);

            await api.post("/cars/users/create/", {
                username,
                password,
                first_name: form.first_name.trim(),
                last_name: form.last_name.trim(),
                email: form.email.trim(),
                role: form.role,
            });

            setForm({
                username: "",
                password: "",
                passwordRepeat: "",
                first_name: "",
                last_name: "",
                email: "",
                role: "measurer",
            });

            setSuccessMessage("Сотрудник успешно создан");

            const usersResponse = await api.get("/cars/get-all-users/");
            setUsers(Array.isArray(usersResponse.data) ? usersResponse.data : []);
        } catch (error) {
            console.error("Ошибка создания сотрудника:", error);
            setErrorMessage(getErrorText(error));
        } finally {
            setCreating(false);
        }
    };

    const startDeleteUser = (userId) => {
        setDeleteUserId(userId);
        setDeleteConfirmText("");
        setEditUserId(null);
        setErrorMessage("");
        setSuccessMessage("");
    };

    const cancelDeleteUser = () => {
        setDeleteUserId(null);
        setDeleteConfirmText("");
    };

    const handleDeleteUser = async (user) => {
        setErrorMessage("");
        setSuccessMessage("");

        if (deleteConfirmText.trim().toLowerCase() !== "удалить") {
            setErrorMessage('Для удаления нужно ввести слово "Удалить".');
            return;
        }

        try {
            setDeleting(true);

            await api.delete(`/cars/users/${user.id}/delete/`, {
                data: {
                    confirm_text: deleteConfirmText,
                },
            });

            setUsers((prev) => prev.filter((item) => item.id !== user.id));
            setDeleteUserId(null);
            setDeleteConfirmText("");
            setSuccessMessage(`Пользователь ${user.username} удалён`);
        } catch (error) {
            console.error("Ошибка удаления сотрудника:", error);
            setErrorMessage(getErrorText(error));
        } finally {
            setDeleting(false);
        }
    };

    const startEditUser = (user) => {
        setEditUserId(user.id);
        setDeleteUserId(null);
        setDeleteConfirmText("");

        setErrorMessage("");
        setSuccessMessage("");

        setEditForm({
            first_name: user.first_name || "",
            last_name: user.last_name || "",
            email: user.email || "",
            role: user.role || "measurer",
            new_password: "",
            current_password: "",
        });
    };

    const cancelEditUser = () => {
        setEditUserId(null);
        setEditForm({
            first_name: "",
            last_name: "",
            email: "",
            role: "measurer",
            new_password: "",
            current_password: "",
        });
    };

    const handleEditChange = (event) => {
        const {name, value} = event.target;

        setEditForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleUpdateUser = async (user) => {
        setErrorMessage("");
        setSuccessMessage("");

        if (!editForm.current_password.trim()) {
            setErrorMessage("Введите текущий пароль исполнительного директора");
            return;
        }

        try {
            setUpdating(true);

            const response = await api.patch(`/cars/users/${user.id}/update/`, {
                first_name: editForm.first_name.trim(),
                last_name: editForm.last_name.trim(),
                email: editForm.email.trim(),
                role: editForm.role,
                new_password: editForm.new_password,
                current_password: editForm.current_password,
            });

            setUsers((prev) =>
                prev.map((item) => (item.id === user.id ? response.data : item))
            );

            setEditUserId(null);
            setEditForm({
                first_name: "",
                last_name: "",
                email: "",
                role: "measurer",
                new_password: "",
                current_password: "",
            });

            setSuccessMessage(`Пользователь ${user.username} изменён`);
        } catch (error) {
            console.error("Ошибка изменения сотрудника:", error);
            setErrorMessage(getErrorText(error));
        } finally {
            setUpdating(false);
        }
    };

    return (
        <>
            <AppHeader/>

            <Box sx={pageSx}>
                <Paper sx={pageInnerSx}>
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
                                Сотрудники
                            </Typography>

                            <Typography
                                variant="body1"
                                sx={{
                                    color: "text.secondary",
                                }}
                            >
                                Создание и управление аккаунтами сотрудников для работы с протоколами.
                            </Typography>
                        </Box>

                        {currentUser && (
                            <Chip
                                label={`Текущий пользователь: ${currentUser.username}`}
                                sx={{
                                    borderRadius: 0,
                                    bgcolor: canManageEmployees ? "black" : "white",
                                    color: canManageEmployees ? "white" : "black",
                                    border: "1px solid black",
                                    fontWeight: 800,
                                }}
                            />
                        )}
                    </Box>

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
                    ) : !canManageEmployees ? (
                        <Paper
                            sx={{
                                ...cardSx,
                                textAlign: "center",
                                p: 4,
                            }}
                        >
                            <Typography
                                variant="h5"
                                sx={{
                                    fontWeight: 800,
                                    mb: 1,
                                }}
                            >
                                Доступ запрещён
                            </Typography>

                            <Typography variant="body1" sx={{color: "text.secondary"}}>
                                Создавать и изменять сотрудников может только исполнительный директор.
                            </Typography>
                        </Paper>
                    ) : (
                        <>
                            {successMessage && (
                                <Alert
                                    severity="success"
                                    sx={{
                                        mb: 2,
                                        borderRadius: 0,
                                    }}
                                >
                                    {successMessage}
                                </Alert>
                            )}

                            {errorMessage && (
                                <Alert
                                    severity="error"
                                    sx={{
                                        mb: 2,
                                        borderRadius: 0,
                                    }}
                                >
                                    {errorMessage}
                                </Alert>
                            )}

                            <Box sx={{display: "grid", gap: 2.5}}>
                                <Paper
                                    component="form"
                                    onSubmit={handleCreateUser}
                                    sx={cardSx}
                                >
                                    <Typography
                                        variant="h5"
                                        sx={{
                                            fontWeight: 800,
                                            mb: 2,
                                        }}
                                    >
                                        Новый сотрудник
                                    </Typography>

                                    <Grid container spacing={2} alignItems="center">
                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                fullWidth
                                                required
                                                label="Логин"
                                                name="username"
                                                value={form.username}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                fullWidth
                                                required
                                                label="Пароль"
                                                name="password"
                                                type="password"
                                                value={form.password}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                fullWidth
                                                required
                                                label="Повторите пароль"
                                                name="passwordRepeat"
                                                type="password"
                                                value={form.passwordRepeat}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                fullWidth
                                                label="Имя"
                                                name="first_name"
                                                value={form.first_name}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                fullWidth
                                                label="Фамилия"
                                                name="last_name"
                                                value={form.last_name}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                fullWidth
                                                label="Email"
                                                name="email"
                                                type="email"
                                                value={form.email}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <TextField
                                                select
                                                fullWidth
                                                required
                                                label="Роль"
                                                name="role"
                                                value={form.role}
                                                onChange={handleChange}
                                                sx={textFieldSx}
                                                disabled={creating}
                                            >
                                                {USER_ROLES.map((role) => (
                                                    <MenuItem key={role.value} value={role.value}>
                                                        {role.label}
                                                    </MenuItem>
                                                ))}
                                            </TextField>
                                        </Grid>

                                        <Grid item xs={12} sm={6} md={2}>
                                            <Button
                                                type="submit"
                                                fullWidth
                                                variant="contained"
                                                disabled={creating}
                                                sx={{
                                                    ...blackButtonSx,
                                                    minHeight: 56,
                                                }}
                                            >
                                                {creating ? "Создание..." : "Создать сотрудника"}
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </Paper>

                                <Paper sx={cardSx}>
                                    <Typography
                                        variant="h5"
                                        sx={{
                                            fontWeight: 800,
                                            mb: 2,
                                        }}
                                    >
                                        Список пользователей
                                    </Typography>

                                    {users.length === 0 ? (
                                        <Typography
                                            variant="body2"
                                            sx={{color: "text.secondary"}}
                                        >
                                            Пользователи не найдены.
                                        </Typography>
                                    ) : (
                                        <Box
                                            sx={{
                                                display: "grid",
                                                gridTemplateColumns: {
                                                    xs: "1fr",
                                                    sm: "repeat(2, minmax(0, 1fr))",
                                                    md: "repeat(3, minmax(0, 1fr))",
                                                    lg: "repeat(5, minmax(0, 1fr))",
                                                },
                                                gap: 1.2,
                                                alignItems: "stretch",
                                            }}
                                        >
                                            {users.map((user) => (
                                                <Paper key={user.id} sx={employeeCardSx}>
                                                    <Box
                                                        sx={{
                                                            display: "flex",
                                                            justifyContent: "space-between",
                                                            alignItems: "flex-start",
                                                            gap: 1,
                                                            flexWrap: "wrap",
                                                        }}
                                                    >
                                                        <Box>
                                                            <Typography
                                                                variant="subtitle1"
                                                                sx={{
                                                                    fontWeight: 800,
                                                                    color: "black",
                                                                    wordBreak: "break-word",
                                                                    lineHeight: 1.2,
                                                                }}
                                                            >
                                                                {user.username}
                                                            </Typography>

                                                            <Typography
                                                                variant="body2"
                                                                sx={{color: "text.secondary"}}
                                                            >
                                                                {[user.last_name, user.first_name]
                                                                    .filter(Boolean)
                                                                    .join(" ") || "ФИО не указано"}
                                                            </Typography>

                                                            {user.email && (
                                                                <Typography
                                                                    variant="body2"
                                                                    sx={{
                                                                        color: "text.secondary",
                                                                        wordBreak: "break-word",
                                                                    }}
                                                                >
                                                                    {user.email}
                                                                </Typography>
                                                            )}
                                                        </Box>

                                                        <Box
                                                            sx={{
                                                                display: "flex",
                                                                gap: 1,
                                                                flexWrap: "wrap",
                                                            }}
                                                        >
                                                            {user.is_superuser && (
                                                                <Chip
                                                                    label="Суперпользователь"
                                                                    size="small"
                                                                    sx={commonSx.inversePill}
                                                                />
                                                            )}

                                                            {!user.is_active && (
                                                                <Chip
                                                                    label="Отключён"
                                                                    size="small"
                                                                    sx={{
                                                                        borderRadius: 0,
                                                                        bgcolor: "white",
                                                                        color: "black",
                                                                        border: "1px solid black",
                                                                        fontWeight: 700,
                                                                    }}
                                                                />
                                                            )}

                                                            {user.is_active && !user.is_superuser && (
                                                                <Chip
                                                                    label={user.role_label || "Без роли"}
                                                                    size="small"
                                                                    sx={{
                                                                        borderRadius: 0,
                                                                        bgcolor:
                                                                            user.role === "manager" || user.role === "executive_director"
                                                                                ? "black"
                                                                                : "white",
                                                                        color:
                                                                            user.role === "manager" || user.role === "executive_director"
                                                                                ? "white"
                                                                                : "black",
                                                                        border: "1px solid black",
                                                                        fontWeight: 700,
                                                                    }}
                                                                />
                                                            )}
                                                        </Box>
                                                    </Box>

                                                    <Divider sx={{my: 1}}/>

                                                    <Box
                                                        sx={{
                                                            display: "flex",
                                                            justifyContent: "space-between",
                                                            alignItems: "center",
                                                            gap: 1,
                                                            flexWrap: "wrap",
                                                        }}
                                                    >
                                                        <Typography
                                                            variant="caption"
                                                            sx={{color: "text.secondary"}}
                                                        >
                                                            ID: {user.id}
                                                        </Typography>

                                                        {!user.is_superuser && (
                                                            <Box
                                                                sx={{
                                                                    display: "flex",
                                                                    gap: 1,
                                                                    flexWrap: "wrap",
                                                                }}
                                                            >
                                                                <Button
                                                                    variant="outlined"
                                                                    size="small"
                                                                    onClick={() => startEditUser(user)}
                                                                    disabled={updating || deleting}
                                                                    sx={outlineButtonSx}
                                                                >
                                                                    Изменить
                                                                </Button>

                                                                {user.id !== currentUser?.id && (
                                                                    <Button
                                                                        variant="outlined"
                                                                        size="small"
                                                                        onClick={() => startDeleteUser(user.id)}
                                                                        disabled={deleting || updating}
                                                                        sx={outlineButtonSx}
                                                                    >
                                                                        Удалить
                                                                    </Button>
                                                                )}
                                                            </Box>
                                                        )}
                                                    </Box>

                                                    {deleteUserId === user.id && (
                                                        <Box
                                                            sx={{
                                                                mt: 2,
                                                                p: 1.5,
                                                                border: "2px solid black",
                                                                bgcolor: "#f2f2f2",
                                                            }}
                                                        >
                                                            <Typography
                                                                variant="body2"
                                                                sx={{
                                                                    fontWeight: 800,
                                                                    mb: 1,
                                                                    color: "black",
                                                                }}
                                                            >
                                                                Для удаления пользователя {user.username} введите
                                                                слово “Удалить”.
                                                            </Typography>

                                                            <TextField
                                                                fullWidth
                                                                size="small"
                                                                value={deleteConfirmText}
                                                                onChange={(event) =>
                                                                    setDeleteConfirmText(event.target.value)
                                                                }
                                                                placeholder="Удалить"
                                                                sx={{
                                                                    mb: 1.5,
                                                                    bgcolor: "white",
                                                                    "& .MuiOutlinedInput-root": {
                                                                        borderRadius: 0,
                                                                    },
                                                                }}
                                                                disabled={deleting}
                                                            />

                                                            <Box
                                                                sx={{
                                                                    display: "flex",
                                                                    gap: 1,
                                                                    flexWrap: "wrap",
                                                                }}
                                                            >
                                                                <Button
                                                                    variant="contained"
                                                                    onClick={() => handleDeleteUser(user)}
                                                                    disabled={
                                                                        deleting ||
                                                                        deleteConfirmText.trim().toLowerCase() !==
                                                                        "удалить"
                                                                    }
                                                                    sx={blackButtonSx}
                                                                >
                                                                    {deleting
                                                                        ? "Удаление..."
                                                                        : "Подтвердить удаление"}
                                                                </Button>

                                                                <Button
                                                                    variant="outlined"
                                                                    onClick={cancelDeleteUser}
                                                                    disabled={deleting}
                                                                    sx={outlineButtonSx}
                                                                >
                                                                    Отмена
                                                                </Button>
                                                            </Box>
                                                        </Box>
                                                    )}
                                                </Paper>
                                            ))}
                                        </Box>
                                    )}
                                </Paper>
                            </Box>
                        </>
                    )}
                </Paper>
            </Box>

            <Dialog
                open={Boolean(editingUser)}
                onClose={updating ? undefined : cancelEditUser}
                maxWidth="sm"
                fullWidth
                BackdropProps={{
                    sx: {
                        bgcolor: "rgba(0, 0, 0, 0.35)",
                        backdropFilter: "blur(4px)",
                    },
                }}
                PaperProps={{
                    sx: modalPaperSx,
                }}
            >
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        gap: 2,
                        borderBottom: "2px solid black",
                        px: 2.5,
                        py: 2,
                    }}
                >
                    <Box>
                        <Typography
                            variant="h5"
                            sx={{
                                fontWeight: 800,
                                color: "black",
                                mb: 0.5,
                            }}
                        >
                            Изменение сотрудника
                        </Typography>

                        <Typography
                            variant="body2"
                            sx={{
                                color: "text.secondary",
                            }}
                        >
                            {editingUser
                                ? `Пользователь: ${editingUser.username}`
                                : "Пользователь не выбран"}
                        </Typography>
                    </Box>

                    <IconButton
                        onClick={cancelEditUser}
                        disabled={updating}
                        sx={{
                            color: "black",
                            borderRadius: 0,
                            border: "1px solid black",
                            width: 36,
                            height: 36,
                            fontWeight: 800,
                            "&:hover": {
                                bgcolor: "#eeeeee",
                            },
                        }}
                    >
                        ×
                    </IconButton>
                </Box>

                <DialogContent
                    sx={{
                        p: 2.5,
                    }}
                >
                    <Box
                        sx={{
                            display: "grid",
                            gap: 1.5,
                        }}
                    >
                        <TextField
                            fullWidth
                            label="Имя"
                            name="first_name"
                            value={editForm.first_name}
                            onChange={handleEditChange}
                            disabled={updating}
                            sx={textFieldSx}
                        />

                        <TextField
                            fullWidth
                            label="Фамилия"
                            name="last_name"
                            value={editForm.last_name}
                            onChange={handleEditChange}
                            disabled={updating}
                            sx={textFieldSx}
                        />

                        <TextField
                            fullWidth
                            label="Email"
                            name="email"
                            type="email"
                            value={editForm.email}
                            onChange={handleEditChange}
                            disabled={updating}
                            sx={textFieldSx}
                        />

                        <TextField
                            select
                            fullWidth
                            required
                            label="Роль"
                            name="role"
                            value={editForm.role}
                            onChange={handleEditChange}
                            disabled={updating}
                            sx={textFieldSx}
                        >
                            {USER_ROLES.map((role) => (
                                <MenuItem key={role.value} value={role.value}>
                                    {role.label}
                                </MenuItem>
                            ))}
                        </TextField>

                        <TextField
                            fullWidth
                            label="Новый пароль сотрудника"
                            name="new_password"
                            type="password"
                            value={editForm.new_password}
                            onChange={handleEditChange}
                            disabled={updating}
                            placeholder="Оставьте пустым, если пароль менять не нужно"
                            sx={textFieldSx}
                        />

                        <TextField
                            fullWidth
                            required
                            label="Текущий пароль исполнительного директора"
                            name="current_password"
                            type="password"
                            value={editForm.current_password}
                            onChange={handleEditChange}
                            disabled={updating}
                            sx={textFieldSx}
                        />

                        <Box
                            sx={{
                                display: "flex",
                                justifyContent: "flex-end",
                                gap: 1,
                                flexWrap: "wrap",
                                mt: 1,
                            }}
                        >
                            <Button
                                variant="outlined"
                                onClick={cancelEditUser}
                                disabled={updating}
                                sx={outlineButtonSx}
                            >
                                Отмена
                            </Button>

                            <Button
                                variant="contained"
                                onClick={() => {
                                    if (editingUser) {
                                        handleUpdateUser(editingUser);
                                    }
                                }}
                                disabled={updating || !editForm.current_password.trim()}
                                sx={blackButtonSx}
                            >
                                {updating ? "Сохранение..." : "Сохранить изменения"}
                            </Button>
                        </Box>
                    </Box>
                </DialogContent>
            </Dialog>
        </>
    );
}

export default Employees;