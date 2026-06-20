// Analytics helper
export function sendEvent(category, action, label) {
    if (window.gtag) {
        window.gtag('event', action, {
            'event_category': category,
            'event_label': label
        });
    } else {
        console.log(`[Analytics Event] ${category} - ${action} - ${label}`);
    }
}
