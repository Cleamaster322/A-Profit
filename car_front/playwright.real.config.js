import {defineConfig, devices} from "@playwright/test";

export default defineConfig({
    testDir: "./tests/e2e",
    testMatch: "real-workflow.spec.js",
    globalSetup: "./tests/e2e/global-setup.js",
    globalTeardown: "./tests/e2e/global-teardown.js",
    timeout: 60_000,
    expect: {timeout: 10_000},
    use: {
        baseURL: "http://127.0.0.1:3000",
        browserName: "chromium",
        channel: "chrome",
        headless: true,
        ...devices["Desktop Chrome"],
    },
    webServer: [
        {
            command: "cd /d ..\\main && ..\\venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000 --noreload",
            url: "http://127.0.0.1:8000/cars/get_csrf_token/",
            reuseExistingServer: true,
            timeout: 120_000,
        },
        {
            command: "npm run dev -- --host 127.0.0.1",
            url: "http://127.0.0.1:3000",
            reuseExistingServer: true,
            timeout: 120_000,
        },
    ],
});
