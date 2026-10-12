import api from "../shared/api.jsx";
import {useLocation} from "react-router-dom";
import {useEffect, useState} from "react";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";


function CarInfo() {
    const location = useLocation();
    const {selectedBrand, selectedModel, selectedGeneration, selectedConfiguration} = location.state || {};

    // Локальные стейты для редактируемых полей
    const [brandName, setBrandName] = useState("");
    const [modelName, setModelName] = useState("");
    const [generationName, setGenerationName] = useState("");
    const [generationDates, setGenerationDates] = useState(""); // например, "2000 - 2005"
    const [configurationName, setConfigurationName] = useState("");
    const [engineName, setEngineName] = useState("");

    // Данные CarData
    const [frontTires, setFrontTires] = useState("");
    const [rearTires, setRearTires] = useState("");
    const [engineCapacity, setEngineCapacity] = useState("");
    const [enginePowerHp, setEnginePowerHp] = useState("");
    const [enginePowerKw, setEnginePowerKw] = useState("");
    const [consumption, setConsumption] = useState("");
    const [fuelType, setFuelType] = useState("");
    const [transmission, setTransmission] = useState("");
    const [driveType, setDriveType] = useState("");
    const [seatsCount, setSeatsCount] = useState("");
    const [doorsCount, setDoorsCount] = useState("");
    const [clearance, setClearance] = useState("");
    const [trunkVolume, setTrunkVolume] = useState("");


    useEffect(() => {
        if (selectedBrand) setBrandName(selectedBrand.name || "");
        if (selectedModel) setModelName(selectedModel.name || "");
        if (selectedGeneration) {
            setGenerationName(selectedGeneration.name || "");
            setGenerationDates(`${selectedGeneration.date_start || ""} - ${selectedGeneration.date_end || ""}`);
        }
        if (selectedConfiguration) {
            setConfigurationName(selectedConfiguration.name || "");
            setEngineName(selectedConfiguration.engine_name || "");

            // Запрос данных CarData по configuration.id
            if (selectedConfiguration.id) {
                api.get(`/cars/car-data/${selectedConfiguration.id}`)
                    .then(({data}) => {
                        setFrontTires(data.front_tires || "");
                        setRearTires(data.rear_tires || "");
                        setEngineCapacity(data.engine_capacity?.toString() || "");
                        setEnginePowerHp(data.engine_power_hp?.toString() || "");
                        setEnginePowerKw(data.engine_power_kw?.toString() || "");
                        setConsumption(data.consumption?.toString() || "");
                        setFuelType(data.fuel_type || "");
                        setTransmission(data.transmission || "");
                        setDriveType(data.drive_type || "");
                        setSeatsCount(data.seats_count?.toString() || "");
                        setDoorsCount(data.doors_count?.toString() || "");
                        setClearance(data.clearance?.toString() || "");
                        setTrunkVolume(data.trunk_volume?.toString() || "");
                    })
                    .catch(err => {
                        console.error("Ошибка загрузки данных CarData:", err);
                        // Можно сбросить поля, если нужно
                    });
            }
        }
    }, [selectedBrand, selectedModel, selectedGeneration, selectedConfiguration]);

    if (!selectedBrand) {
        return <p>Нет данных о выбранной машине. Пожалуйста, выберите машину на предыдущей странице.</p>;
    }

    const handleCreate = async () => {
        const dataToCreate = {
            brand: brandName,
            model: modelName,
            generation: generationName,
            generation_period: generationDates,
            configuration: configurationName,
            engine_name: engineName,
            car_data: {
                front_tires: frontTires,
                rear_tires: rearTires,
                engine_capacity: engineCapacity,
                engine_power_hp: enginePowerHp,
                engine_power_kw: enginePowerKw,
                consumption: consumption,
                fuel_type: fuelType,
                transmission: transmission,
                drive_type: driveType,
                seats_count: seatsCount,
                doors_count: doorsCount,
                clearance: clearance,
                trunk_volume: trunkVolume,
            }
        };
        const userResponse = await api.get('cars/get-user/');
        const userID = userResponse.data.id;

        const dataToCreateProtocol = {
            car: selectedConfiguration.id,
            user: userID,
        }
        api.post('cars/create-word/', dataToCreate, {responseType: 'blob'})
            .then((response) => {
                // Создаем ссылку на скачивание
                const url = window.URL.createObjectURL(new Blob([response.data], {type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}));
                const link = document.createElement('a');
                link.href = url;
                // Имя файла, можно динамическое
                link.setAttribute('download', `${brandName}_${modelName}_car_info.docx`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);
                api.post('cars/protocol/create/', dataToCreateProtocol);

            })
            .catch(err => {
                console.error('Ошибка создания документа:', err);
            });
    };

    return (
        <Box sx={{maxWidth: 600, mx: "auto", mt: 4, display: "flex", flexDirection: "column", gap: 2}}>
            <h2>Редактируемая информация о машине</h2>

            {/* Базовые данные */}
            <TextField label="Бренд" value={brandName} onChange={e => setBrandName(e.target.value)} fullWidth/>
            <TextField label="Модель" value={modelName} onChange={e => setModelName(e.target.value)} fullWidth/>
            <TextField label="Поколение" value={generationName} onChange={e => setGenerationName(e.target.value)}
                       fullWidth/>
            <TextField
                label="Период поколения (начало - конец)"
                value={generationDates}
                onChange={e => setGenerationDates(e.target.value)}
                fullWidth
                placeholder="ГГГГ - ГГГГ"
            />
            <TextField label="Конфигурация" value={configurationName}
                       onChange={e => setConfigurationName(e.target.value)} fullWidth/>
            <TextField label="Название двигателя" value={engineName} onChange={e => setEngineName(e.target.value)}
                       fullWidth/>

            {/* Данные CarData */}
            <TextField label="Передние шины" value={frontTires} onChange={e => setFrontTires(e.target.value)}
                       fullWidth/>
            <TextField label="Задние шины" value={rearTires} onChange={e => setRearTires(e.target.value)} fullWidth/>
            <TextField label="Объем двигателя" value={engineCapacity} onChange={e => setEngineCapacity(e.target.value)}
                       fullWidth/>
            <TextField label="Мощность двигателя (л.с.)" value={enginePowerHp}
                       onChange={e => setEnginePowerHp(e.target.value)} fullWidth/>
            <TextField label="Мощность двигателя (кВт)" value={enginePowerKw}
                       onChange={e => setEnginePowerKw(e.target.value)} fullWidth/>
            <TextField label="Расход топлива" value={consumption} onChange={e => setConsumption(e.target.value)}
                       fullWidth/>
            <TextField label="Тип топлива" value={fuelType} onChange={e => setFuelType(e.target.value)} fullWidth/>
            <TextField label="Трансмиссия" value={transmission} onChange={e => setTransmission(e.target.value)}
                       fullWidth/>
            <TextField label="Тип привода" value={driveType} onChange={e => setDriveType(e.target.value)} fullWidth/>
            <TextField label="Количество мест" value={seatsCount} onChange={e => setSeatsCount(e.target.value)}
                       fullWidth/>
            <TextField label="Количество дверей" value={doorsCount} onChange={e => setDoorsCount(e.target.value)}
                       fullWidth/>
            <TextField label="Клиренс" value={clearance} onChange={e => setClearance(e.target.value)} fullWidth/>
            <TextField label="Объем багажника" value={trunkVolume} onChange={e => setTrunkVolume(e.target.value)}
                       fullWidth/>

            <Button variant="contained" color="primary" onClick={handleCreate} sx={{mt: 3}}>
                Создать
            </Button>
        </Box>
    );
}

export default CarInfo;
