import * as vscode from 'vscode';
// import WebSocket from 'ws';

export function activate(context: vscode.ExtensionContext) {
    console.log('Aditya: The Ghost Writer is now active.');

    // Hover Provider for Contextual Analysis
    const hoverProvider = vscode.languages.registerHoverProvider('*', {
        provideHover(document, position, token) {
            const range = document.getWordRangeAtPosition(position);
            const word = document.getText(range);
            
            // In reality, this sends the word to PhantomEngine via WS
            if (word.length > 3) {
                const markdown = new vscode.MarkdownString();
                markdown.appendMarkdown(`**Aditya Analysis:**\n\n`);
                markdown.appendMarkdown(`I have analyzed \`${word}\`. This structure is optimal, but could benefit from a framer-motion physics wrapper for better UX.`);
                return new vscode.Hover(markdown);
            }
        }
    });

    // The Ghost Writer Command
    let disposable = vscode.commands.registerCommand('aditya.summonGhostWriter', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        const document = editor.document;
        const selection = editor.selection;

        // Mocking the connection to Phantom Engine
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Aditya is writing...",
            cancellable: false
        }, async (progress) => {
            return new Promise<void>((resolve) => {
                setTimeout(() => {
                    editor.edit(editBuilder => {
                        const snippet = `\n// [ADITYA GHOST WRITER]\n// Predicted optimal structure injected.\nfunction optimizedExecution() {\n    console.log("Ascended.");\n}\n`;
                        editBuilder.insert(selection.active, snippet);
                    });
                    vscode.window.showInformationMessage('Aditya: Ghost Writer insertion complete.');
                    resolve();
                }, 1500);
            });
        });
    });

    context.subscriptions.push(hoverProvider, disposable);
}

export function deactivate() {
    console.log('Aditya: The Ghost Writer deactivated.');
}
