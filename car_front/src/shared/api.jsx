import axios from "axios";
import {baseURL} from "./config.jsx";

async function getErrorData(error) {
    const data = error.response?.data;

    if (data instanceof Blob && data.type?.includes("application/json")) {
        try {
            const text = await data.text();
            return JSON.parse(text);
        } catch {
            return data;
        }
    }

    return data;
}

class ApiClient {
    constructor(baseUrl) {
        this.client = axios.create({
            baseURL: baseUrl,
            withCredentials: true,
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        this.csrfClient = axios.create({
            baseURL: baseUrl,
            withCredentials: true,
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
        });

        const token = localStorage.getItem("accessToken");
        if (token) {
            this.client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        }

        this.isRefreshing = false;
        this.refreshPromise = null;
        this.failedRequests = [];

        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                const originalRequest = error.config;

                if (!error.response) {
                    return Promise.reject(error);
                }

                const errorData = await getErrorData(error);

                const isTokenError =
                    (error.response.status === 401 || error.response.status === 403) &&
                    errorData?.code === "token_not_valid";

                if (isTokenError && !originalRequest._retry) {
                    if (this.isRefreshing) {
                        return new Promise((resolve, reject) => {
                            this.failedRequests.push({resolve, reject});
                        })
                            .then((newAccessToken) => {
                                originalRequest.headers = originalRequest.headers || {};
                                originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
                                return this.client(originalRequest);
                            })
                            .catch((err) => Promise.reject(err));
                    }

                    originalRequest._retry = true;
                    this.isRefreshing = true;

                    const refreshToken = localStorage.getItem("refreshToken");

                    if (!refreshToken) {
                        this.isRefreshing = false;
                        this.logout();
                        return Promise.reject(error);
                    }

                    return this.refreshAccessToken()
                        .then((newAccessToken) => {
                            originalRequest.headers = originalRequest.headers || {};
                            originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;

                            this.failedRequests.forEach((request) => {
                                request.resolve(newAccessToken);
                            });
                            this.failedRequests = [];

                            return this.client(originalRequest);
                        })
                        .catch((refreshError) => {
                            this.failedRequests.forEach((request) => {
                                request.reject(refreshError);
                            });
                            this.failedRequests = [];

                            this.logout();
                            return Promise.reject(refreshError);
                        })
                        .finally(() => {
                            this.isRefreshing = false;
                        });
                }

                return Promise.reject(error);
            }
        );

        this.setCsrfToken();
    }

    async refreshAccessToken() {
        if (this.refreshPromise) {
            return this.refreshPromise;
        }

        const refreshToken = localStorage.getItem("refreshToken");

        if (!refreshToken) {
            this.logout();
            throw new Error("Refresh token is missing");
        }

        this.refreshPromise = axios
            .post(`${baseURL}/cars/token/refresh/`, {refresh: refreshToken})
            .then((response) => {
                const newAccessToken = response.data.access;
                const newRefreshToken = response.data.refresh;

                localStorage.setItem("accessToken", newAccessToken);

                if (newRefreshToken) {
                    localStorage.setItem("refreshToken", newRefreshToken);
                }

                this.client.defaults.headers.common["Authorization"] = `Bearer ${newAccessToken}`;
                window.dispatchEvent(new CustomEvent("auth:token-refreshed"));

                return newAccessToken;
            })
            .finally(() => {
                this.refreshPromise = null;
            });

        return this.refreshPromise;
    }

    async logout() {
        const refreshToken = localStorage.getItem("refreshToken");

        if (refreshToken) {
            try {
                await axios.post(`${baseURL}/cars/logout/`, {refresh: refreshToken});
            } catch (error) {
                console.warn("Не удалось отозвать refresh-токен:", error);
            }
        }

        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        delete this.client.defaults.headers.common["Authorization"];
        delete this.client.defaults.headers.common["X-CSRFToken"];

        if (window.location.pathname !== "/") {
            window.location.assign("/");
        }
    }

    async setCsrfToken() {
        try {
            const response = await this.csrfClient.get("/cars/get_csrf_token/");
            if (response.data.csrf_token) {
                this.client.defaults.headers.common["X-CSRFToken"] = response.data.csrf_token;
            }
        } catch (error) {
            console.log("Failed on get csrf", error);
        }
    }

    async setTokenAuth() {
        try {
            const token = localStorage.getItem("accessToken");
            if (token) {
                this.client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
            } else {
                delete this.client.defaults.headers.common["Authorization"];
            }
        } catch (error) {
            console.error("Error on auth set token", error);
        }
    }

    async get(url, config = {}) {
        return this.client.get(url, config);
    }

    async post(url, data = {}, config = {}) {
        if (!this.client.defaults.headers.common["X-CSRFToken"]) {
            await this.setCsrfToken();
        }
        return this.client.post(url, data, config);
    }

    async patch(url, data = {}, config = {}) {
        if (!this.client.defaults.headers.common["X-CSRFToken"]) {
            await this.setCsrfToken();
        }
        return this.client.patch(url, data, config);
    }

    async put(url, data = {}, config = {}) {
        if (!this.client.defaults.headers.common["X-CSRFToken"]) {
            await this.setCsrfToken();
        }
        return this.client.put(url, data, config);
    }

    async delete(url, config = {}) {
        if (!this.client.defaults.headers.common["X-CSRFToken"]) {
            await this.setCsrfToken();
        }
        return this.client.delete(url, config);
    }

    generateProtocolDocx(protocolId) {
        return this.client.post(
            `/cars/protocols/${protocolId}/generate-docx/`,
            {},
            {
                responseType: "blob",
            }
        );
    }

    previewProtocolPdf(protocolId) {
        return this.client.post(
            `/cars/protocols/${protocolId}/preview-pdf/`,
            {},
            {
                responseType: "blob",
            }
        );
    }

    approveProtocol(protocolId) {
        return this.post(`/cars/protocols/${protocolId}/approve/`);
    }

    cancelProtocol(protocolId, revisionComment = "") {
        return this.post(`/cars/protocols/${protocolId}/cancel/`, {
            revision_comment: revisionComment,
        });
    }

    managerReleaseProtocolLock(protocolId) {
        return this.post(`/cars/protocols/${protocolId}/manager-release-lock/`);
    }
}

const api = new ApiClient(baseURL);

export default api;