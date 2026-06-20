import { copyToClipboard } from '../js/utils.js';

describe('Utility Helpers', () => {
    test('clipboard copy resolution', () => {
        expect(typeof copyToClipboard).toBe('function');
    });
});
