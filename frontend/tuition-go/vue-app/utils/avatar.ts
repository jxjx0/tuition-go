/**
 * Returns the image URL if valid, otherwise a deterministic dicebear avatar
 * seeded by the given ID so the same user always gets the same fallback.
 */
export function avatarUrl(imageURL: string | null | undefined, seed: string): string {
  if (imageURL && imageURL.trim()) return imageURL
  return `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(seed)}`
}
