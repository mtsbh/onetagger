<template>
<div class="bulk-tag-container">
    <!-- Main content area -->
    <div class="row" style="height: calc(100vh - 220px);">

        <!-- Left: File List -->
        <div class="col-7 q-pa-md">
            <div class="text-h6 text-primary q-mb-md">Files</div>

            <!-- Controls -->
            <div class="row q-mb-sm items-center">
                <q-btn flat dense icon="mdi-folder-open" label="Select Folder" @click="selectFolder" class="q-mr-sm" />
                <q-btn flat dense label="Select All" @click="selectAll" class="q-mr-sm" size="sm" />
                <q-btn flat dense label="Deselect All" @click="deselectAll" size="sm" />
                <q-space />
                <div class="text-caption text-grey-6">
                    Selected: {{ selectedCount }} / {{ files.length }}
                </div>
            </div>

            <!-- File list -->
            <q-scroll-area style="height: calc(100vh - 380px);" class="bg-darker rounded-borders">
                <q-list dense>
                    <q-item
                        v-for="(file, index) in files"
                        :key="file.path"
                        clickable
                        @click="toggleFile(file)"
                        @dblclick="playTrack(index)"
                        class="file-item"
                        :class="{ 'playing-track': currentTrack === file }"
                    >
                        <q-item-section avatar>
                            <q-checkbox
                                :model-value="file.selected"
                                @click.stop="toggleFile(file)"
                                color="primary"
                            />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label class="text-grey-3">{{ file.filename }}</q-item-label>
                            <q-item-label caption class="text-grey-6">
                                {{ file.artist || 'Unknown' }} - {{ file.title || 'Unknown' }}
                            </q-item-label>
                        </q-item-section>
                    </q-item>
                </q-list>
                <div v-if="files.length === 0" class="text-center q-pa-xl text-grey-6">
                    <q-icon name="mdi-folder-open" size="xl" class="q-mb-md" />
                    <div>No folder selected</div>
                    <div class="text-caption">Click "Select Folder" to load files</div>
                </div>
            </q-scroll-area>
        </div>

        <!-- Right: Operations -->
        <div class="col-5 q-pa-md bg-darker">
            <div class="text-h6 text-primary q-mb-md">Tag Operations</div>

            <q-scroll-area style="height: calc(100vh - 440px);">

                <!-- Operation 1: Replace Text -->
                <q-expansion-item
                    v-model="operations.replace.enabled"
                    icon="mdi-find-replace"
                    label="Replace Text"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.replace.field"
                                :options="tagFields"
                                label="Field"
                                filled
                                dense
                                dark
                            />
                            <q-input
                                v-model="operations.replace.find"
                                label="Find"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                            <q-input
                                v-model="operations.replace.replaceWith"
                                label="Replace with"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                            <q-checkbox
                                v-model="operations.replace.caseSensitive"
                                label="Case sensitive"
                                dark
                                class="q-mt-sm"
                            />
                            <q-checkbox
                                v-model="operations.replace.useRegex"
                                label="Use Regex"
                                dark
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- Operation 2: Trim Whitespace -->
                <q-expansion-item
                    v-model="operations.trim.enabled"
                    icon="mdi-format-text"
                    label="Trim Whitespace"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.trim.field"
                                :options="['ALL FIELDS', ...tagFields]"
                                label="Field"
                                filled
                                dense
                                dark
                            />
                            <q-checkbox
                                v-model="operations.trim.leading"
                                label="Leading spaces"
                                dark
                                class="q-mt-sm"
                            />
                            <q-checkbox
                                v-model="operations.trim.trailing"
                                label="Trailing spaces"
                                dark
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- Operation 3: Copy Field -->
                <q-expansion-item
                    v-model="operations.copy.enabled"
                    icon="mdi-content-copy"
                    label="Copy Field"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.copy.from"
                                :options="tagFields"
                                label="From"
                                filled
                                dense
                                dark
                            />
                            <q-select
                                v-model="operations.copy.to"
                                :options="tagFields"
                                label="To"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                            <q-checkbox
                                v-model="operations.copy.append"
                                label="Append (not replace)"
                                dark
                                class="q-mt-sm"
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- Operation 4: Change Case -->
                <q-expansion-item
                    v-model="operations.case.enabled"
                    icon="mdi-format-letter-case"
                    label="Change Case"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.case.field"
                                :options="tagFields"
                                label="Field"
                                filled
                                dense
                                dark
                            />
                            <q-option-group
                                v-model="operations.case.mode"
                                :options="caseOptions"
                                color="primary"
                                dark
                                class="q-mt-sm"
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- Operation 5: Add Prefix/Suffix -->
                <q-expansion-item
                    v-model="operations.add.enabled"
                    icon="mdi-text-box-plus"
                    label="Add Prefix/Suffix"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.add.field"
                                :options="tagFields"
                                label="Field"
                                filled
                                dense
                                dark
                            />
                            <q-input
                                v-model="operations.add.prefix"
                                label="Prefix"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                            <q-input
                                v-model="operations.add.suffix"
                                label="Suffix"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- Operation 6: Remove Text -->
                <q-expansion-item
                    v-model="operations.remove.enabled"
                    icon="mdi-text-box-remove"
                    label="Remove Text"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.remove.field"
                                :options="tagFields"
                                label="Field"
                                filled
                                dense
                                dark
                            />
                            <q-input
                                v-model="operations.remove.text"
                                label="Text to remove"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

                <!-- Operation 7: Split Field -->
                <q-expansion-item
                    v-model="operations.split.enabled"
                    icon="mdi-format-list-bulleted"
                    label="Split Field"
                    header-class="bg-dark text-grey-3"
                    class="q-mb-sm operation-panel"
                >
                    <q-card class="bg-dark">
                        <q-card-section>
                            <q-select
                                v-model="operations.split.source"
                                :options="tagFields"
                                label="Source"
                                filled
                                dense
                                dark
                            />
                            <q-input
                                v-model="operations.split.separator"
                                label="Separator"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                                placeholder=" - "
                            />
                            <q-select
                                v-model="operations.split.leftField"
                                :options="tagFields"
                                label="Left → Field"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                            <q-select
                                v-model="operations.split.rightField"
                                :options="tagFields"
                                label="Right → Field"
                                filled
                                dense
                                dark
                                class="q-mt-sm"
                            />
                        </q-card-section>
                    </q-card>
                </q-expansion-item>

            </q-scroll-area>

            <!-- Preview Section -->
            <div class="q-mt-md bg-dark q-pa-md rounded-borders">
                <div class="text-subtitle2 text-grey-4 q-mb-sm">Preview</div>
                <div v-if="previewText" class="preview-box">
                    <pre class="text-caption text-grey-3">{{ previewText }}</pre>
                </div>
                <div v-else class="text-caption text-grey-6 text-center q-pa-md">
                    No preview available
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="row q-mt-md q-gutter-sm">
                <q-btn
                    flat
                    icon="mdi-eye"
                    label="Preview"
                    @click="preview"
                    color="primary"
                    :disable="selectedCount === 0"
                    class="col"
                />
                <q-btn
                    unelevated
                    icon="mdi-check"
                    label="Apply to Selected"
                    @click="apply"
                    color="primary"
                    :disable="selectedCount === 0 || !hasEnabledOperations"
                    class="col"
                />
            </div>
        </div>
    </div>

    <!-- Audio Player at bottom -->
    <div class="player-bar bg-darker q-pa-md">
        <div class="row q-mx-md">
            <!-- Meta -->
            <div class="row col-2">
                <!-- Album art -->
                <div class="q-mt-sm">
                    <q-img
                        :src="art"
                        width="46px"
                        height="46px"
                        class="rounded-borders"
                        :placeholder-src="PLACEHOLDER_IMG"
                    >
                        <template v-slot:error>
                            <q-img :src="PLACEHOLDER_IMG" width="46px" height="46px" class="rounded-borders"></q-img>
                        </template>
                    </q-img>
                </div>

                <div class="column q-mt-sm q-pt-xs q-pl-sm" style="width: calc(100% - 50px);">
                    <div class="text-caption text-weight-bold full-width">
                        <div v-if="$1t.player.value.title" class="text-no-wrap overflow-hidden" style="text-overflow: ellipsis">
                            {{ $1t.player.value.title }}
                        </div>
                    </div>

                    <div class="text-caption full-width text-grey-5">
                        <div v-if="$1t.player.value.artists" class="text-no-wrap overflow-hidden" style="text-overflow: ellipsis">
                            {{ $1t.player.value.artists.join(', ') }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Waveform with controls -->
            <div class="col-8">
                <div class="row justify-center">
                    <div class="q-mt-sm">
                        <!-- Play button -->
                        <q-btn
                            round
                            flat
                            icon="mdi-play"
                            class="q-mr-sm"
                            :ripple="false"
                            v-if="!$1t.player.value.playing"
                            @click="$1t.player.value.play()"
                        ></q-btn>
                        <!-- Pause -->
                        <q-btn
                            round
                            flat
                            icon="mdi-pause"
                            class="q-mr-sm"
                            :ripple="false"
                            v-else
                            @click="$1t.player.value.pause()"
                        ></q-btn>
                    </div>

                    <div><Waveform></Waveform></div>
                </div>
            </div>

            <!-- Volume -->
            <div class="row col-2 justify-end">
                <div class="q-pt-sm" style="width: 88px">
                    <q-slider
                        v-model="$1t.player.value.volume"
                        :min="0.0"
                        :max="1.0"
                        :step="0.01"
                        @update:model-value="onVolumeChange"
                        style="margin-top: 6px"
                    ></q-slider>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { get1t } from '../scripts/onetagger';
import { useQuasar } from 'quasar';
import { QuickTagFile, PLACEHOLDER_IMG } from '../scripts/quicktag';
import { httpUrl } from '../scripts/utils';
import Waveform from '../components/Waveform.vue';

const $1t = get1t();
const $q = useQuasar();

// Tag fields
const tagFields = [
    'title', 'artist', 'album', 'albumartist', 'genre',
    'date', 'comment', 'bpm', 'key', 'mood', 'label'
];

const caseOptions = [
    { label: 'Title Case', value: 'title' },
    { label: 'UPPERCASE', value: 'upper' },
    { label: 'lowercase', value: 'lower' },
    { label: 'Sentence case', value: 'sentence' }
];

// File list
interface BulkFile {
    path: string;
    filename: string;
    selected: boolean;
    title?: string;
    artist?: string;
    tags: Record<string, any>;
}

const files = ref<BulkFile[]>([]);
const previewText = ref('');

// Player state (kept for compatibility with file tracking)
const currentTrack = ref<BulkFile | null>(null);
const currentTrackIndex = ref(-1);

// Operations state
const operations = ref({
    replace: {
        enabled: false,
        field: 'title',
        find: '',
        replaceWith: '',
        caseSensitive: false,
        useRegex: false
    },
    trim: {
        enabled: false,
        field: 'ALL FIELDS',
        leading: true,
        trailing: true
    },
    copy: {
        enabled: false,
        from: 'artist',
        to: 'comment',
        append: false
    },
    case: {
        enabled: false,
        field: 'title',
        mode: 'title'
    },
    add: {
        enabled: false,
        field: 'title',
        prefix: '',
        suffix: ''
    },
    remove: {
        enabled: false,
        field: 'title',
        text: ''
    },
    split: {
        enabled: false,
        source: 'title',
        separator: ' - ',
        leftField: 'artist',
        rightField: 'title'
    }
});

// Computed
const selectedCount = computed(() =>
    files.value.filter(f => f.selected).length
);

const hasEnabledOperations = computed(() =>
    Object.values(operations.value).some((op: any) => op.enabled)
);

// Album art for player
const art = computed(() => `${httpUrl()}/thumb?path=${encodeURIComponent($1t.player.value.path??'')}`);

// Methods
function selectFolder() {
    // Use OneTagger's existing browse functionality
    $1t.browse('bulktag');
}

function loadFromQuickTag() {
    // Load files from QuickTag view if available
    if ($1t.quickTag.value.tracks && $1t.quickTag.value.tracks.length > 0) {
        files.value = $1t.quickTag.value.tracks.map((track: QuickTagFile) => ({
            path: track.path,
            filename: track.path.split('/').pop() || track.path.split('\\').pop() || track.path,
            selected: true,
            title: track.title,
            artist: track.artists?.join(', '),
            tags: {
                title: track.title,
                artist: track.artists?.join(', '),
                album: track.tags['ALBUM']?.[0] || track.tags['©alb']?.[0] || '',
                date: track.year?.toString() || '',
                genre: track.genres?.join(', ')
            }
        }));

        $q.notify({
            message: `Loaded ${files.value.length} files from QuickTag`,
            color: 'primary',
            position: 'top-right',
            timeout: 2000
        });
    } else {
        $q.notify({
            message: 'No files in QuickTag. Please use QuickTag to load files first.',
            color: 'warning',
            position: 'top-right'
        });
    }
}

function toggleFile(file: BulkFile) {
    file.selected = !file.selected;
}

function selectAll() {
    files.value.forEach(f => f.selected = true);
}

function deselectAll() {
    files.value.forEach(f => f.selected = false);
}

function preview() {
    if (selectedCount.value === 0) return;

    // Get first selected file for preview
    const file = files.value.find(f => f.selected);
    if (!file) return;

    // Create a copy of tags
    const previewTags = { ...file.tags };

    // Apply operations
    applyOperationsToTags(previewTags);

    // Show preview
    let preview = `Preview for: ${file.filename}\n\n`;
    preview += `Selected files: ${selectedCount.value}\n\n`;

    for (const [key, value] of Object.entries(previewTags)) {
        const oldValue = file.tags[key] || '';
        if (oldValue !== value) {
            preview += `${key.toUpperCase()}:\n`;
            preview += `  Before: '${oldValue}'\n`;
            preview += `  After:  '${value}'\n\n`;
        }
    }

    if (preview === `Preview for: ${file.filename}\n\n` + `Selected files: ${selectedCount.value}\n\n`) {
        preview += 'No changes detected!';
    }

    previewText.value = preview;
}

async function apply() {
    if (selectedCount.value === 0 || !hasEnabledOperations.value) return;

    // Confirm
    const confirmed = await new Promise<boolean>(resolve => {
        $q.dialog({
            title: 'Confirm',
            message: `Apply changes to ${selectedCount.value} file(s)?`,
            cancel: true,
            persistent: true
        }).onOk(() => resolve(true))
          .onCancel(() => resolve(false));
    });

    if (!confirmed) return;

    try {
        // Apply to each selected file
        const selectedFiles = files.value.filter(f => f.selected);

        for (const file of selectedFiles) {
            const newTags = { ...file.tags };
            applyOperationsToTags(newTags);

            // Update local tags
            file.tags = newTags;

            // Update in QuickTag if the file exists there
            const qtTrack = $1t.quickTag.value.tracks.find((t: QuickTagFile) => t.path === file.path);
            if (qtTrack) {
                if (newTags.title) qtTrack.title = newTags.title;
                if (newTags.artist) qtTrack.artists = [newTags.artist];
                // Note: album and date are stored in tags property, not as direct fields
            }
        }

        $q.notify({
            message: `Preview updated for ${selectedFiles.length} files! Use QuickTag to save changes.`,
            color: 'info',
            position: 'top-right',
            timeout: 3000
        });

        previewText.value = '';

    } catch (e) {
        console.error('Failed to apply changes:', e);
        $q.notify({
            message: 'Failed to apply changes',
            color: 'negative',
            position: 'top-right'
        });
    }
}

function applyOperationsToTags(tags: Record<string, any>) {
    const ops = operations.value;

    // Replace
    if (ops.replace.enabled && ops.replace.find) {
        const field = ops.replace.field;
        if (tags[field]) {
            const original = String(tags[field]);
            if (ops.replace.useRegex) {
                try {
                    const flags = ops.replace.caseSensitive ? '' : 'gi';
                    const regex = new RegExp(ops.replace.find, flags);
                    tags[field] = original.replace(regex, ops.replace.replaceWith);
                } catch (e) {
                    console.error('Regex error:', e);
                }
            } else {
                if (ops.replace.caseSensitive) {
                    tags[field] = original.replace(
                        new RegExp(ops.replace.find.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
                        ops.replace.replaceWith
                    );
                } else {
                    tags[field] = original.replace(
                        new RegExp(ops.replace.find.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'),
                        ops.replace.replaceWith
                    );
                }
            }
        }
    }

    // Trim
    if (ops.trim.enabled) {
        const fieldsToTrim = ops.trim.field === 'ALL FIELDS'
            ? Object.keys(tags)
            : [ops.trim.field];

        for (const field of fieldsToTrim) {
            if (tags[field] && typeof tags[field] === 'string') {
                let value = tags[field];
                if (ops.trim.leading) value = value.trimStart();
                if (ops.trim.trailing) value = value.trimEnd();
                tags[field] = value;
            }
        }
    }

    // Copy
    if (ops.copy.enabled) {
        const fromValue = tags[ops.copy.from];
        if (fromValue) {
            if (ops.copy.append && tags[ops.copy.to]) {
                tags[ops.copy.to] = tags[ops.copy.to] + ' ' + fromValue;
            } else {
                tags[ops.copy.to] = fromValue;
            }
        }
    }

    // Case
    if (ops.case.enabled) {
        const field = ops.case.field;
        if (tags[field] && typeof tags[field] === 'string') {
            const value = tags[field];
            switch (ops.case.mode) {
                case 'upper':
                    tags[field] = value.toUpperCase();
                    break;
                case 'lower':
                    tags[field] = value.toLowerCase();
                    break;
                case 'title':
                    tags[field] = value.replace(/\w\S*/g, (txt) =>
                        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
                    );
                    break;
                case 'sentence':
                    tags[field] = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
                    break;
            }
        }
    }

    // Add Prefix/Suffix
    if (ops.add.enabled) {
        const field = ops.add.field;
        if (tags[field]) {
            tags[field] = ops.add.prefix + tags[field] + ops.add.suffix;
        }
    }

    // Remove
    if (ops.remove.enabled && ops.remove.text) {
        const field = ops.remove.field;
        if (tags[field]) {
            tags[field] = String(tags[field]).replace(
                new RegExp(ops.remove.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
                ''
            );
        }
    }

    // Split
    if (ops.split.enabled && ops.split.separator) {
        const value = tags[ops.split.source];
        if (value && typeof value === 'string') {
            const parts = value.split(ops.split.separator, 2);
            if (parts.length >= 1) {
                tags[ops.split.leftField] = parts[0].trim();
            }
            if (parts.length >= 2) {
                tags[ops.split.rightField] = parts[1].trim();
            }
        }
    }
}

// Player functions
function togglePlay() {
    if ($1t.player.value.playing) {
        // Pause
        $1t.player.value.pause();
    } else {
        // Play current or first file
        if (!currentTrack.value && files.value.length > 0) {
            playTrack(0);
        } else if (currentTrack.value) {
            $1t.player.value.play();
        }
    }
}

function playTrack(index: number) {
    if (index < 0 || index >= files.value.length) return;

    const file = files.value[index];
    currentTrack.value = file;
    currentTrackIndex.value = index;

    // Use OneTagger's player
    $1t.player.value.loadTrack(file.path);
    $1t.player.value.play();
}

function stopPlayback() {
    $1t.player.value.stop();
    currentTrack.value = null;
    currentTrackIndex.value = -1;
}

function playNext() {
    if (currentTrackIndex.value < files.value.length - 1) {
        playTrack(currentTrackIndex.value + 1);
    }
}

function playPrevious() {
    if (currentTrackIndex.value > 0) {
        playTrack(currentTrackIndex.value - 1);
    }
}

function onVolumeChange(val: number | null) {
    if (val !== null) {
        $1t.player.value.setVolume(val);
    }
}

onMounted(() => {
    // Load from QuickTag if files are available
    loadFromQuickTag();
});
</script>

<style lang="scss" scoped>
.bulk-tag-container {
    padding: 0;
}

.file-item {
    border-bottom: 1px solid #2d2d2d;

    &:hover {
        background-color: #2d2d2d;
    }

    &.playing-track {
        background-color: #264f78;
        border-left: 3px solid #0d7377;
    }
}

.operation-panel {
    border-radius: 4px;
    background-color: #252526;
}

.preview-box {
    max-height: 150px;
    overflow-y: auto;
    background-color: #1e1e1e;
    padding: 8px;
    border-radius: 4px;

    pre {
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
}

.player-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    border-top: 1px solid #3c3c3c;
    z-index: 1000;
}
</style>
