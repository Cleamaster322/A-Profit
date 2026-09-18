import ProtocolList from "../Features/Protocols/ProtocolList.jsx";

export default function Protocols() {
    return (
        <ProtocolList
            title="Протоколы в работе"
            description="Протоколы замерщиков и операторов, включая возвращённые на доработку."
            statuses={["measurement", "operator", "revision"]}
            emptyTitle="Нет протоколов в работе"
            emptyDescription="Создайте новый протокол через выбор автомобиля."
            showCreateButton={true}
        />
    );
}