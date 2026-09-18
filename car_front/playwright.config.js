import {defineConfig, devices} from "@playwright/test";

export default defineConfig({
    testDir: "./tests/e2e",
    timeout: 30_000,
    expect: {
        timeout: 5_000,
    },
    use: {
        baseURL: "http://127.0.0.1:3000",
        browserName: "chromium",
        channel: "chrome",
        headless: true,
        ...devices["Desktop Chrome"],
    },
    webServer: {
        command: "npm run dev -- --host 127.0.0.1",
        url: "http://127.0.0.1:3000",
        reuseExistingServer: true,
        timeout: 120_000,
    },
});
