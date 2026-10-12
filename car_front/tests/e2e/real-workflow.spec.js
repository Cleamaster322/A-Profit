import {expect, test} from "@playwright/test";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";

const fixture = JSON.parse(
    readFileSync(resolve(process.cwd(), "test-results", "e2e-fixture.json"), "utf8")
);
const password = fixture.E2E_PASSWORD;

async function login(page, username) {
    await page.goto("/");
    await page.getByLabel(/логин/i).fill(username);
    await page.getByLabel(/пароль/i).fill(password);
    await page.getByRole("button", {name: /войти/i}).click();
    await expect.poll(
        () => page.evaluate(() => localStorage.getItem("accessToken"))
    ).toBeTruthy();
}

async function logout(page) {
    await page.getByRole("button", {name: "Выйти"}).click();
    await expect(page).toHaveURL(/\/$/);
}

test("real users can complete the protocol workflow", async ({page}) => {
    const protocolId = fixture.E2E_PROTOCOL_ID;

    await login(page, "e2e_measurer");
    await page.goto(`/protocols/${protocolId}/measurement`);
    await expect(page.getByRole("heading", {name: "Ввод данных замерщика"})).toBeVisible();

    page.once("dialog", (dialog) => dialog.accept());
    await page.getByRole("button", {name: "Передать оператору"}).first().click();
    await expect(page).toHaveURL(/\/home$/);
    await logout(page);

    await login(page, "e2e_operator");
    await page.goto(`/protocols/${protocolId}/inspection`);
    await expect(page.getByRole("heading", {name: "Осмотр автомобиля"})).toBeVisible();

    const submitForReviewButton = page.getByRole("button", {name: "Отправить на проверку"}).first();
    await expect(submitForReviewButton).toBeEnabled();
    page.once("dialog", (dialog) => dialog.accept());
    await submitForReviewButton.click();
    await expect(page).toHaveURL(/\/protocols$/);
    await logout(page);

    await login(page, "e2e_manager");
    await page.goto("/protocols/completed");
    await expect(page.getByRole("button", {name: "Утвердить"})).toBeVisible();

    page.once("dialog", (dialog) => dialog.accept());
    await page.getByRole("button", {name: "Утвердить"}).click();
    await expect(page.getByText("Нет завершённых протоколов")).toBeVisible();
});

test("a second user cannot open a locked protocol", async ({browser}) => {
    const measurerContext = await browser.newContext();
    const operatorContext = await browser.newContext();
    const measurerPage = await measurerContext.newPage();
    const operatorPage = await operatorContext.newPage();
    const protocolId = fixture.E2E_LOCK_PROTOCOL_ID;

    await login(measurerPage, "e2e_measurer");
    await measurerPage.goto(`/protocols/${protocolId}/measurement`);
    await expect(measurerPage.getByRole("heading", {name: "Ввод данных замерщика"})).toBeVisible();

    await login(operatorPage, "e2e_operator");
    await operatorPage.goto(`/protocols/${protocolId}/inspection`);
    await expect(
        operatorPage.getByText(/Протокол уже редактируется пользователем/i)
    ).toBeVisible();

    await measurerContext.close();
    await operatorContext.close();
});

test("changing generation clears stale configuration state", async ({page}) => {
    const protocolId = fixture.E2E_SELECTION_PROTOCOL_ID;

    await login(page, "e2e_measurer");
    await page.goto(`/protocols/${protocolId}/vehicle-selection`);
    await expect(page.getByRole("heading", {name: "Выбор автомобиля"})).toBeVisible();

    await page.getByText("E2E-Generation A", {exact: true}).click();
    await expect(page.getByRole("heading", {name: "Конфигурация"})).toBeVisible();
    await expect(page.getByText("E2E-Configuration A", {exact: true})).toBeVisible();

    await page.getByText("E2E-Generation B", {exact: true}).click();
    await expect(page.getByText("E2E-Configuration B", {exact: true})).toBeVisible();
    await expect(page.getByText("E2E-Configuration A", {exact: true})).toHaveCount(0);

    await page.getByText("E2E-Configuration B", {exact: true}).click();
    await page.getByRole("button", {name: "Сбросить фильтры"}).click();
    await expect(page.getByRole("button", {name: "Выберите конфигурацию"})).toBeVisible();
});
