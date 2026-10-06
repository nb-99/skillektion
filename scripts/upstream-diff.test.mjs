import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { copyFile, mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const script = fileURLToPath(new URL("./upstream-diff.mjs", import.meta.url));

test("upstream checker reports content, deletion, binary, and license changes, then clears stale diffs", async () => {
  const scratch = path.join(tmpdir(), "opencode");
  await mkdir(scratch, { recursive: true });
  const root = await mkdtemp(path.join(scratch, "upstream-diff-test-"));
  try {
    const upstream = path.join(root, "upstream");
    const catalog = path.join(root, "catalog");
    const env = {
      ...Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith("GIT_"))),
      GIT_CONFIG_GLOBAL: "/dev/null", GIT_CONFIG_NOSYSTEM: "1", TMPDIR: root,
    };
    await mkdir(path.join(upstream, "changed"), { recursive: true });
    await mkdir(path.join(upstream, "unchanged"));
    await mkdir(path.join(catalog, "scripts"), { recursive: true });
    await copyFile(script, path.join(catalog, "scripts", "upstream-diff.mjs"));
    const git = (...args) => run("git", ["-C", upstream, ...args], { env });
    const commit = () => {
      git("add", ".");
      git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "fixture");
      return git("rev-parse", "HEAD").stdout.trim();
    };
    git("init", "--quiet", "-b", "main");
    await writeFile(path.join(upstream, "changed", "SKILL.md"), "Before\n");
    await writeFile(path.join(upstream, "changed", "removed.md"), "Remove me\n");
    await writeFile(path.join(upstream, "changed", "image.bin"), Buffer.from([0, 1]));
    await writeFile(path.join(upstream, "unchanged", "SKILL.md"), "Stable\n");
    await writeFile(path.join(upstream, "LICENSE"), "Stable license\n");
    await writeFile(path.join(upstream, "CHANGED-LICENSE"), "Old license\n");
    const base = commit();
    await writeFile(path.join(upstream, "changed", "SKILL.md"), "After\n");
    await rm(path.join(upstream, "changed", "removed.md"));
    await writeFile(path.join(upstream, "changed", "image.bin"), Buffer.from([0, 2]));
    await writeFile(path.join(upstream, "CHANGED-LICENSE"), "New license\n");
    const head = commit();
    const source = (directory, license = "LICENSE") => ({
      mode: "mirror", repository: upstream, revision: base,
      path: directory, license: { path: license },
    });
    const manifest = { skills: {
      changed: source("changed"),
      unchanged: source("unchanged"),
      "license-only": { ...source("unchanged", "CHANGED-LICENSE"), mode: "adapted" },
      owned: { mode: "owned" },
    } };
    const manifestPath = path.join(catalog, "sources.json");
    await writeFile(manifestPath, JSON.stringify(manifest));
    const check = () => run(process.execPath, [path.join(catalog, "scripts", "upstream-diff.mjs")], {
      env,
    });
    const first = check();
    assert.match(first.stdout, /changed: upstream changes found/);
    assert.match(first.stdout, /unchanged: no upstream changes/);
    assert.match(first.stdout, /license-only: upstream changes found/);
    assert.match(first.stdout, /wrote 2 upstream diffs/);
    const output = path.join(catalog, "scratch", "upstream-diffs");
    assert.deepEqual((await readdir(output)).sort(), ["01-changed.diff", "03-license-only.diff"]);
    const diff = await readFile(path.join(output, "01-changed.diff"), "utf8");
    assert.ok(diff.includes(`# tracked revision: ${base}`));
    assert.ok(diff.includes(`# origin revision: ${head}`));
    assert.match(diff, /-Before\n\+After/);
    assert.match(diff, /deleted file mode/);
    assert.match(diff, /GIT binary patch/);
    assert.match(await readFile(path.join(output, "03-license-only.diff"), "utf8"), /-Old license\n\+New license/);
    await writeFile(path.join(output, "manual.diff"), "Unrelated file\n");
    manifest.skills.changed.revision = "0".repeat(40);
    await writeFile(manifestPath, JSON.stringify(manifest));
    const failed = spawnSync(process.execPath, [path.join(catalog, "scripts", "upstream-diff.mjs")], {
      encoding: "utf8", env,
    });
    assert.notEqual(failed.status, 0);
    assert.match(failed.stderr, /git diff failed for changed/);
    assert.doesNotMatch(failed.stdout, /^changed: no upstream changes$/m);
    assert.deepEqual(await readdir(output), ["manual.diff"]);
    manifest.skills.changed.revision = base;
    await writeFile(manifestPath, JSON.stringify(manifest));
    assert.match(check().stdout, /wrote 2 upstream diffs/);
    manifest.skills = {
      unchanged: { ...manifest.skills.unchanged, revision: head },
      changed: { ...manifest.skills.changed, revision: head },
      owned: manifest.skills.owned,
    };
    await writeFile(manifestPath, JSON.stringify(manifest));
    assert.match(check().stdout, /wrote 0 upstream diffs/);
    assert.deepEqual(await readdir(output), ["manual.diff"]);
    assert.equal(await readFile(path.join(output, "manual.diff"), "utf8"), "Unrelated file\n");
    assert.deepEqual((await readdir(root)).sort(), ["catalog", "upstream"]);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: "utf8", ...options });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  return result;
}
