import {useEffect, useMemo, useState} from "react";
import {useNavigate} from "react-router-dom";

import AppHeader from "../Features/AppHeader/AppHeader.jsx";
import api from "../shared/api.jsx";
import {getApiErrorMessage} from "../shared/errorHandler.jsx";

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import {commonSx} from "../theme.js";

const pageSx = commonSx.page;
const panelSx = commonSx.panel;

function getProtocolTitle(protocol) {
    return `${protocol.brand_name || ""} ${protocol.commercial_name || ""}`.trim() || "Машина не указана";
}

function MeasurementDashboard() {
    const navigate = useNavigate();
    const [protocols, setProtocols] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadProtocols() {
            try {
                const response = await api.get("/cars/protocols/");
                setProtocols(response.data.results || []);
            } catch (requestError) {
                console.error(requestError);
                setError(getApiErrorMessage(requestError, "Не удалось загрузить ваши протоколы"));
            } finally {
                setLoading(false);
            }
        }

        loadProtocols();
    }, []);

    const visibleProtocols = useMemo(() => {
        const query = search.trim().toLowerCase();
        const filtered = protocols.filter((protocol) =>
            ["measurement", "operator"].includes(protocol.status)
        );

        if (!query) return filtered;

        return filtered.filter((protocol) => [
            protocol.protocol_number,
            protocol.brand_name,
            protocol.commercial_name,
            protocol.vin,
        ].some((value) => String(value || "").toLowerCase().includes(query)));
    }, [protocols, search]);

    return (
        <>
            <AppHeader />
            <Box sx={pageSx}>
                <Box sx={{maxWidth: 1400, mx: "auto", display: "grid", gap: 2}}>
                    <Box sx={{display: "flex", justifyContent: "space-between", gap: 2, alignItems: "center", flexWrap: "wrap"}}>
                        <Box>
                            <Typography variant="h4" sx={{fontWeight: 800}}>Рабочее место замерщика</Typography>
                            <Typography sx={{color: "text.secondary", mt: 0.5}}>Создавайте замеры и отслеживайте переданные оператору протоколы.</Typography>
                        </Box>
                        <Button variant="contained" onClick={() => navigate("/home")} sx={commonSx.primaryButton}>
                            Новая машина
                        </Button>
                    </Box>

                    {error && <Alert severity="error">{error}</Alert>}

                    <Paper sx={panelSx}>
                        <Typography variant="h5" sx={{fontWeight: 800, mb: 1.5}}>Мои протоколы</Typography>
                        <TextField fullWidth size="small" label="Поиск по марке, модели, номеру или VIN" value={search} onChange={(event) => setSearch(event.target.value)} sx={{...commonSx.field, mb: 2}} />

                        {loading && <Typography>Загрузка...</Typography>}
                        {!loading && visibleProtocols.length === 0 && <Typography sx={{color: "text.secondary"}}>Протоколов пока нет.</Typography>}

                        <Box sx={{display: "grid", gap: 1}}>
                            {visibleProtocols.map((protocol) => {
                                const isDraft = protocol.status === "measurement";
                                return (
                                    <Box key={protocol.id} sx={{border: "1px solid #999", p: 1.5, display: "flex", justifyContent: "space-between", alignItems: "center", gap: 2, flexWrap: "wrap"}}>
                                        <Box>
                                            <Typography sx={{fontWeight: 800}}>{getProtocolTitle(protocol)}</Typography>
                                            <Typography variant="body2" sx={{color: "text.secondary", mt: 0.3}}>Протокол № {protocol.protocol_number || protocol.id}</Typography>
                                        </Box>
                                        <Box sx={{display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap"}}>
                                            <Chip label={isDraft ? "Незавершённый замер" : "Передан оператору"} sx={{...commonSx.pill, bgcolor: isDraft ? "#fff8e1" : commonSx.pill.bgcolor}} />
                                            <Button variant="outlined" onClick={() => navigate(isDraft ? `/protocols/${protocol.id}/measurement` : `/measurement/${protocol.id}`)} sx={commonSx.secondaryButton}>
                                                {isDraft ? "Продолжить замер" : "Открыть просмотр"}
                                            </Button>
                                        </Box>
                                    </Box>
                                );
                            })}
                        </Box>
                    </Paper>
                </Box>
            </Box>
        </>
    );
}

export default MeasurementDashboard;
