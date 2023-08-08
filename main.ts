import { App, Modal, Plugin, PluginSettingTab, Setting } from 'obsidian';
import * as childProcess from 'child_process';
import * as path from 'path';

interface MyPluginSettings {
    automaticallyTag: boolean;
    createBacklinks: boolean;
    userTags: string[];
}

const DEFAULT_SETTINGS: MyPluginSettings = {
    automaticallyTag: false,
    createBacklinks: false,
    userTags: []
};

export default class MyPlugin extends Plugin {
    settings: MyPluginSettings;

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    async onload() {
        await this.loadSettings();

        const ribbonIconEl = this.addRibbonIcon('download-cloud', 'Goodnotes Sync', () => {
            new SamplePopup(this.app).open();
        });


        this.addSettingTab(new SampleSettingTab(this.app, this));

    }

}

class SamplePopup extends Modal {
    constructor(app: App) {
        super(app);
    }

    onOpen() {
        const { contentEl } = this;

        contentEl.createEl('h2', { text: 'Goodnotes Sync' });
        contentEl.createEl('p', { text: 'Import goodnotes from Google Drive to obsidian.' });

        // Create a button to run Python code
        const runButton = contentEl.createEl('button', {
            text: 'Sync Notes',
            cls: 'mod-cta'
        });

        runButton.addEventListener('click', () => {
            this.close();
            this.runPythonCode();
        });

        // Create a button to close the modal
        const closeButton = contentEl.createEl('button', { text: 'Close', cls: 'mod-cta' });

        closeButton.addEventListener('click', () => this.close());
    }

    onClose() {
        const { contentEl } = this;
        contentEl.empty();
    }

    runPythonCode() {
        // Get the path to your plugin's directory using __dirname
        const pluginDir = this.app.vault.adapter.basePath
        // Construct the path to your Python script relative to the plugin directory
        const workingDir = path.join(pluginDir, '.obsidian', 'plugins', 'goodnotes-obsidian-sync', 'DriveToObsidian');
        const pythonScriptPath = path.join(workingDir, 'sg.py')

        // Execute the Python script
        childProcess.exec(`python "${pythonScriptPath}"`, { cwd: workingDir }, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error executing Python script: ${error}`);
                return;
            }

            console.log('Python script executed successfully');
            console.log('Standard Output:', stdout);
            console.error('Standard Error:', stderr);
        });
    }
}

class SampleSettingTab extends PluginSettingTab {
    plugin: MyPlugin;

    constructor(app: App, plugin: MyPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const { containerEl } = this;
        containerEl.empty();

        new Setting(containerEl)
            .setName('Drive folder:')
            .setDesc('Set this to the name of the folder goodnotes is syncing to in your drive')
            .addText(text => text
                .setPlaceholder('Folder name')
                .setValue(this.plugin.settings.driveFolder)
                .onChange(async (value) => {
                    this.plugin.settings.driveFolder = value
                    await this.plugin.saveSettings();
                }));

        new Setting(containerEl)
            .setName('Create backlinks between adjacent notes')
            .setDesc('Toggle to create backlinks between adjacent notes.')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.createBacklinks)
                .onChange(async (value) => {
                    this.plugin.settings.createBacklinks = value;
                    await this.plugin.saveSettings();
                }));


        new Setting(containerEl)
            .setName('Automatically tag imported notes')
            .setDesc('Allows you to choose tags to be applied to each imported note.')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.automaticallyTag)
                .onChange(async (value) => {
                    this.plugin.settings.automaticallyTag = value;
                    await this.plugin.saveSettings();
                }));


        new Setting(containerEl)
            .setName('User Tags')
            .setDesc('Add tags for the plugin to use.')
            .addText(text => text
                .setPlaceholder('Enter tag')
                .setValue(this.tagInputValue)
                .onChange((value) => {
                    this.tagInputValue = value;
                }))
            .addButton(button => button
                .setButtonText('Add Tag')
                .onClick(() => this.addTag()));

        // Create the tag list
        this.tagList = containerEl.createEl('ul');

        // Populate the tag list with saved user tags
        this.plugin.settings.userTags.forEach(tag => {
            this.addTagElement(tag);
        });
    }

    addTag() {
        if (this.tagInputValue) {
            this.plugin.settings.userTags.push(this.tagInputValue);
            this.plugin.saveSettings();
            this.addTagElement(this.tagInputValue);
            this.tagInputValue = ''; // Clear the input value
        }
    }

    addTagElement(tag: string) {
        if (this.tagList) {
            const tagItem = this.tagList.createEl('li');
            tagItem.setText(tag);

            const deleteButton = tagItem.createEl('button', {
                cls: 'tag-delete-button',
                attr: {
                    style: 'cursor: pointer; margin-left: 8px;'
                }
            });
            deleteButton.createEl('span', {
                text: 'X',
                cls: 'tag-delete-icon'
            });

            // Add custom CSS classes for styling
            deleteButton.addClass('small-button');
            deleteButton.addClass('less-tall-button');

            deleteButton.addEventListener('click', () => {
                this.removeTag(tag);
            });
        }
    }



    removeTag(tag: string) {
        const updatedTags = this.plugin.settings.userTags.filter(t => t !== tag);
        this.plugin.settings.userTags = updatedTags;
        this.plugin.saveSettings();
        this.display(); // Refresh the settings tab
    }

}
