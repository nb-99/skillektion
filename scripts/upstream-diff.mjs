import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = path.join(root, "scratch", "upstream-diffs");
const manifest = JSON.parse(
  await readFile(path.join(root, "sources.json"), "utf8"),
);
const sources = Object.entries(manifest.skills).filter(
  ([, source]) => source.mode === "mirror" || source.mode === "adapted",
);
const temporaryRoot = await mkdtemp(
  path.join(tmpdir(), "skillektion-upstream-diff-"),
);

await mkdir(outputDir, { recursive: true });
for (const [index, [name]] of sources.entries()) {
  await rm(path.join(outputDir, filename(index, name)), { force: true });
}

let changed = 0;
try {
  for (const [index, [name, source]] of sources.entries()) {
    const checkout = path.join(temporaryRoot, `${name}-checkout`);
    run("git", [
      "clone",
      "--quiet",
      "--filter=blob:none",
      "--no-checkout",
      source.repository,
      checkout,
    ]);

    const originRef = runOutput("git", [
      "-C",
      checkout,
      "symbolic-ref",
      "--quiet",
      "refs/remotes/origin/HEAD",
    ]);
    const originRevision = runOutput("git", [
      "-C",
      checkout,
      "rev-parse",
      "--verify",
      `${originRef}^{commit}`,
    ]);
    const paths = [...new Set([source.path, source.license.path])];
    const diffArgs = [
      "-C",
      checkout,
      "diff",
      "--no-ext-diff",
      "--binary",
      "--unified=3",
      source.revision,
      originRef,
      "--",
      ...paths,
    ];
    const diff = spawnSync("git", diffArgs, { encoding: "utf8" });
    if (diff.error) {
      throw diff.error;
    }
    if (diff.status !== 0 && diff.status !== 1) {
      throw new Error(
        `git diff failed for ${name} with exit code ${diff.status}: ${diff.stderr}`,
      );
    }
    if (diff.status === 0) {
      console.log(`${name}: no upstream changes`);
      continue;
    }

    const header = [
      `# Upstream diff for ${name}`,
      `# mode: ${source.mode}`,
      `# repository: ${source.repository}`,
      `# tracked revision: ${source.revision}`,
      `# origin ref: ${originRef}`,
      `# origin revision: ${originRevision}`,
      `# upstream paths: ${paths.join(", ")}`,
      "",
    ].join("\n");
    await writeFile(
      path.join(outputDir, filename(index, name)),
      `${header}${diff.stdout}`,
    );
    changed += 1;
    console.log(`${name}: upstream changes found`);
  }
} finally {
  await rm(temporaryRoot, { recursive: true, force: true });
}

console.log(
  `wrote ${changed} upstream diff${changed === 1 ? "" : "s"} to ${path.relative(root, outputDir)}`,
);

function filename(index, name) {
  return `${String(index + 1).padStart(2, "0")}-${name}.diff`;
}

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(
      `${command} ${args.join(" ")} failed with exit code ${result.status}`,
    );
  }
}

function runOutput(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8" });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(
      `${command} ${args.join(" ")} failed with exit code ${result.status}: ${result.stderr}`,
    );
  }
  return result.stdout.trim();
}
