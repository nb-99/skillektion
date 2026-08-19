import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cp, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const manifest = JSON.parse(await readFile(path.join(root, "sources.json"), "utf8"));
const check = process.argv.includes("--check");
const selected = process.argv.slice(2).filter((argument) => argument !== "--check");
const mirrors = Object.entries(manifest.skills).filter(
  ([name, source]) => source.mode === "mirror" && (selected.length === 0 || selected.includes(name)),
);

const unknown = selected.filter((name) => !mirrors.some(([mirror]) => mirror === name));
if (unknown.length > 0) {
  throw new Error(`not a mirrored skill: ${unknown.join(", ")}`);
}

const temporaryRoot = await mkdtemp(path.join(tmpdir(), "skillektion-sync-"));

try {
  for (const [name, source] of mirrors) {
    validateSource(name, source);

    const checkout = path.join(temporaryRoot, `${name}-checkout`);
    run("git", ["clone", "--quiet", "--filter=blob:none", "--no-checkout", source.repository, checkout]);
    run("git", ["-C", checkout, "sparse-checkout", "set", "--", source.path]);
    run("git", ["-C", checkout, "checkout", "--quiet", source.revision]);

    const generated = path.join(temporaryRoot, `${name}-generated`);
    await cp(path.join(checkout, source.path), generated, { recursive: true });
    await writeFile(
      path.join(generated, "LICENSE.upstream"),
      gitShow(checkout, source.revision, source.license.path),
    );

    const destination = path.join(root, "skills", name);
    if (check) {
      assertSameFiles(name, await files(destination), await files(generated));
      console.log(`verified ${name} at ${source.revision}`);
    } else {
      await rm(destination, { recursive: true, force: true });
      await cp(generated, destination, { recursive: true });
      console.log(`synced ${name} from ${source.revision}`);
    }
  }
} finally {
  await rm(temporaryRoot, { recursive: true, force: true });
}

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed with exit code ${result.status}`);
  }
}

function gitShow(checkout, revision, file) {
  const result = spawnSync("git", ["-C", checkout, "show", `${revision}:${file}`]);
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`could not read ${file} at ${revision}`);
  }
  return result.stdout;
}

function validateSource(name, source) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)) {
    throw new Error(`invalid skill name: ${name}`);
  }
  if (!/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(source.repository)) {
    throw new Error(`invalid repository for ${name}`);
  }
  if (!/^[0-9a-f]{40}$/.test(source.revision)) {
    throw new Error(`invalid revision for ${name}`);
  }
  for (const value of [source.path, source.license?.path]) {
    if (!value || value.startsWith("-") || path.isAbsolute(value) || value.split("/").includes("..")) {
      throw new Error(`invalid upstream path for ${name}`);
    }
  }
}

async function files(directory, prefix = "") {
  const result = new Map();
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const relative = path.join(prefix, entry.name);
    if (entry.isDirectory()) {
      for (const [name, content] of await files(path.join(directory, entry.name), relative)) {
        result.set(name, content);
      }
    } else if (entry.isFile()) {
      result.set(relative, await readFile(path.join(directory, entry.name)));
    } else {
      throw new Error(`unsupported entry in ${directory}: ${entry.name}`);
    }
  }
  return result;
}

function assertSameFiles(name, actual, expected) {
  assert.equal(actual.size, expected.size, `${name} has a different file count than upstream`);
  for (const [file, content] of expected) {
    assert.ok(actual.has(file), `${name} is missing ${file}`);
    assert.deepEqual(actual.get(file), content, `${name}/${file} differs from upstream`);
  }
}
