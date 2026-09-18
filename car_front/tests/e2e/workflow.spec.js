import {expect, test} from "@playwright/test";

const user = {
    id: 1,
    username: "smoke-user",
    role: "measurer",
    is_superuser: false,
};

const measurementProtocol = {
    id: 1,
    protocol_number: "00001",
    status: "measurement",
    brand_name: "KIA",
    commercial_name: "RIO",
    vin: "TESTVIN",
};

async function mockApi(page, role = "measurer") {
    await page.route("**/cars/**", async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        const path = url.pathname;

        if (path.endsWith("/get_csrf_token/")) {
            await route.fulfill({json: {csrf_token: "smoke-csrf"}});
            return;
        }

        if (path.endsWith("/get-user/")) {
            await route.fulfill({json: {...user, role}});
            return;
        }

        if (path.endsWith("/protocols/") && request.method() === "GET") {
            const protocols = role === "operator"
                ? [{...measurementProtocol, status: "operator"}]
                : [measurementProtocol];
            await route.fulfill({json: {count: protocols.length, results: protocols}});
            return;
        }

        if (path.endsWith("/protocols/1/full/") && request.method() === "GET") {
            await route.fulfill({json: measurementProtocol});
            return;
        }

        if (path.endsWith("/start-editing/") && request.method() === "POST") {
            await route.fulfill({json: {...measurementProtocol, locked_by_id: 1}});
            return;
        }

        if (path.endsWith("/brands/") && request.method() === "GET") {
            await route.fulfill({json: {count: 0, results: []}});
            return;
        }

        await route.fulfill({json: {}});
    });
}

async function authenticate(page) {
    await page.addInitScript(() => {
        localStorage.setItem("accessToken", "smoke-access");
        localStorage.setItem("refreshToken", "smoke-refresh");
    });
}

test("login route renders the authentication form", async ({page}) => {
    await page.goto("/");

    await expect(page.getByRole("button", {name: /войти/i})).toBeVisible();
    await expect(page.getByLabel(/логин/i)).toBeVisible();
    await expect(page.getByLabel(/пароль/i)).toBeVisible();
});

test("main workflow routes render with mocked API", async ({page}) => {
    await authenticate(page);
    await mockApi(page);

    await page.goto("/measurement");
    await expect(page.getByRole("heading", {name: "Рабочее место замерщика"})).toBeVisible();

    await page.goto("/protocols");
    await expect(page.getByRole("heading", {name: "Протоколы в работе"})).toBeVisible();

    await page.goto("/protocols/completed");
    await expect(page.getByRole("heading", {name: "Завершённые протоколы"})).toBeVisible();

    await page.goto("/protocols/approved");
    await expect(page.getByRole("heading", {name: "Утверждённые протоколы"})).toBeVisible();
});

test("measurer can open a protocol measurement route from the dashboard", async ({page}) => {
    await authenticate(page);
    await mockApi(page);

    await page.goto("/measurement");
    await page.getByRole("button", {name: "Продолжить замер"}).click();

    await expect(page).toHaveURL(/\/protocols\/1\/measurement$/);
});

test("operator route renders operator protocol list", async ({page}) => {
    await authenticate(page);
    await mockApi(page, "operator");

    await page.goto("/protocols");

    await expect(page.getByRole("heading", {name: "Протоколы в работе"})).toBeVisible();
    await expect(page.getByText("№ 00001")).toBeVisible();
    await expect(page.getByText("У оператора")).toBeVisible();
});
