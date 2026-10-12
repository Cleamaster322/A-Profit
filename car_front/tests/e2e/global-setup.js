import {execFileSync} from "node:child_process";
import {mkdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";

export default async function globalSetup() {
    const repoRoot = resolve(process.cwd(), "..");
    const mainDir = resolve(repoRoot, "main");
    const python = process.env.E2E_PYTHON || resolve(repoRoot, "venv", "Scripts", "python.exe");
    const output = execFileSync(
        python,
        ["manage.py", "e2e_fixture", "prepare"],
        {cwd: mainDir, encoding: "utf8"}
    );
    const values = Object.fromEntries(
        output
            .split(/\r?\n/)
            .filter((line) => line.startsWith("E2E_"))
            .map((line) => line.split("="))
    );

    const fixturePath = resolve(process.cwd(), "test-results", "e2e-fixture.json");
    mkdirSync(dirname(fixturePath), {recursive: true});
    writeFileSync(fixturePath, JSON.stringify(values), "utf8");
}
