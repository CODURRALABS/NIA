export function logError(error: unknown): void {
  if (!process.env.NIA_INK_DEBUG_ERRORS) {
    return
  }

  console.error(error)
}
