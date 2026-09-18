import ReactDOM from "react-dom/client";
import "./index.css";
import {ThemeProvider} from "@mui/material/styles";

import appTheme from "./theme.js";
import App from "./App.jsx";
import CarSelection from "./Pages/CarSelection.jsx";
import CarInfo from "./Pages/CarInfo.jsx";
import Protocols from "./Pages/Protocols.jsx";
import CompletedProtocols from "./Pages/CompletedProtocols.jsx";
import ProtocolInspection from "./Pages/ProtocolInspection.jsx";
import Employees from "./Pages/Employees.jsx";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import ApprovedProtocols from "./Pages/ApprovedProtocols.jsx";
import ProtocolVehicleSelection from "./Pages/ProtocolVehicleSelection.jsx";
import MeasurementDashboard from "./Pages/MeasurementDashboard.jsx";
import MeasurementReadOnly from "./Pages/MeasurementReadOnly.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
    <ThemeProvider theme={appTheme}>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<App />} />
                <Route path="/home" element={<CarSelection />} />
                <Route path="/CarInfo" element={<CarInfo />} />
                <Route path="/protocols" element={<Protocols />} />
                <Route path="/protocols/completed" element={<CompletedProtocols />} />
                <Route path="/protocols/approved" element={<ApprovedProtocols />} />
                <Route path="/protocols/:id/inspection" element={<ProtocolInspection />} />
                <Route path="/protocols/:id/measurement" element={<ProtocolInspection measurementMode />} />
                <Route path="/protocols/:id/vehicle-selection" element={<ProtocolVehicleSelection />} />
                <Route path="/measurement" element={<MeasurementDashboard />} />
                <Route path="/measurement/:id" element={<MeasurementReadOnly />} />
                <Route path="/employees" element={<Employees />} />
            </Routes>
        </BrowserRouter>
    </ThemeProvider>
);