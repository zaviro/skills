#!/usr/bin/env -S node --experimental-strip-types

import { access } from "node:fs/promises";
import { constants } from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const args = process.argv.slice(2);

function usage(exitCode = 0) {
  const text = `
desktopctl — thin runtime/validation wrapper for Niri + Noctalia

Usage:
  desktopctl doctor
  desktopctl inspect noctalia
  desktopctl validate niri [config-path]
  desktopctl validate noctalia [config-path]
  desktopctl action niri <action> [args...]
  desktopctl action noctalia <command> [args...]
  desktopctl paths
`.trim();
  console.error(text);
  process.exit(exitCode);
}

function run(command, commandArgs = [], options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, commandArgs, {
      stdio: options.capture ? ["inherit", "pipe", "pipe"] : "inherit",
      env: process.env,
    });

    let stdout = "";
    let stderr = "";

    if (options.capture) {
      child.stdout?.setEncoding("utf8");
      child.stderr?.setEncoding("utf8");
      child.stdout?.on("data", (chunk) => (stdout += chunk));
      child.stderr?.on("data", (chunk) => (stderr += chunk));
    }

    child.on("error", reject);
    child.on("close", (code) => {
      if (options.capture) {
        resolve({ code: code ?? 1, stdout, stderr });
      } else if (code === 0) {
        resolve({ code: 0, stdout: "", stderr: "" });
      } else {
        process.exitCode = code ?? 1;
        resolve({ code: code ?? 1, stdout: "", stderr: "" });
      }
    });
  });
}

async function existsOnPath(command) {
  const result = await run("sh", ["-lc", `command -v -- "$1" >/dev/null 2>&1`, "sh", command], {
    capture: true,
  });
  return result.code === 0;
}

async function fileExists(filePath) {
  try {
    await access(filePath, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

function xdgPath(envName, fallback) {
  return process.env[envName] || path.join(os.homedir(), fallback);
}

const paths = {
  niriConfig: process.env.NIRI_CONFIG || path.join(xdgPath("XDG_CONFIG_HOME", ".config"), "niri", "config.kdl"),
  noctaliaConfigDir: path.join(
    process.env.NOCTALIA_CONFIG_HOME || xdgPath("XDG_CONFIG_HOME", ".config"),
    "noctalia",
  ),
  noctaliaStateDir: path.join(
    process.env.NOCTALIA_STATE_HOME || xdgPath("XDG_STATE_HOME", ".local/state"),
    "noctalia",
  ),
  agentStateDir: path.join(xdgPath("XDG_STATE_HOME", ".local/state"), "desktop-agent"),
};

async function doctor() {
  const commands = ["niri", "noctalia", "nix"];
  let failed = false;

  for (const command of commands) {
    const ok = await existsOnPath(command);
    console.log(`${ok ? "ok" : "missing"}\t${command}`);
    if (!ok && command !== "noctalia") failed = true;
  }

  console.log(`${(await fileExists(paths.niriConfig)) ? "ok" : "missing"}\tniri-config\t${paths.niriConfig}`);
  console.log(`${(await fileExists(paths.noctaliaConfigDir)) ? "ok" : "missing"}\tnoctalia-config-dir\t${paths.noctaliaConfigDir}`);
  console.log(`info\tagent-state-dir\t${paths.agentStateDir}`);

  if (failed) process.exitCode = 1;
}

async function inspect(target) {
  if (target === "noctalia") {
    await run("noctalia", ["config", "export", "full"]);
    return;
  }
  throw new Error(`unsupported inspect target: ${target}`);
}

async function validate(target, candidate) {
  if (target === "niri") {
    const commandArgs = ["validate"];
    if (candidate) commandArgs.push("--config", candidate);
    await run("niri", commandArgs);
    return;
  }

  if (target === "noctalia") {
    const commandArgs = ["config", "validate"];
    if (candidate) commandArgs.push(candidate);
    await run("noctalia", commandArgs);
    return;
  }

  throw new Error(`unsupported validator: ${target}`);
}

async function action(target, forwarded) {
  if (forwarded.length === 0) {
    throw new Error(`missing ${target} action`);
  }

  if (target === "niri") {
    await run("niri", ["msg", "action", ...forwarded]);
    return;
  }

  if (target === "noctalia") {
    await run("noctalia", ["msg", ...forwarded]);
    return;
  }

  throw new Error(`unsupported action target: ${target}`);
}

async function main() {
  if (args.length === 0) usage(1);

  const [command, target, ...rest] = args;

  switch (command) {
    case "doctor":
      await doctor();
      break;
    case "inspect":
      if (!target) usage(1);
      await inspect(target);
      break;
    case "validate":
      if (!target) usage(1);
      await validate(target, rest[0]);
      break;
    case "action":
      if (!target) usage(1);
      await action(target, rest);
      break;
    case "paths":
      console.log(JSON.stringify(paths, null, 2));
      break;
    case "-h":
    case "--help":
    case "help":
      usage(0);
      break;
    default:
      usage(1);
  }
}

main().catch((error) => {
  console.error(`desktopctl: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
