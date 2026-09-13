import { UserDirectoryUnavailableError } from "../domain/errors";
import type { KnownUser, UserDirectory } from "../domain/user-directory";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export class HttpUserDirectory implements UserDirectory {
  constructor(
    private readonly baseUrl: string,
    private readonly timeoutMs: number,
    private readonly retries: number = 1,
  ) {}

  async findById(userId: string): Promise<KnownUser | null> {
    let lastReason = "sin intentos";

    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}/users/${userId}`, {
          headers: { accept: "application/json" },
          signal: AbortSignal.timeout(this.timeoutMs),
        });

        if (response.ok) {
          const body = (await response.json()) as KnownUser;
          return { id: body.id, name: body.name, email: body.email };
        }

        if (response.status === 404) {
          return null;
        }

        lastReason = `respuesta inesperada HTTP ${response.status}`;
      } catch (error) {
        lastReason = error instanceof Error ? error.message : String(error);
      }

      if (attempt < this.retries) {
        await sleep(100 * (attempt + 1));
      }
    }

    throw new UserDirectoryUnavailableError(lastReason);
  }

  async isReachable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}
