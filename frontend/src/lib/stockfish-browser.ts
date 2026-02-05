/**
 * Stockfish WASM wrapper for browser-based chess engine.
 * Uses Stockfish compiled to WebAssembly running in a Web Worker.
 */

type StockfishCallback = (bestMove: string) => void;

interface StockfishConfig {
  depth: number;
  skillLevel: number;
}

// Difficulty presets matching backend BOT_DIFFICULTY_LABELS
export const DIFFICULTY_CONFIGS: Record<string, StockfishConfig> = {
  beginner: { depth: 1, skillLevel: 0 },
  easy: { depth: 3, skillLevel: 3 },
  medium: { depth: 8, skillLevel: 8 },
  hard: { depth: 12, skillLevel: 14 },
  expert: { depth: 16, skillLevel: 18 },
  master: { depth: 20, skillLevel: 20 },
};

export class StockfishBrowser {
  private worker: Worker | null = null;
  private isReady = false;
  private pendingCallback: StockfishCallback | null = null;
  private currentConfig: StockfishConfig = DIFFICULTY_CONFIGS.medium;

  async init(): Promise<void> {
    if (this.worker) {
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        // Create worker from stockfish.js in public folder
        this.worker = new Worker("/stockfish/stockfish.js");

        this.worker.onmessage = (event: MessageEvent) => {
          const message = event.data;

          if (message === "uciok") {
            this.isReady = true;
            // Configure Stockfish
            this.worker?.postMessage("setoption name Threads value 1");
            this.worker?.postMessage("setoption name Hash value 16");
            this.worker?.postMessage(`setoption name Skill Level value ${this.currentConfig.skillLevel}`);
            this.worker?.postMessage("isready");
          } else if (message === "readyok") {
            resolve();
          } else if (typeof message === "string" && message.startsWith("bestmove")) {
            const parts = message.split(" ");
            const bestMove = parts[1];
            if (this.pendingCallback && bestMove && bestMove !== "(none)") {
              this.pendingCallback(bestMove);
              this.pendingCallback = null;
            }
          }
        };

        this.worker.onerror = (error) => {
          console.error("Stockfish worker error:", error);
          reject(error);
        };

        // Initialize UCI protocol
        this.worker.postMessage("uci");
      } catch (error) {
        reject(error);
      }
    });
  }

  setDifficulty(difficulty: string): void {
    const config = DIFFICULTY_CONFIGS[difficulty] || DIFFICULTY_CONFIGS.medium;
    this.currentConfig = config;

    if (this.worker && this.isReady) {
      this.worker.postMessage(`setoption name Skill Level value ${config.skillLevel}`);
    }
  }

  getBestMove(fen: string, callback: StockfishCallback): void {
    if (!this.worker || !this.isReady) {
      console.error("Stockfish not initialized");
      return;
    }

    this.pendingCallback = callback;
    this.worker.postMessage(`position fen ${fen}`);
    this.worker.postMessage(`go depth ${this.currentConfig.depth}`);
  }

  stop(): void {
    if (this.worker) {
      this.worker.postMessage("stop");
    }
  }

  terminate(): void {
    if (this.worker) {
      this.worker.postMessage("quit");
      this.worker.terminate();
      this.worker = null;
      this.isReady = false;
    }
  }
}

// Singleton instance
let stockfishInstance: StockfishBrowser | null = null;

export function getStockfish(): StockfishBrowser {
  if (!stockfishInstance) {
    stockfishInstance = new StockfishBrowser();
  }
  return stockfishInstance;
}
