import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const manifest = JSON.parse(await readFile(path.join(root, "sources.json"), "utf8"));
const namePattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const shaPattern = /^[0-9a-f]{40}$/;
const reservedNames = new Set(["agent-memory", "nix-home-manager-expert"]);

test("catalog and source ledger agree", async () => {
  assert.deepEqual(Object.keys(manifest).sort(), ["skills", "version"]);
  assert.equal(manifest.version, 1);
  const entries = await readdir(path.join(root, "skills"), { withFileTypes: true });
  const directories = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();
  const declared = Object.keys(manifest.skills).sort();

  assert.deepEqual(directories, declared);
});

for (const [name, source] of Object.entries(manifest.skills)) {
  test(`${name} is a valid skill`, async () => {
    assert.match(name, namePattern);
    assert.ok(!reservedNames.has(name), `${name} is reserved by a consumer`);

    const skill = await readFile(path.join(root, "skills", name, "SKILL.md"), "utf8");
    const frontmatter = skill.match(/^---\n([\s\S]*?)\n---\n/);
    assert.ok(frontmatter, "SKILL.md must start with YAML frontmatter");
    assert.match(frontmatter[1], new RegExp(`^name: ["']?${name}["']?$`, "m"));
    assert.match(frontmatter[1], /^description: .+$/m);

    assert.deepEqual(
      Object.keys(source).sort(),
      source.mode === "owned"
        ? ["mode"]
        : ["license", "mode", "notes", "path", "repository", "revision"].filter(
            (key) => key !== "notes" || source.mode === "adapted",
          ),
    );
    assert.ok(["owned", "mirror", "adapted"].includes(source.mode));
    if (source.mode === "owned") {
      return;
    }

    assert.match(source.repository, /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/);
    assert.match(source.revision, shaPattern);
    assert.ok(source.path.length > 0);
    assert.deepEqual(Object.keys(source.license).sort(), ["path", "spdx"]);
    assert.ok(source.license.path.length > 0);
    assert.ok(source.license.spdx.length > 0);
    await readFile(path.join(root, "skills", name, "LICENSE.upstream"), "utf8");
    if (source.mode === "adapted") {
      assert.ok(source.notes, "adapted skills must explain their portability changes");
    }
  });
}
