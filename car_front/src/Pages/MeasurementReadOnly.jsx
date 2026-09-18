import {useEffect, useState} from "react";
import {useNavigate, useParams} from "react-router-dom";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";
import {getApiErrorMessage} from "../shared/errorHandler.jsx";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";

function valueOrDash(value) {
    return value === null || value === undefined || value === "" ? "—" : String(value);
}

function MeasurementReadOnly() {
    const {id} = useParams();
    const navigate = useNavigate();
    const [protocol, setProtocol] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        api.get(`/cars/protocols/${id}/full/`)
            .then((response) => setProtocol(response.data))
            .catch((requestError) => {
                console.error(requestError);
                setError(getApiErrorMessage(requestError, "Не удалось открыть протокол"));
            });
    }, [id]);

    if (error) {
        return <Alert severity="error" sx={{m: 3, borderRadius: 0}}>{error}</Alert>;
    }

    if (!protocol) {
        return <Typography sx={{p: 3}}>Загрузка...</Typography>;
    }

    const measurement = protocol.measurement || {};

    return (
        <>
            <AppHeader />
            <Box sx={{p: 3, bgcolor: "#f2f2f2", minHeight: "calc(100vh - 56px)"}}>
                <Box sx={{maxWidth: 1100, mx: "auto", display: "grid", gap: 2}}>
                    <Box sx={{display: "flex", justifyContent: "space-between", gap: 2, alignItems: "center", flexWrap: "wrap"}}>
                        <Box>
                            <Typography variant="h4" sx={{fontWeight: 800}}>Переданный замер</Typography>
                            <Typography sx={{color: "text.secondary", mt: 0.5}}>{protocol.brand_name} {protocol.commercial_name}</Typography>
                        </Box>
                        <Chip label="Передан оператору" sx={{borderRadius: 0, bgcolor: "black", color: "white", fontWeight: 800}} />
                    </Box>

                    <Paper sx={{border: "2px solid black", borderRadius: 0, boxShadow: "none", p: 2.5}}>
                        <Typography variant="h5" sx={{fontWeight: 800, mb: 2}}>Данные замера</Typography>
                        <Box sx={{display: "grid", gridTemplateColumns: {xs: "1fr", sm: "repeat(2, 1fr)"}, gap: 1.5}}>
                            {[
                                ["Марка", protocol.brand_name],
                                ["Модель", protocol.commercial_name],
                                ["VIN", protocol.vin],
                                ["Топливо", measurement.fuel_type],
                                ["Нагнетатель", protocol.supercharger],
                                ["Колёсная формула", measurement.wheel_formula],
                                ["Места", measurement.seats_count],
                                ["Пробег, км", measurement.mileage_km],
                                ["Передние шины", protocol.wheel_marking_front],
                                ["Задние шины", protocol.wheel_marking_rear],
                            ].map(([label, value]) => (
                                <Box key={label} sx={{borderBottom: "1px solid #ddd", py: 0.8}}>
                                    <Typography variant="caption" sx={{color: "text.secondary", display: "block"}}>{label}</Typography>
                                    <Typography sx={{fontWeight: 600}}>{valueOrDash(value)}</Typography>
                                </Box>
                            ))}
                        </Box>
                    </Paper>

                    <Box sx={{display: "flex", justifyContent: "flex-end"}}>
                        <button type="button" onClick={() => navigate("/measurement")} style={{padding: "10px 18px", background: "black", color: "white", border: "1px solid black", cursor: "pointer"}}>
                            Вернуться к моим протоколам
                        </button>
                    </Box>
                </Box>
            </Box>
        </>
    );
}

export default MeasurementReadOnly;
