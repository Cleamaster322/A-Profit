import api from "./api.jsx";

// Слоты фотофиксации: [{photo_type, title, description, group}] в порядке схемы.
export const getProtocolPhotoSlots = async () => {
    const response = await api.get("/cars/protocol-photo-slots/");
    return response.data;
};

export const getProtocolPhotos = async (protocolId) => {
    const response = await api.get(`/cars/protocols/${protocolId}/photos/`);
    return response.data;
};

// В слоте одно фото: загрузка заменяет предыдущее фото этого слота.
export const uploadProtocolPhoto = async (protocolId, file, photoType) => {
    const formData = new FormData();

    formData.append("photo_type", photoType);
    formData.append("file", file);

    const response = await api.post(
        `/cars/protocols/${protocolId}/photos/create/`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};

export const deleteProtocolPhoto = async (photoId) => {
    await api.delete(`/cars/protocol-photos/${photoId}/delete/`);
};

// Фото отдаются защищённым адресом с JWT, поэтому <img src> напрямую не подходит:
// грузим файл через api и показываем как blob-ссылку.
export const fetchProtocolPhotoBlob = async (fileUrl) => {
    const response = await api.get(fileUrl, { responseType: "blob" });
    return response.data;
};
