import { BrowserStorageAdapter } from "./storage.adapter";

describe("BrowserStorageAdapter", () => {
  beforeEach(() => window.localStorage.clear());

  it("persists a versioned value", () => {
    const storage = new BrowserStorageAdapter(window.localStorage, "test");
    storage.set("preferences", { theme: "dark" });

    expect(storage.get("preferences", { theme: "light" })).toEqual({ theme: "dark" });
  });

  it("returns the fallback for invalid JSON", () => {
    window.localStorage.setItem("test:preferences", "invalid");
    const storage = new BrowserStorageAdapter(window.localStorage, "test");

    expect(storage.get("preferences", { theme: "light" })).toEqual({ theme: "light" });
  });
});
