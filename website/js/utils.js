// Utility scripts
export function copyToClipboard(text) {
    return navigator.clipboard.writeText(text);
}
export function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
