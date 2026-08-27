const status = {
  codex: { ready: true, note: "Default research and synthesis route." },
  apple: { ready: true, note: "Public Search API; network and service limits still apply." },
  appstoretracker: { ready: null, note: "Confirm subscription/session manually; no secret is read by this check." },
  openalex: { ready: Boolean(process.env.OPENALEX_API_KEY), env: "OPENALEX_API_KEY", note: "A key is recommended for reliable production use." },
  perplexity: { ready: Boolean(process.env.PERPLEXITY_API_KEY), env: "PERPLEXITY_API_KEY", optional: true },
  manus: { ready: Boolean(process.env.MANUS_API_KEY), env: "MANUS_API_KEY", optional: true, note: "Authenticated platform sessions may also require human setup." },
};

process.stdout.write(`${JSON.stringify(status, null, 2)}\n`);
