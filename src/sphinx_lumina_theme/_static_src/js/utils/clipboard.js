/**
 * @module utils/clipboard
 * @description Thin wrapper over ``navigator.clipboard.writeText``. The
 * Clipboard API is gated on a secure context (HTTPS, localhost, or
 * ``file://``); on plain HTTP origins it's either undefined or rejects.
 * Callers should ``.catch()`` to surface the failure — silent swallow
 * makes copy buttons feel broken.
 */

/**
 * Copy text to the clipboard.
 *
 * @param {string} text — Plain text to copy.
 * @returns {Promise<void>} Resolves on success; rejects with the underlying
 *   ``DOMException`` (permission denied, focus lost) or a synthesized
 *   ``Error`` if the API is unavailable.
 */
export function copyText(text) {
  if (!navigator.clipboard) {
    return Promise.reject(
      new Error(
        "Clipboard API unavailable — requires a secure context (HTTPS or localhost).",
      ),
    );
  }
  return navigator.clipboard.writeText(text);
}
