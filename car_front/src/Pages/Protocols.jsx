import {useEffect, useState} from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";
import api from "../shared/api.jsx";
import ProtocolList from "../Features/Protocols/ProtocolList.jsx";

export default function Protocols() {
    const [userRole, setUserRole] = useState(null);

    useEffect(() => {
        api.get("/cars/get-user/")
            .then((response) => {
                setUserRole(response.data?.role || null);
            })
            .catch(() => {
                setUserRole(null);
            });
    }, []);

    if (userRole === null) {
        return (
            <Box sx={{display: "flex", justifyContent: "center", alignItems: "center", minHeight: 200}}>
                <CircularProgress sx={{color: "black"}}/>
            </Box>
        );
    }

    const statuses = userRole === "operator"
        ? ["operator", "revision"]
        : ["measurement", "operator", "revision"];

    return (
        <ProtocolList
            key={userRole}
            title="Протоколы в работе"
            description={
                userRole === "operator"
                    ? "Протоколы, переданные на этап оператора, включая возвращённые на доработку."
                    : "Протоколы замерщиков и операторов, включая возвращённые на доработку."
            }
            statuses={statuses}
            emptyTitle={userRole === "operator" ? "Нет протоколов на этапе оператора" : "Нет протоколов в работе"}
            emptyDescription={
                userRole === "operator"
                    ? "Пока не передано ни одного протокола на проверку оператором."
                    : "Создайте новый протокол через выбор автомобиля."
            }
            showCreateButton={userRole !== "operator"}
        />
    );
}