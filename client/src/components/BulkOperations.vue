<template>
<div class="bulk-operations">
    <div class="text-subtitle2 text-primary q-mb-md">Select Operations</div>

    <!-- Replace Text -->
    <q-expansion-item
        v-model="operations.replace.enabled"
        icon="mdi-find-replace"
        label="Replace Text"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-select dense filled v-model="operations.replace.field" :options="fieldOptions" label="Field" />
                </div>
                <div>
                    <q-input dense filled v-model="operations.replace.find" label="Find" placeholder="Text to find" />
                </div>
                <div>
                    <q-input dense filled v-model="operations.replace.replaceWith" label="Replace with" placeholder="Replacement text" />
                </div>
                <div class="row q-gutter-md">
                    <q-checkbox v-model="operations.replace.caseSensitive" label="Case sensitive" dense />
                    <q-checkbox v-model="operations.replace.useRegex" label="Use regex" dense />
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Trim Whitespace -->
    <q-expansion-item
        v-model="operations.trim.enabled"
        icon="mdi-format-text"
        label="Trim Whitespace"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-select dense filled v-model="operations.trim.field" :options="['ALL FIELDS', ...fieldOptions]" label="Field" />
                </div>
                <div class="row q-gutter-md">
                    <q-checkbox v-model="operations.trim.leading" label="Leading" dense />
                    <q-checkbox v-model="operations.trim.trailing" label="Trailing" dense />
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Change Case -->
    <q-expansion-item
        v-model="operations.changeCase.enabled"
        icon="mdi-format-letter-case"
        label="Change Case"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-select dense filled v-model="operations.changeCase.field" :options="['ALL FIELDS', ...fieldOptions]" label="Field" />
                </div>
                <div>
                    <q-select dense filled v-model="operations.changeCase.case" :options="['Title Case', 'UPPERCASE', 'lowercase']" label="Case" />
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Add Prefix/Suffix -->
    <q-expansion-item
        v-model="operations.addPrefixSuffix.enabled"
        icon="mdi-format-text-wrapping-wrap"
        label="Add Prefix/Suffix"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-select dense filled v-model="operations.addPrefixSuffix.field" :options="fieldOptions" label="Field" />
                </div>
                <div>
                    <q-input dense filled v-model="operations.addPrefixSuffix.prefix" label="Prefix" placeholder="Text to add at the beginning" />
                </div>
                <div>
                    <q-input dense filled v-model="operations.addPrefixSuffix.suffix" label="Suffix" placeholder="Text to add at the end" />
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Remove Text -->
    <q-expansion-item
        v-model="operations.removeText.enabled"
        icon="mdi-eraser"
        label="Remove Text"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-select dense filled v-model="operations.removeText.field" :options="fieldOptions" label="Field" />
                </div>
                <div>
                    <q-input dense filled v-model="operations.removeText.removeText" label="Text to remove" placeholder="Text to remove from field" />
                </div>
                <div>
                    <q-checkbox v-model="operations.removeText.caseSensitive" label="Case sensitive" dense />
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Split Field -->
    <q-expansion-item
        v-model="operations.splitField.enabled"
        icon="mdi-call-split"
        label="Split Field"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-select dense filled v-model="operations.splitField.field" :options="fieldOptions" label="Field" />
                </div>
                <div>
                    <q-input dense filled v-model="operations.splitField.separator" label="Separator" placeholder="e.g., , or ; or /" />
                </div>
                <div>
                    <q-select dense filled v-model="operations.splitField.keepPart" :options="['first', 'last', 'all (join with space)']" label="Keep Part" />
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Number Tracks -->
    <q-expansion-item
        v-model="operations.numberTracks.enabled"
        icon="mdi-format-list-numbered"
        label="Number Tracks"
        header-class="bg-dark text-grey-3"
        class="q-mb-sm">
        <q-card class="bg-darker q-pa-md">
            <div class="q-gutter-md">
                <div>
                    <q-input dense filled v-model.number="operations.numberTracks.startFrom" type="number" label="Start from" min="1" />
                </div>
                <div>
                    <q-input dense filled v-model.number="operations.numberTracks.padding" type="number" label="Zero padding" min="1" max="4" />
                    <div class="text-caption text-grey-5 q-mt-xs">e.g., 2 = 01, 02, 03...</div>
                </div>
            </div>
        </q-card>
    </q-expansion-item>

    <!-- Apply Button -->
    <div class="row justify-end q-mt-lg">
        <q-btn
            push
            color="primary"
            label="Apply to Selected Tracks"
            icon="mdi-check"
            @click="applyOperations"
            :disable="!hasEnabledOperations"
            class="text-black"
        />
    </div>
</div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';

const props = defineProps<{
    selectedTracks: any[]
}>();

const emit = defineEmits(['close']);

const $q = useQuasar();

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
    changeCase: {
        enabled: false,
        field: 'title',
        case: 'Title Case'
    },
    addPrefixSuffix: {
        enabled: false,
        field: 'title',
        prefix: '',
        suffix: ''
    },
    removeText: {
        enabled: false,
        field: 'title',
        removeText: '',
        caseSensitive: false
    },
    splitField: {
        enabled: false,
        field: 'artist',
        separator: ',',
        keepPart: 'first'
    },
    numberTracks: {
        enabled: false,
        startFrom: 1,
        padding: 2
    }
});

const fieldOptions = [
    'title',
    'artist',
    'album',
    'album_artist',
    'genre',
    'date',
    'year',
    'comment'
];

const hasEnabledOperations = computed(() =>
    Object.values(operations.value).some((op: any) => op.enabled)
);

function applyOperations() {
    if (!hasEnabledOperations.value) return;

    const confirmed = $q.dialog({
        title: 'Confirm Bulk Operation',
        message: `Apply operations to ${props.selectedTracks.length} tracks?`,
        cancel: true,
        persistent: true
    });

    confirmed.onOk(async () => {
        const progressNotif = $q.notify({
            group: false,
            timeout: 0,
            spinner: true,
            message: 'Processing tracks...',
            position: 'top-right'
        });

        try {
            let successCount = 0;

            for (let i = 0; i < props.selectedTracks.length; i++) {
                const track = props.selectedTracks[i];

                try {
                    applyToTrack(track, i);
                    successCount++;
                } catch (e) {
                    console.error(`Failed to process track:`, e);
                }

                progressNotif({
                    message: `Processing ${i + 1}/${props.selectedTracks.length} tracks...`
                });
            }

            progressNotif();

            $q.notify({
                message: `Successfully processed ${successCount}/${props.selectedTracks.length} tracks!`,
                color: 'positive',
                position: 'top-right',
                timeout: 3000
            });

            emit('close');
        } catch (e) {
            progressNotif();
            $q.notify({
                message: 'Failed to apply operations',
                color: 'negative',
                position: 'top-right'
            });
        }
    });
}

function applyToTrack(track: any, index: number) {
    const ops = operations.value;

    // Replace
    if (ops.replace.enabled) {
        const field = ops.replace.field.toLowerCase();
        if (track[field]) {
            track[field] = applyReplace(track[field], ops.replace);
        }
    }

    // Trim
    if (ops.trim.enabled) {
        if (ops.trim.field === 'ALL FIELDS') {
            for (const key in track) {
                if (typeof track[key] === 'string') {
                    track[key] = applyTrim(track[key], ops.trim);
                }
            }
        } else {
            const field = ops.trim.field.toLowerCase();
            if (track[field]) {
                track[field] = applyTrim(track[field], ops.trim);
            }
        }
    }

    // Change Case
    if (ops.changeCase.enabled) {
        if (ops.changeCase.field === 'ALL FIELDS') {
            for (const key in track) {
                if (typeof track[key] === 'string') {
                    track[key] = applyChangeCase(track[key], ops.changeCase.case);
                }
            }
        } else {
            const field = ops.changeCase.field.toLowerCase();
            if (track[field]) {
                track[field] = applyChangeCase(track[field], ops.changeCase.case);
            }
        }
    }

    // Add Prefix/Suffix
    if (ops.addPrefixSuffix.enabled) {
        const field = ops.addPrefixSuffix.field.toLowerCase();
        if (track[field]) {
            if (ops.addPrefixSuffix.prefix) {
                track[field] = ops.addPrefixSuffix.prefix + track[field];
            }
            if (ops.addPrefixSuffix.suffix) {
                track[field] = track[field] + ops.addPrefixSuffix.suffix;
            }
        }
    }

    // Remove Text
    if (ops.removeText.enabled && ops.removeText.removeText) {
        const field = ops.removeText.field.toLowerCase();
        if (track[field]) {
            const flags = ops.removeText.caseSensitive ? 'g' : 'gi';
            const regex = new RegExp(ops.removeText.removeText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), flags);
            track[field] = track[field].replace(regex, '');
        }
    }

    // Split Field
    if (ops.splitField.enabled && ops.splitField.separator) {
        const field = ops.splitField.field.toLowerCase();
        if (track[field]) {
            const parts = track[field].split(ops.splitField.separator);
            if (ops.splitField.keepPart === 'first') {
                track[field] = parts[0]?.trim() || track[field];
            } else if (ops.splitField.keepPart === 'last') {
                track[field] = parts[parts.length - 1]?.trim() || track[field];
            } else if (ops.splitField.keepPart === 'all (join with space)') {
                track[field] = parts.map((p: string) => p.trim()).join(' ');
            }
        }
    }

    // Number Tracks
    if (ops.numberTracks.enabled) {
        const trackNum = ops.numberTracks.startFrom + index;
        const padded = trackNum.toString().padStart(ops.numberTracks.padding, '0');
        track.track = padded;
    }
}

function applyReplace(value: string, opts: any): string {
    if (opts.useRegex) {
        const flags = opts.caseSensitive ? 'g' : 'gi';
        const regex = new RegExp(opts.find, flags);
        return value.replace(regex, opts.replaceWith);
    } else {
        const flags = opts.caseSensitive ? 'g' : 'gi';
        const regex = new RegExp(opts.find.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), flags);
        return value.replace(regex, opts.replaceWith);
    }
}

function applyTrim(value: string, opts: any): string {
    if (opts.leading && opts.trailing) {
        return value.trim();
    } else if (opts.leading) {
        return value.replace(/^\s+/, '');
    } else if (opts.trailing) {
        return value.replace(/\s+$/, '');
    }
    return value;
}

function applyChangeCase(value: string, caseType: string): string {
    if (caseType === 'Title Case') {
        return value.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    } else if (caseType === 'UPPERCASE') {
        return value.toUpperCase();
    } else if (caseType === 'lowercase') {
        return value.toLowerCase();
    }
    return value;
}
</script>

<style scoped>
.bulk-operations {
    max-height: 70vh;
    overflow-y: auto;
}
</style>
