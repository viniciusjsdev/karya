const status = {
  codex: { ready: true, role: "Strategy, content, preparation, and analysis." },
  manus: { ready: Boolean(process.env.MANUS_API_KEY), env: "MANUS_API_KEY", role: "Bounded native execution and metrics retrieval." },
  platform_connectors: { ready: null, note: "Confirm each connected account and minimum permissions manually." },
  human_owner: { ready: null, note: "Required for account creation, authentication, verification, 2FA, and action confirmation." },
};
process.stdout.write(`${JSON.stringify(status, null, 2)}\n`);
