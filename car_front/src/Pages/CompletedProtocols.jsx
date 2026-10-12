import ProtocolList from "../Features/Protocols/ProtocolList.jsx";

export default function CompletedProtocols() {
    return (
        <ProtocolList
            title="Завершённые протоколы"
            description="Протоколы, заполнение которых завершено."
            statuses={["review"]}
            emptyTitle="Нет завершённых протоколов"
            emptyDescription="После завершения протокола он появится в этом разделе."
            showCreateButton={false}
        />
    );
}