interface StorageEnvelope<T> {
  version: 1;
  data: T;
}

export interface StorageAdapter {
  get<T>(key: string, fallback: T): T;
  set<T>(key: string, value: T): void;
  remove(key: string): void;
}

export class BrowserStorageAdapter implements StorageAdapter {
  public constructor(
    private readonly storage: Storage,
    private readonly namespace = "karya"
  ) {}

  public get<T>(key: string, fallback: T): T {
    const rawValue = this.storage.getItem(this.key(key));
    if (!rawValue) return fallback;

    try {
      const envelope = JSON.parse(rawValue) as StorageEnvelope<T>;
      return envelope.version === 1 ? envelope.data : fallback;
    } catch {
      return fallback;
    }
  }

  public set<T>(key: string, value: T): void {
    const envelope: StorageEnvelope<T> = { version: 1, data: value };
    this.storage.setItem(this.key(key), JSON.stringify(envelope));
  }

  public remove(key: string): void {
    this.storage.removeItem(this.key(key));
  }

  private key(key: string): string {
    return `${this.namespace}:${key}`;
  }
}

export const browserStorage = new BrowserStorageAdapter(window.localStorage);
