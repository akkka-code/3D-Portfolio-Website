export const BILLBOARD_VIDEO_PATHS = [
  "/video/billboards/chrono-rebellion.mp4",
  "/video/billboards/behind-the-smile.mp4",
  "/video/billboards/paper-dash.mp4",
  "/video/billboards/solar-system.mp4",
  "/video/billboards/voxelcraft.mp4",
  "/video/billboards/pac-man.mp4",
  "/video/billboards/ar-memory.mp4",
  "/video/billboards/ar-face-filter.mp4",
];

export function createShuffledVideoPool() {
  const pool = [...BILLBOARD_VIDEO_PATHS];

  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }

  return pool;
}
