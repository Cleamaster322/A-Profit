import {execFileSync} from "node:child_process";
import {resolve} from "node:path";

export default async function globalTeardown() {
    const repoRoot = resolve(process.cwd(), "..");
    const mainDir = resolve(repoRoot, "main");
    const python = process.env.E2E_PYTHON || resolve(repoRoot, "venv", "Scripts", "python.exe");

    execFileSync(
        python,
        ["manage.py", "e2e_fixture", "cleanup"],
        {cwd: mainDir, stdio: "inherit"}
    );
}
