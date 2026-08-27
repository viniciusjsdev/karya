import fs from "node:fs";

function parseArgs(argv) {
  const args = { country: "us", limit: 20 };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--term") args.term = argv[++i];
    else if (token === "--country") args.country = argv[++i];
    else if (token === "--limit") args.limit = Number(argv[++i]);
    else if (token === "--out") args.out = argv[++i];
    else throw new Error(`Unknown argument: ${token}`);
  }
  if (!args.term) throw new Error("--term is required.");
  if (!/^[a-z]{2}$/i.test(args.country)) throw new Error("--country must be a two-letter storefront code.");
  if (!Number.isInteger(args.limit) || args.limit < 1 || args.limit > 200) throw new Error("--limit must be an integer from 1 to 200.");
  return args;
}

function normalize(item) {
  return {
    track_id: item.trackId,
    bundle_id: item.bundleId,
    name: item.trackName,
    developer: item.artistName,
    developer_id: item.artistId,
    primary_genre: item.primaryGenreName,
    genres: item.genres,
    price: item.price,
    currency: item.currency,
    rating: item.averageUserRating,
    rating_count: item.userRatingCount,
    version: item.version,
    released_at: item.releaseDate,
    current_version_released_at: item.currentVersionReleaseDate,
    minimum_os_version: item.minimumOsVersion,
    store_url: item.trackViewUrl,
    artwork_url: item.artworkUrl512 ?? item.artworkUrl100,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const url = new URL("https://itunes.apple.com/search");
  url.searchParams.set("term", args.term);
  url.searchParams.set("country", args.country.toLowerCase());
  url.searchParams.set("entity", "software");
  url.searchParams.set("limit", String(args.limit));

  const response = await fetch(url, { headers: { "User-Agent": "karya-research-router/1.0" } });
  if (!response.ok) throw new Error(`Apple Search API returned HTTP ${response.status}.`);
  const data = await response.json();
  const output = {
    schema_version: "1.0",
    source: "Apple Search API",
    query: { term: args.term, country: args.country.toLowerCase(), limit: args.limit },
    retrieved_at: new Date().toISOString(),
    result_count: data.resultCount,
    results: data.results.map(normalize),
    limitations: ["Apple Search API metadata does not provide download or revenue estimates."],
  };
  const serialized = `${JSON.stringify(output, null, 2)}\n`;
  if (args.out) fs.writeFileSync(args.out, serialized, "utf8");
  else process.stdout.write(serialized);
}

try { await main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
